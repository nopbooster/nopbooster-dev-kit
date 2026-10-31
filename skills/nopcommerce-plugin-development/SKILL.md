---
name: nopcommerce-plugin-development
description: This skill should be used when writing, editing or explaining nopCommerce plugin code (C#, Razor, plugin.json, .csproj) — "nopCommerce plugin", "nop plugin", "widget plugin", "payment plugin", "shipping plugin", "admin page for my plugin", "plugin settings", "plugin migration", "event consumer", "IWidgetPlugin", "BasePlugin", "INopStartup", "IRouteProvider". Targets nopCommerce 5.00 by default and knows how 4.70, 4.80 and 4.90 differ.
---

# nopCommerce plugin development (5.00 default)

Apply these rules whenever producing or changing nopCommerce plugin code. They were checked against the nopCommerce source of releases 4.70.5, 4.80.9, 4.90.8 and 5.00.0.

## 1. Establish the target version first

1. Look for the version before writing code: `SupportedVersions` in an existing `plugin.json`, `<TargetFramework>` in a plugin `.csproj`, or `NopVersion.CURRENT_VERSION` in `src/Libraries/Nop.Core/NopVersion.cs`.
2. If nothing tells you, target **5.00** and say so in one line. (4.70–4.90 run on .NET 8/9, which lose Microsoft support on 10 November 2026.)
3. Version facts:

| | 4.70 | 4.80 | 4.90 | 5.00 |
|---|---|---|---|---|
| .NET | net8.0 | net9.0 | net9.0 | **net10.0** |
| Visual Studio | 17.9+ | 17.12+ | 17.14+ | 2026 (18.x) |
| `SupportedVersions` | `["4.70"]` | `["4.80"]` | `["4.90"]` | `["5.00"]` |
| Admin menu | `IAdminMenuPlugin` + `SiteMapNode` | `AdminMenuCreatedEvent` | `AdminMenuCreatedEvent` | same |
| Permission check | `IPermissionService.AuthorizeAsync(StandardPermissionProvider.X)` | `[CheckPermission(StandardPermission.Area.X)]` | same as 4.80 | same as 4.80 |
| Object mapping | AutoMapper | AutoMapper | AutoMapper | **Mapster** via `BaseMapperProfile` |
| `IWebHelper` namespace | `Nop.Core` | `Nop.Core` | `Nop.Core` | **`Nop.Services.Helpers`** |

Minor releases (e.g. 4.90.0–4.90.8) are binary compatible: a plugin built for 4.90 works on every 4.90.x.

5.00 specifics when writing new code: derive mapping profiles from `BaseMapperProfile`; `using Nop.Services.Helpers;` for `IWebHelper` and `using Nop.Services.Themes;` for `IThemeContext`; only async service methods exist; forums, news and polls are plugins now (`Nop.Plugin.Misc.Forums/News/Polls`), not core; in migrations use `this.AddOrUpdateLocaleResource(dict)`. Details: the `nop-upgrade` skill's `references/490-to-500.md`.

## 2. Non-negotiable conventions

- **Naming:** project `Nop.Plugin.{Group}.{Name}`, SystemName `{Group}.{Name}`, output folder `Presentation/Nop.Web/Plugins/{Group}.{Name}`. Common groups: `Widgets`, `Payments`, `Shipping`, `Tax`, `Misc`, `ExternalAuth`, `DiscountRules`, `Pickup`, `ExchangeRate`, `MultiFactorAuth`, `Search`.
- **Everything async.** Use the `...Async` service methods. Never block with `.Result` / `.Wait()`.
- **Extend, never edit core.** Change behaviour through events, widgets, DI overrides in `INopStartup`, or view overrides in a theme — not by modifying `Nop.*` projects.
- **Classes `public`, members `protected virtual`/`public virtual`** where core does the same, so other developers can override.
- **Namespaces are file-scoped** (`namespace X;`) and the 4.90/5.00 projects use `ImplicitUsings`.
- **Localization:** every user-facing string is a locale resource named `Plugins.{Group}.{Name}.{Key}`. Add them in `InstallAsync` with `AddOrUpdateLocaleResourceAsync(Dictionary<string,string>)` and remove in `UninstallAsync` with `DeleteLocaleResourcesAsync("Plugins.{Group}.{Name}")`.
- **Settings:** a class implementing `ISettings`, saved with `ISettingService.SaveSettingAsync` on install, deleted with `DeleteSettingAsync<T>()` on uninstall. For multi-store support use `LoadSettingAsync<T>(storeScope)` and `SaveSettingOverridablePerStoreAsync`.
- **Admin controllers:** inherit `BasePluginController` and carry `[Area(AreaNames.ADMIN)]`, `[AuthorizeAdmin]`, `[AutoValidateAntiforgeryToken]`; protect each action with `[CheckPermission(...)]` (4.80+).
- **Always call `base.InstallAsync()` / `base.UninstallAsync()`** at the end of the overrides.

## 3. Minimal file set

```
Nop.Plugin.{Group}.{Name}/
  Nop.Plugin.{Group}.{Name}.csproj
  plugin.json
  logo.png
  {Name}Plugin.cs            // BasePlugin + plugin-type interface(s)
  {Name}Settings.cs          // ISettings (if configurable)
  {Name}Defaults.cs          // SystemName, route names, constants
  Controllers/{Name}Controller.cs
  Models/ConfigurationModel.cs
  Views/Configure.cshtml
  Views/_ViewImports.cshtml
  Infrastructure/RouteProvider.cs   // only if custom routes
  Infrastructure/NopStartup.cs      // only if registering services
  Components/…ViewComponent.cs      // widgets
  Domain/, Data/                    // only if own tables
  Services/                         // services + EventConsumer
```

## 4. Where to look next

Read only the reference that matches the task:

- `references/project-setup.md` — exact `.csproj` and `plugin.json` for 5.00 (and the 4.70–4.90 differences), the plugin class, install/uninstall/update.
- `references/admin-ui.md` — configuration page, controller, routes, admin menu items, multi-store settings.
- `references/permissions.md` — `[CheckPermission]`, `StandardPermission` constants, adding custom permissions.
- `references/data-events-widgets.md` — entities, `NopMigration`, events (`IConsumer<T>`), widgets, `INopStartup`, schedule tasks.

## 5. Before saying a plugin is done

1. The project builds (`dotnet build` from the solution root, so `$(SolutionDir)` resolves).
2. `plugin.json` `FileName` equals the built DLL name and `SystemName` matches `{Group}.{Name}`.
3. Every view and `logo.png` is marked `CopyToOutputDirectory` in the `.csproj`.
4. Install → configure → uninstall → reinstall leaves no orphaned settings, locale resources or tables.
5. Tell the user to restart the application after copying a new build, and to use **Admin → Configuration → Local plugins → Reload list of plugins** after adding a new one.
