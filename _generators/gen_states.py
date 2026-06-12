#!/usr/bin/env python3
import json, re, os, html
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
SDIR = os.path.join(SITE, "states")
os.makedirs(SDIR, exist_ok=True)
ROWS = json.load(open(os.path.join(HERE,"data","benefits.json")))
def esc(s): return html.escape(s or "", quote=True)

# top-20 states by veteran population (search-demand order)
ORDER = ["CA","TX","FL","VA","NC","GA","PA","NY","OH","WA","AZ","MI","TN","IL","CO","MO","SC","MD","IN","AL"]
NAMES = {r["state_code"]: r["state_name"] for r in ROWS}
BY = defaultdict(list)
for r in ROWS: BY[r["state_code"]].append(r)

CAT_ORDER = ["Property Tax","Income Tax","Education","Employment","Vehicle","Recreation","General"]
def cat_rank(c): return CAT_ORDER.index(c) if c in CAT_ORDER else 99

gtext = open(os.path.join(HERE,"gen_guides.py")).read()
m = re.search(r'CSS = """(.*?)"""', gtext, re.S)
CSS = (m.group(1) if m else "") + """
    .meta { color:var(--gray); font-size:14px; margin:4px 0 14px; }
    .meta strong { color:var(--white); }
    .catblock { margin:22px 0 6px; }
    .catblock h2 { margin-bottom:6px; }
    ol.blist { list-style:none; padding:0; margin:0; }
    li.ben { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:15px 17px; margin:0 0 13px; }
    .ben-top { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin-bottom:6px; }
    .ben-name { color:var(--white); font-weight:800; font-size:17px; }
    .badge { font-size:11px; text-transform:uppercase; letter-spacing:.6px; padding:3px 9px; border-radius:999px; border:1px solid var(--line); color:var(--tan); }
    .badge.req { background:rgba(201,162,77,.16); color:var(--gold); border-color:transparent; }
    .ben-val { color:var(--gold); font-weight:700; font-size:14px; margin:2px 0 6px; }
    .ben p { color:var(--tan); font-size:15px; margin:5px 0; }
    .ben .how { color:var(--tan); font-size:14px; }
    .ben .how strong { color:var(--white); }
    .ben-foot { display:flex; flex-wrap:wrap; gap:6px 14px; align-items:center; margin-top:8px; font-size:13px; color:var(--gray); }
    .ben-foot a { color:var(--gold); font-weight:700; text-decoration:none; }
    .ben-foot a:hover { text-decoration:underline; }
    .trustline { font-size:13.5px; color:var(--tan); background:var(--card); border:1px solid var(--line); border-left:3px solid var(--gold); border-radius:10px; padding:9px 13px; margin:14px 0 4px; }
    .trustline a { color:var(--gold); font-weight:700; text-decoration:none; }
    .pillrow { display:flex; flex-wrap:wrap; gap:8px; margin:6px 0 16px; }
    .pillrow span { font-size:13px; background:var(--card); border:1px solid var(--line); color:var(--tan); padding:6px 12px; border-radius:999px; }
"""

