# Changelog

All notable changes to the NopBooster Dev Kit. Versions follow [semantic versioning](https://semver.org).

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
