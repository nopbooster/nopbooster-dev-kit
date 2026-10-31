"""Regenerates the README illustrations in docs/images. Requires Pillow.

    python docs/images/generate.py
"""
import base64, io, os
from PIL import Image, ImageDraw

OUT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(OUT))
SANS = "Inter, 'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SF Mono', Consolas, 'DejaVu Sans Mono', Menlo, monospace"
BLUE = "#1975B4"
NAVY = "#0B1220"
INK = "#0F172A"
MUTED = "#475569"
LINE = "#CBD5E1"
CYAN = "#22D3EE"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def icon_data_uri():
    im = Image.open(os.path.join(ROOT, ".claude-plugin", "icon.png")).convert("RGBA").resize((240, 240), Image.LANCZOS)
    mask = Image.new("L", (240 * 4, 240 * 4), 0)
    ImageDraw.Draw(mask).ellipse([14, 14, 240 * 4 - 14, 240 * 4 - 14], fill=255)
    mask = mask.resize((240, 240), Image.LANCZOS)
    im.putalpha(mask)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def save(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)


def chip(x, y, text, w, fill, color, stroke=None):
    s = f' stroke="{stroke}"' if stroke else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="38" rx="19" fill="{fill}"{s}/>'
            f'<text x="{x + w / 2}" y="{y + 25}" text-anchor="middle" font-family="{SANS}" font-size="16" font-weight="600" fill="{color}">{esc(text)}</text>')


# ---------------------------------------------------------------- banner
def banner():
    W, H = 1280, 440
    icon = icon_data_uri()
    dots = "".join(
        f'<circle cx="{1000 + c * 34 + (r % 2) * 17}" cy="{30 + r * 34}" r="5" fill="{CYAN}" opacity="{0.05 + 0.02 * c}"/>'
        for r in range(12) for c in range(9))
    code = [
        ("prompt", "> /nop-new-plugin Widgets.ProductBadges"),
        ("dim", "  show New and Sale badges on product pages"),
        ("blank", ""),
        ("ok", "Nop.Plugin.Widgets.ProductBadges.csproj"),
        ("ok", "plugin.json  ·  SupportedVersions 4.90"),
        ("ok", "ProductBadgesPlugin.cs  ·  install/uninstall"),
        ("ok", "Admin page with [CheckPermission]"),
        ("ok", "ProductBadgesViewComponent + view"),
        ("ok", "Locale resources, settings, README"),
    ]
    lines = []
    y = 150
    for kind, t in code:
        if kind == "prompt":
            lines.append(f'<text x="772" y="{y}" font-family="{MONO}" font-size="15" fill="#E2E8F0"><tspan fill="{CYAN}">&gt;</tspan>{esc(t[1:])}</text>')
        elif kind == "dim":
            lines.append(f'<text x="772" y="{y}" font-family="{MONO}" font-size="15" fill="#94A3B8">{esc(t)}</text>')
        elif kind == "ok":
            lines.append(f'<text x="772" y="{y}" font-family="{MONO}" font-size="15" fill="#CBD5E1"><tspan fill="#4ADE80">✓ </tspan>{esc(t)}</text>')
        y += 27
    chips = (chip(80, 330, "Build for 4.90", 170, "#13365A", "#DBEAFE", "#2A5C8C")
             + chip(262, 330, "Upgrade 4.70 → 4.80 → 4.90", 286, "#13365A", "#DBEAFE", "#2A5C8C")
             + chip(560, 330, "Review & scan", 160, "#13365A", "#DBEAFE", "#2A5C8C"))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">NopBooster Dev Kit</title>
