#!/usr/bin/env python3
import json, re, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
GUIDES_DIR = os.path.join(SITE, "guides")
os.makedirs(GUIDES_DIR, exist_ok=True)
DATA = json.load(open(os.path.join(HERE,"data","guides.json")))

# ---------- helpers ----------
def slugify(s):
    s = s.split("—")[0].split("–")[0].strip()        # core name before the dash
    s = s.lower().replace("&", " and ").replace("/", " ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-+", "-", s)
    return s

def esc(s): return html.escape(s, quote=True)

def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(https?://[^\s<]+)", r'<a href="\1" rel="nofollow noopener" target="_blank">\1</a>', s)
    return s

def md_to_html(md):
    out, para, list_type = [], [], None
    def flush():
        if para: out.append("<p>" + inline(" ".join(para)) + "</p>"); para.clear()
    def closel():
        nonlocal list_type
        if list_type: out.append(f"</{list_type}>"); list_type = None
    for raw in md.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flush(); closel()
        elif line.startswith("### "):
            flush(); closel(); out.append("<h3>" + inline(line[4:]) + "</h3>")
        elif line.startswith("## "):
            flush(); closel(); out.append("<h2>" + inline(line[3:]) + "</h2>")
        elif re.match(r"^[-*] ", line):
            flush()
            if list_type != "ul": closel(); out.append("<ul>"); list_type = "ul"
            out.append("<li>" + inline(line[2:]) + "</li>")
        elif re.match(r"^\d+\. ", line):
            flush()
            if list_type != "ol": closel(); out.append("<ol>"); list_type = "ol"
            out.append("<li>" + inline(re.sub(r"^\d+\. ", "", line)) + "</li>")
        else:
            closel(); para.append(line)
    flush(); closel()
    return "\n".join(out)

def meta_desc(s):
    s = s.strip().replace("\n", " ")
    return (s[:152].rsplit(" ", 1)[0] + "…") if len(s) > 155 else s

# ---------- enrich rows ----------
for g in DATA:
    g["slug"] = slugify(g["title"])
    g["is_form"] = g["sort_order"] >= 200
    g["url"] = f"/guides/{g['slug']}.html"
    g["date"] = (g.get("created_at") or "2026-06-07")[:10]

# unique slug guard
seen = {}
for g in DATA:
    if g["slug"] in seen:
        g["slug"] = g["slug"] + "-" + str(g["id"]); g["url"] = f"/guides/{g['slug']}.html"
    seen[g["slug"]] = True

process = [g for g in DATA if not g["is_form"]]
forms = [g for g in DATA if g["is_form"]]

CSS = """
    * { margin:0; padding:0; box-sizing:border-box; }
    :root { --navy:#0a0f1a; --card:#141b2d; --gold:#d9a621; --tan:#c8bda5; --white:#fff; --green:#34a853; --gray:#8a93a6; --line:rgba(255,255,255,0.08); }
    body { font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display','Segoe UI',sans-serif; background:var(--navy); color:var(--white); line-height:1.75; -webkit-font-smoothing:antialiased; }
    a { color:var(--gold); text-decoration:none; }
    .wrap { max-width:760px; margin:0 auto; padding:0 22px; }
    nav { display:flex; align-items:center; justify-content:space-between; padding:18px 22px; max-width:1080px; margin:0 auto; }
    .nav-brand { display:flex; align-items:center; gap:10px; }
    .nav-brand img { width:34px; height:34px; border-radius:9px; }
    .nav-brand span { font-size:14px; font-weight:900; letter-spacing:2px; white-space:nowrap; }
    .nav-links a { font-size:13px; color:var(--tan); margin-left:16px; font-weight:600; white-space:nowrap; }
    .crumb { font-size:12.5px; color:var(--gray); padding:26px 0 4px; }
    .crumb a { color:var(--tan); }
    .eyebrow { display:inline-flex; align-items:center; gap:10px; font-size:11px; font-weight:800; letter-spacing:2.5px; text-transform:uppercase; color:var(--gold); margin:14px 0 8px; }
    .eyebrow::before { content:""; width:24px; height:2px; background:var(--gold); }
    h1 { font-size:33px; line-height:1.2; font-weight:900; letter-spacing:-0.5px; margin-bottom:14px; }
    .lede { font-size:18px; color:var(--tan); margin-bottom:18px; }
    .meta { font-size:12.5px; color:var(--gray); border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:12px 0; margin-bottom:26px; }
    .meta strong { color:var(--tan); font-weight:700; }
    article h2 { font-size:22px; font-weight:800; color:var(--white); margin:30px 0 10px; letter-spacing:-0.3px; }
    article h3 { font-size:17px; font-weight:800; color:var(--gold); margin:22px 0 8px; }
    article p { color:var(--tan); margin-bottom:14px; font-size:16px; }
    article strong { color:var(--white); }
    article ul, article ol { margin:0 0 16px 4px; padding-left:22px; }
    article li { color:var(--tan); margin-bottom:7px; font-size:16px; }
    article a { word-break:break-word; }
    .cta { background:var(--card); border:1px solid var(--line); border-left:3px solid var(--gold); border-radius:14px; padding:22px 24px; margin:34px 0; }
    .cta h3 { font-size:18px; font-weight:800; color:var(--white); margin-bottom:6px; }
    .cta p { color:var(--tan); font-size:14.5px; margin-bottom:14px; }
    .btns { display:flex; gap:10px; flex-wrap:wrap; }
    .btn { display:inline-block; background:var(--gold); color:#1a1205; font-weight:800; font-size:14px; padding:11px 18px; border-radius:11px; }
    .btn.ghost { background:transparent; color:var(--tan); border:1px solid var(--line); }
    .cta-pro { margin:14px 0 16px; padding:15px 17px; background:rgba(217,166,33,0.06); border:1px solid rgba(217,166,33,0.22); border-radius:11px; }
    .pro-pill { display:inline-block; font-size:10px; font-weight:900; letter-spacing:1px; text-transform:uppercase; color:#1a1205; background:var(--gold); padding:2px 9px; border-radius:6px; margin-bottom:9px; }
    .cta-pro p { color:var(--tan); font-size:14px; margin:0; }
    .cta-pro strong { color:var(--white); }
    .related { margin:34px 0; }
    .related h2 { font-size:18px; font-weight:800; margin-bottom:12px; }
    .related a { display:block; background:var(--card); border:1px solid var(--line); border-radius:11px; padding:13px 16px; margin-bottom:9px; color:var(--white); font-weight:700; font-size:15px; }
    .related a span { display:block; color:var(--gray); font-weight:400; font-size:12.5px; margin-top:2px; }
    .disclaimer { font-size:12px; color:var(--gray); line-height:1.7; border-top:1px solid var(--line); padding:22px 0; margin-top:10px; }
    footer { text-align:center; padding:40px 22px; border-top:1px solid var(--line); margin-top:10px; }
    footer p { font-size:12px; color:var(--gray); }
    .footer-links a { color:var(--tan); font-size:12px; margin:0 10px; }
    /* hub */
    .hub-sec { margin:34px 0; }
    .hub-sec > .eyebrow { margin-bottom:14px; }
    .hub-grid { display:grid; gap:11px; }
    .hub-card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px 18px; }
    .hub-card a { color:var(--white); font-weight:800; font-size:16px; }
    .hub-card p { color:var(--tan); font-size:13.5px; margin-top:5px; }
    @media (max-width:560px){ h1{font-size:27px;} }
    .nv-burger { display:none; font-size:25px; color:var(--tan); cursor:pointer; line-height:1; padding:2px 6px; user-select:none; }
    .nv-cb { display:none; }
    @media (max-width:960px){
      nav { flex-wrap:wrap; }
      .nv-burger { display:block; }
      .nav-links { display:none; flex-basis:100%; flex-direction:column; align-items:stretch; gap:0; margin-top:10px; }
      .nv-cb:checked ~ .nav-links { display:flex; }
      .nav-links a { margin-left:0; padding:12px 2px; border-top:1px solid var(--line); font-size:15px; white-space:normal; }
    }
"""

NAV = """<nav>
    <a href="/index.html" class="nav-brand"><img src="/logo.png" alt="VA Ready logo" width="34" height="34"><span>VA READY <span style="color:var(--gray);font-weight:400;">/</span> VET READY</span></a>
    <input type="checkbox" id="nv" class="nv-cb">
    <label for="nv" class="nv-burger" aria-label="Open menu">&#9776;</label>
    <div class="nav-links"><a href="/va-disability-calculator.html">Calculator</a><a href="/conditions.html">Conditions</a><a href="/exposures.html">Exposures</a><a href="/va-disability-pay-rates.html">Pay Rates</a><a href="/states.html">State Benefits</a><a href="/guides.html">Guides</a><a href="/founders.html">Our Story</a><a href="/index.html#download">Get the App</a></div>
</nav>"""

FOOTER = """<footer>
    <p>&copy; 2026 JDL Software LLC. VA Ready (iOS) &amp; Vet Ready (Android) are not affiliated with the U.S. Department of Veterans Affairs.</p>
    <div class="footer-links"><a href="/index.html">Home</a><a href="/conditions.html">Conditions</a><a href="/exposures.html">Exposures</a><a href="/va-disability-pay-rates.html">Pay Rates</a><a href="/states.html">State Benefits</a><a href="/guides.html">Guides</a><a href="/va-disability-calculator.html">Calculator</a><a href="/founders.html">Our Story</a><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a></div>
</footer>
<script defer src="/_vercel/insights/script.js"></script>
<script defer src="/track.js"></script>"""

APP_CTA = """<div class="cta">
    <h3>This guide is free in the VA Ready app</h3>
    <p>Free, no account: all 50+ filing guides, a personalized timeline from your separation date, an evidence checklist for every condition, and the combined-rating calculator with real VA math.</p>
    <div class="cta-pro">
        <span class="pro-pill">With Pro</span>
        <p>You walk away with the documents that move claims: a <strong>VSO-ready Claim Summary PDF</strong> with a peer-reviewed evidence appendix, an <strong>Exposure Profile PDF</strong> mapping every presumptive your service earned, the <strong>actual 38 CFR rating criteria</strong> for your exact conditions, and <strong>all 50 states&rsquo;</strong> benefits.</p>
    </div>
    <div class="btns"><a href="https://apps.apple.com/app/id6761733758" class="btn">Get VA Ready for iOS</a><a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US" class="btn ghost">Get Vet Ready for Android</a></div>
</div>"""

DISCLAIMER = """<div class="disclaimer">This guide is for general informational purposes only and is not legal or medical advice. VA Ready is not affiliated with, endorsed by, or connected to the U.S. Department of Veterans Affairs. Regulations and procedures change; always verify current requirements at VA.gov and consult a VA-accredited representative for help with your claim.</div>"""

def guide_page(g, related):
    body = md_to_html(g["content"])
    cat = "VA Forms" if g["is_form"] else "Filing Guides"
    cfr = f'<strong>{esc(g["cfr_reference"])}</strong> &middot; ' if g.get("cfr_reference") else ""
    rel_html = ""
    if related:
        items = "".join(
            f'<a href="{r["url"]}">{esc(r["title"].split("—")[0].strip())}<span>{esc(meta_desc(r["summary"]))}</span></a>'
            for r in related)
        rel_html = f'<div class="related"><h2>Related guides</h2>{items}</div>'
    desc = meta_desc(g["summary"])
    title_tag = f'{esc(g["title"])} | VA Ready'
    canon = f'https://vareadyapp.com{g["url"]}'
    breadcrumb = json.dumps({
        "@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
            {"@type":"ListItem","position":2,"name":"VA Claim Guides","item":"https://vareadyapp.com/guides.html"},
            {"@type":"ListItem","position":3,"name":g["title"],"item":canon}]})
    article_ld = json.dumps({
        "@context":"https://schema.org","@type":"Article","headline":g["title"][:110],
        "description":g["summary"],"datePublished":g["date"],"dateModified":g["date"],
        "author":{"@type":"Organization","name":"JDL Software LLC"},
        "publisher":{"@type":"Organization","name":"VA Ready"},
        "mainEntityOfPage":canon, "inLanguage":"en-US"})
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_tag}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="{esc(g['title'])}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{esc(g['title'])}">
<meta name="twitter:description" content="{esc(desc)}">
<link rel="icon" type="image/png" href="/logo.png">
<script type="application/ld+json">{breadcrumb}</script>
<script type="application/ld+json">{article_ld}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/guides.html">VA Claim Guides</a> / {esc(cat)}</div>
    <div class="eyebrow">{esc(cat)}</div>
    <h1>{esc(g['title'])}</h1>
    <p class="lede">{esc(g['summary'])}</p>
    <div class="meta">{cfr}Free guide from VA Ready</div>
    <article>
{body}
    </article>
    {APP_CTA}
    {rel_html}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""