NAV = """<nav>
    <a href="/index.html" class="nav-brand"><img src="/logo.png" alt="VA Ready logo" width="34" height="34"><span>VA READY <span style="color:var(--gray);font-weight:400;">/</span> VET READY</span></a>
    <input type="checkbox" id="nv" class="nv-cb">
    <label for="nv" class="nv-burger" aria-label="Open menu">&#9776;</label>
    <div class="nav-links"><a href="/va-disability-calculator.html">Calculator</a><a href="/conditions.html">Conditions</a><a href="/exposures.html">Exposures</a><a href="/va-disability-pay-rates.html">Pay Rates</a><a href="/states.html">State Benefits</a><a href="/federal-benefits.html">Federal Benefits</a><a href="/guides.html">Guides</a><a href="/find-a-vso.html">Find a VSO</a><a href="/index.html#download">Get the App</a></div>
</nav>"""
FOOTER = """<footer>
    <p>&copy; 2026 JDL Software LLC. VA Ready (iOS) &amp; Vet Ready (Android) are not affiliated with the U.S. Department of Veterans Affairs.</p>
    <div class="footer-links"><a href="/index.html">Home</a><a href="/conditions.html">Conditions</a><a href="/exposures.html">Exposures</a><a href="/va-disability-pay-rates.html">Pay Rates</a><a href="/states.html">State Benefits</a><a href="/federal-benefits.html">Federal Benefits</a><a href="/guides.html">Guides</a><a href="/va-disability-calculator.html">Calculator</a><a href="/find-a-vso.html">Find a VSO</a><a href="/founders.html">Our Story</a><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a></div>
</footer>
<script defer src="/_vercel/insights/script.js"></script>
<script defer src="/track.js"></script>"""
APP_CTA = """<div class="cta">
    <h3>See every benefit you've earned &mdash; free</h3>
    <p>VA Ready checks your rating against state and federal benefits for all 50 states, builds your combined rating with real VA math, and walks you through filing. No account required.</p>
    <div class="cta-pro"><span class="pro-pill">With Pro</span><p>Get your full <strong>Benefits &amp; Exposure Profile PDF</strong>, every-state lookups, and the complete criteria for all 755 conditions.</p></div>
    <div class="btns"><a href="https://apps.apple.com/app/id6761733758" class="btn">Get VA Ready for iOS</a><a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US" class="btn ghost">Get Vet Ready for Android</a></div>
</div>"""

def slug(name): return re.sub(r"[^a-z0-9]+","-", name.lower()).strip("-")

def money(v):
    try:
        n = float(v)
        if n <= 0: return None
        return "${:,.0f}".format(n)
    except: return None

def badges(r):
    out = []
    if r.get("requires_pt"): out.append('<span class="badge req">100% P&amp;T</span>')
    pct = r.get("min_rating_pct")
    if pct and int(pct) > 0 and not r.get("requires_pt"): out.append(f'<span class="badge req">{int(pct)}%+ rating</span>')
    if r.get("requires_combat"): out.append('<span class="badge req">Combat service</span>')
    if not out: out.append('<span class="badge">All veterans</span>')
    return "".join(out)

def benefit_li(r):
    val = money(r.get("estimated_annual_value")); vd = r.get("value_description")
    if val and vd: vline = f'<div class="ben-val">Est. {val}/yr &middot; {esc(vd)}</div>'
    elif val: vline = f'<div class="ben-val">Est. value: {val}/yr</div>'
    elif vd: vline = f'<div class="ben-val">{esc(vd)}</div>'
    else: vline = ""
    how = f'<p class="how"><strong>How to claim:</strong> {esc(r["how_to_claim"])}</p>' if r.get("how_to_claim") else ""
    foot = []
    if r.get("agency"): foot.append(esc(r["agency"]))
    if r.get("form_name"): foot.append("Form " + esc(r["form_name"]))
    link = r.get("source_url") or r.get("website_url")
    foot_html = " &middot; ".join(foot)
    if link: foot_html += (' &middot; ' if foot_html else '') + f'<a href="{esc(link)}" target="_blank" rel="noopener">Official details &#8599;</a>'
    return (f'<li class="ben"><div class="ben-top"><span class="ben-name">{esc(r["benefit_name"])}</span>{badges(r)}</div>'
            f'{vline}<p>{esc(r.get("description"))}</p>{how}'
            + (f'<div class="ben-foot">{foot_html}</div>' if foot_html else '') + '</li>')