<desc id="d">nopCommerce expertise for Claude: build plugins and themes for 4.90, upgrade from 4.70 and 4.80.</desc>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset="1" stop-color="#123456"/></linearGradient>
<linearGradient id="glow" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}" stop-opacity="0.35"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>
</defs>
<rect width="{W}" height="{H}" rx="24" fill="url(#bg)"/>
{dots}
<circle cx="150" cy="140" r="120" fill="url(#glow)"/>
<image x="80" y="70" width="140" height="140" href="{icon}"/>
<text x="80" y="268" font-family="{SANS}" font-size="58" font-weight="800" fill="#FFFFFF" letter-spacing="-1">NopBooster Dev Kit</text>
<text x="82" y="308" font-family="{SANS}" font-size="24" fill="#9CC9EA">nopCommerce expertise for Claude</text>
{chips}
<rect x="748" y="70" width="456" height="322" rx="14" fill="#0A0F1A" stroke="#1E3A5F"/>
<circle cx="772" cy="94" r="6" fill="#F87171"/><circle cx="792" cy="94" r="6" fill="#FBBF24"/><circle cx="812" cy="94" r="6" fill="#4ADE80"/>
<text x="1180" y="99" text-anchor="end" font-family="{MONO}" font-size="12" fill="#64748B">Claude Code</text>
<line x1="748" y1="114" x2="1204" y2="114" stroke="#1E293B"/>
{"".join(lines)}
</svg>'''
    save("banner.svg", svg)


# ---------------------------------------------------------------- how it works
def wrap(text, n):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w) if cur else w
    if cur:
        lines.append(cur)
    return lines


def how_it_works():
    W, H = 1200, 600
    out = []
    cards = [(40, "1", "You ask"), (435, "2", "Claude + Dev Kit"), (830, "3", "You get")]
    for x, n, title in cards:
        hl = n == "2"
        out.append(f'<rect x="{x}" y="40" width="330" height="520" rx="18" fill="{"#EFF6FF" if hl else "#FFFFFF"}" stroke="{BLUE if hl else LINE}" stroke-width="{2 if hl else 1.5}"/>')
        out.append(f'<circle cx="{x + 40}" cy="88" r="18" fill="{BLUE}"/><text x="{x + 40}" y="94" text-anchor="middle" font-family="{SANS}" font-size="17" font-weight="700" fill="#fff">{n}</text>')
        out.append(f'<text x="{x + 70}" y="95" font-family="{SANS}" font-size="22" font-weight="700" fill="{INK}">{esc(title)}</text>')
    # arrows
    for ax in (378, 773):
        out.append(f'<path d="M{ax} 300 h40" stroke="{BLUE}" stroke-width="3" fill="none" marker-end="url(#ah)"/>')
    # left: prompts
    prompts = ["“Scaffold a widget plugin that shows badges on product pages.”",
               "“Upgrade our ERP sync plugin from 4.70 to 4.90.”",
               "“Review this payment plugin before we sell it.”"]
    y = 130
    for p in prompts:
        ls = wrap(p, 30)
        h = 26 + 22 * len(ls)
        out.append(f'<rect x="64" y="{y}" width="282" height="{h}" rx="14" fill="#F1F5F9"/>')
        for i, l in enumerate(ls):
            out.append(f'<text x="82" y="{y + 30 + 22 * i}" font-family="{SANS}" font-size="16" fill="{INK}">{esc(l)}</text>')
        y += h + 18
    out.append(f'<text x="64" y="{y + 20}" font-family="{SANS}" font-size="14" fill="{MUTED}">Plain English, or a slash command.</text>')
    # centre: components
    comps = [("nopcommerce-plugin-development", "loads automatically"),
             ("nopcommerce-theme-development", "loads automatically"),
             ("/nop-new-plugin", "scaffold a plugin"),
             ("/nop-upgrade", "upgrade + scanner"),
             ("/nop-review", "pre-release review"),
             ("nop-upgrade-engineer", "agent for bulk upgrades")]
    y = 130
    for name, note in comps:
        out.append(f'<rect x="459" y="{y}" width="282" height="52" rx="10" fill="#FFFFFF" stroke="#BFDBFE"/>')
        out.append(f'<text x="475" y="{y + 22}" font-family="{MONO}" font-size="14" font-weight="600" fill="{BLUE}">{esc(name)}</text>')
        out.append(f'<text x="475" y="{y + 41}" font-family="{SANS}" font-size="13" fill="{MUTED}">{esc(note)}</text>')
        y += 62
    out.append(f'<text x="600" y="522" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{MUTED}">Checked against nopCommerce source</text>')
    out.append(f'<text x="600" y="541" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="600" fill="{INK}">4.70.5 · 4.80.9 · 4.90.8</text>')
    # right: results
    res = [("Buildable plugin project", "csproj, plugin.json, install / uninstall, admin page, views, locales"),
           ("Upgraded code + report", "one version hop at a time, file:line findings, build verified"),
           ("Review with fixes", "must fix · should fix · nice to have, with code")]
    y = 130
    for t, d in res:
        ls = wrap(d, 34)
        h = 44 + 20 * len(ls)
        out.append(f'<rect x="854" y="{y}" width="282" height="{h}" rx="12" fill="#F8FAFC" stroke="{LINE}"/>')
        out.append(f'<text x="872" y="{y + 28}" font-family="{SANS}" font-size="16" font-weight="700" fill="{INK}"><tspan fill="#16A34A">✓ </tspan>{esc(t)}</text>')
        for i, l in enumerate(ls):
            out.append(f'<text x="872" y="{y + 52 + 20 * i}" font-family="{SANS}" font-size="14" fill="{MUTED}">{esc(l)}</text>')
        y += h + 18
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">How the NopBooster Dev Kit works: you ask, Claude uses the Dev Kit skills, you get a plugin, an upgrade or a review</title>
<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{BLUE}"/></marker></defs>
<rect width="{W}" height="{H}" rx="20" fill="#F8FAFC"/>
{"".join(out)}
</svg>'''
    save("how-it-works.svg", svg)