def hub_page():
    def cards(items):
        return "".join(
            f'<div class="hub-card"><a href="{g["url"]}">{esc(g["title"].split("—")[0].strip())}</a><p>{esc(meta_desc(g["summary"]))}</p></div>'
            for g in items)
    desc = "Free VA claim guides: how to file, C&P exam prep, nexus letters, the PACT Act, TDIU, appeals, and a plain-language explainer for every VA form."
    breadcrumb = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"VA Claim Guides","item":"https://vareadyapp.com/guides.html"}]})
    itemlist = json.dumps({"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"url":f'https://vareadyapp.com{g["url"]}',"name":g["title"]} for i,g in enumerate(DATA)]})
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VA Claim Guides — Free Filing Help &amp; VA Form Explainers | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="https://vareadyapp.com/guides.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="VA Claim Guides — Free Filing Help &amp; VA Form Explainers">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="https://vareadyapp.com/guides.html">
<meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="/logo.png">
<script type="application/ld+json">{breadcrumb}</script>
<script type="application/ld+json">{itemlist}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / VA Claim Guides</div>
    <div class="eyebrow">Free Guides</div>
    <h1>VA Claim Guides</h1>
    <p class="lede">Plain-language help for filing your VA disability claim — and a straight explainer for every VA form. All free, all sourced from the regulations (38 CFR) and VA.gov.</p>
    <div class="hub-sec">
        <div class="eyebrow">Filing your claim, step by step</div>
        <div class="hub-grid">{cards(process)}</div>
    </div>
    <div class="hub-sec">
        <div class="eyebrow">Every VA form, explained</div>
        <div class="hub-grid">{cards(forms)}</div>
    </div>
    {APP_CTA}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""

# ---------- write pages ----------
n = 0
for g in DATA:
    pool = process if not g["is_form"] else forms
    related = [r for r in pool if r["id"] != g["id"]]
    # nearest by sort_order
    related.sort(key=lambda r: abs(r["sort_order"] - g["sort_order"]))
    open(os.path.join(GUIDES_DIR, g["slug"] + ".html"), "w").write(guide_page(g, related[:4]))
    n += 1
open(os.path.join(SITE, "guides.html"), "w").write(hub_page())

# ---------- sitemap ----------
core = [("https://vareadyapp.com/","1.0"),
        ("https://vareadyapp.com/va-disability-calculator.html","0.9"),
        ("https://vareadyapp.com/guides.html","0.8"),
        ("https://vareadyapp.com/the-va-ready-difference.html","0.8"),
        ("https://vareadyapp.com/privacy.html","0.5"),
        ("https://vareadyapp.com/terms.html","0.5")]
urls = "".join(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-06-07</lastmod>\n    <priority>{p}</priority>\n  </url>\n' for u,p in core)
for g in DATA:
    urls += f'  <url>\n    <loc>https://vareadyapp.com{g["url"]}</loc>\n    <lastmod>2026-06-07</lastmod>\n    <priority>0.7</priority>\n  </url>\n'
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n'
open(os.path.join(SITE, "sitemap.xml"), "w").write(sitemap)

print(f"generated {n} guide pages + hub")
print("process:", len(process), "| forms:", len(forms))
print("sample slugs:", [g["slug"] for g in DATA[:5]])
print("sitemap urls:", len(core) + len(DATA))