def state_page(sc):
    rows = sorted(BY[sc], key=lambda r:(cat_rank(r["benefit_category"]), r["benefit_name"]))
    sn = NAMES[sc]; sl = slug(sn)
    cats = []
    for c in sorted(set(r["benefit_category"] for r in rows), key=cat_rank): cats.append(c)
    lastv = max((r.get("last_verified") or "") for r in rows) or ""
    url = f"/states/{sl}.html"; canon = f"https://vareadyapp.com{url}"
    catlist = ", ".join(cats).lower()
    desc = f"{sn} veterans benefits: property tax exemptions, education, vehicle, and recreation perks for disabled veterans. What you qualify for and how to claim it. Free VA tools."
    desc = desc[:158]
    # category blocks
    blocks = ""
    for c in cats:
        crows = [r for r in rows if r["benefit_category"] == c]
        items = "".join(benefit_li(r) for r in crows)
        blocks += f'<div class="catblock"><h2>{esc(c)}</h2><ol class="blist">{items}</ol></div>'
    # FAQ
    top_names = [r["benefit_name"] for r in rows][:3]
    faqs = [(f"What benefits do {sn} veterans get?",
             f"{sn} offers veteran benefits across {catlist}. Highlights include {', '.join(top_names)}. Eligibility varies — some benefits require a VA disability rating, 100% P&T status, or combat service.")]
    pt = next((r for r in rows if r["benefit_category"]=="Property Tax"), None)
    if pt: faqs.append((f"What property tax exemption do disabled veterans get in {sn}?", re.sub("<.*?>","",pt.get("description") or "")[:300]))
    it = next((r for r in rows if r["benefit_category"]=="Income Tax"), None)
    if it: faqs.append((f"Does {sn} tax military retirement or VA disability pay?", re.sub("<.*?>","",it.get("description") or "")[:300]))
    faqs.append((f"Do I need a VA rating to claim {sn} benefits?",
                 "Many state benefits are tied to your VA disability rating — the higher your rating, the more you may qualify for. Use the free VA Ready calculator to confirm your combined rating, then check which state benefits you've earned."))
    faq_visible = "".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q,a in faqs)
    faq_ld = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]})
    bc_ld = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"Veterans Benefits by State","item":"https://vareadyapp.com/states.html"},
        {"@type":"ListItem","position":3,"name":f"{sn} Veterans Benefits","item":canon}]})
    art_ld = json.dumps({"@context":"https://schema.org","@type":"Article",
        "headline":f"{sn} Veterans Benefits","description":desc,"datePublished":"2026-06-08",
        "dateModified": lastv or "2026-06-08",
        "author":{"@type":"Organization","name":"JDL Software LLC"},"publisher":{"@type":"Organization","name":"VA Ready"},
        "mainEntityOfPage":canon,"inLanguage":"en-US"})
    lastv_str = f"Last verified {lastv}" if lastv else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(sn)} Veterans Benefits (2026) &mdash; Disabled Veteran Perks | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="{esc(sn)} Veterans Benefits (2026)">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="/logo.png">
<script type="application/ld+json">{bc_ld}</script>
<script type="application/ld+json">{art_ld}</script>
<script type="application/ld+json">{faq_ld}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/states.html">State Benefits</a> / {esc(sn)}</div>
    <div class="eyebrow">Veterans Benefits by State</div>
    <h1>{esc(sn)} Veterans Benefits</h1>
    <p class="lede">Beyond your federal VA disability compensation, {esc(sn)} offers its own benefits for veterans &mdash; {catlist}. Here's what {esc(sn)} veterans can claim, who qualifies, and how to apply.</p>
    <div class="meta"><strong>{len(rows)} state benefits</strong> &middot; {esc(', '.join(cats))}{(' &middot; ' + lastv_str) if lastv_str else ''}</div>
    <p class="trustline">Not sure what your rating qualifies you for? <a href="/va-disability-calculator.html">Check your combined rating &rarr;</a></p>
    {blocks}
    <p style="margin:22px 0;"><a href="/va-disability-calculator.html" class="btn">Estimate your combined rating &rarr;</a> &nbsp; <a href="/conditions.html" class="btn ghost">Browse conditions</a></p>
    {APP_CTA}
    <h2 style="font-size:20px;margin-top:30px;">Common questions</h2>
    {faq_visible}
    <div class="disclaimer">State benefit rules, amounts, and eligibility change and vary by county or municipality. Estimated values are approximate. Always confirm current details with the state agency or the official source linked above before relying on a benefit. VA Ready is not affiliated with the U.S. Department of Veterans Affairs or any state agency, and this page is not legal, tax, or financial advice.</div>
