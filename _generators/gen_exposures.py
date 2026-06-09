#!/usr/bin/env python3
"""Exposure / presumptive landing pages (Cluster B), from exposure_catalog.
Marquee lists (Agent Orange, Camp Lejeune, burn pits, Gulf War) verified vs VA.gov."""
import json, re, os, html
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
EXDIR = os.path.join(SITE, "exposures")
os.makedirs(EXDIR, exist_ok=True)
def esc(s): return html.escape(str(s) if s is not None else "", quote=True)

ROWS = json.load(open(os.path.join(HERE,"data","exposure_catalog.json")))

# dc -> condition page slug (the 20 condition pages we publish)
COND_SLUG = {"6260":"tinnitus","9411":"ptsd","5237":"back-pain","5260":"knee-pain","6847":"sleep-apnea",
"8100":"migraines","9434":"depression","5003":"arthritis","5201":"shoulder","5271":"ankle",
"5257":"knee-instability","7806":"eczema","6602":"asthma","8520":"sciatica","5242":"degenerative-disc-disease",
"6100":"hearing-loss","7101":"hypertension","7346":"gerd-acid-reflux","7913":"diabetes","7805":"scars"}

# 12 marquee pages: slug, h1, lede, and the exposure_name substrings that feed it
PAGES = [
 ("agent-orange","Agent Orange Exposure & VA Presumptive Conditions",
  "Agent Orange and other tactical herbicides were sprayed in Vietnam and stored, tested, or used at sites across Asia and the Pacific. If you served in a recognized location and time, VA presumes certain conditions are service-connected — you don't have to prove the link.",
  ["Agent Orange"]),
 ("burn-pits-pact-act","Burn Pits & the PACT Act — Presumptive Conditions",
  "Open-air burn pits and airborne hazards exposed Gulf War and post-9/11 veterans to smoke and fine particulate. The PACT Act made dozens of cancers and respiratory illnesses presumptive for veterans who served in qualifying locations.",
  ["Burn Pits","Kuwait Oil Well"]),
 ("camp-lejeune","Camp Lejeune Water Contamination — VA Claims & Presumptive Conditions",
  "From 1953 to 1987, the drinking water at Marine Corps Base Camp Lejeune and MCAS New River was contaminated with industrial solvents. Veterans, reservists, and guardsmen who served there at least 30 days qualify for presumptive disability benefits for several conditions.",
  ["Camp Lejeune"]),
 ("gulf-war-illness","Gulf War Illness — Undiagnosed Illness & Presumptive Conditions",
  "Many Gulf War veterans returned with chronic, medically unexplained symptoms. VA recognizes Gulf War Illness — including undiagnosed illnesses and chronic multisymptom conditions — as presumptively service-connected for those who served in the Southwest Asia theater.",
  ["Gulf War Illness"]),
 ("afff-pfas","AFFF / PFAS Firefighting Foam Exposure — VA Claims",
  "Aqueous Film-Forming Foam (AFFF) used in military firefighting contains PFAS 'forever chemicals' linked to cancers and other illnesses. Veterans exposed at flight lines, fire-training pits, and crash crews may have a claim.",
  ["AFFF / PFAS"]),
 ("k2-karshi-khanabad","K2 (Karshi-Khanabad) Air Base Exposure — VA Claims",
  "Veterans stationed at K2 — Karshi-Khanabad Air Base in Uzbekistan — were exposed to a stew of jet fuel, solvents, particulate, and possible radiological hazards. K2 service is now recognized under the PACT Act.",
  ["K2 - Karshi"]),
 ("asbestos","Military Asbestos Exposure — VA Claims & Conditions",
  "Asbestos was everywhere in older ships, buildings, brakes, and insulation. Navy veterans and many trades faced heavy exposure, and asbestos-related diseases can appear decades later.",
  ["Asbestos"]),
 ("radiation","Radiation Exposure & Atomic Veterans — VA Presumptive Conditions",
  "Atomic veterans and others exposed to ionizing radiation — from atmospheric nuclear tests to cleanup missions and occupational sources — may qualify for presumptive benefits for radiogenic cancers.",
  ["Ionizing Radiation","Radiofrequency"]),
 ("depleted-uranium","Depleted Uranium (DU) Exposure — VA Claims",
  "Depleted uranium was used in armor and munitions. Veterans wounded by DU fragments, or who worked on or around struck vehicles, may have internal exposure that VA monitors and evaluates.",
  ["Depleted Uranium"]),
 ("jet-fuel-petroleum","Jet Fuel & Petroleum Exposure (JP-8) — VA Claims",
  "Jet fuels and petroleum products (JP-4, JP-5, JP-8) exposed flight-line crews, fuel handlers, and maintainers to benzene and other toxins linked to blood disorders and cancers.",
  ["Jet Fuel"]),
 ("fort-mcclellan","Fort McClellan Exposure — VA Claims",
  "Fort McClellan, Alabama hosted the Army Chemical Corps and sat near industrial PCB and chemical contamination. Veterans who trained or served there may have multiple exposure pathways.",
  ["Fort McClellan"]),
 ("project-112-shad","Project 112 / Project SHAD — Chemical & Biological Testing",
  "Project 112 and its naval arm Project SHAD were Cold War DoD tests of chemical and biological agents on service members, often without their knowledge. VA recognizes participants for exposure-related claims.",
  ["Project 112"]),
]

