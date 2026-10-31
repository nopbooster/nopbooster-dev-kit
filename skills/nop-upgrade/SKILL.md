---
name: nop-upgrade
description: This skill should be used when upgrading or migrating nopCommerce plugins, themes or customised code between versions — "/nop-upgrade", "upgrade my plugin to 4.90", "migrate from 4.70 to 4.80", "port this plugin to nopCommerce 4.90", "what breaks when upgrading nopCommerce", "upgrade check", "my plugin doesn't compile after upgrading". Covers 4.70 → 4.80 → 4.90.
argument-hint: "[path to plugin or theme] [target version, default 4.90]"
---

# Upgrade nopCommerce plugins and themes (4.70 / 4.80 → 4.90)

Upgrade **one major version at a time**: 4.70 → 4.80 → 4.90. Each hop has its own reference; apply them in order.

## 1. Establish versions

- Current: `SupportedVersions` in each `plugin.json`, or `<TargetFramework>` (net8.0 = 4.70).
- Target: 4.90 unless the user says otherwise.
- Store database upgrades are separate from code upgrades: nopCommerce upgrades the database on first start of the new version (back up first; for very old stores the release's UpgradeScripts package applies). Say this once if the user is upgrading a live store.

## 2. Scan

Run the scanner on the plugin or theme folder (a folder containing several plugins also works):

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/nop-upgrade/scripts/scan_upgrade.py" <path> --to 4.90
```

Add `--from 4.70|4.80` if no `plugin.json` is present. Use `python3` where `python` is not available. The report groups findings as BREAK (won't compile/run), CHECK (compiles, may misbehave) and TIDY (recommended), with file:line references. Its rules come from diffs of the real 4.70.5 / 4.80.9 / 4.90.8 source.

The scanner finds known patterns; the compiler finds the rest. Treat both as the work list.

## 3. Fix, hop by hop

For each hop read the matching reference and work through its checklist:

- 4.70 → 4.80: `references/470-to-480.md` (net9.0, `$(SolutionDir)` csproj, permission system rewrite, admin menu events)
- 4.80 → 4.90: `references/480-to-490.md` (service splits, payment custom values, menus, `INopUrlHelper`)
- Themes and overridden views (any hop): `references/theme-upgrade.md`

Rules while fixing:

1. Change only what the upgrade needs. No refactors, renames or "improvements" beyond the TIDY items the user accepts.
2. Match how core did the same change — when the target-version source is available, open the corresponding core file and copy its pattern.
3. Keep behaviour identical: settings keys, locale resource names, table/column names and route URLs must not change, or existing stores lose data.
4. Bump `Version` in `plugin.json` and add `MigrationProcessType.Update` migrations for any locale/setting/schema change, so existing installs update in place without uninstalling.
5. For permission changes, pick View vs CreateEditDelete constants by what each action does (see the plugin-development skill's `references/permissions.md`).

## 4. Verify

1. `dotnet build` from the target-version solution with zero errors and no new warnings in the plugin.
2. Re-run the scanner: no BREAK items left.
3. Runtime check on a copy of the store: install/upgrade the plugin, open its configuration page as admin **and** as a restricted admin role, use its admin menu entry, and exercise its storefront feature. For payment/shipping/tax plugins place a test order end to end.

## 5. Report

Summarise: version hop(s) done, files changed, any behaviour the store owner must act on (e.g. re-assign custom role permissions after 4.70 → 4.80, re-create header links as Menus after 4.90), and anything that could not be verified.

If many plugins or a whole theme need upgrading, use the `nop-upgrade-engineer` agent to work through them one at a time.
