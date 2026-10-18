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

# Short topic per page, used for the <title>, the meta description and the hub
# card. Explicit on purpose: this used to be derived by splitting the h1 on an
# em dash, so editing the h1 silently rewrote the title. It also keeps titles
# near the ~60 chars Google actually renders, instead of the 100+ the derived
# version produced.
TOPICS = {
    "agent-orange":       "Agent Orange exposure",
    "burn-pits-pact-act": "Burn pits and the PACT Act",
    "camp-lejeune":       "Camp Lejeune water contamination",
    "gulf-war-illness":   "Gulf War illness",
    "afff-pfas":          "AFFF / PFAS firefighting foam",
    "k2-karshi-khanabad": "K2 (Karshi-Khanabad) Air Base",
    "asbestos":           "Military asbestos exposure",
    "radiation":          "Radiation and atomic veterans",
    "depleted-uranium":   "Depleted uranium (DU)",
    "jet-fuel-petroleum": "Jet fuel and petroleum (JP-8)",
    "fort-mcclellan":     "Fort McClellan exposure",
    "project-112-shad":   "Project 112 and Project SHAD",
}

# 12 marquee pages: slug, h1, lede, and the exposure_name substrings that feed it
PAGES = [
 ("agent-orange","Agent Orange exposure and VA presumptive conditions",
  "Agent Orange and other tactical herbicides were sprayed in Vietnam and stored, tested, or used at sites across Asia and the Pacific. If you served in a recognized location and time, VA presumes certain conditions are service-connected, you don't have to prove the link.",
  ["Agent Orange"]),
 ("burn-pits-pact-act","Burn pits and the PACT Act: presumptive conditions",
  "Open-air burn pits and airborne hazards exposed Gulf War and post-9/11 veterans to smoke and fine particulate. The PACT Act made dozens of cancers and respiratory illnesses presumptive for veterans who served in qualifying locations.",
  ["Burn Pits","Kuwait Oil Well"]),
 ("camp-lejeune","Camp Lejeune water contamination and presumptive conditions",
  "From 1953 to 1987, the drinking water at Marine Corps Base Camp Lejeune and MCAS New River was contaminated with industrial solvents. Veterans, reservists, and guardsmen who served there at least 30 days qualify for presumptive disability benefits for several conditions.",
  ["Camp Lejeune"]),
 ("gulf-war-illness","Gulf War illness: undiagnosed illness and presumptive conditions",
  "Many Gulf War veterans returned with chronic, medically unexplained symptoms. VA recognizes Gulf War Illness, including undiagnosed illnesses and chronic multisymptom conditions, as presumptively service-connected for those who served in the Southwest Asia theater.",
  ["Gulf War Illness"]),
 ("afff-pfas","AFFF / PFAS firefighting foam exposure",
  "Aqueous Film-Forming Foam (AFFF) used in military firefighting contains PFAS 'forever chemicals' linked to cancers and other illnesses. Veterans exposed at flight lines, fire-training pits, and crash crews may have a claim.",
  ["AFFF / PFAS"]),
 ("k2-karshi-khanabad","K2 (Karshi-Khanabad) Air Base exposure",
  "Veterans stationed at K2 (Karshi-Khanabad Air Base) in Uzbekistan from 2001 to 2005 were exposed to leaking jet fuel, low-level depleted uranium contamination, particulate matter, asbestos, and lead-based paint. K2 service is recognized under the PACT Act.",
  ["K2 - Karshi"]),
 ("asbestos","Military asbestos exposure and related conditions",
  "Asbestos was used in older ships, buildings, brakes, and insulation. Navy veterans and many trades faced heavy exposure, and asbestos-related diseases can appear decades later.",
  ["Asbestos"]),
 ("radiation","Radiation exposure, atomic veterans and presumptive conditions",
  "Atomic veterans and others exposed to ionizing radiation, from atmospheric nuclear tests to cleanup missions and occupational sources, may qualify for presumptive benefits for radiogenic cancers.",
  ["Ionizing Radiation","Radiofrequency"]),
 ("depleted-uranium","Depleted uranium (DU) exposure",
  "Depleted uranium was used in armor and munitions. Veterans wounded by DU fragments, or who worked on or around struck vehicles, may have internal exposure that VA monitors and evaluates.",
  ["Depleted Uranium"]),
 ("jet-fuel-petroleum","Jet fuel and petroleum exposure (JP-8)",
  "Jet fuels and petroleum products (JP-4, JP-5, JP-8) exposed flight-line crews, fuel handlers, and maintainers to benzene and other toxins linked to blood disorders and cancers.",
  ["Jet Fuel"]),
 ("fort-mcclellan","Fort McClellan exposure",
  "Fort McClellan, Alabama hosted the Army Chemical Corps and sat near industrial PCB and chemical contamination. Veterans who trained or served there may have multiple exposure pathways.",
  ["Fort McClellan"]),
 ("project-112-shad","Project 112 and Project SHAD: chemical and biological testing",
  "Project 112 and its naval arm Project SHAD were Cold War DoD tests of chemical and biological agents on service members, often without their knowledge. VA recognizes participants for exposure-related claims.",
  ["Project 112"]),
]

