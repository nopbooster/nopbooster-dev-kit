# Data, migrations, events, widgets, services, scheduled tasks

## Own tables

Entity (in `Domain/`):

```csharp
using Nop.Core;

namespace Nop.Plugin.Misc.MyFeature.Domain;

public class MyRecord : BaseEntity
{
    public int ProductId { get; set; }
    public string Note { get; set; }
    public DateTime CreatedOnUtc { get; set; }
}
```

`BaseEntity` provides `Id`. Table name = class name. Columns are created by convention from properties; customise with a builder only when needed (`Data/Mapping/`):

```csharp
using FluentMigrator.Builders.Create.Table;
using Nop.Data.Mapping.Builders;

public class MyRecordBuilder : NopEntityBuilder<MyRecord>
{
    public override void MapEntity(CreateTableExpressionBuilder table)
    {
        table.WithColumn(nameof(MyRecord.Note)).AsString(400).Nullable();
    }
}
```

Schema migration (`Data/SchemaMigration.cs`):

```csharp
using FluentMigrator;
using Nop.Data.Extensions;
using Nop.Data.Migrations;

namespace Nop.Plugin.Misc.MyFeature.Data;

[NopMigration("2026/10/31 12:00:00", "Misc.MyFeature base schema", MigrationProcessType.Installation)]
public class SchemaMigration : AutoReversingMigration
{
    public override void Up()
    {
        Create.TableFor<MyRecord>();
    }
}
```

- The date string must be unique across all migrations ever loaded — use the real date/time you write it.
- `MigrationProcessType`: `Installation` (runs when the plugin is installed), `Update` (runs on app start when not yet applied — use for changes in later plugin versions), `NoMatter`.
- On uninstall nopCommerce runs the plugin assembly's **down** migrations, so `AutoReversingMigration` drops the table automatically. For hand-written `Migration` classes implement `Down()` yourself.

Later change (version 1.01):

```csharp
[NopMigration("2026/12/01 09:00:00", "Misc.MyFeature 1.01 add Status", MigrationProcessType.Update)]
public class AddStatusMigration : Migration
{
    public override void Up()
    {
        if (!Schema.Table(nameof(MyRecord)).Column("Status").Exists())
            Alter.Table(nameof(MyRecord)).AddColumn("Status").AsInt32().NotNullable().WithDefaultValue(0);
    }

    public override void Down() { }
}
```

Locale-resource-only updates follow the same pattern (see `Migrations/UpgradeTo470/LocalizationMigration.cs` in the core Google Analytics plugin): guard with `if (!DataSettingsManager.IsDatabaseInstalled()) return;`, resolve `ILocalizationService` via `EngineContext.Current.Resolve<ILocalizationService>()`, then call the synchronous `AddOrUpdateLocaleResource(dictionary, languageId)`.

Data access: inject `IRepository<MyRecord>` and use `GetByIdAsync`, `GetAllAsync(query => …)`, `GetAllPagedAsync(...)`, `InsertAsync`, `UpdateAsync`, `DeleteAsync`. Never query the DbContext directly; nopCommerce uses Linq2DB, not Entity Framework.

## Registering services (Infrastructure/NopStartup.cs)

```csharp
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Nop.Core.Infrastructure;

namespace Nop.Plugin.Misc.MyFeature.Infrastructure;

public class NopStartup : INopStartup
{
    public void ConfigureServices(IServiceCollection services, IConfiguration configuration)
    {
        services.AddScoped<IMyRecordService, MyRecordService>();
        // services.AddHttpClient<MyApiClient>().WithProxy();   // WithProxy: Nop.Web.Framework.Infrastructure.Extensions
    }

    public void Configure(IApplicationBuilder application) { }

    public int Order => 1;
}
```

Core plugins use a small `Order` (e.g. 1) for their own registrations. To **replace a core service**, register your implementation for the core interface from a startup whose `Order` is greater than core's service registration (`Nop.Web.Framework` NopStartup uses 2000, so use e.g. 3000) and derive from the core class so you override only what you need. Event consumers (`IConsumer<T>`), view components, controllers and `IPermissionConfigManager` are discovered automatically — do not register them.

## Events

