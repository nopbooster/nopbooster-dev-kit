# Permissions (ACL)

## 4.80 and 4.90

Admin permissions are strings, grouped as constants in `Nop.Services.Security.StandardPermission` (nested classes `Security`, `Customers`, `Orders`, `Reports`, `Catalog`, `Promotions`, `ContentManagement`, `Configuration`, `System`, `PublicStore`, …). They are granular: `PRODUCTS_VIEW` and `PRODUCTS_CREATE_EDIT_DELETE` are separate.

### Checking a permission

On a controller action — preferred:

```csharp
using Nop.Services.Security;
using Nop.Web.Framework.Mvc.Filters;

[CheckPermission(StandardPermission.Configuration.MANAGE_PLUGINS)]
public async Task<IActionResult> Configure() { … }

// several (customer needs any one of them), and an explicit result for AJAX grids:
[HttpPost]
[CheckPermission([StandardPermission.Catalog.PRODUCTS_VIEW, StandardPermission.Catalog.PRODUCTS_CREATE_EDIT_DELETE], CheckPermissionResultType.Json)]
public async Task<IActionResult> ProductList(MySearchModel searchModel) { … }
```

`CheckPermissionResultType`: `Default` (HTML redirect to Access denied on GET, JSON for AJAX POST), `Html`, `Text`, `Json`.

Anywhere else (services, view components, event consumers):

```csharp
if (!await _permissionService.AuthorizeAsync(StandardPermission.Configuration.MANAGE_PLUGINS))
    return;
```

Do not hand-write `AccessDeniedView()` checks in new 4.80+ controllers — the attribute replaces them.

### Adding a custom permission

1. Constants:

```csharp
namespace Nop.Plugin.Misc.MyFeature;

public static class MyFeaturePermissions
{
    public const string VIEW = "MyFeature.View";
    public const string MANAGE = "MyFeature.Manage";
}
```

2. A class implementing `IPermissionConfigManager` (it needs a parameterless constructor — nopCommerce creates it with `Activator.CreateInstance`):

```csharp
using Nop.Core.Domain.Customers;
using Nop.Services.Security;

namespace Nop.Plugin.Misc.MyFeature;

public class MyFeaturePermissionConfigManager : IPermissionConfigManager
{
    public IList<PermissionConfig> AllConfigs => new List<PermissionConfig>
    {
        new("Admin area. My feature. View", MyFeaturePermissions.VIEW, "MyFeature", NopCustomerDefaults.AdministratorsRoleName),
        new("Admin area. My feature. Manage", MyFeaturePermissions.MANAGE, "MyFeature", NopCustomerDefaults.AdministratorsRoleName)
    };
}
```

`PermissionConfig(name, systemName, category, params string[] defaultCustomerRoles)`.

3. Use it: `[CheckPermission(MyFeaturePermissions.MANAGE)]`.

nopCommerce finds every `IPermissionConfigManager` by type scanning and inserts missing permission records on **application start** (`AppStartedConsumer` → `IPermissionService.InsertPermissionsAsync()`), so a new permission appears after the restart that follows install. To insert immediately during `InstallAsync`, call `await _permissionService.InsertPermissionsAsync();`.

4. On uninstall remove them: `await _permissionService.DeletePermissionAsync(MyFeaturePermissions.VIEW);` (once per permission).

## 4.70 (only when targeting 4.70)

```csharp
if (!await _permissionService.AuthorizeAsync(StandardPermissionProvider.ManagePlugins))
    return AccessDeniedView();
```

Custom permissions implement `IPermissionProvider` (`GetPermissions()` returning `PermissionRecord`s and `GetDefaultPermissions()`), installed with `_permissionService.InstallPermissionsAsync(provider)` and removed with `UninstallPermissionsAsync(provider)`. All three (`StandardPermissionProvider`, `IPermissionProvider`, `Install/UninstallPermissionsAsync`) are gone in 4.80.

## Mapping old → new (common ones)

| 4.70 `StandardPermissionProvider.` | 4.80+ `StandardPermission.` |
|---|---|
| `ManagePlugins` | `Configuration.MANAGE_PLUGINS` |
| `ManageWidgets` | `Configuration.MANAGE_WIDGETS` |
| `ManageSettings` | `Configuration.MANAGE_SETTINGS` |
| `ManagePaymentMethods` | `Configuration.MANAGE_PAYMENT_METHODS` |
| `ManageShippingSettings` | `Configuration.MANAGE_SHIPPING_SETTINGS` |
| `ManageTaxSettings` | `Configuration.MANAGE_TAX_SETTINGS` |
| `ManageExternalAuthenticationMethods` | `Configuration.MANAGE_EXTERNAL_AUTHENTICATION_METHODS` |
| `ManageMultifactorAuthenticationMethods` | `Configuration.MANAGE_MULTIFACTOR_AUTHENTICATION_METHODS` |
| `ManageProducts` | `Catalog.PRODUCTS_VIEW` (read) / `Catalog.PRODUCTS_CREATE_EDIT_DELETE` (write) |
| `ManageCategories` | `Catalog.CATEGORIES_VIEW` / `Catalog.CATEGORIES_CREATE_EDIT_DELETE` |
| `ManageOrders` | `Orders.ORDERS_VIEW` / `Orders.ORDERS_CREATE_EDIT_DELETE` |
| `ManageCustomers` | `Customers.CUSTOMERS_VIEW` / `Customers.CUSTOMERS_CREATE_EDIT_DELETE` |
| `ManageDiscounts` | `Promotions.DISCOUNTS_VIEW` / `Promotions.DISCOUNTS_CREATE_EDIT_DELETE` |
| `AccessAdminPanel` | `Security.ACCESS_ADMIN_PANEL` |
| `DisplayPrices` | `PublicStore.DISPLAY_PRICES` |

For anything not in this table open `StandardPermission.cs` of the target version and choose the View vs CreateEditDelete constant by what the action does. Store owners must re-check custom role permissions after a 4.70 → 4.80 upgrade (the release notes say custom permissions must be re-configured manually).
