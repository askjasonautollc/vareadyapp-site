#!/usr/bin/env python3
"""Federal benefits page for disabled veterans, from federal_benefits (34 rows)."""
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
# Exclude DB entries that aren't true federal benefit programs, are mis-categorized, or duplicate another.
# id 10 = "10% Bilateral Factor" (a rating-combination rule, handled by the calculator, not a benefit);
EXCLUDE_IDS = {10}  # bilateral factor: kept in DB/app, hidden on the web benefits list (it's a rating rule, not a benefit)
ROWS = [r for r in ROWS if r.get("id") not in EXCLUDE_IDS]
CAT = [("financial","Financial & Compensation"),("healthcare","Health Care"),("housing","Housing"),
       ("education","Education"),("employment","Employment"),("life_insurance","Life Insurance"),("other","Other")]
CATLABEL = dict(CAT)
def catrank(c): return [k for k,_ in CAT].index(c) if c in dict(CAT) else 99

CSS = re.search(r'CSS = """(.*?)"""', open(os.path.join(HERE,"gen_guides.py")).read(), re.S).group(1) + """
    .meta { color:var(--gray); font-size:14px; margin:4px 0 14px; } .meta strong { color:var(--white); }
    .catblock { margin:22px 0 6px; } .catblock h2 { margin-bottom:6px; }
    ol.blist { list-style:none; padding:0; margin:0; }
    li.ben { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:15px 17px; margin:0 0 13px; }
    .ben-top { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin-bottom:6px; }
    .ben-name { color:var(--white); font-weight:800; font-size:17px; }
    .badge { font-size:11px; text-transform:uppercase; letter-spacing:.6px; padding:3px 9px; border-radius:999px; border:1px solid var(--line); color:var(--tan); }
    .badge.req { background:rgba(201,162,77,.16); color:var(--gold); border-color:transparent; }
    .ben-val { color:var(--gold); font-weight:700; font-size:14px; margin:2px 0 6px; }
    .ben p { color:var(--tan); font-size:15px; margin:5px 0; }
    .ben .how { color:var(--tan); font-size:14px; } .ben .how strong { color:var(--white); }
    .ben-foot { display:flex; flex-wrap:wrap; gap:6px 14px; align-items:center; margin-top:8px; font-size:13px; color:var(--gray); }
    .ben-foot a { color:var(--gold); font-weight:700; text-decoration:none; } .ben-foot a:hover { text-decoration:underline; }
    .trustline { font-size:13.5px; color:var(--tan); background:var(--card); border:1px solid var(--line); border-left:3px solid var(--gold); border-radius:10px; padding:9px 13px; margin:14px 0; }
    .trustline a { color:var(--gold); font-weight:700; text-decoration:none; }
    .spotlight { background:linear-gradient(135deg, rgba(217,166,33,0.12), rgba(217,166,33,0.02)); border:1px solid rgba(217,166,33,0.30); border-radius:16px; padding:20px 22px; margin:18px 0 24px; }
    .spotlight .spot-tag { display:inline-block; font-size:11px; font-weight:900; letter-spacing:1px; text-transform:uppercase; color:#1a1205; background:var(--gold); padding:3px 10px; border-radius:6px; margin-bottom:11px; }
    .spotlight h2 { font-size:21px; font-weight:900; color:var(--white); margin:0 0 8px; letter-spacing:-0.3px; }
    .spotlight > p { color:var(--tan); font-size:15px; margin:0 0 11px; line-height:1.6; }
    .spot-elig { color:var(--tan); font-size:14px; background:rgba(255,255,255,0.04); border-left:2px solid var(--gold); border-radius:8px; padding:8px 12px; margin:0 0 13px; }
    .spot-elig strong { color:var(--white); }
    a.spot-cta { display:inline-block; background:var(--gold); color:#1a1205; font-weight:800; font-size:14px; padding:9px 16px; border-radius:10px; }
"""
NAV = re.search(r'NAV = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)
FOOTER = re.search(r'FOOTER = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)
APP_CTA = re.search(r'APP_CTA = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)

def badges(r):
    out=[]
    if r.get("requires_pt"): out.append('<span class="badge req">100% P&amp;T</span>')
    if r.get("requires_tdiu"): out.append('<span class="badge req">TDIU</span>')
    pct=r.get("min_rating_pct")
    if pct and int(pct)>0 and not r.get("requires_pt"): out.append(f'<span class="badge req">{int(pct)}%+ rating</span>')
    if not out: out.append('<span class="badge">Any veteran</span>')
    return "".join(out)

def ben(r):
    val=money(r.get("estimated_annual_value")); vd=r.get("value_description")
    if val and vd: vline=f'<div class="ben-val">Est. {val}/yr &middot; {esc(vd)}</div>'
    elif val: vline=f'<div class="ben-val">Est. value: {val}/yr</div>'
    elif vd: vline=f'<div class="ben-val">{esc(vd)}</div>'
    else: vline=""
    how=f'<p class="how"><strong>How to claim:</strong> {esc(r["how_to_claim"])}</p>' if r.get("how_to_claim") else ""
    foot=[]
    if r.get("cfr_reference"): foot.append(esc(r["cfr_reference"]))
    link=r.get("website_url")
    fh=" &middot; ".join(foot)
    if link: fh += (' &middot; ' if fh else '')+f'<a href="{esc(link)}" target="_blank" rel="noopener">Official details &#8599;</a>'
    return (f'<li class="ben"><div class="ben-top"><span class="ben-name">{esc(r["benefit_name"])}</span>{badges(r)}</div>'
            f'{vline}<p>{esc(r.get("description"))}</p>{how}'+(f'<div class="ben-foot">{fh}</div>' if fh else '')+'</li>')

# Featured spotlight — pulled from the TSA PreCheck row so it stays in sync with the data.
def spotlight():
    row=next((r for r in ROWS if "vets-safe" in (r.get("website_url") or "")), None)
    if not row: return ""
    return (f'<div class="spotlight"><span class="spot-tag">New federal benefit</span>'
            f'<h2>{esc(row["benefit_name"])}</h2>'
            f'<p>{esc(row["description"])}</p>'
            f'<div class="spot-elig"><strong>Who qualifies:</strong> Veterans enrolled in VA health care who have a '
            f'service-connected disability of permanent blindness, or who require a VA-issued wheelchair or prosthetic limb.</div>'
            f'<a class="spot-cta" href="{esc(row["website_url"])}" target="_blank" rel="noopener">How to enroll on TSA.gov &#8599;</a></div>')
SPOTLIGHT=spotlight()

cats_present=[c for c,_ in CAT if any(r["benefit_category"]==c for r in ROWS)]
blocks=""
for c in cats_present:
    rows=sorted([r for r in ROWS if r["benefit_category"]==c], key=lambda r:r["benefit_name"])
    blocks+=f'<div class="catblock"><h2>{esc(CATLABEL[c])}</h2><ol class="blist">{"".join(ben(r) for r in rows)}</ol></div>'

canon="https://vareadyapp.com/federal-benefits.html"
desc="Federal benefits for disabled veterans: health care, housing, education, financial, and employment programs you may qualify for by VA rating. What you get and how to claim it."
desc=desc[:160]
faqs=[
 ("What federal benefits do disabled veterans get?",
  f"Beyond monthly compensation, VA rating unlocks {len(ROWS)} federal benefits across health care, housing, education, financial, and employment — like VR&E, the VA home loan funding-fee waiver, CHAMPVA, Chapter 35 education, and property/loan programs. Eligibility depends on your rating, and some require 100% P&T or TDIU."),
 ("Do federal veteran benefits depend on my disability rating?",
  "Many do. Some are open to any service-connected veteran; others require a minimum rating, 100% Permanent & Total, or TDIU. Use the free calculator to confirm your combined rating, then see what you qualify for."),
 ("Are these different from state benefits?",
  "Yes. These are federal programs available nationwide. Your state also offers its own benefits (property-tax exemptions, tuition, vehicle and recreation perks) — see the State Benefits pages for yours."),
]
faq_v="".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q,a in faqs)
lds=[
 {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
   {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
   {"@type":"ListItem","position":2,"name":"Federal Benefits","item":canon}]},
 {"@context":"https://schema.org","@type":"Article","headline":"Federal Benefits for Disabled Veterans","description":desc,"datePublished":"2026-06-12","dateModified":"2026-06-12","author":{"@type":"Organization","name":"JDL Software LLC"},"publisher":{"@type":"Organization","name":"VA Ready"},"mainEntityOfPage":canon,"inLanguage":"en-US"},
 {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]},
]
lds_html="\n".join(f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in lds)
page=f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Federal Benefits for Disabled Veterans ({len(ROWS)} programs) | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="Federal Benefits for Disabled Veterans"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" href="/logo.png">
{lds_html}
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / Federal Benefits</div>
    <div class="eyebrow">Federal Veteran Benefits</div>
    <h1>Federal Benefits for Disabled Veterans</h1>
    <p class="lede">Your VA disability rating unlocks far more than a monthly check. These are the <strong>{len(ROWS)}</strong> federal programs &mdash; health care, housing, education, financial, and employment &mdash; that a service-connected rating can make you eligible for, nationwide.</p>
    <div class="meta"><strong>{len(ROWS)} federal benefits</strong> &middot; {', '.join(esc(CATLABEL[c]) for c in cats_present)}</div>
    <p class="trustline">Not sure what your rating qualifies you for? <a href="/va-disability-calculator.html">Check your combined rating &rarr;</a></p>
    {SPOTLIGHT}
    {blocks}
    <p style="margin:22px 0;"><a href="/va-disability-calculator.html" class="btn">Estimate your combined rating &rarr;</a> &nbsp; <a href="/states.html" class="btn ghost">Your state's benefits too &rarr;</a></p>
    {APP_CTA}
    <p class="trustline">More from VA Ready: <a href="/states.html">state benefits</a> &middot; <a href="/va-disability-pay-rates.html">pay rates</a> &middot; <a href="/find-a-vso.html">find a free VSO</a></p>
    <h2 style="font-size:20px;margin-top:26px;">Common questions</h2>
    {faq_v}
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