# ---------------------------------------------------------------- upgrade path
def upgrade_path():
    W, H = 1200, 470
    out = []
    nodes = [(150, "4.70", ".NET 8"), (600, "4.80", ".NET 9"), (1050, "4.90", ".NET 9")]
    out.append(f'<line x1="150" y1="110" x2="1050" y2="110" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>')
    for x, v, net in nodes:
        fill = BLUE if v == "4.90" else "#FFFFFF"
        col = "#FFFFFF" if v == "4.90" else INK
        out.append(f'<circle cx="{x}" cy="110" r="50" fill="{fill}" stroke="{BLUE}" stroke-width="4"/>')
        out.append(f'<text x="{x}" y="112" text-anchor="middle" font-family="{SANS}" font-size="26" font-weight="800" fill="{col}">{v}</text>')
        out.append(f'<text x="{x}" y="134" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{"#DBEAFE" if v == "4.90" else MUTED}">{net}</text>')
    hops = [(152, "Hop 1 · 4.70 → 4.80", [
                "Permissions rewritten → [CheckPermission]",
                "IPermissionProvider → IPermissionConfigManager",
                "SiteMapNode menu → AdminMenuCreatedEvent",
                ".csproj → net9.0 + $(SolutionDir) paths"]),
            (608, "Hop 2 · 4.80 → 4.90", [
                "Reviews → IProductReviewService",
                "Warehouses, shipping methods split out",
                "Payment CustomValues reworked",
                "Themes: TopMenu → MainMenu"])]
    for x, title, items in hops:
        out.append(f'<rect x="{x}" y="190" width="440" height="210" rx="16" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>')
        out.append(f'<text x="{x + 24}" y="226" font-family="{SANS}" font-size="18" font-weight="700" fill="{BLUE}">{esc(title)}</text>')
        for i, it in enumerate(items):
            out.append(f'<circle cx="{x + 30}" cy="{260 + i * 36}" r="4" fill="{BLUE}"/>')
            out.append(f'<text x="{x + 44}" y="{265 + i * 36}" font-family="{SANS}" font-size="15.5" fill="{INK}">{esc(it)}</text>')
        out.append(f'<path d="M{x + 222} 190 v-22" stroke="{LINE}" stroke-width="2" stroke-dasharray="4 4"/>')
    steps = ["Scan", "Fix", "Build", "Test"]
    sx = 380
    out.append(f'<text x="{sx - 20}" y="447" text-anchor="end" font-family="{SANS}" font-size="15" fill="{MUTED}">Every hop:</text>')
    for i, s in enumerate(steps):
        x = sx + i * 120
        out.append(chip(x, 420, s, 96, "#EFF6FF", BLUE, "#BFDBFE"))
        if i < 3:
            out.append(f'<text x="{x + 108}" y="446" text-anchor="middle" font-family="{SANS}" font-size="18" fill="{MUTED}">→</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">Upgrade path: 4.70 to 4.80 to 4.90, with the main breaking changes of each hop</title>
<rect width="{W}" height="{H}" rx="20" fill="#F8FAFC"/>
{"".join(out)}
</svg>'''
    save("upgrade-path.svg", svg)


# ---------------------------------------------------------------- scanner output
def scanner():
    W, H = 1160, 540
    rows = [
        ("BREAK", "net8", "4.80", "Nop.Plugin.Misc.Legacy.csproj:3"),
        ("BREAK", "permission-provider", "4.80", "Controllers/LegacyController.cs:15"),
        ("BREAK", "sitemap-menu", "4.80", "LegacyPlugin.cs:8, :10"),
        ("BREAK", "product-reviews-moved", "4.90", "Services/LegacyService.cs:22"),
        ("BREAK", "warehouses-moved", "4.90", "Services/LegacyService.cs:23"),
        ("BREAK", "shipping-methods-moved", "4.90", "Services/LegacyService.cs:24"),
        ("BREAK", "payment-custom-values", "4.90", "Services/LegacyService.cs:25"),
        ("CHECK", "admin-menu-plugin", "4.80", "LegacyPlugin.cs:6, :8"),
        ("TIDY", "access-denied-guard", "4.80", "Controllers/LegacyController.cs:16"),
        ("TIDY", "csproj-relative", "4.80", "Nop.Plugin.Misc.Legacy.csproj:4, :8, :9"),
    ]
    col = {"BREAK": "#F87171", "CHECK": "#FBBF24", "TIDY": "#94A3B8"}
    out = []
    y0 = 92
    out.append(f'<text x="36" y="{y0}" font-family="{MONO}" font-size="15" fill="#E2E8F0"><tspan fill="{CYAN}">$</tspan> python skills/nop-upgrade/scripts/scan_upgrade.py tests/fixtures --to 4.90</text>')
    out.append(f'<text x="36" y="{y0 + 40}" font-family="{MONO}" font-size="16" font-weight="700" fill="#FFFFFF"># nopCommerce upgrade scan: 4.70 → 4.90</text>')
    out.append(f'<text x="36" y="{y0 + 72}" font-family="{MONO}" font-size="15" fill="#CBD5E1"><tspan fill="#F87171" font-weight="700">8 BREAK</tspan> · <tspan fill="#FBBF24" font-weight="700">2 CHECK</tspan> · <tspan fill="#94A3B8" font-weight="700">4 TIDY</tspan>   <tspan fill="#64748B">+ plugin.json SupportedVersions needs "4.90"</tspan></text>')
    for hx, ht in ((36, "SEVERITY"), (136, "RULE"), (384, "CHANGED IN"), (492, "WHERE")):
        out.append(f'<text x="{hx}" y="{y0 + 108}" font-family="{MONO}" font-size="13" fill="#64748B">{ht}</text>')
    for i, (sev, rule, v, where) in enumerate(rows):
        y = y0 + 136 + i * 30
        out.append(f'<text x="36" y="{y}" font-family="{MONO}" font-size="15" fill="{col[sev]}" font-weight="700">[{sev}]</text>')
        out.append(f'<text x="136" y="{y}" font-family="{MONO}" font-size="15" fill="#E2E8F0">{esc(rule)}</text>')
        out.append(f'<text x="384" y="{y}" font-family="{MONO}" font-size="15" fill="#94A3B8">{v}</text>')
        out.append(f'<text x="492" y="{y}" font-family="{MONO}" font-size="15" fill="#7DD3FC">{esc(where)}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">Upgrade scanner report for a 4.70 sample plugin: 8 breaking, 2 check, 4 tidy findings with file and line</title>
<rect width="{W}" height="{H}" rx="18" fill="#0A0F1A"/>
<rect x="0" y="0" width="{W}" height="46" rx="18" fill="#111827"/><rect x="0" y="28" width="{W}" height="18" fill="#111827"/>
<circle cx="28" cy="23" r="7" fill="#F87171"/><circle cx="50" cy="23" r="7" fill="#FBBF24"/><circle cx="72" cy="23" r="7" fill="#4ADE80"/>
<text x="{W / 2}" y="28" text-anchor="middle" font-family="{SANS}" font-size="13" fill="#64748B">nop-upgrade scanner · summary of the Markdown report</text>
{"".join(out)}
</svg>'''
    save("scanner-report.svg", svg)


# ---------------------------------------------------------------- new plugin flow
def new_plugin_flow():
    W, H = 1200, 270
    steps = [("Describe it", "one line in plain English"),
             ("Inputs settled", "version, group, name, settings"),
             ("Files generated", "csproj, plugin.json, plugin class, admin page, views, locales"),
             ("Built", "dotnet build from the solution, errors fixed"),
             ("Install", "Local plugins → Reload list → Install")]
    out = []
    xs = [120 + i * 240 for i in range(5)]
    out.append(f'<line x1="{xs[0]}" y1="90" x2="{xs[-1]}" y2="90" stroke="#BFDBFE" stroke-width="4"/>')
    for i, (x, (t, d)) in enumerate(zip(xs, steps)):
        last = i == 4
        out.append(f'<circle cx="{x}" cy="90" r="34" fill="{BLUE if last else "#FFFFFF"}" stroke="{BLUE}" stroke-width="3"/>')
        out.append(f'<text x="{x}" y="99" text-anchor="middle" font-family="{SANS}" font-size="26" font-weight="800" fill="{"#fff" if last else BLUE}">{i + 1}</text>')
        out.append(f'<text x="{x}" y="160" text-anchor="middle" font-family="{SANS}" font-size="18" font-weight="700" fill="{INK}">{esc(t)}</text>')
        for j, l in enumerate(wrap(d, 24)):
            out.append(f'<text x="{x}" y="{188 + j * 21}" text-anchor="middle" font-family="{SANS}" font-size="15" fill="{MUTED}">{esc(l)}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">What /nop-new-plugin does, in five steps</title>
<rect width="{W}" height="{H}" rx="20" fill="#F8FAFC"/>
{"".join(out)}
</svg>'''
    save("new-plugin-flow.svg", svg)


banner(); how_it_works(); upgrade_path(); scanner(); new_plugin_flow()
print(sorted(os.listdir(OUT)))
