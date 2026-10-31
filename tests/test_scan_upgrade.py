"""
Self-test for skills/nop-upgrade/scripts/scan_upgrade.py.

Runs the scanner on tests/fixtures/Nop.Plugin.Misc.Legacy470 (deliberately
outdated 4.70 code) and checks that every expected rule fires, and that
4.80 → 4.90 scanning ignores the 4.70-only rules.

    python tests/test_scan_upgrade.py
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCANNER = os.path.join(ROOT, "skills", "nop-upgrade", "scripts", "scan_upgrade.py")
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "Nop.Plugin.Misc.Legacy470")


def run(*args):
    out = subprocess.run([sys.executable, "-I", SCANNER, FIXTURE, *args],
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

    if failures:
        print("FAILED")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print(f"OK — {len(expected)} rules verified on the 4.70 fixture, hop filtering verified.")


if __name__ == "__main__":
    main()
