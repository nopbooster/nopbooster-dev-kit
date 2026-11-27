# Changelog

All notable changes to the NopBooster Dev Kit. Versions follow [semantic versioning](https://semver.org).

## [0.4.0] — 2026-11-27

Shorter, clearer names, one skill fewer, and stricter guard rails. Nothing was published under the old names, so there is nothing to migrate.

### Changed — names
| Before | Now |
|---|---|
| `nopcommerce-plugin-development` + `nop-new-plugin` | `nop-plugin` |
| `nopcommerce-theme-development` | `nop-theme` |
| `nop-upgrade` | `nop-migrate` |
| `nop-review` | `nop-audit` |
| `nop-upgrade-engineer` (agent) | `nop-bulk-migrator` |

- `nop-new-plugin` is merged into `nop-plugin`: its workflow is now `references/new-plugin.md`, read only when a plugin is created from scratch. `/nop-plugin Group.Name what it should do` scaffolds a plugin.
- Plain requests ("upgrade my plugin to 5.00", "review my plugin") still trigger the right skill.

### Added — guard rails
- `nop-migrate` and `nop-bulk-migrator` check for version control and a clean working tree before editing, and never commit, push, reset or discard changes on their own.
- `nop-plugin` never overwrites an existing plugin folder.
- `nop-audit` is read-only unless fixes are asked for.
- Every skill and the agent must say when a build, install or check could not be run, instead of reporting it as done.
- CI checks that each skill's `name` matches its folder.

### Changed — directory review and accuracy
- `plugin.json` now names the listing icon with the `icon` field.
- README illustrations redrawn for nopCommerce 5.00 and the new names.
- .NET 8 and .NET 9 support ended on 10 November 2026: the README and skills now say so in the past tense.
- README: .NET badge includes 10, the knowledge table and install note corrected for 5.00.
- Issue templates offer 5.00.x and the new skill names.

### Verified
- nopCommerce `release-5.00.1` diffed against `release-5.00.0`: no change to any API, project file, view path or theme file the Dev Kit describes.

## [0.3.0] — 2026-11-07

Instructions-only release, so the plugin meets the Claude plugin directory's file-type rules.

### Changed
- The upgrade scan is now a Markdown checklist, `skills/nop-upgrade/references/scan-rules.md`, that Claude runs with its own search. It carries all 61 rules of the former `scan_upgrade.py` unchanged (patterns, severities, fixes and "already fixed" checks). `/nop-upgrade`, `/nop-review` and the `nop-upgrade-engineer` agent use it.
- README illustrations are PNG instead of SVG.

### Removed
- `scan_upgrade.py`, its test suite and the C# sample fixtures. The plugin no longer ships or runs any script.

## [0.2.0] — 2026-10-31

nopCommerce 5.00 support.

### Added
- `/nop-upgrade` hop **4.90 → 5.00** with a new reference (`490-to-500.md`): .NET 10, AutoMapper → Mapster, FluentValidation 12, forums/news/polls moved to plugins, moved namespaces, removed synchronous methods, migration helpers, signature changes, view and front-end changes.
- 25 new scanner rules for 5.00; `--to` now defaults to 5.00; skip a rule for files that already have the fix (e.g. the new `using`, including through `_ViewImports.cshtml`); path-based rule for theme overrides of views that left core.
- Sample 4.90 plugin fixture and tests for the new rules, version detection and fixed-file skipping. The 5.00 rules report no breaking issues on the 5.00.0 core plugins.

### Changed
- New plugins, themes and reviews target **5.00** by default (4.70–4.90 on request); version tables, `.csproj` and `plugin.json` templates updated.
- README: 5.00 coverage, .NET 8/9 end-of-support note, new upgrade-path illustration.

Version facts verified against nopCommerce source tag `release-5.00.0`.

## [0.1.0] — 2026-10-31

First release.

### Added
- `nopcommerce-plugin-development` skill — plugin project setup, `plugin.json`, lifecycle, admin UI and menus, permissions, data and migrations, events, widgets, services and scheduled tasks for nopCommerce 4.90, with 4.70 and 4.80 differences.
- `nopcommerce-theme-development` skill — theme structure, view overrides, CSS/RTL and version differences.
- `/nop-new-plugin` — scaffold a complete, buildable plugin.
- `/nop-upgrade` — hop-by-hop upgrades 4.70 → 4.80 → 4.90 with references for each hop and for themes.
- `scan_upgrade.py` — dependency-free scanner with BREAK / CHECK / TIDY findings by file and line.
- `/nop-review` — release review checklist.
- `nop-upgrade-engineer` agent for bulk upgrades.
- Scanner self-test with a sample 4.70 plugin, run in CI.

Version facts verified against nopCommerce source tags `release-4.70.5`, `release-4.80.9` and `release-4.90.8`.
