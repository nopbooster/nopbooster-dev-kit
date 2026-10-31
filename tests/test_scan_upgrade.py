"""
Self-test for skills/nop-upgrade/scripts/scan_upgrade.py.

Runs the scanner on the deliberately outdated fixtures in tests/fixtures:
- Nop.Plugin.Misc.Legacy470 (4.70 code): every expected rule fires, and
  4.80 → 4.90 scanning ignores the 4.70-only rules;
- Nop.Plugin.Misc.Legacy490 (4.90 code): every 5.00 rule fires, version
  auto-detection picks 4.90, and fixed files are not reported.

    python tests/test_scan_upgrade.py
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCANNER = os.path.join(ROOT, "skills", "nop-upgrade", "scripts", "scan_upgrade.py")
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "Nop.Plugin.Misc.Legacy470")
FIXTURE_490 = os.path.join(ROOT, "tests", "fixtures", "Nop.Plugin.Misc.Legacy490")


def run(*args, fixture=FIXTURE):
    out = subprocess.run([sys.executable, "-I", SCANNER, fixture, *args],
                         capture_output=True, text=True, check=True)
    return out.stdout


def main():
    failures = []

    full = run("--to", "4.90")
    expected = [
        "net8", "permission-provider", "sitemap-menu", "admin-menu-plugin",
        "access-denied-guard", "csproj-relative",
        "product-reviews-moved", "warehouses-moved", "shipping-methods-moved",
        "payment-custom-values",
    ]
    for rule in expected:
        if f"] {rule} (" not in full:
            failures.append(f"4.70→4.90: expected rule '{rule}' did not fire")
    if "[BREAK] `" not in full or "SupportedVersions" not in full:
        failures.append("4.70→4.90: plugin.json SupportedVersions check missing")

    hop = run("--from", "4.80", "--to", "4.90")
    for rule in ["permission-provider", "sitemap-menu", "net8"]:
        if f"] {rule} (" in hop:
            failures.append(f"4.80→4.90: 4.70-only rule '{rule}' should not fire")
    for rule in ["product-reviews-moved", "warehouses-moved"]:
        if f"] {rule} (" not in hop:
            failures.append(f"4.80→4.90: expected rule '{rule}' did not fire")

    # 4.90 -> 5.00, version auto-detected from plugin.json, default target 5.00
    v5 = run(fixture=FIXTURE_490)
    expected_500 = [
        "net9", "automapper", "automapper-package", "fluentvalidation-aspnetcore", "is-credit-card",
        "iwebhelper-namespace", "ithemecontext-namespace", "forums-news-polls", "removed-widget-zones",
        "sync-localization", "sync-settings", "sync-logger", "migration-language-data",
        "url-helper-extensions", "format-base-price", "allowed-tokens", "swiper",
    ]
    if "scan: 4.90 → 5.00" not in v5:
        failures.append("4.90 fixture: version was not auto-detected as 4.90 → 5.00")
    for rule in expected_500:
        if f"] {rule} (" not in v5:
            failures.append(f"4.90→5.00: expected rule '{rule}' did not fire")
    for rule in ["product-reviews-moved", "permission-provider", "net8"]:
        if f"] {rule} (" in v5:
            failures.append(f"4.90→5.00: older rule '{rule}' should not fire")

    # a file that already has the new using is not reported for the namespace rule
    import shutil, tempfile
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "Fixed.cs"), "w") as f:
            f.write("using Nop.Services.Helpers;\nusing Nop.Services.Themes;\n"
                    "public class Fixed { public Fixed(IWebHelper w, IThemeContext t) { } }\n")
        fixed = run("--from", "4.90", fixture=tmp)
        for rule in ["iwebhelper-namespace", "ithemecontext-namespace"]:
            if f"] {rule} (" in fixed:
                failures.append(f"fixed file: '{rule}' should not fire once the new using is present")
    finally:
        shutil.rmtree(tmp)
    total = len(expected) + len(expected_500)

    if failures:
        print("FAILED")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print(f"OK — {total} rules verified on the 4.70 and 4.90 fixtures; hop filtering, version detection and fixed-file skipping verified.")


if __name__ == "__main__":
    main()
