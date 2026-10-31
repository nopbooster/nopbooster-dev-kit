---
name: nop-review
description: This skill should be used when reviewing nopCommerce plugin or theme code for correctness, conventions, security and upgrade-safety — "/nop-review", "review my nopCommerce plugin", "is this nop plugin OK", "check this plugin before I sell it", "audit this nopCommerce customisation".
argument-hint: "[path to plugin, theme or diff]"
---

# Review nopCommerce plugin or theme code

Review against nopCommerce conventions for the plugin's target version (from `plugin.json`). Load `${CLAUDE_PLUGIN_ROOT}/skills/nopcommerce-plugin-development/SKILL.md` first; open its references only for areas where you find problems.

## Checklist

Work through every section; skip only what does not apply.

**Packaging**
- `plugin.json`: `SystemName` = `{Group}.{Name}`, `FileName` = built DLL, `SupportedVersions` = major version only, `Version` bumped if behaviour changed.
- `.csproj`: right `TargetFramework`, `$(SolutionDir)` paths (4.80+), `ClearPluginAssemblies` target present, every view/static file has `CopyToOutputDirectory`, `CopyLocalLockFileAssemblies` true only when the plugin brings NuGet packages core lacks.
- No core project edited; no files written into core folders.

**Install / uninstall symmetry**
- Everything added on install is removed on uninstall: settings (`DeleteSettingAsync<T>`), locale resources (`DeleteLocaleResourcesAsync(prefix)`), widget activation, schedule tasks, custom permissions, generic attributes the plugin owns.
- Tables created by `Installation` migrations are dropped by `Down()` (automatic with `AutoReversingMigration`).
- `base.InstallAsync()` / `base.UninstallAsync()` called.

**Security**
- Every admin action has `[CheckPermission(...)]` (4.80+) or an `AuthorizeAsync` guard (4.70) with the least-privileged fitting permission; AJAX/grid actions use `CheckPermissionResultType.Json`.
- Admin controllers: `[Area(AreaNames.ADMIN)]`, `[AuthorizeAdmin]`, `[AutoValidateAntiforgeryToken]`.
- Public endpoints (webhooks, callbacks) validate signatures/tokens and never trust posted amounts or order IDs without re-loading from the database.
- Output encoding: no `@Html.Raw` of user or setting input unless it is deliberately HTML that only admins set.
- No secrets in code or `plugin.json`; API keys live in settings and are rendered as password inputs.
- Multi-store and ACL: data access respects `storeId` and `IAclService`/`IStoreMappingService` where core entities are shown publicly.

**Correctness and performance**
- Fully async; no `.Result`, `.Wait()`, `async void`.
- No queries in loops (N+1); use repository `GetAllAsync` with filters, or batch methods.
- Expensive lookups cached with `IStaticCacheManager` and cleared on change.
- Event consumers are fast and exception-safe (a throw in a consumer is logged but its work is lost).
- `HttpClient` registered with `AddHttpClient<T>().WithProxy()`, not `new HttpClient()`.
- Settings loaded with the current store scope where per-store overrides exist.

**Conventions**
- Naming (`Nop.Plugin.{Group}.{Name}`, locale keys `Plugins.{Group}.{Name}.*`), file-scoped namespaces, `protected virtual` members, models as `record` deriving from `BaseNopModel`.
- All UI text localized; no hard-coded English in views.
- Widget views keep working when `additionalData` is null.

**Upgrade safety**
- Run `python "${CLAUDE_PLUGIN_ROOT}/skills/nop-upgrade/scripts/scan_upgrade.py" <path> --from <current> --to 4.90` when the code targets 4.70/4.80 and report what a future upgrade will cost.
- Theme: count overridden core views; flag overrides that could be replaced by CSS or a widget zone.

## Output

Lead with a one-line verdict (ship / ship after fixes / not ready). Then findings grouped **Must fix** (bugs, security, data loss), **Should fix** (conventions, performance, upgrade cost), **Nice to have**, each with `file:line`, the problem, and the concrete fix (code when short). Do not restate code that is fine.