def fmt_date(s):
    if not s: return None
    try:
        y,m,d = s.split("-"); return f"{['','January','February','March','April','May','June','July','August','September','October','November','December'][int(m)]} {int(d)}, {y}"
    except: return s

CSS = re.search(r'CSS = """(.*?)"""', open(os.path.join(HERE,"gen_guides.py")).read(), re.S).group(1) + """
    .pactnote { font-size:14px; color:var(--tan); margin:0 0 10px; }
    .covered { list-style:none; padding:0; margin:8px 0 16px; max-width:none; }
    .covered li { border-top:1px solid var(--line); padding:12px 0; margin:0; }
    .covered .loc { color:var(--white); font-weight:700; }
    .covered .win { color:var(--gray); font-size:13.5px; font-variant-numeric:tabular-nums; }
    .covered .dsc { color:var(--tan); font-size:14.5px; margin-top:3px; }
    .condgrid { display:flex; flex-wrap:wrap; gap:4px 18px; margin:10px 0 16px; }
    .condgrid a, .condgrid span { font-size:15px; color:var(--tan); padding:8px 0; }
    .condgrid a { color:var(--white); }
    .docs { margin:8px 0 16px; padding-left:18px; }
    .docs li { color:var(--tan); font-size:15px; margin-bottom:6px; }
    .trustline { font-size:14.5px; color:var(--tan); margin:14px 0; max-width:68ch; }
    .page-cta { margin:26px 0; }
"""
NAV = re.search(r'NAV = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)
FOOTER = re.search(r'FOOTER = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)
APP_CTA = """<div class="cta cta-line"><p>The exposure catalog with primary sources is free in <a href="https://apps.apple.com/app/id6761733758">VA Ready for iOS</a>, <a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US">Vet Ready for Android</a> and <a href="https://apps.microsoft.com/detail/9p8xfcqvfjhf">VA Ready for Windows</a>; Pro adds Claim Intel and the full 38 CFR rating criteria for every condition.</p></div>"""

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
    topic = TOPICS.get(slug) or re.split(r"[.:]", h1)[0].split("(")[0].strip()
    desc = f"{topic}: who qualifies, " + (f"the {len(conds)} presumptive conditions, " if conds else "the conditions VA evaluates, ") + "and the documents VA asks for."
    desc = desc[:160]
    # who's covered
    cov_items=""
    for r in rows:
        loc = esc(clean_loc(r["exposure_name"]))
        ws, we = fmt_date(r.get("date_window_start")), fmt_date(r.get("date_window_end"))
        win = (f'<span class="win">{ws} &ndash; {we}</span>' if ws and we else (f'<span class="win">from {ws}</span>' if ws else ""))
        dsc = esc(r.get("description") or "")
        cov_items += f'<li><div class="loc">{loc}</div>{win}{f"<div class=\"dsc\">{dsc}</div>" if dsc else ""}</li>'
    covered = f'<ul class="covered">{cov_items}</ul>'
    # conditions
    cond_html=""
    if conds:
        names = [esc(c.get("name")) for c in conds]
        cells = "".join(f"<span>{n}</span>" for n in names)
        seen_sl = []
        for c in conds:
            sl = COND_SLUG.get(str(c.get("dc") or ""))
            if sl and sl not in seen_sl: seen_sl.append(sl); 
        links = ", ".join(f'<a href="/conditions/{sl}.html">{esc(next(x.get("name") for x in conds if COND_SLUG.get(str(x.get("dc") or "")) == sl).lower())}</a>' for sl in seen_sl)
        cond_html = (f'<h2>Presumptive conditions ({len(conds)})</h2>'
                     f'<p>With a qualifying diagnosis and the service above, VA presumes these conditions are connected to the exposure.</p>'
                     f'<div class="condgrid">{cells}</div>'
                     + (f'<p>Rating tables: {links}.</p>' if links else ''))
    # docs
    doc_html=""
    if docs:
        def _lc1(t): t = str(t or ""); return t[:1].lower() + t[1:] if t[:2].upper() != t[:2] else t
        items="".join(f'<li>{esc(d.get("type"))}: {esc(_lc1(d.get("why")))}</li>' for d in docs)
        doc_html = f'<h2>Documents VA asks for</h2><ul class="docs">{items}</ul>'
    bc=[{"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"Toxic exposures","item":"https://vareadyapp.com/exposures.html"},
        {"@type":"ListItem","position":3,"name":topic,"item":canon}]
    lds=[{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":bc},
         {"@context":"https://schema.org","@type":"Article","headline":h1,"description":desc,"datePublished":"2026-06-09","dateModified":"2026-06-09","author":{"@type":"Organization","name":"JDL Software LLC"},"publisher":{"@type":"Organization","name":"VA Ready"},"mainEntityOfPage":canon,"inLanguage":"en-US"}]
    lds_html="\n".join(f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in lds)
    auth_html = f'<h2>Legal authority and sources</h2><p style="color:var(--gray);font-size:14px;">{esc(authority)}</p>' if authority else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(topic)}: VA presumptive conditions and claims | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="{esc(h1)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
{lds_html}
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/exposures.html">Toxic exposures</a> / {esc(topic)}</div>
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
    <article>
        <h2>Who is covered</h2>
        <p>{"Qualifying locations and dates under the PACT Act:" if is_pact else "Exposures and service VA recognizes:"}</p>
        {covered}
        {cond_html}
        <p class="trustline">To see how these conditions combine with others, use the <a href="/va-disability-calculator.html">combined-rating calculator</a>.</p>
        {doc_html}
        <p class="trustline">Related guides: <a href="/guides/intent-to-file.html">Intent to File</a> &middot; <a href="/guides/c-and-p-exam-preparation.html">C&amp;P exam preparation</a> &middot; <a href="/guides/nexus-letters.html">nexus letters</a></p>
        {auth_html}
    </article>
    {APP_CTA}
    <p class="trustline">More from VA Ready: <a href="/exposures.html">all toxic exposures</a> &middot; <a href="/conditions.html">ratings by condition</a> &middot; <a href="/va-disability-pay-rates.html">pay rates</a></p>
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
        topic=TOPICS.get(slug) or re.split(r"[.:]", h1)[0].split("(")[0].strip()
        sub=(f'{nc} presumptive conditions' if nc else 'No presumptive list') + (' &middot; PACT Act' if pact else '')
        cards+=f'<div class="hub-card"><a href="/exposures/{slug}.html">{esc(topic)}</a><p>{sub}</p></div>'
    desc="Military toxic exposures and VA presumptive conditions: Agent Orange, burn pits & the PACT Act, Camp Lejeune, Gulf War Illness, AFFF/PFAS, K2, asbestos, and radiation. Who qualifies and how to file."
    bc={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},{"@type":"ListItem","position":2,"name":"Toxic exposures","item":canon}]}
    items={"@context":"https://schema.org","@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"https://vareadyapp.com/exposures/{s}.html","name":h} for i,(s,h,l,m) in enumerate(PAGES)]}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Military toxic exposures and VA presumptive conditions | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="Military toxic exposures and VA presumptive conditions"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<script type="application/ld+json">{json.dumps(bc)}</script>
<script type="application/ld+json">{json.dumps(items)}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / Toxic exposures</div>
    <h1>Military toxic exposures and presumptive conditions</h1>
    <p class="lede">For veterans exposed to certain toxic substances in service, VA presumes some conditions are service-connected, so you do not have to prove the link. Pick an exposure to see who qualifies, the presumptive conditions, and the documents VA asks for.</p>

    <div class="hub-sec"><h2>Exposures by topic</h2><div class="hub-grid">{cards}</div></div>
    {APP_CTA}
    <p class="trustline">More from VA Ready: <a href="/conditions.html">ratings by condition</a> &middot; <a href="/mos.html">VA disability by MOS</a> &middot; <a href="/va-disability-pay-rates.html">pay rates</a> &middot; <a href="/states.html">state benefits</a></p>
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
