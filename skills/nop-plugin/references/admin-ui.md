# Admin UI: configuration page, routes, admin menu

## Defaults class

```csharp
namespace Nop.Plugin.Widgets.MyWidget;

public static class MyWidgetDefaults
{
    public static string SystemName => "Widgets.MyWidget";
    public static string ConfigurationRouteName => "Plugin.Widgets.MyWidget.Configure";
}
```

## Route (Infrastructure/RouteProvider.cs)

```csharp
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Routing;
using Nop.Web.Framework;
using Nop.Web.Framework.Mvc.Routing;

namespace Nop.Plugin.Widgets.MyWidget.Infrastructure;

public class RouteProvider : IRouteProvider
{
    public void RegisterRoutes(IEndpointRouteBuilder endpointRouteBuilder)
    {
        endpointRouteBuilder.MapControllerRoute(name: MyWidgetDefaults.ConfigurationRouteName,
            pattern: "Admin/MyWidget/Configure",
            defaults: new { controller = "MyWidget", action = "Configure", area = AreaNames.ADMIN });
    }

    public int Priority => 0;
}
```

`AreaNames.ADMIN` is the constant in 4.70–4.90. Code written for much older versions uses `AreaNames.Admin`; replace it.

## Settings and model

```csharp
using Nop.Core.Configuration;

public class MyWidgetSettings : ISettings
{
    public string Message { get; set; }
}
```

```csharp
using Nop.Web.Framework.Models;
using Nop.Web.Framework.Mvc.ModelBinding;

public record ConfigurationModel : BaseNopModel
{
    public int ActiveStoreScopeConfiguration { get; set; }

    [NopResourceDisplayName("Plugins.Widgets.MyWidget.Fields.Message")]
    public string Message { get; set; }
    public bool Message_OverrideForStore { get; set; }
}
```

Models are `record` types deriving from `BaseNopModel` (or `BaseNopEntityModel` when they carry an `Id`).

## Controller

```csharp
using Microsoft.AspNetCore.Mvc;
using Nop.Core;
using Nop.Plugin.Widgets.MyWidget.Models;
using Nop.Services.Configuration;
using Nop.Services.Localization;
using Nop.Services.Messages;
using Nop.Services.Security;
using Nop.Web.Framework;
using Nop.Web.Framework.Controllers;
using Nop.Web.Framework.Mvc.Filters;

namespace Nop.Plugin.Widgets.MyWidget.Controllers;

[Area(AreaNames.ADMIN)]
[AuthorizeAdmin]
[AutoValidateAntiforgeryToken]
public class MyWidgetController : BasePluginController
{
    protected readonly ILocalizationService _localizationService;
    protected readonly INotificationService _notificationService;
    protected readonly ISettingService _settingService;
    protected readonly IStoreContext _storeContext;

    public MyWidgetController(ILocalizationService localizationService,
        INotificationService notificationService,
        ISettingService settingService,
        IStoreContext storeContext)
    {
        _localizationService = localizationService;
        _notificationService = notificationService;
        _settingService = settingService;
        _storeContext = storeContext;
    }

    [CheckPermission(StandardPermission.Configuration.MANAGE_WIDGETS)]
    public async Task<IActionResult> Configure()
    {
        var storeScope = await _storeContext.GetActiveStoreScopeConfigurationAsync();
        var settings = await _settingService.LoadSettingAsync<MyWidgetSettings>(storeScope);

        var model = new ConfigurationModel
        {
            Message = settings.Message,
            ActiveStoreScopeConfiguration = storeScope
        };

        if (storeScope > 0)
            model.Message_OverrideForStore = await _settingService.SettingExistsAsync(settings, x => x.Message, storeScope);

        return View("~/Plugins/Widgets.MyWidget/Views/Configure.cshtml", model);
    }

    [HttpPost]
    [CheckPermission(StandardPermission.Configuration.MANAGE_WIDGETS)]
    public async Task<IActionResult> Configure(ConfigurationModel model)
    {
        if (!ModelState.IsValid)
            return await Configure();

        var storeScope = await _storeContext.GetActiveStoreScopeConfigurationAsync();
        var settings = await _settingService.LoadSettingAsync<MyWidgetSettings>(storeScope);

        settings.Message = model.Message;

        await _settingService.SaveSettingOverridablePerStoreAsync(settings, x => x.Message, model.Message_OverrideForStore, storeScope, false);
        await _settingService.ClearCacheAsync();

        _notificationService.SuccessNotification(await _localizationService.GetResourceAsync("Admin.Plugins.Saved"));

        return await Configure();
    }
}
```

Pick the permission that matches the plugin type: `MANAGE_WIDGETS`, `MANAGE_PAYMENT_METHODS`, `MANAGE_SHIPPING_SETTINGS`, `MANAGE_TAX_SETTINGS`, `MANAGE_EXTERNAL_AUTHENTICATION_METHODS`, `MANAGE_MULTIFACTOR_AUTHENTICATION_METHODS`, or `MANAGE_PLUGINS` for Misc plugins. All live in `StandardPermission.Configuration` — confirm the exact name in `src/Libraries/Nop.Services/Security/StandardPermission.cs` of the target version.

Views are referenced by their **deployed** path: `~/Plugins/{Group}.{Name}/Views/X.cshtml`.

## Views

`Views/_ViewImports.cshtml` (copy from a core plugin of the same version):

