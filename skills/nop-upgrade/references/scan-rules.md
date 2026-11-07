# Upgrade scan rules (4.70 → 4.80 → 4.90 → 5.00)

Known code that breaks or needs attention when a nopCommerce plugin or theme moves to a newer version. The rules come from diffs of the real nopCommerce 4.70.5, 4.80.9, 4.90.8 and 5.00.0 source.

Severity: **BREAK** = will not compile or run · **CHECK** = compiles, may behave differently · **TIDY** = recommended.

## How to run the scan

1. **Current version.** Read `SupportedVersions` from every `plugin.json` under the folder. Without one, use `<TargetFramework>` in the `.csproj`: `net8.0` = 4.70, `net9.0` = 4.80 (treat as 4.80 so the 4.90 rules are included), `net10.0` = 5.00. If neither is there, ask the user.
2. **Which rules.** Apply every hop after the current version up to the target (default 5.00). From 4.70 to 5.00 that is all three sections below.
3. **plugin.json.** For each `plugin.json`, report BREAK if `SupportedVersions` does not include the target: set it to `["<target>"]` and bump `Version`.
4. **Search.** For each rule, search with the Grep tool (it uses ripgrep regex) over the listed file types. Skip `bin`, `obj`, `node_modules`, `.git`, `.vs`, `packages`, `wwwroot/lib` and `lib_npm`. Search the whole folder in one call per rule rather than file by file.
5. **Drop false hits.** Ignore lines whose trimmed text starts with `//` or `///`. If a rule has an "Already fixed" pattern, drop hits in files that contain it.
6. **Report** in Markdown: a header `nopCommerce upgrade scan: <from> → <to>`, the plugin.json results, a count line `N BREAK · N CHECK · N TIDY`, then one section per rule that matched, ordered BREAK → CHECK → TIDY and then by version: `## [SEV] id (changed in X)`, the Fix text, and each hit as `` `path:line` — `code` `` (at most 50 per rule, then "… and N more"). If nothing matched, say "No known breaking patterns found. Build against the target version to confirm."

The scan finds known patterns; the compiler finds the rest. Always build afterwards.

## 4.70 → 4.80 (14 rules)

### [BREAK] permission-provider

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bStandardPermissionProvider\.`
- **Fix:** StandardPermissionProvider was removed. Use StandardPermission.{Area}.{CONST} with [CheckPermission(...)] on actions or IPermissionService.AuthorizeAsync(string).

### [BREAK] ipermissionprovider

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bIPermissionProvider\b|\b(Install|Uninstall)PermissionsAsync\s*\(`
- **Fix:** IPermissionProvider and Install/UninstallPermissionsAsync were removed. Implement IPermissionConfigManager (parameterless ctor) and call DeletePermissionAsync(name) on uninstall.

### [BREAK] sitemap-menu

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bSiteMapNode\b|\bI?XmlSiteMap\b`
- **Fix:** SiteMapNode/XmlSiteMap were removed. Build menu items with AdminMenuItem via an IConsumer<AdminMenuCreatedEvent> or BaseAdminMenuCreatedEventConsumer.

### [BREAK] acl-supported-factory

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bI?AclSupportedModelFactory\b`
- **Fix:** IAclSupportedModelFactory/AclSupportedModelFactory were removed from Nop.Web.Framework.Factories.

### [BREAK] localized-enum

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bILocalizedEnum\b`
- **Fix:** ILocalizedEnum was removed from Nop.Core.

### [BREAK] product-flags

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bUpdateHasDiscountsAppliedAsync\s*\(|\bUpdateHasTierPricesPropertyAsync\s*\(`
- **Fix:** IProductService.UpdateHasDiscountsAppliedAsync / UpdateHasTierPricesPropertyAsync were removed.

### [BREAK] net8

- **Search in:** `*.csproj`
- **Pattern:** `<TargetFramework>\s*net8\.0\s*</TargetFramework>`
- **Fix:** nopCommerce 4.80+ requires net9.0.

