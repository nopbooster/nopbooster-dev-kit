#!/usr/bin/env python3
"""
NopBooster upgrade scanner for nopCommerce plugins and themes.

Finds code that breaks or needs attention when moving a plugin/theme
from nopCommerce 4.70, 4.80 or 4.90 to a newer version (default target 5.00).
Rules were derived from diffs of the nopCommerce 4.70.5, 4.80.9, 4.90.8 and
5.00.0 source.

Usage:
    python scan_upgrade.py <path> [--from 4.70|4.80|4.90] [--to 4.80|4.90|5.00]

<path> is a plugin folder, a theme folder, or a folder containing several.
--from is auto-detected from plugin.json / .csproj when omitted.
Output is Markdown, grouped by rule, with file:line references.
The scanner is a guide, not a compiler: always build afterwards.
"""

import argparse
import json
import os
import re
import sys

VERSIONS = ["4.70", "4.80", "4.90", "5.00"]

# (introduced_in, severity, id, regex, file_glob_kind, message[, skip_if])
# skip_if (optional): regex; files containing it are already fixed for this rule
# introduced_in: the version whose upgrade causes the issue
# severity: BREAK (won't compile/run), CHECK (compiles but may misbehave), TIDY (recommended)
RULES = [
    # ---------------- 4.70 -> 4.80 ----------------
    ("4.80", "BREAK", "permission-provider",
     r"\bStandardPermissionProvider\.", "cs",
     "StandardPermissionProvider was removed. Use StandardPermission.{Area}.{CONST} with [CheckPermission(...)] on actions or IPermissionService.AuthorizeAsync(string)."),
    ("4.80", "BREAK", "ipermissionprovider",
     r"\bIPermissionProvider\b|\b(Install|Uninstall)PermissionsAsync\s*\(", "cs",
     "IPermissionProvider and Install/UninstallPermissionsAsync were removed. Implement IPermissionConfigManager (parameterless ctor) and call DeletePermissionAsync(name) on uninstall."),
    ("4.80", "TIDY", "access-denied-guard",
     r"return\s+AccessDeniedView\s*\(\s*\)", "cs",
     "Manual permission guard. In 4.80+ replace the AuthorizeAsync + AccessDeniedView() pair with a [CheckPermission(...)] attribute on the action."),
    ("4.80", "BREAK", "sitemap-menu",
     r"\bSiteMapNode\b|\bI?XmlSiteMap\b", "cs",
     "SiteMapNode/XmlSiteMap were removed. Build menu items with AdminMenuItem via an IConsumer<AdminMenuCreatedEvent> or BaseAdminMenuCreatedEventConsumer."),
    ("4.80", "CHECK", "admin-menu-plugin",
     r"\bIAdminMenuPlugin\b|\bManageSiteMapAsync\s*\(", "cs",
     "IAdminMenuPlugin is obsolete from 4.80 (parameter is now AdminMenuItem). Move the menu code to AdminMenuCreatedEvent handling."),
    ("4.80", "BREAK", "acl-supported-factory",
     r"\bI?AclSupportedModelFactory\b", "cs",
     "IAclSupportedModelFactory/AclSupportedModelFactory were removed from Nop.Web.Framework.Factories."),
    ("4.80", "BREAK", "localized-enum",
     r"\bILocalizedEnum\b", "cs",
     "ILocalizedEnum was removed from Nop.Core."),
    ("4.80", "BREAK", "product-flags",
     r"\bUpdateHasDiscountsAppliedAsync\s*\(|\bUpdateHasTierPricesPropertyAsync\s*\(", "cs",
     "IProductService.UpdateHasDiscountsAppliedAsync / UpdateHasTierPricesPropertyAsync were removed."),
    ("4.80", "CHECK", "logger-return",
     r"=\s*await\s+_?logger\.InsertLogAsync\s*\(|=\s*_?logger\.InsertLog\s*\(", "cs",
     "ILogger.InsertLogAsync now returns Task (was Task<Log>) and InsertLog returns void. Remove the assignment."),
    ("4.80", "CHECK", "store-tokens",
     r"\bAddStoreTokensAsync\s*\(", "cs",
     "AddStoreTokensAsync gained a required int languageId parameter in 4.80."),
    ("4.80", "CHECK", "campaign-send",
     r"\bSendCampaignAsync\s*\(", "cs",
     "ICampaignService.SendCampaignAsync(campaign, emailAccount, email) gained a required int languageId parameter in 4.80."),
    ("4.80", "BREAK", "net8",
     r"<TargetFramework>\s*net8\.0\s*</TargetFramework>", "csproj",
     "nopCommerce 4.80+ requires net9.0."),
    ("4.80", "CHECK", "review-helpfulness-view",
     r"_ProductReviewHelpfulness", "view",
     "_ProductReviewHelpfulness moved from Views/Product to Views/Shared in 4.80 — move theme overrides."),

    # ---------------- 4.80 -> 4.90 ----------------
    ("4.90", "BREAK", "product-reviews-moved",
     r"[pP]roductService\s*\.\s*(GetAllProductReviewsAsync|GetProductReviewByIdAsync|GetProductReviewsByIdsAsync|InsertProductReviewAsync|UpdateProductReviewAsync|DeleteProductReviewsAsync|DeleteProductReviewAsync|SetProductReviewHelpfulnessAsync|UpdateProductReviewHelpfulnessTotalsAsync|UpdateProductReviewTotalsAsync|CanAddReviewAsync)\b", "cs",
     "Product review methods moved from IProductService to IProductReviewService in 4.90. Inject IProductReviewService."),
    ("4.90", "BREAK", "product-store-mappings",
     r"\bUpdateProductStoreMappingsAsync\s*\(", "cs",
     "IProductService.UpdateProductStoreMappingsAsync was removed in 4.90."),
    ("4.90", "BREAK", "warehouses-moved",
     r"[sS]hippingService\s*\.\s*(GetWarehouseByIdAsync|GetAllWarehousesAsync|GetNearestWarehouseAsync|InsertWarehouseAsync|UpdateWarehouseAsync|DeleteWarehouseAsync)\b", "cs",
     "Warehouse methods moved from IShippingService to IWarehouseService in 4.90."),
    ("4.90", "BREAK", "shipping-methods-moved",
     r"[sS]hippingService\s*\.\s*(GetShippingMethodByIdAsync|GetAllShippingMethodsAsync|InsertShippingMethodAsync|UpdateShippingMethodAsync|DeleteShippingMethodAsync|GetShippingMethodCountryMappingAsync|InsertShippingMethodCountryMappingAsync|DeleteShippingMethodCountryMappingAsync|CountryRestrictionExistsAsync)\b", "cs",
     "Shipping-method methods moved from IShippingService to IShippingMethodsService in 4.90."),
    ("4.90", "BREAK", "payment-custom-values",
     r"\bGenerateOrderGuidAsync\s*\(|\bSerializeCustomValues\s*\(|\bDeserializeCustomValues\s*\(|\bDictionarySerializer\b", "cs",
     "IPaymentService.GenerateOrderGuidAsync/SerializeCustomValues/DeserializeCustomValues and DictionarySerializer were removed. Use IOrderProcessingService.Set/GetProcessPaymentRequestAsync and the CustomValues class (SerializeToXml/FillByXml)."),
    ("4.90", "BREAK", "order-payment-session",
     r"[\"']OrderPaymentInfo[\"']", "cs",
     "The in-progress ProcessPaymentRequest is no longer kept in session 'OrderPaymentInfo'. Use IOrderProcessingService.GetProcessPaymentRequestAsync()/SetProcessPaymentRequestAsync()."),
    ("4.90", "CHECK", "custom-values-dictionary",
     r"CustomValues\s*(\.\s*(Add\s*\(\s*[\"']|ContainsKey\s*\()|\[\s*[\"'][^\"']+[\"']\s*\]\s*=)|new\s+Dictionary<string,\s*object>\s*\(\s*\)\s*;?\s*//.*CustomValues|CustomValues\s*=\s*new\s+Dictionary", "cs",
     "ProcessPaymentRequest.CustomValues is now a CustomValues list, not Dictionary<string, object>. Use CustomValues.Add(new CustomValue(name, value, ...)), TryGetValue, Remove."),
    ("4.90", "BREAK", "spec-attributes",
     r"\bGetSpecificationAttributesAsync\s*\(", "cs",
     "ISpecificationAttributeService.GetSpecificationAttributesAsync was renamed GetAllSpecificationAttributesAsync in 4.90."),
    ("4.90", "CHECK", "product-attributes-positional",
     r"\bGetAllProductAttributesAsync\s*\(\s*(\d|pageIndex|[a-zA-Z_]*[pP]age)", "cs",
     "GetAllProductAttributesAsync now starts with string name = null. Positional page arguments must become named (pageIndex:, pageSize:)."),
    ("4.90", "BREAK", "attribute-value-picture",
     r"\bDeleteProductAttributeValuePictureAsync\s*\(", "cs",
     "Replaced by DeleteProductAttributeValuePicturesAsync(IList<ProductAttributeValuePicture>) in 4.90."),
    ("4.90", "BREAK", "newsletter-lookups",
     r"\bGetNewsLetterSubscriptionByEmailAndStoreIdAsync\s*\(|\bGetNewsLetterSubscriptionByGuidAsync\s*\(", "cs",
     "Replaced by GetNewsLetterSubscriptionsByEmailAsync(email, storeId, subscriptionTypeId, isActive) / GetNewsLetterSubscriptionsByGuidAsync(guid), which return lists."),
    ("4.90", "BREAK", "newsletter-casing",
     r"\bExportNewsletterSubscribersToTxtAsync\b|\bImportNewsletterSubscribersFromTxtAsync\b", "cs",
     "Renamed to ...NewsLetterSubscribers... (capital L) in 4.90."),
    ("4.90", "BREAK", "token-events-namespace",
     r"\b(MessageTokensAddedEvent|EntityTokensAddedEvent)\b", "cs",
     "MessageTokensAddedEvent / EntityTokensAddedEvent moved from Nop.Core.Domain.Messages to Nop.Services.Messages in 4.90 — update the using."),
    ("4.90", "BREAK", "pdf-sources",
     r"\b(InvoiceSource|ShipmentSource|CatalogSource|DocumentSource)\b", "cs",
     "PDF sources were replaced by InvoiceDocument / ShipmentDocument / CatalogDocument (PdfDocument<T>) in 4.90."),
    ("4.90", "BREAK", "azure-core",
     r"\bAzurePictureService\b|\bAzureBlobConfig\b", "cs",
     "Azure Blob storage left core in 4.90; it is now the Nop.Plugin.Misc.AzureBlob plugin."),
    ("4.90", "BREAK", "menu-settings",
     r"\bDisplayDefaultMenuItemSettings\b|\bDisplayDefaultFooterItemSettings\b", "cs",
     "Removed in 4.90 — header/footer links are managed by the Menus feature (IMenuService)."),
    ("4.90", "CHECK", "message-token-groups",
     r"\bGetListOfAllowedTokensAsync\s*\(", "cs",
     "Parameter type changed from IEnumerable<string> to IList<string> in 4.90."),
    ("4.90", "CHECK", "topics-overloads",
     r"\bGetAllTopicsAsync\s*\(", "cs",
     "ITopicService.GetAllTopicsAsync overloads changed in 4.90: (storeId, ignoreAcl, showHidden) and (storeId, keywords, ignoreAcl, showHidden). Check arguments."),
    ("4.90", "CHECK", "theme-provider",
     r":\s*[^{]*\bIThemeProvider\b", "cs",
     "IThemeProvider gained InitializeAsync() in 4.90 (only matters if you implement it)."),
    ("4.90", "BREAK", "iplugin-direct",
     r"class\s+\w+\s*:\s*(?![^{]*\bBasePlugin\b)[^{]*\bIPlugin\b", "cs",
     "IPlugin gained InstallSampleDataAsync() in 4.90. Derive from BasePlugin or implement it."),
    ("4.90", "TIDY", "url-helper-factory",
     r"\bIUrlHelperFactory\b|\bIActionContextAccessor\b", "cs",
     "4.90 core plugins build URLs with INopUrlHelper.RouteUrl(routeName) instead of IUrlHelperFactory + IActionContextAccessor."),
    ("4.80", "TIDY", "csproj-relative",
     r"\.\.\\\.\.\\Presentation\\Nop\.Web|\$\(MSBuildProjectDirectory\)\\\.\.\\\.\.\\Build", "csproj",
     "From 4.80 core plugins use $(SolutionDir)-based OutputPath/ProjectReference/ClearPluginAssemblies paths; build from the solution."),
    ("4.90", "BREAK", "top-menu",
     r"\bTopMenuViewComponent\b|Components[/\\]TopMenu\b|\bTopMenuModel\b", "any",
     "TopMenu was replaced by MainMenu (and FooterMenu) in 4.90. Rebuild header navigation customisations on Components/MainMenu."),

    # ---------------- 4.90 -> 5.00 ----------------
    ("5.00", "BREAK", "net9",
     r"<TargetFramework>\s*net[89]\.0\s*</TargetFramework>", "csproj",
     "nopCommerce 5.00 requires net10.0 (and the .NET 10 SDK). Update Microsoft.* package references to 10.0.x as well."),
    ("5.00", "BREAK", "automapper",
     r"\busing\s+AutoMapper\b|:\s*Profile\s*,\s*IOrderedMapperProfile|\bAutoMapperConfiguration\b|\bIMapper\b", "cs",
     "AutoMapper was replaced by Mapster in 5.00. Derive mapping profiles from BaseMapperProfile (Nop.Core.Infrastructure.Mapper), drop 'using AutoMapper' and the Order property; ForMember(..., o => o.Ignore()/MapFrom()) still works."),
    ("5.00", "BREAK", "automapper-package",
     r"Include=\"AutoMapper\"|Include=\"FluentValidation\.AspNetCore\"", "csproj",
     "Core no longer ships AutoMapper or FluentValidation.AspNetCore in 5.00. Remove the package reference (use Mapster via BaseMapperProfile; FluentValidation 12 is provided by core)."),
    ("5.00", "BREAK", "fluentvalidation-aspnetcore",
     r"\busing\s+FluentValidation\.AspNetCore\b", "cs",
     "FluentValidation.AspNetCore is gone in 5.00 (FluentValidation 12). Remove the using; automatic validation comes from [AutoValidation] on BaseController."),
    ("5.00", "BREAK", "is-credit-card",
     r"\.IsCreditCard\s*\(|\bCreditCardPropertyValidator\b", "cs",
     "nop's IsCreditCard()/CreditCardPropertyValidator were removed in 5.00. Use FluentValidation's built-in .CreditCard()."),
    ("5.00", "BREAK", "iwebhelper-namespace",
     r"\bI?WebHelper\b", "cs",
     "IWebHelper/WebHelper moved from Nop.Core to Nop.Services.Helpers in 5.00. Add 'using Nop.Services.Helpers;'.",
     r"using\s+Nop\.Services\.Helpers\b"),
    ("5.00", "BREAK", "ithemecontext-namespace",
     r"\bIThemeContext\b|\busing\s+Nop\.Web\.Framework\.Themes\s*;", "any",
     "IThemeContext moved from Nop.Web.Framework.Themes to Nop.Services.Themes in 5.00. Update the using.",
     r"using\s+Nop\.Services\.Themes\b"),
    ("5.00", "BREAK", "forums-news-polls",
     r"\bNop\.(Core\.Domain|Services)\.(Forums|News|Polls)\b|\bI(Forum|News|Poll)Service\b|\bIsForumModeratorAsync\b", "any",
     "Forums, News and Polls left core in 5.00 and are now the Nop.Plugin.Misc.Forums/News/Polls plugins (PrivateMessage moved to Nop.Core.Domain.Customers). Reference the plugin's own types, or drop the feature."),
    ("5.00", "BREAK", "forum-news-messages",
     r"[tT]okenProvider\s*\.\s*Add(Forum|ForumTopic|ForumPost|NewsComment)TokensAsync\b|[mM]essageService\s*\.\s*(Send(NewForumTopic|NewForumPost)MessageAsync|SendNewsCommentStoreOwnerNotificationMessageAsync)\b", "cs",
     "Forum and news message tokens and notifications were removed from core message services in 5.00."),
    ("5.00", "BREAK", "removed-widget-zones",
     r"\b(Public|Admin)WidgetZones\s*\.\s*(Boards\w*|NewsItemPage\w*|NewsListPage\w*|HomepageBeforeNews|HomepageBeforePoll|CustomerForumSubscriptions\w*|Forum\w*|News(CommentListButtons|DetailsBlock|DetailsButtons|ItemsDetailsBlock|ListButtons|SettingsButtons)|Poll\w*)\b", "cs",
     "This widget zone was removed with forums/news/polls in 5.00; the widget will no longer render there."),
    ("5.00", "BREAK", "bbcode",
     r"\bI?BBCodeHelper\b|\bResolveLinksHelper\b|\bNop\.Services\.Html\.CodeFormatter\b|\bnop-bb-code-editor\b", "any",
     "BBCode helpers, ResolveLinksHelper and the code formatter were removed from core in 5.00."),
    ("5.00", "BREAK", "sync-localization",
     r"[lL]ocalizationService\s*\.\s*(AddOrUpdateLocaleResource|DeleteLocaleResources|DeleteLocaleStringResource|UpdateLocaleStringResource)\s*\(", "cs",
     "Synchronous ILocalizationService methods were removed in 5.00. Use the ...Async versions, or this.AddOrUpdateLocaleResource(dict) / this.DeleteLocaleResources(names) inside a migration."),
    ("5.00", "BREAK", "sync-settings",
     r"[sS]ettingService\s*\.\s*(InsertSetting|UpdateSetting|DeleteSetting|ClearCache)\s*\(", "cs",
     "Synchronous ISettingService methods were removed in 5.00. Use the ...Async versions, or this.SetSettingIfNotExists/GetSettingByKey/DeleteSettings inside a migration."),
    ("5.00", "BREAK", "sync-logger",
     r"[lL]ogger\s*\.\s*(Error|Information|Warning|InsertLog)\s*\(", "cs",
     "Synchronous ILogger methods were removed in 5.00. Use ErrorAsync/InformationAsync/WarningAsync/InsertLogAsync."),
    ("5.00", "BREAK", "sync-store",
     r"[sS]toreService\s*\.\s*UpdateStore\s*\(", "cs",
     "IStoreService.UpdateStore was removed in 5.00. Use UpdateStoreAsync."),
    ("5.00", "BREAK", "migration-language-data",
     r"\bGetLanguageData\s*\(", "cs",
     "MigrationExtension.GetLanguageData() was removed in 5.00 (now MigrationExtensions). Use this.AddOrUpdateLocaleResource(dict) and this.RenameLocales(dict) without language/service arguments."),
    ("5.00", "BREAK", "url-helper-extensions",
     r"\.\s*RouteTopicUrl\s*\(|\bUrl\s*\.\s*RouteUrl\s*<", "any",
     "Nop.Web.Framework.Mvc.Routing.UrlHelperExtensions (RouteUrl<TEntity>, RouteTopicUrl) was removed in 5.00. Use INopUrlHelper.RouteGenericUrlAsync<TEntity>() / RouteTopicUrlAsync()."),
    ("5.00", "BREAK", "removed-mvc-infra",
     r"\bNopMetadataProvider\b|\bIModelAttribute\b|\bInvariantNumberModelBinder(Provider)?\b|\bRoxyFileman\w*\b", "cs",
     "Removed in 5.00 (model metadata/binder infrastructure; RoxyFileman was replaced by elFinder)."),
    ("5.00", "BREAK", "format-base-price",
     r"\bFormatBasePriceAsync\s*\([^)]*,[^)]*,", "cs",
     "IPriceFormatter.FormatBasePriceAsync now takes (product, decimal? basePrice). Get the base price from IProductService.GetBaseProductPriceAsync(product, productPrice, totalWeight)."),
    ("5.00", "CHECK", "return-request-tokens",
     r"\bAddReturnRequestTokensAsync\s*\(", "cs",
     "AddReturnRequestTokensAsync gained an Order parameter before orderItem in 5.00."),
    ("5.00", "CHECK", "allowed-tokens",
     r"\bGetListOfAllowedTokensAsync\s*\(\s*(?!messageTemplate\s*:|tokenGroups\s*:|\))", "cs",
     "GetListOfAllowedTokensAsync is now (MessageTemplate messageTemplate = null, IList<string> tokenGroups = null). Pass token groups by name (tokenGroups: ...)."),
    ("5.00", "CHECK", "contact-us-message",
     r"\bSendContactUsMessageAsync\s*\(", "cs",
     "SendContactUsMessageAsync gained IDictionary<string, string> customAttributes in 5.00."),
    ("5.00", "BREAK", "search-term-by-keyword",
     r"\bGetSearchTermByKeywordAsync\s*\(", "cs",
     "ISearchTermService.GetSearchTermByKeywordAsync was removed in 5.00 (search terms are per customer: SearchTermHistoryItemsAsync, DeleteSearchTermsByKeywordAsync)."),
    ("5.00", "CHECK", "swiper",
     r"\bnew\s+Swiper\s*\(|\bswiper-(bundle|container)\b", "any",
     "Swiper went from 11 to 14 in 5.00. Check slider options and markup against the Swiper 14 migration notes."),
    ("5.00", "CHECK", "removed-public-views",
     r"(^|[/\\])Views[/\\]((Boards|News)[/\\]|Shared[/\\]Components[/\\](HomepageNews|HomepagePolls|PollBlock|NewsRssHeaderLink)[/\\]|Profile[/\\]Components[/\\]ProfilePosts[/\\]|Boards[/\\]Components[/\\])", "path",
     "These public views moved from Nop.Web into the Forums/News/Polls plugins in 5.00; theme overrides at these paths are no longer used."),
]