</div>
{FOOTER}
</body>
</html>"""

written = 0
for sc in ORDER:
    if sc in BY:
        open(os.path.join(SDIR, slug(NAMES[sc]) + ".html"), "w").write(state_page(sc))
        written += 1

# hub
def hub():
    cards = ""
    for sc in ORDER:
        if sc not in BY: continue
        sn = NAMES[sc]; rows = BY[sc]
        cats = sorted(set(r["benefit_category"] for r in rows), key=cat_rank)
        cards += (f'<div class="hub-card"><a href="/states/{slug(sn)}.html">{esc(sn)} Veterans Benefits</a>'
                  f'<p>{len(rows)} benefits &middot; {esc(", ".join(cats[:3]))}{"&hellip;" if len(cats)>3 else ""}</p></div>')
    desc = "Veterans benefits by state: property tax exemptions, education, vehicle, and recreation perks for the 20 states with the most veterans. What disabled veterans qualify for and how to claim it."
    bc = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"Veterans Benefits by State","item":"https://vareadyapp.com/states.html"}]})
    items = json.dumps({"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"url":f"https://vareadyapp.com/states/{slug(NAMES[sc])}.html","name":f"{NAMES[sc]} Veterans Benefits"}
        for i,sc in enumerate(ORDER) if sc in BY]})
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Veterans Benefits by State (2026) &mdash; Property Tax, Education &amp; More | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="https://vareadyapp.com/states.html">
<meta property="og:type" content="website"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="Veterans Benefits by State"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="https://vareadyapp.com/states.html"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" href="/logo.png">
<script type="application/ld+json">{bc}</script>
<script type="application/ld+json">{items}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / Veterans Benefits by State</div>
    <div class="eyebrow">By State</div>
    <h1>Veterans Benefits by State</h1>
    <p class="lede">Your VA rating can unlock more than federal compensation. Most states offer their own benefits &mdash; property-tax exemptions, free or reduced tuition, vehicle and license breaks, and hunting/fishing perks. Here are the states with the most veterans; the VA Ready app covers all 50.</p>
    <div class="hub-sec"><div class="hub-grid">{cards}</div></div>
    <p class="trustline">More from VA Ready: <a href="/conditions.html">VA ratings by condition</a> &middot; <a href="/guides.html">VA claim guides</a> &middot; <a href="/va-disability-calculator.html">Combined-rating calculator</a></p>
    {APP_CTA}
    <div class="disclaimer">State benefit rules and amounts change and vary locally. Always confirm with the state agency before relying on a benefit. VA Ready is not affiliated with the U.S. Department of Veterans Affairs.</div>
</div>
{FOOTER}
</body>
</html>"""
open(os.path.join(SITE, "states.html"), "w").write(hub())

# sitemap merge
sp = os.path.join(SITE, "sitemap.xml")
xml = open(sp).read(); new = []
urls = [("https://vareadyapp.com/states.html","0.8")] + [(f"https://vareadyapp.com/states/{slug(NAMES[sc])}.html","0.7") for sc in ORDER if sc in BY]
for u,p in urls:
    if u not in xml:
        new.append(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-06-08</lastmod>\n    <priority>{p}</priority>\n  </url>')
if new:
    xml = xml.replace("</urlset>", "\n".join(new) + "\n</urlset>"); open(sp,"w").write(xml)

# validate all JSON-LD
import glob
bad = 0
for f in [os.path.join(SITE,"states.html")] + glob.glob(os.path.join(SDIR,"*.html")):
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', open(f).read(), re.S):
        try: json.loads(blk)
        except Exception as e: bad += 1; print("BAD JSON-LD", f, e)
print(f"wrote {written} state pages + hub; sitemap +{len(new)} urls; JSON-LD bad={bad}")
