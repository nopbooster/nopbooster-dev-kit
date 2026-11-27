# Create a new nopCommerce plugin

The workflow for a plugin that does not exist yet. Produce a complete, buildable plugin — not a skeleton with TODOs.

## 1. Settle the inputs

Get these from the request; ask only for what is missing and cannot be defaulted (one short question at most):

| Input | Default |
|---|---|
| Target version | 5.00 — confirm from the solution if one is open (`src/Libraries/Nop.Core/NopVersion.cs`) |
| Group | Infer from purpose: shows content → `Widgets`; takes payment → `Payments`; rates → `Shipping`; anything else → `Misc` |
| Name | PascalCase from the purpose, e.g. `ProductBadges` |
| Author / company | Ask once if publishing; else `{Company}` placeholder |
| Configurable? | Yes if there is anything a store owner would want to change |
| Own tables? | Only if data cannot live in settings or generic attributes |

SystemName = `{Group}.{Name}`, project = `Nop.Plugin.{Group}.{Name}`.

If a folder or project with that name already exists, stop and ask whether to extend it or pick another name. Never overwrite an existing plugin.

## 2. Load the rules

The conventions in this skill's `SKILL.md` apply to everything you generate. From this folder, read only the references the plugin needs:

- always: `project-setup.md`
- configuration page or admin menu: `admin-ui.md`
- permissions beyond the standard ones: `permissions.md`
- tables, events, widgets, services, scheduled tasks: `data-events-widgets.md`

If the nopCommerce source for the target version is available locally, open the closest core plugin (`src/Plugins/Nop.Plugin.Widgets.GoogleAnalytics` for widgets, `Nop.Plugin.Misc.Zettle` for tables/menu/tasks, `Nop.Plugin.Pickup.PickupInStore` for entity builders) and match its patterns exactly.

## 3. Generate

Create, in this order:

1. `Nop.Plugin.{Group}.{Name}.csproj` and `plugin.json` (version-correct).
2. `{Name}Defaults.cs`, `{Name}Settings.cs`.
3. `{Name}Plugin.cs` with full `InstallAsync` / `UninstallAsync` (settings, locale resources, widget activation, schedule tasks, permissions — whatever applies, all reversed on uninstall).
4. Feature code: controller + model + views, view components, services + `NopStartup`, event consumers, domain + migration.
5. `Views/_ViewImports.cshtml`, a `logo.png` placeholder note, and `Content` entries in the `.csproj` for every view/static file.
6. `README.md` in the plugin folder: what it does, supported version, install steps, settings.

Every user-visible string → locale resource `Plugins.{Group}.{Name}.…`, added on install.

## 4. Wire into the solution

If the nopCommerce solution is present: place the project under `src/Plugins/`, add it with `dotnet sln src/NopCommerce.sln add src/Plugins/Nop.Plugin.{Group}.{Name}/Nop.Plugin.{Group}.{Name}.csproj --solution-folder Plugins` (on older SDKs omit `--solution-folder`), then run `dotnet build src/NopCommerce.sln` and fix every error and warning in the new project.

If no solution is present, say the project must be placed in `src/Plugins/` of a nopCommerce {version} source tree to build.

## 5. Report

Reply briefly: what was created, the build result (or, if the build could not be run, that it was not built and why), and how to install it (restart → Admin → Configuration → Local plugins → Reload list → Install → restart if prompted → Configure). Do not paste whole files into chat.