SEV_ORDER = {"BREAK": 0, "CHECK": 1, "TIDY": 2}
SKIP_DIRS = {"bin", "obj", "node_modules", ".git", ".vs", "packages", "wwwroot\\lib", "lib_npm"}


def kind_of(path):
    p = path.lower()
    if p.endswith(".cs"):
        return "cs"
    if p.endswith(".csproj"):
        return "csproj"
    if p.endswith(".cshtml"):
        return "view"
    if p.endswith(".js"):
        return "js"
    if p.endswith("plugin.json") or p.endswith("theme.json"):
        return "json"
    return None


def detect_from_version(root):
    found = set()
    by_framework = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            full = os.path.join(dirpath, f)
            if f == "plugin.json":
                try:
                    with open(full, encoding="utf-8-sig") as fh:
                        data = json.load(fh)
                    for v in data.get("SupportedVersions", []):
                        found.add(str(v)[:4])
                except Exception:
                    pass
            elif f.endswith(".csproj"):
                try:
                    txt = open(full, encoding="utf-8-sig", errors="ignore").read()
                    if "net8.0" in txt:
                        by_framework.add("4.70")
                    elif "net9.0" in txt:
                        by_framework.add("4.80")  # 4.80 or 4.90: scan from the older one
                except Exception:
                    pass
    known = [v for v in VERSIONS if v in found] or [v for v in VERSIONS if v in by_framework]
    return known[0] if known else None


