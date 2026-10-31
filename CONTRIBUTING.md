# Contributing

Thanks for helping make Claude better at nopCommerce.

## Reporting a problem

Open an issue and include:

- the **nopCommerce version** (e.g. 4.90.8) and whether it is about a plugin or a theme;
- what Claude produced or the scanner reported, and what is actually correct;
- if possible, a link to the nopCommerce source that proves it (file and tag on [nopSolutions/nopCommerce](https://github.com/nopSolutions/nopCommerce)).

## Changing the knowledge

Every version-specific statement must be checkable against the nopCommerce source. When you change one:

1. Compare the relevant files between release tags (e.g. `git diff release-4.80.9 release-4.90.8 -- src/Libraries/Nop.Services/Catalog/IProductService.cs`).
2. Update the matching file:
   - plugin rules → `skills/nopcommerce-plugin-development/references/`
   - upgrade notes → `skills/nop-upgrade/references/`
   - theme rules → `skills/nopcommerce-theme-development/SKILL.md`
3. Keep `SKILL.md` files short; put detail in `references/`.

## Adding a scanner rule

1. Add a tuple to `RULES` in `skills/nop-upgrade/scripts/scan_upgrade.py`: the version that introduced the change, severity (`BREAK`, `CHECK`, `TIDY`), a short id, the regex, the file kind (`cs`, `csproj`, `view`, `any`) and a message that says what to do instead.
2. Add code that triggers it to `tests/fixtures/Nop.Plugin.Misc.Legacy470/` and its id to the expected list in `tests/test_scan_upgrade.py`.
3. Run `python tests/test_scan_upgrade.py`.

## Before opening a pull request

```bash
python tests/test_scan_upgrade.py
claude plugin validate .
```

Both must pass.

## License

By contributing you agree that your contribution is licensed under the [MIT License](LICENSE).
