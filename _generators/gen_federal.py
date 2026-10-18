#!/usr/bin/env python3
"""Federal benefits page for disabled veterans, from federal_benefits (32 rows)."""
import json, re, os, html
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
def esc(s): return html.escape(str(s) if s is not None else "", quote=True)
def money(v):
    try:
        n=float(v)
        if n<=0: return None
        return "${:,.0f}".format(n)
    except: return None

ROWS = json.load(open(os.path.join(HERE,"data","federal_benefits.json")))
# Every row in federal_benefits is listed, so the count in the copy matches the app (32).
EXCLUDE_IDS = set()
ROWS = [r for r in ROWS if r.get("id") not in EXCLUDE_IDS]
CAT = [("financial","Financial and compensation"),("healthcare","Health care"),("housing","Housing"),
       ("education","Education"),("employment","Employment"),("life_insurance","Life insurance"),("other","Other")]
CATLABEL = dict(CAT)
def catrank(c): return [k for k,_ in CAT].index(c) if c in dict(CAT) else 99

CSS = re.search(r'CSS = """(.*?)"""', open(os.path.join(HERE,"gen_guides.py")).read(), re.S).group(1) + """
    .catblock { margin:26px 0 6px; } .catblock h2 { font-size:21px; font-weight:800; margin-bottom:6px; }
    ol.blist { list-style:none; padding:0; margin:0; }
    li.ben { border-top:1px solid var(--line); padding:16px 0; margin:0; }
    .ben-top { display:flex; flex-wrap:wrap; align-items:baseline; gap:2px 12px; margin-bottom:4px; }
    .ben-name { color:var(--white); font-weight:700; font-size:17px; }
    .badge { font-size:13px; color:var(--gray); }
    .ben-val { color:var(--white); font-weight:600; font-size:14.5px; margin:2px 0 6px; font-variant-numeric:tabular-nums; }
    .ben p { color:var(--tan); font-size:15px; margin:5px 0; max-width:68ch; }
    .ben .how { color:var(--tan); font-size:14.5px; }
    .ben-foot { display:flex; flex-wrap:wrap; gap:0 14px; align-items:center; margin-top:6px; font-size:13px; color:var(--gray); }
    .ben-foot a { display:inline-block; padding:8px 0; }
    .trustline { font-size:14.5px; color:var(--tan); margin:14px 0; max-width:68ch; }
    .page-cta { margin:26px 0; }
"""
NAV = re.search(r'NAV = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)
FOOTER = re.search(r'FOOTER = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)
APP_CTA = """<div class="cta cta-line"><p>Federal benefits at every rating are free in <a href="https://apps.apple.com/app/id6761733758">VA Ready for iOS</a>, <a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US">Vet Ready for Android</a> and <a href="https://apps.microsoft.com/detail/9p8xfcqvfjhf">VA Ready for Windows</a>, along with the combined-rating calculator; Pro adds every state's benefits and Claim Intel.</p></div>"""

def badges(r):
    out=[]
    if r.get("requires_pt"): out.append('<span class="badge req">100% P&amp;T</span>')
    if r.get("requires_tdiu"): out.append('<span class="badge req">TDIU</span>')
    pct=r.get("min_rating_pct")
    if pct and int(pct)>0 and not r.get("requires_pt"): out.append(f'<span class="badge req">{int(pct)}%{"+" if int(pct) < 100 else ""} rating</span>')
    if not out: out.append('<span class="badge">Any veteran</span>')
    return "".join(out)

# One-time benefits carry an amount in the data, but "per year" is wrong for them.
# Label them as one-time and show no yearly figure; the description holds any cap.
ONE_TIME = {26: "One-time grant", 27: "One-time grant", 28: "One-time grant",
            34: "One-time discharge", 29: "One-time savings at closing", 3: "One-time savings at closing"}

def ben(r):
    val=money(r.get("estimated_annual_value")); vd=r.get("value_description")
    ot = ONE_TIME.get(r.get("id"))
    if ot:
        vline = f'<div class="ben-val">{ot}{" &middot; " + esc(vd) if vd else ""}</div>'
    elif val and vd: vline=f'<div class="ben-val">Est. {val}/yr &middot; {esc(vd)}</div>'
    elif val: vline=f'<div class="ben-val">Est. {val}/yr</div>'
    elif vd: vline=f'<div class="ben-val">{esc(vd)}</div>'
    else: vline=""
    how=f'<p class="how">How to claim: {esc(r["how_to_claim"])}</p>' if r.get("how_to_claim") else ""
    if "vets-safe" in (r.get("website_url") or ""):
        how += ('<p class="how">Who qualifies: Veterans enrolled in VA health care who have a service-connected disability of '
                'permanent blindness, or who require a VA-issued wheelchair or prosthetic limb.</p>')
    foot=[]
    if r.get("cfr_reference"): foot.append(esc(r["cfr_reference"]))
    link=r.get("website_url")
    fh=" &middot; ".join(foot)
    nm = esc(r["benefit_name"])
    if link: nm = f'<a href="{esc(link)}" target="_blank" rel="noopener">{nm}</a>'
    return (f'<li class="ben"><div class="ben-top"><span class="ben-name">{nm}</span>{badges(r)}</div>'
            f'{vline}<p>{esc(r.get("description"))}</p>{how}'+(f'<div class="ben-foot">{fh}</div>' if fh else '')+'</li>')

cats_present=[c for c,_ in CAT if any(r["benefit_category"]==c for r in ROWS)]
blocks=""
for c in cats_present:
    rows=sorted([r for r in ROWS if r["benefit_category"]==c], key=lambda r:r["benefit_name"])
    blocks+=f'<div class="catblock"><h2>{esc(CATLABEL[c])}</h2><ol class="blist">{"".join(ben(r) for r in rows)}</ol></div>'

canon="https://vareadyapp.com/federal-benefits.html"
desc="Federal benefits for disabled veterans: health care, housing, education, financial, and employment programs you may qualify for by VA rating. What you get and how to claim it."
desc=desc[:160]
lds=[
 {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
   {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
   {"@type":"ListItem","position":2,"name":"Federal benefits","item":canon}]},
 {"@context":"https://schema.org","@type":"Article","headline":"Federal benefits for disabled veterans","description":desc,"datePublished":"2026-06-12","dateModified":"2026-06-12","author":{"@type":"Organization","name":"JDL Software LLC"},"publisher":{"@type":"Organization","name":"VA Ready"},"mainEntityOfPage":canon,"inLanguage":"en-US"},
]
lds_html="\n".join(f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in lds)
page=f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Federal benefits for disabled veterans ({len(ROWS)} programs) | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="Federal benefits for disabled veterans"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
{lds_html}
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / Federal benefits</div>
    <h1>Federal benefits for disabled veterans</h1>
    <p class="lede">A service-connected rating can make you eligible for {len(ROWS)} federal programs nationwide, across health care, housing, education, financial support, and employment. Each entry lists the minimum rating and how to claim it.</p>
    {blocks}
    <div class="btns page-cta"><a href="/va-disability-calculator.html" class="btn">Estimate your combined rating</a><a href="/states.html" class="btn ghost">Your state's benefits</a></div>
    {APP_CTA}
    <p class="trustline">More from VA Ready: <a href="/states.html">state benefits</a> &middot; <a href="/va-disability-pay-rates.html">pay rates</a> &middot; <a href="/find-a-vso.html">find a free VSO</a></p>
    <div class="disclaimer">Federal benefit eligibility, amounts, and rules change. Estimated values are approximate. Always confirm current details at VA.gov or the linked agency before relying on a benefit. VA Ready is not affiliated with the U.S. Department of Veterans Affairs, and this page is not legal, tax, or financial advice.</div>
</div>
{FOOTER}
</body>
</html>"""
open(os.path.join(SITE,"federal-benefits.html"),"w").write(page)

sp=os.path.join(SITE,"sitemap.xml"); xml=open(sp).read()
if canon not in xml:
    xml=xml.replace("</urlset>", f'  <url>\n    <loc>{canon}</loc>\n    <lastmod>2026-06-12</lastmod>\n    <priority>0.8</priority>\n  </url>\n</urlset>'); open(sp,"w").write(xml); added=1
else: added=0
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S): json.loads(b)
print(f"federal-benefits.html written ({len(ROWS)} benefits, {len(cats_present)} categories); sitemap +{added}; JSON-LD valid")