```cshtml
@inherits Nop.Web.Framework.Mvc.Razor.NopRazorPage<TModel>
@addTagHelper *, Microsoft.AspNetCore.Mvc.TagHelpers
@addTagHelper *, Nop.Web.Framework

@using Microsoft.AspNetCore.Mvc.ViewFeatures
@using Nop.Web.Areas.Admin.Components
@using Nop.Web.Framework.UI
@using Nop.Web.Framework.Extensions
@using System.Text.Encodings.Web
```

`Views/Configure.cshtml`:

```cshtml
@model Nop.Plugin.Widgets.MyWidget.Models.ConfigurationModel
@{
    Layout = "_ConfigurePlugin";
}

@await Component.InvokeAsync(typeof(StoreScopeConfigurationViewComponent))

<form asp-controller="MyWidget" asp-action="Configure" method="post">
    <div class="cards-group">
        <div class="card card-default">
            <div class="card-body">
                <div class="form-group row">
                    <div class="col-md-3">
                        <nop-override-store-checkbox asp-for="Message_OverrideForStore" asp-input="Message" asp-store-scope="@Model.ActiveStoreScopeConfiguration" />
                        <nop-label asp-for="Message" />
                    </div>
                    <div class="col-md-9">
                        <nop-editor asp-for="Message" />
                        <span asp-validation-for="Message"></span>
                    </div>
                </div>
                <div class="form-group row">
                    <div class="col-md-9 offset-md-3">
                        <button type="submit" name="save" class="btn btn-primary">@T("Admin.Common.Save")</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</form>
```

Admin tag helpers: `nop-label`, `nop-editor`, `nop-textarea`, `nop-select`, `nop-nested-setting`, `nop-override-store-checkbox`, `nop-card`, `nop-cards`. Admin UI is AdminLTE 3.2 + Bootstrap 4.6 in all three versions.

## Admin menu item (4.80 and 4.90)

`IAdminMenuPlugin` is marked `[Obsolete]` from 4.80 and its parameter type changed from `SiteMapNode` (4.70) to `AdminMenuItem`. Use the event instead.

**Simplest — derive from `BaseAdminMenuCreatedEventConsumer`** (used by core's Zettle plugin):

```csharp
using Nop.Services.Plugins;
using Nop.Services.Security;
using Nop.Web.Framework.Events;
using Nop.Web.Framework.Menu;

namespace Nop.Plugin.Widgets.MyWidget.Services;

public class AdminMenuEventConsumer : BaseAdminMenuCreatedEventConsumer
{
    protected readonly IPermissionService _permissionService;

    public AdminMenuEventConsumer(IPermissionService permissionService, IPluginManager<IPlugin> pluginManager)
        : base(pluginManager)
    {
        _permissionService = permissionService;
    }

    protected override async Task<bool> CheckAccessAsync()
    {
        return await _permissionService.AuthorizeAsync(StandardPermission.Configuration.MANAGE_PLUGINS);
    }

    protected override string PluginSystemName => MyWidgetDefaults.SystemName;

    protected override MenuItemInsertType InsertType => MenuItemInsertType.Before;

    protected override string BeforeMenuSystemName => "Local plugins";
}
```

By default it inserts `plugin.GetAdminMenuItem()` — the plugin's FriendlyName linking to `GetConfigurationPageUrl()`. Override `GetAdminMenuItemAsync(IPlugin plugin)` to return a custom `AdminMenuItem` with child nodes. It returns early while the plugin is not yet installed, which avoids the null-reference bug people hit with hand-written consumers.

**Custom placement — handle the event directly:**

```csharp
public class AdminMenuEventConsumer : IConsumer<AdminMenuCreatedEvent>
{
    public async Task HandleEventAsync(AdminMenuCreatedEvent eventMessage)
    {
        // check permissions first
        eventMessage.RootMenuItem.InsertBefore("Local plugins", new AdminMenuItem
        {
            SystemName = "Widgets.MyWidget.Menu",
            Title = "My widget",
            Url = eventMessage.GetMenuItemUrl("MyWidget", "Configure"),
            IconClass = "far fa-dot-circle",
            Visible = true
        });
    }
}
```

`AdminMenuItem` members: `SystemName`, `Title`, `Url`, `IconClass`, `Visible`, `OpenUrlInNewTab`, `PermissionNames`, `ChildNodes`, plus `InsertBefore`, `InsertAfter`, `GetItemBySystemName`, `ContainsSystemName`. To add under the "Third party plugins" node use `ThirdPartyPluginsMenuItemCreatedEvent` (its `MenuItem` is that node).

## 4.70 admin menu (only when targeting 4.70)

```csharp
public class MyWidgetPlugin : BasePlugin, IWidgetPlugin, IAdminMenuPlugin
{
    public Task ManageSiteMapAsync(SiteMapNode rootNode)
    {
        var item = new SiteMapNode
        {
            SystemName = "Widgets.MyWidget",
            Title = "My widget",
            ControllerName = "MyWidget",
            ActionName = "Configure",
            IconClass = "far fa-dot-circle",
            Visible = true,
            RouteValues = new RouteValueDictionary { { "area", AreaNames.ADMIN } }
        };
        var pluginNode = rootNode.ChildNodes.FirstOrDefault(x => x.SystemName == "Third party plugins");
        (pluginNode?.ChildNodes ?? rootNode.ChildNodes).Add(item);
        return Task.CompletedTask;
    }
}
```
