# Changelog

All notable changes to the NopBooster Dev Kit. Versions follow [semantic versioning](https://semver.org).

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