def view_imports_text(view_path, root):
    """Text of every _ViewImports.cshtml from the view's folder up to the scan root."""
    out = []
    d = os.path.dirname(os.path.abspath(view_path))
    stop = os.path.abspath(root)
    while True:
        vi = os.path.join(d, "_ViewImports.cshtml")
        if os.path.isfile(vi) and os.path.abspath(vi) != os.path.abspath(view_path):
            try:
                out.append(open(vi, encoding="utf-8-sig", errors="ignore").read())
            except Exception:
                pass
        if d == stop or len(d) <= len(stop):
            break
        d = os.path.dirname(d)
    return "\n" + "\n".join(out)


def scan(root, from_v, to_v):
    applicable = [r for r in RULES
                  if VERSIONS.index(from_v) < VERSIONS.index(r[0]) <= VERSIONS.index(to_v)]
    compiled = [(r, re.compile(r[3]), re.compile(r[6]) if len(r) > 6 else None) for r in applicable]
    hits = {}
    supported_versions = []
    files_scanned = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            full = os.path.join(dirpath, f)
            k = kind_of(full)
            if not k:
                continue
            files_scanned += 1
            try:
                lines = open(full, encoding="utf-8-sig", errors="ignore").read().splitlines()
            except Exception:
                continue
            rel = os.path.relpath(full, root)
            if f == "plugin.json":
                try:
                    data = json.loads("\n".join(lines))
                    supported_versions.append((rel, data.get("SupportedVersions", []), data.get("Version")))
                except Exception:
                    pass
            whole = "\n".join(lines)
            if k == "view":
                # usings in _ViewImports.cshtml apply to every view below it
                whole += view_imports_text(full, root)
            for (rule, rx, skip) in compiled:
                rk = rule[4]
                if skip and skip.search(whole):
                    continue
                if rk == "path":
                    if k == "view" and rx.search(rel):
                        hits.setdefault(rule[2], (rule, []))[1].append((rel, 1, "(file path)"))
                    continue
                # C# rules also apply to Razor code in views
                if not (rk == "any" or rk == k or (rk == "cs" and k == "view")):
                    continue
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped.startswith("//") or stripped.startswith("///"):
                        continue
                    if rx.search(line):
                        hits.setdefault(rule[2], (rule, []))[1].append((rel, i, stripped[:160]))
    return hits, supported_versions, files_scanned


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--from", dest="from_v", choices=VERSIONS[:-1])
    ap.add_argument("--to", dest="to_v", choices=VERSIONS[1:], default="5.00")
    a = ap.parse_args()

    if not os.path.isdir(a.path):
        print(f"Not a folder: {a.path}", file=sys.stderr)
        sys.exit(2)

    from_v = a.from_v or detect_from_version(a.path)
    if not from_v:
        print("Could not detect the current version (no plugin.json SupportedVersions). Pass --from 4.70, 4.80 or 4.90.", file=sys.stderr)
        sys.exit(2)
    if VERSIONS.index(from_v) >= VERSIONS.index(a.to_v):
        print(f"Nothing to do: --from {from_v} is not older than --to {a.to_v}.")
        return

    hits, sv, n = scan(a.path, from_v, a.to_v)

    print(f"# nopCommerce upgrade scan: {from_v} → {a.to_v}\n")
    print(f"Scanned {n} files under `{a.path}`.\n")

    if sv:
        print("## plugin.json\n")
        for rel, versions, ver in sv:
            ok = a.to_v in [str(v)[:4] for v in versions]
            mark = "OK" if ok else "BREAK"
            print(f"- [{mark}] `{rel}` SupportedVersions={versions} Version={ver}"
                  + ("" if ok else f" → set SupportedVersions to [\"{a.to_v}\"] and bump Version"))
        print()

    if not hits:
        print("No known breaking patterns found. Build against the target version to confirm.")
        return

    counts = {"BREAK": 0, "CHECK": 0, "TIDY": 0}
    ordered = sorted(hits.values(), key=lambda h: (SEV_ORDER[h[0][1]], VERSIONS.index(h[0][0]), h[0][2]))
    for rule, items in ordered:
        counts[rule[1]] += len(items)
    print(f"**{counts['BREAK']} BREAK · {counts['CHECK']} CHECK · {counts['TIDY']} TIDY**\n")
    print("BREAK = will not compile or run · CHECK = compiles, may behave differently · TIDY = recommended\n")

    for rule, items in ordered:
        intro, sev, rid, _, _, msg = rule[:6]
        print(f"## [{sev}] {rid} (changed in {intro})\n")
        print(f"{msg}\n")
        for rel, ln, text in items[:50]:
            print(f"- `{rel}:{ln}` — `{text}`")
        if len(items) > 50:
            print(f"- … and {len(items) - 50} more")
        print()


if __name__ == "__main__":
    main()