### [CHECK] admin-menu-plugin

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bIAdminMenuPlugin\b|\bManageSiteMapAsync\s*\(`
- **Fix:** IAdminMenuPlugin is obsolete from 4.80 (parameter is now AdminMenuItem). Move the menu code to AdminMenuCreatedEvent handling.

### [CHECK] logger-return

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `=\s*await\s+_?logger\.InsertLogAsync\s*\(|=\s*_?logger\.InsertLog\s*\(`
- **Fix:** ILogger.InsertLogAsync now returns Task (was Task<Log>) and InsertLog returns void. Remove the assignment.

### [CHECK] store-tokens

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bAddStoreTokensAsync\s*\(`
- **Fix:** AddStoreTokensAsync gained a required int languageId parameter in 4.80.

### [CHECK] campaign-send

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bSendCampaignAsync\s*\(`
- **Fix:** ICampaignService.SendCampaignAsync(campaign, emailAccount, email) gained a required int languageId parameter in 4.80.

### [CHECK] review-helpfulness-view

- **Search in:** `*.cshtml`
- **Pattern:** `_ProductReviewHelpfulness`
- **Fix:** _ProductReviewHelpfulness moved from Views/Product to Views/Shared in 4.80 — move theme overrides.

### [TIDY] access-denied-guard

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `return\s+AccessDeniedView\s*\(\s*\)`
- **Fix:** Manual permission guard. In 4.80+ replace the AuthorizeAsync + AccessDeniedView() pair with a [CheckPermission(...)] attribute on the action.

### [TIDY] csproj-relative

- **Search in:** `*.csproj`
- **Pattern:** `\.\.\\\.\.\\Presentation\\Nop\.Web|\$\(MSBuildProjectDirectory\)\\\.\.\\\.\.\\Build`
- **Fix:** From 4.80 core plugins use $(SolutionDir)-based OutputPath/ProjectReference/ClearPluginAssemblies paths; build from the solution.

## 4.80 → 4.90 (22 rules)

### [BREAK] product-reviews-moved

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `[pP]roductService\s*\.\s*(GetAllProductReviewsAsync|GetProductReviewByIdAsync|GetProductReviewsByIdsAsync|InsertProductReviewAsync|UpdateProductReviewAsync|DeleteProductReviewsAsync|DeleteProductReviewAsync|SetProductReviewHelpfulnessAsync|UpdateProductReviewHelpfulnessTotalsAsync|UpdateProductReviewTotalsAsync|CanAddReviewAsync)\b`
- **Fix:** Product review methods moved from IProductService to IProductReviewService in 4.90. Inject IProductReviewService.

### [BREAK] product-store-mappings

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bUpdateProductStoreMappingsAsync\s*\(`
- **Fix:** IProductService.UpdateProductStoreMappingsAsync was removed in 4.90.

### [BREAK] warehouses-moved

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `[sS]hippingService\s*\.\s*(GetWarehouseByIdAsync|GetAllWarehousesAsync|GetNearestWarehouseAsync|InsertWarehouseAsync|UpdateWarehouseAsync|DeleteWarehouseAsync)\b`
- **Fix:** Warehouse methods moved from IShippingService to IWarehouseService in 4.90.

### [BREAK] shipping-methods-moved

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `[sS]hippingService\s*\.\s*(GetShippingMethodByIdAsync|GetAllShippingMethodsAsync|InsertShippingMethodAsync|UpdateShippingMethodAsync|DeleteShippingMethodAsync|GetShippingMethodCountryMappingAsync|InsertShippingMethodCountryMappingAsync|DeleteShippingMethodCountryMappingAsync|CountryRestrictionExistsAsync)\b`
- **Fix:** Shipping-method methods moved from IShippingService to IShippingMethodsService in 4.90.

### [BREAK] payment-custom-values

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bGenerateOrderGuidAsync\s*\(|\bSerializeCustomValues\s*\(|\bDeserializeCustomValues\s*\(|\bDictionarySerializer\b`
- **Fix:** IPaymentService.GenerateOrderGuidAsync/SerializeCustomValues/DeserializeCustomValues and DictionarySerializer were removed. Use IOrderProcessingService.Set/GetProcessPaymentRequestAsync and the CustomValues class (SerializeToXml/FillByXml).

### [BREAK] order-payment-session

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `[\"']OrderPaymentInfo[\"']`
- **Fix:** The in-progress ProcessPaymentRequest is no longer kept in session 'OrderPaymentInfo'. Use IOrderProcessingService.GetProcessPaymentRequestAsync()/SetProcessPaymentRequestAsync().

### [BREAK] spec-attributes

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bGetSpecificationAttributesAsync\s*\(`
- **Fix:** ISpecificationAttributeService.GetSpecificationAttributesAsync was renamed GetAllSpecificationAttributesAsync in 4.90.

### [BREAK] attribute-value-picture

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bDeleteProductAttributeValuePictureAsync\s*\(`
- **Fix:** Replaced by DeleteProductAttributeValuePicturesAsync(IList<ProductAttributeValuePicture>) in 4.90.

### [BREAK] newsletter-lookups

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bGetNewsLetterSubscriptionByEmailAndStoreIdAsync\s*\(|\bGetNewsLetterSubscriptionByGuidAsync\s*\(`
- **Fix:** Replaced by GetNewsLetterSubscriptionsByEmailAsync(email, storeId, subscriptionTypeId, isActive) / GetNewsLetterSubscriptionsByGuidAsync(guid), which return lists.

### [BREAK] newsletter-casing

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bExportNewsletterSubscribersToTxtAsync\b|\bImportNewsletterSubscribersFromTxtAsync\b`
- **Fix:** Renamed to ...NewsLetterSubscribers... (capital L) in 4.90.

### [BREAK] token-events-namespace

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\b(MessageTokensAddedEvent|EntityTokensAddedEvent)\b`
- **Fix:** MessageTokensAddedEvent / EntityTokensAddedEvent moved from Nop.Core.Domain.Messages to Nop.Services.Messages in 4.90 — update the using.

### [BREAK] pdf-sources

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\b(InvoiceSource|ShipmentSource|CatalogSource|DocumentSource)\b`
- **Fix:** PDF sources were replaced by InvoiceDocument / ShipmentDocument / CatalogDocument (PdfDocument<T>) in 4.90.

### [BREAK] azure-core

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bAzurePictureService\b|\bAzureBlobConfig\b`
- **Fix:** Azure Blob storage left core in 4.90; it is now the Nop.Plugin.Misc.AzureBlob plugin.

### [BREAK] menu-settings

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bDisplayDefaultMenuItemSettings\b|\bDisplayDefaultFooterItemSettings\b`
- **Fix:** Removed in 4.90 — header/footer links are managed by the Menus feature (IMenuService).

### [BREAK] iplugin-direct

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `class\s+\w+\s*:[^{]*\bIPlugin\b`, then keep only classes whose base list does **not** also name `BasePlugin`
- **Exact rule** (uses a look-ahead; for reference): `class\s+\w+\s*:\s*(?![^{]*\bBasePlugin\b)[^{]*\bIPlugin\b`
- **Fix:** IPlugin gained InstallSampleDataAsync() in 4.90. Derive from BasePlugin or implement it.

### [BREAK] top-menu

- **Search in:** `*.cs`, `*.cshtml`, `*.csproj`, `*.js`, `plugin.json`, `theme.json`
- **Pattern:** `\bTopMenuViewComponent\b|Components[/\\]TopMenu\b|\bTopMenuModel\b`
- **Fix:** TopMenu was replaced by MainMenu (and FooterMenu) in 4.90. Rebuild header navigation customisations on Components/MainMenu.

### [CHECK] custom-values-dictionary

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `CustomValues\s*(\.\s*(Add\s*\(\s*[\"']|ContainsKey\s*\()|\[\s*[\"'][^\"']+[\"']\s*\]\s*=)|new\s+Dictionary<string,\s*object>\s*\(\s*\)\s*;?\s*//.*CustomValues|CustomValues\s*=\s*new\s+Dictionary`
- **Fix:** ProcessPaymentRequest.CustomValues is now a CustomValues list, not Dictionary<string, object>. Use CustomValues.Add(new CustomValue(name, value, ...)), TryGetValue, Remove.

### [CHECK] product-attributes-positional

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bGetAllProductAttributesAsync\s*\(\s*(\d|pageIndex|[a-zA-Z_]*[pP]age)`
- **Fix:** GetAllProductAttributesAsync now starts with string name = null. Positional page arguments must become named (pageIndex:, pageSize:).

### [CHECK] message-token-groups

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bGetListOfAllowedTokensAsync\s*\(`
- **Fix:** Parameter type changed from IEnumerable<string> to IList<string> in 4.90.

### [CHECK] topics-overloads

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bGetAllTopicsAsync\s*\(`
- **Fix:** ITopicService.GetAllTopicsAsync overloads changed in 4.90: (storeId, ignoreAcl, showHidden) and (storeId, keywords, ignoreAcl, showHidden). Check arguments.

### [CHECK] theme-provider

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `:\s*[^{]*\bIThemeProvider\b`
- **Fix:** IThemeProvider gained InitializeAsync() in 4.90 (only matters if you implement it).

### [TIDY] url-helper-factory

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bIUrlHelperFactory\b|\bIActionContextAccessor\b`
- **Fix:** 4.90 core plugins build URLs with INopUrlHelper.RouteUrl(routeName) instead of IUrlHelperFactory + IActionContextAccessor.

## 4.90 → 5.00 (25 rules)

### [BREAK] net9

- **Search in:** `*.csproj`
- **Pattern:** `<TargetFramework>\s*net[89]\.0\s*</TargetFramework>`
- **Fix:** nopCommerce 5.00 requires net10.0 (and the .NET 10 SDK). Update Microsoft.* package references to 10.0.x as well.

### [BREAK] automapper

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\busing\s+AutoMapper\b|:\s*Profile\s*,\s*IOrderedMapperProfile|\bAutoMapperConfiguration\b|\bIMapper\b`
- **Fix:** AutoMapper was replaced by Mapster in 5.00. Derive mapping profiles from BaseMapperProfile (Nop.Core.Infrastructure.Mapper), drop 'using AutoMapper' and the Order property; ForMember(..., o => o.Ignore()/MapFrom()) still works.

### [BREAK] automapper-package

- **Search in:** `*.csproj`
- **Pattern:** `Include=\"AutoMapper\"|Include=\"FluentValidation\.AspNetCore\"`
- **Fix:** Core no longer ships AutoMapper or FluentValidation.AspNetCore in 5.00. Remove the package reference (use Mapster via BaseMapperProfile; FluentValidation 12 is provided by core).

### [BREAK] fluentvalidation-aspnetcore

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\busing\s+FluentValidation\.AspNetCore\b`
- **Fix:** FluentValidation.AspNetCore is gone in 5.00 (FluentValidation 12). Remove the using; automatic validation comes from [AutoValidation] on BaseController.

### [BREAK] is-credit-card

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\.IsCreditCard\s*\(|\bCreditCardPropertyValidator\b`
- **Fix:** nop's IsCreditCard()/CreditCardPropertyValidator were removed in 5.00. Use FluentValidation's built-in .CreditCard().

### [BREAK] iwebhelper-namespace

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bI?WebHelper\b`
- **Already fixed if the file contains:** `using\s+Nop\.Services\.Helpers\b` (for a view, also look in every `_ViewImports.cshtml` from its folder up to the scanned folder)
- **Fix:** IWebHelper/WebHelper moved from Nop.Core to Nop.Services.Helpers in 5.00. Add 'using Nop.Services.Helpers;'.

### [BREAK] ithemecontext-namespace

- **Search in:** `*.cs`, `*.cshtml`, `*.csproj`, `*.js`, `plugin.json`, `theme.json`
- **Pattern:** `\bIThemeContext\b|\busing\s+Nop\.Web\.Framework\.Themes\s*;`
- **Already fixed if the file contains:** `using\s+Nop\.Services\.Themes\b` (for a view, also look in every `_ViewImports.cshtml` from its folder up to the scanned folder)
- **Fix:** IThemeContext moved from Nop.Web.Framework.Themes to Nop.Services.Themes in 5.00. Update the using.

### [BREAK] forums-news-polls

- **Search in:** `*.cs`, `*.cshtml`, `*.csproj`, `*.js`, `plugin.json`, `theme.json`
- **Pattern:** `\bNop\.(Core\.Domain|Services)\.(Forums|News|Polls)\b|\bI(Forum|News|Poll)Service\b|\bIsForumModeratorAsync\b`
- **Fix:** Forums, News and Polls left core in 5.00 and are now the Nop.Plugin.Misc.Forums/News/Polls plugins (PrivateMessage moved to Nop.Core.Domain.Customers). Reference the plugin's own types, or drop the feature.

### [BREAK] forum-news-messages

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `[tT]okenProvider\s*\.\s*Add(Forum|ForumTopic|ForumPost|NewsComment)TokensAsync\b|[mM]essageService\s*\.\s*(Send(NewForumTopic|NewForumPost)MessageAsync|SendNewsCommentStoreOwnerNotificationMessageAsync)\b`
- **Fix:** Forum and news message tokens and notifications were removed from core message services in 5.00.

### [BREAK] removed-widget-zones

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\b(Public|Admin)WidgetZones\s*\.\s*(Boards\w*|NewsItemPage\w*|NewsListPage\w*|HomepageBeforeNews|HomepageBeforePoll|CustomerForumSubscriptions\w*|Forum\w*|News(CommentListButtons|DetailsBlock|DetailsButtons|ItemsDetailsBlock|ListButtons|SettingsButtons)|Poll\w*)\b`
- **Fix:** This widget zone was removed with forums/news/polls in 5.00; the widget will no longer render there.

### [BREAK] bbcode

- **Search in:** `*.cs`, `*.cshtml`, `*.csproj`, `*.js`, `plugin.json`, `theme.json`
- **Pattern:** `\bI?BBCodeHelper\b|\bResolveLinksHelper\b|\bNop\.Services\.Html\.CodeFormatter\b|\bnop-bb-code-editor\b`
- **Fix:** BBCode helpers, ResolveLinksHelper and the code formatter were removed from core in 5.00.

### [BREAK] sync-localization

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `[lL]ocalizationService\s*\.\s*(AddOrUpdateLocaleResource|DeleteLocaleResources|DeleteLocaleStringResource|UpdateLocaleStringResource)\s*\(`
- **Fix:** Synchronous ILocalizationService methods were removed in 5.00. Use the ...Async versions, or this.AddOrUpdateLocaleResource(dict) / this.DeleteLocaleResources(names) inside a migration.

### [BREAK] sync-settings

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `[sS]ettingService\s*\.\s*(InsertSetting|UpdateSetting|DeleteSetting|ClearCache)\s*\(`
- **Fix:** Synchronous ISettingService methods were removed in 5.00. Use the ...Async versions, or this.SetSettingIfNotExists/GetSettingByKey/DeleteSettings inside a migration.

### [BREAK] sync-logger

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `[lL]ogger\s*\.\s*(Error|Information|Warning|InsertLog)\s*\(`
- **Fix:** Synchronous ILogger methods were removed in 5.00. Use ErrorAsync/InformationAsync/WarningAsync/InsertLogAsync.

### [BREAK] sync-store

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `[sS]toreService\s*\.\s*UpdateStore\s*\(`
- **Fix:** IStoreService.UpdateStore was removed in 5.00. Use UpdateStoreAsync.

### [BREAK] migration-language-data

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bGetLanguageData\s*\(`
- **Fix:** MigrationExtension.GetLanguageData() was removed in 5.00 (now MigrationExtensions). Use this.AddOrUpdateLocaleResource(dict) and this.RenameLocales(dict) without language/service arguments.

### [BREAK] url-helper-extensions

- **Search in:** `*.cs`, `*.cshtml`, `*.csproj`, `*.js`, `plugin.json`, `theme.json`
- **Pattern:** `\.\s*RouteTopicUrl\s*\(|\bUrl\s*\.\s*RouteUrl\s*<`
- **Fix:** Nop.Web.Framework.Mvc.Routing.UrlHelperExtensions (RouteUrl<TEntity>, RouteTopicUrl) was removed in 5.00. Use INopUrlHelper.RouteGenericUrlAsync<TEntity>() / RouteTopicUrlAsync().

### [BREAK] removed-mvc-infra

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bNopMetadataProvider\b|\bIModelAttribute\b|\bInvariantNumberModelBinder(Provider)?\b|\bRoxyFileman\w*\b`
- **Fix:** Removed in 5.00 (model metadata/binder infrastructure; RoxyFileman was replaced by elFinder).

### [BREAK] format-base-price

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bFormatBasePriceAsync\s*\([^)]*,[^)]*,`
- **Fix:** IPriceFormatter.FormatBasePriceAsync now takes (product, decimal? basePrice). Get the base price from IProductService.GetBaseProductPriceAsync(product, productPrice, totalWeight).

### [BREAK] search-term-by-keyword

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bGetSearchTermByKeywordAsync\s*\(`
- **Fix:** ISearchTermService.GetSearchTermByKeywordAsync was removed in 5.00 (search terms are per customer: SearchTermHistoryItemsAsync, DeleteSearchTermsByKeywordAsync).

### [CHECK] return-request-tokens

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bAddReturnRequestTokensAsync\s*\(`
- **Fix:** AddReturnRequestTokensAsync gained an Order parameter before orderItem in 5.00.

### [CHECK] allowed-tokens

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bGetListOfAllowedTokensAsync\s*\(`, then keep only calls whose first argument is not `messageTemplate:`, `tokenGroups:` or empty
- **Exact rule** (uses a look-ahead; for reference): `\bGetListOfAllowedTokensAsync\s*\(\s*(?!messageTemplate\s*:|tokenGroups\s*:|\))`
- **Fix:** GetListOfAllowedTokensAsync is now (MessageTemplate messageTemplate = null, IList<string> tokenGroups = null). Pass token groups by name (tokenGroups: ...).

### [CHECK] contact-us-message

- **Search in:** `*.cs`, and Razor code in `*.cshtml`
- **Pattern:** `\bSendContactUsMessageAsync\s*\(`
- **Fix:** SendContactUsMessageAsync gained IDictionary<string, string> customAttributes in 5.00.

### [CHECK] swiper

- **Search in:** `*.cs`, `*.cshtml`, `*.csproj`, `*.js`, `plugin.json`, `theme.json`
- **Pattern:** `\bnew\s+Swiper\s*\(|\bswiper-(bundle|container)\b`
- **Fix:** Swiper went from 11 to 14 in 5.00. Check slider options and markup against the Swiper 14 migration notes.

### [CHECK] removed-public-views

- **Search in:** the **file path** of each `*.cshtml` (relative to the scanned folder), not its contents
- **Pattern:** `(^|[/\\])Views[/\\]((Boards|News)[/\\]|Shared[/\\]Components[/\\](HomepageNews|HomepagePolls|PollBlock|NewsRssHeaderLink)[/\\]|Profile[/\\]Components[/\\]ProfilePosts[/\\]|Boards[/\\]Components[/\\])`
- **Fix:** These public views moved from Nop.Web into the Forums/News/Polls plugins in 5.00; theme overrides at these paths are no longer used.

