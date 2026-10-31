#!/usr/bin/env python3
"""
NopBooster upgrade scanner for nopCommerce plugins and themes.

Finds code that breaks or needs attention when moving a plugin/theme
from nopCommerce 4.70 or 4.80 to a newer version (default target 4.90).
Rules were derived from diffs of the nopCommerce 4.70.5, 4.80.9 and 4.90.8 source.

Usage:
    python scan_upgrade.py <path> [--from 4.70|4.80] [--to 4.80|4.90]

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

VERSIONS = ["4.70", "4.80", "4.90"]

# (introduced_in, severity, id, regex, file_glob_kind, message)
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
                        found.add("4.70")
                except Exception:
                    pass
    known = [v for v in VERSIONS if v in found]
    return known[0] if known else None


def scan(root, from_v, to_v):
    applicable = [r for r in RULES
                  if VERSIONS.index(from_v) < VERSIONS.index(r[0]) <= VERSIONS.index(to_v)]
    compiled = [(r, re.compile(r[3])) for r in applicable]
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
            for (rule, rx) in compiled:
                rk = rule[4]
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
    ap.add_argument("--to", dest="to_v", choices=VERSIONS[1:], default="4.90")
    a = ap.parse_args()

    if not os.path.isdir(a.path):
        print(f"Not a folder: {a.path}", file=sys.stderr)
        sys.exit(2)

    from_v = a.from_v or detect_from_version(a.path)
    if not from_v:
        print("Could not detect the current version (no plugin.json SupportedVersions). Pass --from 4.70 or --from 4.80.", file=sys.stderr)
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
        intro, sev, rid, _, _, msg = rule
        print(f"## [{sev}] {rid} (changed in {intro})\n")
        print(f"{msg}\n")
        for rel, ln, text in items[:50]:
            print(f"- `{rel}:{ln}` — `{text}`")
        if len(items) > 50:
            print(f"- … and {len(items) - 50} more")
        print()


if __name__ == "__main__":
    main()
