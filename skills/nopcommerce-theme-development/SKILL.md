---
name: nopcommerce-theme-development
description: This skill should be used when creating, editing or upgrading a nopCommerce storefront theme — "nopCommerce theme", "nop theme", "override a view", "theme.json", "DefaultClean", "change the header/footer/product page layout", "RTL theme", "theme CSS". Targets nopCommerce 5.00 and knows the 4.70/4.80/4.90 differences.
---

# nopCommerce theme development (5.00 default)

Checked against DefaultClean in 4.70.5, 4.80.9, 4.90.8 and 5.00.0.

## How themes work

- A theme lives in `src/Presentation/Nop.Web/Themes/{ThemeName}/`.
- A view placed in the theme **overrides** the core view at the same relative path: `Themes/MyTheme/Views/Product/ProductTemplate.Simple.cshtml` replaces `Views/Product/ProductTemplate.Simple.cshtml`. Anything not overridden falls back to core.
- Override as few views as possible. Every overridden view must be re-merged on each nopCommerce upgrade — between 4.80.9 and 4.90.8 alone, 176 public view files changed (51 more between 4.90.8 and 5.00.0). Prefer CSS, widget zones and plugins over copying views.
- The working theme is chosen in **Admin → Configuration → Settings → General settings** (and per customer if "Allow customers to select a theme" is on).

## Minimal theme

```
Themes/MyTheme/
  theme.json
  preview.jpg
  Content/css/styles.css
  Content/css/styles.rtl.css     // only if SupportRTL = true
  Content/css/print.css
  Content/images/
  Views/_ViewImports.cshtml      // copy from DefaultClean of the SAME version
  Views/Shared/Head.cshtml       // registers the CSS files
```

`theme.json` (unchanged format 4.70 → 4.90):

```json
{
  "SystemName": "MyTheme",
  "FriendlyName": "My theme",
  "SupportRTL": true,
  "PreviewImageUrl": "~/Themes/MyTheme/preview.jpg",
  "PreviewText": "The 'MyTheme' site theme"
}
```

`Views/Shared/Head.cshtml` — start from DefaultClean's; the key line resolves the theme name dynamically:

```cshtml
NopHtml.AppendCssFileParts($"~/Themes/{themeName}/Content/css/styles{(supportRtl ? ".rtl" : "")}.css");
```

Start a new theme by copying `Themes/DefaultClean` and renaming folder + `SystemName`. Never edit DefaultClean itself — upgrades overwrite it.

## Rules

1. **Copy `_ViewImports.cshtml` from the target version's DefaultClean.** A stale one causes "type or namespace not found" errors after upgrades.
2. **Keep every widget zone** (`@await Component.InvokeAsync(typeof(WidgetViewComponent), new { widgetZone = PublicWidgetZones.X })`) when overriding a view — plugins depend on them.
3. **Scripts:** use `<script asp-location="Footer">` for inline scripts and `NopHtml.AppendScriptParts(ResourceLocation.Footer, "~/Themes/…/x.js")` for files. jQuery is loaded at the end of the page, so inline code must sit in the footer.
4. **Public front-end stack in 4.70–5.00:** jQuery 3.7, jquery-migrate, jQuery UI 1.13, jquery-validation. Bootstrap/AdminLTE are **admin only** — the public store has no Bootstrap; do not assume its classes exist.
5. **RTL:** if `SupportRTL` is true, maintain `styles.rtl.css` alongside `styles.css`.
6. **Images and fonts** go in `Content/` and are referenced as `~/Themes/MyTheme/Content/...`.
7. **Selling a theme:** ship it as a zip containing the `Themes/MyTheme` folder (plus a companion plugin if it needs settings). State the supported nopCommerce major version clearly — themes are version-specific.

## Version differences that affect themes

| Change | Version | Impact |
|---|---|---|
| Forums, news and polls left core: `Views/Boards/*`, `Views/News/*`, `Shared/Components/HomepageNews`, `HomepagePolls`, `PollBlock`, `NewsRssHeaderLink`, `Profile/Components/ProfilePosts` moved into the `Misc.Forums`/`Misc.News`/`Misc.Polls` plugins; their widget zones were removed | 5.00 | Theme overrides at those paths are ignored. Re-style the plugins' views from the theme CSS, or override them at the plugin's view path. |
| New views: `Checkout/_DesiredDeliveryDate`, `Common/_ContactFormAttributes`, `Customer/OtpPhoneVerification`, `Product/_ProductDetails3dObject`, `ReturnRequest/Find`, `Shared/_RenameWishlistModal`, `Shared/_ShoppingCartItems` | 5.00 | Style them. 51 existing public views also changed (Shared 15, Product 7, Checkout 7, Catalog 5) — re-merge overrides. |
| DefaultClean `styles.css` shrank ~870 lines (forum styles left with the plugins) and Swiper went 11 → 14 | 5.00 | Diff the DefaultClean CSS; check slider code against Swiper 14. |
| `TopMenu` view component replaced by `MainMenu` (and new `FooterMenu`), backed by the new admin-managed **menus** feature | 4.90 | Overrides of `Views/Shared/Components/TopMenu/*` no longer render. Rebuild the header navigation on `Components/MainMenu/`, and the footer on `Components/FooterMenu/` if the theme customises footer links. |
| New views: `_AddWishlistModal`, `_MoveToWishlistModal` (multiple wishlists), `Order/CustomerRecurringPayments`, `Catalog/SearchByFilterLevelValues`, filter-level components, `Boards/_MarkdownEditor` | 4.90 | Style them; they are unstyled in a theme whose CSS predates 4.90. |
| DefaultClean `styles.css` grew ~340 lines | 4.90 | Diff the DefaultClean CSS between versions and port the new rules into your theme. |
| `_ProductReviewHelpfulness` moved from `Views/Product` to `Views/Shared`; vendor review views added | 4.80 | Move overrides to the new path. |
| Font Awesome 5 → 6 (4.80) → 7 (4.90) | admin only | Only matters for admin views in plugins. |

For a full theme upgrade follow the `nop-upgrade` skill, theme section.
