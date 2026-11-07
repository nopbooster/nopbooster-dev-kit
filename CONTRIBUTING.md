# Contributing

Thanks for helping make Claude better at nopCommerce.

## Reporting a problem

Open an issue and include:

- the **nopCommerce version** (e.g. 4.90.8) and whether it is about a plugin or a theme;
- what Claude produced or the upgrade scan reported, and what is actually correct;
- if possible, a link to the nopCommerce source that proves it (file and tag on [nopSolutions/nopCommerce](https://github.com/nopSolutions/nopCommerce)).

## Changing the knowledge

Every version-specific statement must be checkable against the nopCommerce source. When you change one:

1. Compare the relevant files between release tags (e.g. `git diff release-4.80.9 release-4.90.8 -- src/Libraries/Nop.Services/Catalog/IProductService.cs`).
2. Update the matching file:
   - plugin rules → `skills/nopcommerce-plugin-development/references/`
   - upgrade notes → `skills/nop-upgrade/references/`
   - theme rules → `skills/nopcommerce-theme-development/SKILL.md`
3. Keep `SKILL.md` files short; put detail in `references/`.

## Adding an upgrade scan rule

Add an entry to the matching version section of `skills/nop-upgrade/references/scan-rules.md`, in the same shape as the others: severity (`BREAK`, `CHECK`, `TIDY`) and a short id in the heading, the file types to search, a ripgrep-compatible pattern, an "already fixed" pattern if one applies, and a fix that says what to do instead. Check the pattern against real code with `rg` before submitting.

## Keep the plugin to allowed file types

The plugin directory only accepts Markdown, text, JSON, YAML and PNG/JPEG/GIF/WebP/ICO images from this publisher. Do not add scripts, source code, SVGs or package-manager files anywhere in the repository.

## Before opening a pull request

```bash
claude plugin validate .
```

It must pass.

## License

By contributing you agree that your contribution is licensed under the [MIT License](LICENSE).