def fmt_date(s):
    if not s: return None
    try:
        y,m,d = s.split("-"); return f"{['','January','February','March','April','May','June','July','August','September','October','November','December'][int(m)]} {int(d)}, {y}"
    except: return s

CSS = re.search(r'CSS = """(.*?)"""', open(os.path.join(HERE,"gen_guides.py")).read(), re.S).group(1) + """
    .pactbadge { display:inline-block; font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:.6px; background:rgba(52,168,83,.16); color:var(--green); border:1px solid transparent; border-radius:999px; padding:4px 11px; margin:0 0 10px; }
    .covered { list-style:none; padding:0; margin:8px 0 16px; }
    .covered li { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:11px 14px; margin:0 0 9px; }
    .covered .loc { color:var(--white); font-weight:700; }
    .covered .win { color:var(--gold); font-size:13px; font-weight:700; }
    .covered .dsc { color:var(--tan); font-size:13.5px; margin-top:3px; }
    .condgrid { display:flex; flex-wrap:wrap; gap:8px; margin:10px 0 16px; }
    .condgrid a, .condgrid span { font-size:13.5px; background:var(--card); border:1px solid var(--line); color:var(--tan); padding:7px 13px; border-radius:999px; }
    .condgrid a { color:var(--gold); font-weight:700; text-decoration:none; }
    .docs { margin:8px 0 16px; padding-left:18px; }
    .docs li { color:var(--tan); font-size:14.5px; margin-bottom:6px; }
    .docs li strong { color:var(--white); }
    .trustline { font-size:13.5px; color:var(--tan); background:var(--card); border:1px solid var(--line); border-left:3px solid var(--gold); border-radius:10px; padding:9px 13px; margin:14px 0; }
    .trustline a { color:var(--gold); font-weight:700; text-decoration:none; }
"""
NAV = re.search(r'NAV = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)
FOOTER = re.search(r'FOOTER = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)
APP_CTA = re.search(r'APP_CTA = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)

def clean_loc(name):
    # strip leading topic prefix before " - " for display
    return name

def page(slug, h1, lede, matches):
    rows = [r for r in ROWS if any(m in r["exposure_name"] for m in matches)]
    canon = f"https://vareadyapp.com/exposures/{slug}.html"
    is_pact = any(r.get("is_pact_eligible") for r in rows)
    # union presumptive conditions (dedupe by dc+name)
    seen=set(); conds=[]
    for r in rows:
        for c in (r.get("presumptive_conditions") or []):
            k=(c.get("dc"),c.get("name"))
            if k in seen: continue
            seen.add(k); conds.append(c)
    # union docs by type
    dseen=set(); docs=[]
    for r in rows:
        for d in (r.get("documentation_requirements") or []):
            t=d.get("type")
            if t in dseen: continue
            dseen.add(t); docs.append(d)
    authority = next((r.get("presumptive_authority") for r in rows if r.get("presumptive_authority")), None)
    topic = h1.split("—")[0].split("(")[0].strip()
    desc = f"{topic}: who qualifies, the VA presumptive conditions, and how to file a claim. " + (f"{len(conds)} presumptive conditions. " if conds else "") + "Free VA rating tools."
    desc = desc[:160]
    # who's covered
    cov_items=""
    for r in rows:
        loc = esc(clean_loc(r["exposure_name"]))
        ws, we = fmt_date(r.get("date_window_start")), fmt_date(r.get("date_window_end"))
        win = (f'<span class="win">{ws} &ndash; {we}</span>' if ws and we else (f'<span class="win">from {ws}</span>' if ws else ""))
        dsc = esc((r.get("description") or "")[:240])
        cov_items += f'<li><div class="loc">{loc}</div>{win}{f"<div class=\"dsc\">{dsc}</div>" if dsc else ""}</li>'
    covered = f'<ul class="covered">{cov_items}</ul>'
    # conditions
    cond_html=""
    if conds:
        cells=""
        for c in conds:
            nm=esc(c.get("name")); dc=str(c.get("dc") or "")
            sl=COND_SLUG.get(dc)
            cells += f'<a href="/conditions/{sl}.html">{nm}</a>' if sl else f'<span>{nm}</span>'
        cond_html = f'<h2>Presumptive conditions ({len(conds)})</h2><p>If you have a qualifying diagnosis and the service above, VA presumes these are connected to your exposure &mdash; you don\'t have to prove causation:</p><div class="condgrid">{cells}</div>'
    # docs
    doc_html=""
    if docs:
        items="".join(f'<li><strong>{esc(d.get("type"))}</strong> &mdash; {esc(d.get("why"))}</li>' for d in docs)
        doc_html = f'<h2>What you need to file</h2><ul class="docs">{items}</ul>'
    # FAQ
    cond_names=[c.get("name") for c in conds][:4]
    faqs=[(f"What conditions are presumptive for {topic}?",
           (f"VA recognizes {len(conds)} presumptive conditions, including {', '.join(cond_names)}. With qualifying service you don't have to prove the connection." if conds else f"VA evaluates {topic} claims based on documented exposure and a current diagnosis."))]
    faqs.append((f"Who qualifies for {topic} benefits?",
                 "You generally need qualifying service in a recognized location and time period (listed above), a current diagnosis, and a discharge that isn't dishonorable."))
    if is_pact:
        faqs.append((f"Is {topic} covered under the PACT Act?",
                     "Yes. This exposure is recognized under the PACT Act, which expanded presumptive conditions and eligibility for toxic-exposed veterans."))
    faqs.append(("How do I file an exposure claim?",
                 "File a disability claim listing your condition and exposure. Start with an Intent to File to lock your effective date, get a current diagnosis, and bring your service records. The VA Ready app and guides walk you through each step."))
    faq_visible = "".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q,a in faqs)
    bc=[{"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"Toxic Exposures","item":"https://vareadyapp.com/exposures.html"},
        {"@type":"ListItem","position":3,"name":topic,"item":canon}]
    lds=[{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":bc},
         {"@context":"https://schema.org","@type":"Article","headline":h1,"description":desc,"datePublished":"2026-06-09","dateModified":"2026-06-09","author":{"@type":"Organization","name":"JDL Software LLC"},"publisher":{"@type":"Organization","name":"VA Ready"},"mainEntityOfPage":canon,"inLanguage":"en-US"},
         {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}]
    lds_html="\n".join(f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in lds)
    auth_html = f'<h2>Legal authority &amp; sources</h2><p style="color:var(--gray);font-size:14px;">{esc(authority)}</p>' if authority else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(topic)} &mdash; VA Presumptive Conditions &amp; Claims | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="{esc(h1)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" href="/logo.png">
{lds_html}
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/exposures.html">Toxic Exposures</a> / {esc(topic)}</div>
    <div class="eyebrow">Toxic Exposure &amp; Presumptive Conditions</div>
    <h1>{h1}</h1>
    {'<div class="pactbadge">PACT Act recognized</div>' if is_pact else ''}
    <p class="lede">{lede}</p>
    <article>
        <h2>Who's covered</h2>
        <p>VA recognizes exposure for service in these locations and time periods:</p>
        {covered}
        {cond_html}
        <p class="trustline">See your conditions and what they rate, then build your combined rating &mdash; <a href="/va-disability-calculator.html">open the free calculator &rarr;</a></p>
        {doc_html}
        <h2>How to file</h2>
        <p>File a disability claim for your diagnosed condition and note the exposure. The usual path: lock your date with an <a href="/guides/intent-to-file.html">Intent to File</a>, get a current diagnosis, gather your service records, and prepare for your <a href="/guides/c-and-p-exam-preparation.html">C&amp;P exam</a>. If service connection isn't obvious, a <a href="/guides/nexus-letters.html">nexus letter</a> can help.</p>
        {auth_html}
    </article>
    {APP_CTA}
    <p class="trustline">More from VA Ready: <a href="/exposures.html">all toxic exposures</a> &middot; <a href="/conditions.html">ratings by condition</a> &middot; <a href="/va-disability-pay-rates.html">pay rates</a></p>
    <h2 style="font-size:20px;margin-top:26px;">Common questions</h2>
    {faq_visible}
    <div class="disclaimer">Presumptive conditions, eligible locations, and dates are summarized from VA.gov and the cited authorities and can change. Always confirm current eligibility at VA.gov or with a VA-accredited representative. VA Ready is not affiliated with the U.S. Department of Veterans Affairs, and this page is not legal or medical advice.</div>
</div>
{FOOTER}
</body>
</html>"""

# write pages
written=[]
for slug,h1,lede,matches in PAGES:
    open(os.path.join(EXDIR,slug+".html"),"w").write(page(slug,h1,lede,matches)); written.append((slug,h1))

# hub
def hub():
    canon="https://vareadyapp.com/exposures.html"
    cards=""
    for slug,h1,lede,matches in PAGES:
        rows=[r for r in ROWS if any(m in r["exposure_name"] for m in matches)]
        nc=len({(c.get("dc"),c.get("name")) for r in rows for c in (r.get("presumptive_conditions") or [])})
        pact=any(r.get("is_pact_eligible") for r in rows)
        topic=h1.split("—")[0].split("(")[0].strip()
        sub=f'{nc} presumptive conditions' + (' &middot; PACT Act' if pact else '')
        cards+=f'<div class="hub-card"><a href="/exposures/{slug}.html">{esc(topic)}</a><p>{sub}</p></div>'
    desc="Military toxic exposures and VA presumptive conditions: Agent Orange, burn pits & the PACT Act, Camp Lejeune, Gulf War Illness, AFFF/PFAS, K2, asbestos, and radiation. Who qualifies and how to file."
    bc={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},{"@type":"ListItem","position":2,"name":"Toxic Exposures","item":canon}]}
    items={"@context":"https://schema.org","@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"https://vareadyapp.com/exposures/{s}.html","name":h.split('—')[0].strip()} for i,(s,h,l,m) in enumerate(PAGES)]}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Military Toxic Exposures &amp; VA Presumptive Conditions | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="Military Toxic Exposures &amp; VA Presumptive Conditions"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" href="/logo.png">
<script type="application/ld+json">{json.dumps(bc)}</script>
<script type="application/ld+json">{json.dumps(items)}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / Toxic Exposures</div>
    <div class="eyebrow">By Exposure</div>
    <h1>Military Toxic Exposures &amp; Presumptive Conditions</h1>
    <p class="lede">If you were exposed to toxic substances in service, VA may presume certain conditions are service-connected &mdash; meaning you don't have to prove the link. Here are the major exposures, who qualifies, the presumptive conditions, and how to file. The VA Ready app maps every base and aircraft you served on to the exposures you may have earned.</p>
    <div class="hub-sec"><div class="hub-grid">{cards}</div></div>
    {APP_CTA}
    <p class="trustline">More from VA Ready: <a href="/conditions.html">ratings by condition</a> &middot; <a href="/va-disability-pay-rates.html">pay rates</a> &middot; <a href="/states.html">state benefits</a></p>
    <div class="disclaimer">Presumptive lists and eligibility are summarized from VA.gov and can change; confirm current rules at VA.gov. VA Ready is not affiliated with the U.S. Department of Veterans Affairs.</div>
</div>
{FOOTER}
</body>
</html>"""
open(os.path.join(SITE,"exposures.html"),"w").write(hub())

# sitemap
sp=os.path.join(SITE,"sitemap.xml"); xml=open(sp).read(); new=[]
urls=[("https://vareadyapp.com/exposures.html","0.8")]+[(f"https://vareadyapp.com/exposures/{s}.html","0.7") for s,h,l,m in PAGES]
for u,pr in urls:
    if u not in xml: new.append(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-06-09</lastmod>\n    <priority>{pr}</priority>\n  </url>')
if new: xml=xml.replace("</urlset>","\n".join(new)+"\n</urlset>"); open(sp,"w").write(xml)

# validate
import glob
bad=0
for f in [os.path.join(SITE,"exposures.html")]+glob.glob(os.path.join(EXDIR,"*.html")):
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', open(f).read(), re.S):
        try: json.loads(blk)
        except Exception as e: bad+=1; print("BAD JSON-LD",f,e)
print(f"wrote {len(written)} exposure pages + hub; sitemap +{len(new)}; JSON-LD bad={bad}")