```csharp
using Nop.Core.Domain.Orders;
using Nop.Core.Events;
using Nop.Services.Events;

public class EventConsumer :
    IConsumer<OrderPaidEvent>,
    IConsumer<EntityUpdatedEvent<Nop.Core.Domain.Catalog.Product>>
{
    public async Task HandleEventAsync(OrderPaidEvent eventMessage) { var order = eventMessage.Order; … }

    public async Task HandleEventAsync(EntityUpdatedEvent<Nop.Core.Domain.Catalog.Product> eventMessage) { var product = eventMessage.Entity; … }
}
```

- Entity events: `EntityInsertedEvent<T>`, `EntityUpdatedEvent<T>`, `EntityDeletedEvent<T>` for any `BaseEntity`.
- Domain events (in `Nop.Core.Domain.*`): `OrderPlacedEvent`, `OrderPaidEvent`, `OrderAuthorizedEvent`, `OrderStatusChangedEvent`, `OrderRefundedEvent`, `OrderVoidedEvent`, `ShipmentSentEvent`, `CustomerRegisteredEvent`, `CustomerLoggedinEvent`, `ProductReviewApprovedEvent`, … Find the full list with a search for `class .*Event` under `src/Libraries/Nop.Core/Domain` of the target version.
- Model events let a plugin change view models before render: `ModelPreparedEvent<BaseNopModel>` (e.g. add `CustomProperties`), and `AdminTabStripCreated` (Nop.Web.Framework.Events) to add a tab to an admin edit page.
- Consumers run synchronously in the publishing request — keep them fast; push slow work to a scheduled task or queue.

## Widgets

The plugin implements `IWidgetPlugin` (see project-setup.md). The view component:

```csharp
using Microsoft.AspNetCore.Mvc;
using Nop.Web.Framework.Components;
using Nop.Web.Models.Catalog;

namespace Nop.Plugin.Widgets.MyWidget.Components;

public class MyWidgetViewComponent : NopViewComponent
{
    public async Task<IViewComponentResult> InvokeAsync(string widgetZone, object additionalData)
    {
        if (additionalData is not ProductDetailsModel product)
            return Content(string.Empty);

        return View("~/Plugins/Widgets.MyWidget/Views/PublicInfo.cshtml", product);
    }
}
```

- Zones: `PublicWidgetZones` (Nop.Web.Framework.Infrastructure) and `AdminWidgetZones`. Use the constants, not raw strings.
- `additionalData` is the page's model for zones that pass one (product page zones pass `ProductDetailsModel`).
- A widget only renders if its SystemName is in `WidgetSettings.ActiveWidgetSystemNames` — add it on install.
- Public views must also be listed in the `.csproj` as content.
- Scripts: `<script asp-location="Footer">…</script>` and `<link rel="stylesheet" href="~/Plugins/…/Content/x.css" />` (nopCommerce bundles through its tag helpers).

## Scheduled tasks

```csharp
using Nop.Services.ScheduleTasks;

public class MySyncTask : IScheduleTask
{
    public async Task ExecuteAsync() { … }
}
```

Install (and remove on uninstall) a `ScheduleTask` record whose `Type` is the task's assembly-qualified short name:

```csharp
var type = "Nop.Plugin.Misc.MyFeature.Services.MySyncTask, Nop.Plugin.Misc.MyFeature";
if (await _scheduleTaskService.GetTaskByTypeAsync(type) is null)
    await _scheduleTaskService.InsertTaskAsync(new()
    {
        Enabled = true,
        StopOnError = false,
        LastEnabledUtc = DateTime.UtcNow,
        Name = "My feature sync",
        Type = type,
        Seconds = 3600
    });
```

Uninstall: `GetTaskByTypeAsync(type)` then `DeleteTaskAsync(task)`.

## Caching

Use `IStaticCacheManager` with a `CacheKey` defined in your Defaults class, e.g. `new CacheKey("Nop.myfeature.byproduct.{0}", "Nop.myfeature.")`, `await _staticCacheManager.GetAsync(_staticCacheManager.PrepareKeyForDefaultCache(key, productId), async () => …)`, and clear by prefix with `RemoveByPrefixAsync("Nop.myfeature.")` when data changes.
