# Upgrading a theme (and plugin view overrides)

Themes break silently: an outdated overridden view usually still renders, but loses new features, model properties or widget zones — or throws at runtime when a model property was removed.

## Procedure

1. **Get both DefaultClean versions and both core `Views` folders** (old and target), e.g. from the nopCommerce source zips or the GitHub tags `release-4.90.8` and `release-5.00.0`.
2. **List the theme's overrides:** every file under `Themes/{Theme}/Views/` except `_ViewImports.cshtml`.
3. **For each override, three-way compare:** old core view → target core view (what nopCommerce changed) and old core view → theme view (what the theme changed). Re-apply the theme's changes onto the **target** core view. Never just keep the old theme file.
   - Quick classification: `diff -rq old/Views new/Views` lists changed core views; overrides of unchanged core views need no work.
4. **Replace `Views/_ViewImports.cshtml`** with the target DefaultClean one, then re-add any theme-specific `@using`/`@inject` lines.
5. **Port CSS:** diff DefaultClean `Content/css/styles.css` (and `.rtl.css`) old → new and add styles for new elements to the theme CSS.
6. **Check removed/moved views** (below) and delete or move overrides accordingly.
7. **Run the store** with the theme active and walk: home, category with filters, product (simple, grouped, with attributes), search, cart, wishlist, checkout (one-page and multi-step if enabled), account pages, mobile width, and RTL if supported.

## Known view moves

| Version | Change |
|---|---|
| 4.80 | `Views/Product/_ProductReviewHelpfulness.cshtml` → `Views/Shared/_ProductReviewHelpfulness.cshtml`; added `Catalog/VendorReviews.cshtml`, `Catalog/_VendorProductReviews.cshtml` |
| 5.00 | Removed from `Nop.Web` (now in the Forums/News/Polls plugins): `Boards/*`, `News/*`, `Shared/Components/HomepageNews/`, `HomepagePolls/`, `PollBlock/`, `NewsRssHeaderLink/`, `Profile/Components/ProfilePosts/`, `Boards/Components/*`. Added: `Checkout/_DesiredDeliveryDate`, `Common/_ContactFormAttributes`, `Customer/OtpPhoneVerification`, `Product/_ProductDetails3dObject`, `ReturnRequest/Find`, `Shared/_RenameWishlistModal`, `Shared/_ShoppingCartItems` |
| 4.90 | `Shared/Components/TopMenu/` removed → `Shared/Components/MainMenu/`; `Shared/Components/FooterMenu/` added (rendered from `Footer/Default.cshtml`); added `Shared/_AddWishlistModal`, `Shared/_MoveToWishlistModal`, `Shared/_OrderCustomValues`, `Order/CustomerRecurringPayments`, `Catalog/SearchByFilterLevelValues`, `Shared/Components/FilterLevelValueSearch/`, `Shared/Components/CompatibleWithFilterLevelValues/`, `Boards/_MarkdownEditor` |

5.00 changed 51 existing public view files compared with 4.90.8 (Shared 15, Product 7, Checkout 7, Catalog 5, Customer 3, others ≤2); DefaultClean `styles.css` lost ~870 lines and Swiper moved 11 → 14. 4.90 changed 176 public view files compared with 4.80.9 (Shared 50, Product 22, Customer 18, Boards 18, Catalog 16, Checkout 10, Order 4, Blog 4, others ≤3). 4.80 changed 27 compared with 4.70.5.

## Menu migration (4.90)

The header menu is now built from **Admin → Content management → Menus**, so links that a 4.80 theme hard-coded in `TopMenu` (or toggled with the removed `DisplayDefaultMenuItemSettings`/`DisplayDefaultFooterItemSettings`) should become menu items the store owner manages. Re-skin `Components/MainMenu/Default.cshtml` (and `FooterMenu`) rather than recreating the old markup.
