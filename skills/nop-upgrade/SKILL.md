---
name: nop-upgrade
description: This skill should be used when upgrading or migrating nopCommerce plugins, themes or customised code between versions — "/nop-upgrade", "upgrade my plugin to 5.00", "migrate from 4.70 to 4.80", "port this plugin to nopCommerce 4.90", "move to .NET 10", "what breaks when upgrading nopCommerce", "upgrade check", "my plugin doesn't compile after upgrading". Covers 4.70 → 4.80 → 4.90 → 5.00.
argument-hint: "[path to plugin or theme] [target version, default 5.00]"
---

# Upgrade nopCommerce plugins and themes (4.70 / 4.80 / 4.90 → 5.00)

Upgrade **one major version at a time**: 4.70 → 4.80 → 4.90 → 5.00. Each hop has its own reference; apply them in order.

Why now: Microsoft ends support for .NET 8 and .NET 9 on 10 November 2026, so 4.70 (.NET 8), 4.80 and 4.90 (.NET 9) stop getting .NET security fixes. 5.00 runs on .NET 10 (supported to November 2028). Mention this once when the user asks which version to target.

## 1. Establish versions

- Current: `SupportedVersions` in each `plugin.json`, or `<TargetFramework>` (net8.0 = 4.70, net9.0 = 4.80 or 4.90, net10.0 = 5.00).
- Target: 5.00 unless the user says otherwise (or their store cannot move to .NET 10 yet — then 4.90).
- Store database upgrades are separate from code upgrades: nopCommerce upgrades the database on first start of the new version (back up first; for very old stores the release's UpgradeScripts package applies). Say this once if the user is upgrading a live store.

## 2. Scan

Read `references/scan-rules.md` and follow its "How to run the scan" steps on the plugin or theme folder (a folder containing several plugins also works). It lists every known breaking pattern per version hop as a search pattern, the file types to search and the fix, taken from diffs of the real 4.70.5 / 4.80.9 / 4.90.8 / 5.00.0 source. Report findings as BREAK (won't compile/run), CHECK (compiles, may misbehave) and TIDY (recommended), with file:line references.

The scan finds known patterns; the compiler finds the rest. Treat both as the work list.

## 3. Fix, hop by hop

For each hop read the matching reference and work through its checklist:

- 4.70 → 4.80: `references/470-to-480.md` (net9.0, `$(SolutionDir)` csproj, permission system rewrite, admin menu events)
- 4.80 → 4.90: `references/480-to-490.md` (service splits, payment custom values, menus, `INopUrlHelper`)
- 4.90 → 5.00: `references/490-to-500.md` (net10.0, AutoMapper → Mapster, FluentValidation 12, forums/news/polls moved to plugins, `IWebHelper` namespace, sync methods removed, migration helpers)
- Themes and overridden views (any hop): `references/theme-upgrade.md`

Rules while fixing:

1. Change only what the upgrade needs. No refactors, renames or "improvements" beyond the TIDY items the user accepts.
2. Match how core did the same change — when the target-version source is available, open the corresponding core file and copy its pattern.
3. Keep behaviour identical: settings keys, locale resource names, table/column names and route URLs must not change, or existing stores lose data.
4. Bump `Version` in `plugin.json` and add `MigrationProcessType.Update` migrations for any locale/setting/schema change, so existing installs update in place without uninstalling.
5. For permission changes, pick View vs CreateEditDelete constants by what each action does (see the plugin-development skill's `references/permissions.md`).

## 4. Verify

1. `dotnet build` from the target-version solution with zero errors and no new warnings in the plugin.
2. Re-run the scan from `references/scan-rules.md`: no BREAK items left.
3. Runtime check on a copy of the store: install/upgrade the plugin, open its configuration page as admin **and** as a restricted admin role, use its admin menu entry, and exercise its storefront feature. For payment/shipping/tax plugins place a test order end to end.

## 5. Report

Summarise: version hop(s) done, files changed, any behaviour the store owner must act on (e.g. re-assign custom role permissions after 4.70 → 4.80, re-create header links as Menus after 4.90, install the Forums/News/Polls plugins after 5.00 if the store used them, move the server to .NET 10), and anything that could not be verified.

If many plugins or a whole theme need upgrading, use the `nop-upgrade-engineer` agent to work through them one at a time.
