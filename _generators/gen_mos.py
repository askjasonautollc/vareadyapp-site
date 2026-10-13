#!/usr/bin/env python3
"""MOS / AFSC / rating pages (/mos/<code>.html) + /mos.html hub, from mos_profiles.

Governing rule: the page gives the GENERIC, category-level answer for a job
(typical exposures, commonly associated conditions, the location-based PACT
note) and stops at the personalization line. No combined rating, no merging of
several MOS, no base/ship/aircraft cross-reference, no claim list. That is the
app's job and the reason to download it.

The VA keeps no per-MOS list of conditions. Copy must never imply it does.

pact_conditions from mos_profiles is deliberately NOT rendered: it carries
loose labels such as "Any cancer". The PACT note below is the location-based
list already verified vs VA.gov on /exposures/burn-pits-pact-act.html.
"""
import json, re, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
OUT = os.path.join(SITE, "mos")
os.makedirs(OUT, exist_ok=True)
def esc(s): return html.escape(str(s) if s is not None else "", quote=True)

ROWS = json.load(open(os.path.join(HERE, "data", "mos_profiles.json")))
N_PROFILES = len(ROWS)

# Phase 1: highest-population jobs. (code, branch). Codes shared by two branches
# (BM, IT, GM, OS, ET) are left out until the URL scheme handles the collision.
PHASE1 = [
 ("11B","Army"),("11C","Army"),("68W","Army"),("13F","Army"),("13B","Army"),("19K","Army"),
 ("19D","Army"),("12B","Army"),("31B","Army"),("88M","Army"),("91B","Army"),("92A","Army"),
 ("92F","Army"),("92Y","Army"),("92G","Army"),("25B","Army"),("25U","Army"),("15T","Army"),
 ("15R","Army"),("35F","Army"),("42A","Army"),("74D","Army"),
 ("0311","Marine Corps"),("0331","Marine Corps"),("0341","Marine Corps"),("0811","Marine Corps"),
 ("3531","Marine Corps"),("0621","Marine Corps"),
 ("3E8X1","Air Force"),("2A5X1","Air Force"),("3P0X1","Air Force"),("2W1X1","Air Force"),
 ("4N0X1","Air Force"),("2F0X1","Air Force"),("2A3X3","Air Force"),("1N0X1","Air Force"),
 ("HM","Navy"),("AM","Navy"),("AD","Navy"),("MA","Navy"),("ABH","Navy"),("EN","Navy"),
 ("AO","Navy"),("MM","Navy"),
]
BRANCH_ORDER = ["Army","Marine Corps","Navy","Air Force"]
CODE_WORD = {"Army":"MOS","Marine Corps":"MOS","Air Force":"AFSC","Navy":"rating"}
MEMBER = {"Army":"soldiers","Marine Corps":"Marines","Air Force":"Airmen","Navy":"Sailors"}

# dc -> published condition page (same map as gen_exposures.py)
COND_SLUG = {"6260":"tinnitus","9411":"ptsd","5237":"back-pain","5260":"knee-pain","6847":"sleep-apnea",
"8100":"migraines","9434":"depression","5003":"arthritis","5201":"shoulder","5271":"ankle",
"5257":"knee-instability","7806":"eczema","6602":"asthma","8520":"sciatica","5242":"degenerative-disc-disease",
"6100":"hearing-loss","7101":"hypertension","7346":"gerd-acid-reflux","7913":"diabetes","7805":"scars"}

# Raw exposure keys -> plain-language category. Order here is display order.
CATS = [
 ("noise","Hazardous noise","Weapons fire, engines, aircraft, generators, or machinery at levels linked to tinnitus and hearing loss.",None,
  {"noise","noise exposure","weapons noise","aircraft noise","extreme noise","construction noise","headset noise","hearing_loss_noise","jet blast","engine_test","flightline"}),
 ("blast","Blast and overpressure","Explosions, artillery, breaching, and demolitions. Repeated blast exposure is tied to concussion, headaches, and hearing damage.",None,
  {"blast","blast_overpressure","blast overpressure","explosives","demolitions","explosive compounds","ordnance chemicals","propellant residue","propellant fumes","propellant_gases","propellants"}),
 ("combat","Combat and traumatic stress","Firefights, casualties, mass-casualty care, and sustained threat, the kind of experience behind PTSD and depression claims.",None,
  {"combat","combat stress","psychological_trauma","secondary_trauma","psychological_stress","chronic_stress","stress","detainee operations"}),
 ("loads","Heavy loads and impact","Rucks, body armor, lifting, carrying patients or ammunition, and hard landings that wear on the back, knees, and feet.",None,
  {"heavy_lifting","heavy load bearing","lifting","parachute","parachute_operations","heavy rigging","protective_gear","falls","physical training","heavy_equipment"}),
 ("strain","Repetitive strain, vibration, and posture","The same motion thousands of times, long hours seated in vehicles or at a console, or constant vibration from vehicles and tools.",None,
  {"repetitive_strain","ergonomic_strain","vibration","vehicle_vibration","sedentary","sedentary_strain","sedentary duty","prolonged_standing","prolonged_sitting","screen_strain"}),
 ("burn","Burn pits and airborne hazards","Smoke and fine particulate from open-air burn pits, dust, and sand during Southwest Asia and post-9/11 deployments.","/exposures/burn-pits-pact-act.html",
  {"burn_pits","smoke","particulates","dust","smoke_residue","combustion_byproducts"}),
 ("fuel","Fuels, exhaust, and petroleum products","JP-8, JP-5, diesel, turbine oil, and engine exhaust handled or breathed on the job.","/exposures/jet-fuel-petroleum.html",
  {"jp8_fuel","jp5_fuel","jet_fuel","jp8","fuel","fuel_vapors","fuel fumes","petroleum","petroleum_products","aviation_fuel","jet_fuel_petroleum","turbine_oil","turbine oil","turbine lubricants","diesel_exhaust","exhaust","engine exhaust","jet exhaust","vehicle exhaust","vehicle_diesel_exhaust","diesel_generator_exhaust","fuel oil","marine fuel","forklift exhaust","fuel_exhaust","lubricants"}),
 ("chem","Chemicals and solvents","Solvents, degreasers, paints, cleaning agents, and other industrial chemicals used in the field, the shop, or on the line.",None,
  {"chemicals","solvents","carc","hydraulic_fluid","hydraulic_fluids","deicing","deicing_chemicals","shipboard_chemicals","shipboard_solvents","cleaning agents","cleaning chemicals","chemical cleaning agents","sealants","composites","isocyanates","paints","refrigerants","detergents","disinfectants","chemical_agents","decontamination_agents","weapons_lubricants","chemical_biological_radiological_nuclear","hazmat","fumes","aerosols"}),
 ("metal","Lead, metals, and welding fumes","Lead from firing ranges and solder, heavy metals, and welding or metal fumes.",None,
  {"lead","lead_solder","lead solder","heavy_metals","welding_fumes","welding smoke","metal fumes","metal_dust","metal dust","chromium","beryllium"}),
 ("asb","Asbestos","Older ships, buildings, brake and insulation work.","/exposures/asbestos.html",
  {"asbestos","shipboard asbestos"}),
 ("afff","AFFF firefighting foam (PFAS)","Aqueous film-forming foam used on flight lines, in hangars, and in firefighting training.","/exposures/afff-pfas.html",
  {"afff_pfas","afff_foam","PFAS"}),
 ("rad","Radiation","Ionizing radiation sources, or radio-frequency energy from radar and transmitters, depending on the duty.","/exposures/radiation.html",
  {"radiation","ionizing_radiation","ionizing_radiation_occupational","depleted_uranium"}),
 ("rf","Radio-frequency and electromagnetic energy","Radar, antennas, and high-power transmitters.",None,
  {"rf_radiation","electromagnetic_fields","radar","radar emissions","rf_emf","rf_microwave_radiation","microwave radiation","microwave_radiation"}),
 ("bio","Bloodborne pathogens and clinical hazards","Needlesticks, blood and body fluids, infectious disease, latex, and disinfectants in medical work.",None,
  {"bloodborne","blood_borne_pathogens","bloodborne_pathogens","infectious_disease","biological_hazards","biological_agents","biological","latex","pharmaceuticals","anesthetic_gases","medical chemicals"}),
 ("heat","Heat and cold","Hot flight lines, engine rooms, galleys, desert operations, and cold-weather training.",None,
  {"heat","heat_injury","heat_stress","cold","cold_injury","cold_weather","extreme_weather","weather","weather exposure"}),
 ("sleep","Sleep disruption and shift work","Rotating shifts, night operations, and long watches.",None,
  {"sleep_disruption","shift_work"}),
]
KEY2CAT = {k: c[0] for c in CATS for k in c[4]}

PREV_LBL = {"high":"Frequently claimed","moderate":"Also commonly claimed","low":"Sometimes claimed"}
PREV_RANK = {"high":0,"moderate":1,"low":2}

def slug(code): return code.lower()

def find(code, branch):
    rs = [r for r in ROWS if r["mos_code"] == code and r["branch"] == branch]
    if len(rs) != 1: raise SystemExit(f"expected one row for {code}/{branch}, got {len(rs)}")
    return rs[0]

PAGES = [find(c, b) for c, b in PHASE1]

# ---------- shared chrome, read from gen_guides.py / gen_conditions.py ----------
gtext = open(os.path.join(HERE, "gen_guides.py")).read()
CSS = re.search(r'CSS = """(.*?)"""', gtext, re.S).group(1)
ctext = open(os.path.join(HERE, "gen_conditions.py")).read()
NAV = re.search(r'NAV = """(.*?)"""', ctext, re.S).group(1)
FOOTER = re.search(r'FOOTER = """(.*?)"""', ctext, re.S).group(1)
CSS += """
    .pillrow { display:flex; flex-wrap:wrap; gap:4px 18px; margin:6px 0 16px; }
    .pillrow a { font-size:15px; padding:8px 0; }
    .trustline { font-size:14.5px; color:var(--tan); margin:14px 0 4px; max-width:68ch; }
    ul.xlist, ul.clist { list-style:none; padding:0; margin:8px 0 18px; max-width:none; }
    ul.xlist li, ul.clist li { border-top:1px solid var(--line); padding:12px 0; margin:0; }
    ul.xlist li .cn, ul.clist li .cn { color:var(--white); font-weight:700; }
    ul.xlist li p, ul.clist li p { color:var(--tan); font-size:15px; margin:4px 0 0; }
    ul.clist li .cn a { color:var(--white); }
    ul.clist li .dc { color:var(--gray); font-size:13px; font-weight:400; margin-left:6px; }
    .ctag { font-size:13px; color:var(--gray); margin-left:8px; }
    .xlink { font-size:14px; }
    .pact { border-top:1px solid var(--line); padding-top:6px; margin:26px 0; }
    .pact h2 { font-size:22px; font-weight:800; margin:18px 0 10px; line-height:1.3; }
    .pact p { color:var(--tan); max-width:68ch; margin-bottom:14px; }
    .branch-h { font-size:21px; font-weight:800; margin:30px 0 6px; }
    .page-cta { margin:26px 0; }
    table.rt { width:100%; border-collapse:collapse; margin:8px 0 18px; }
    table.rt th, table.rt td { text-align:left; padding:11px 12px; border-bottom:1px solid var(--line); font-size:15px; vertical-align:top; color:var(--tan); }
    table.rt th { color:var(--gray); font-size:13px; font-weight:600; }
    table.rt td.pct { color:var(--white); font-weight:700; width:74px; font-variant-numeric:tabular-nums; }
    .wrap > p:not(.lede):not(.note):not(.trustline) { color:var(--tan); margin:0 0 14px; max-width:68ch; }
"""

APP_CTA = """<div class="cta cta-line"><p>Claim Intel in <a href="https://apps.apple.com/app/id6761733758">VA Ready for iOS</a> and <a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US">Vet Ready for Android</a> is a Pro feature that merges the conditions from every job you held and cross-references your exposures; the combined-rating calculator is free.</p></div>"""
DISCLAIMER = """<div class="disclaimer">This page is for general informational purposes only and is not legal or medical advice. It describes what a job typically involved, not what any one veteran experienced, and the VA does not keep a list of conditions by MOS, AFSC, or rating. The VA decides service connection and ratings from your own records, evidence, and exam. VA Ready is not affiliated with the U.S. Department of Veterans Affairs. For free help filing, work with a <a href="/find-a-vso.html">VA-accredited VSO</a>.</div>"""

ORG_ID = "https://vareadyapp.com/#organization"

def exposures_for(r):
    seen = []
    for k in r.get("exposures") or []:
        c = KEY2CAT.get(k)
        if c and c not in seen: seen.append(c)
    order = [c[0] for c in CATS]
    return [next(c for c in CATS if c[0] == k) for k in sorted(seen, key=order.index)]

def conditions_for(r):
    cs = list(r.get("common_conditions") or [])
    out, dcs = [], set()
    for i, c in sorted(enumerate(cs), key=lambda t: (PREV_RANK.get(t[1].get("prevalence"), 3), t[0])):
        if c["dc"] in dcs: continue
        dcs.add(c["dc"]); out.append(c)
    return out

def cond_name_html(c):
    nm = esc(c["name"])
    sl = COND_SLUG.get(c["dc"])
    return f'<a href="/conditions/{sl}.html">{nm}</a>' if sl else nm

# Plain names for running prose, where the schedule-style names ("Knee,
# limitation of flexion") read badly inside a comma list.
PLAIN = {"6260":"tinnitus","6100":"hearing loss","9411":"PTSD","5237":"back or neck strain",
"5260":"limited knee flexion","5257":"knee instability","8520":"sciatica","5271":"limited ankle motion",
"8100":"migraines","5201":"limited shoulder motion","7806":"eczema or dermatitis","6847":"sleep apnea",
"9434":"depression","5003":"degenerative arthritis","5284":"foot injuries","6602":"asthma",
"7101":"hypertension","8515":"carpal tunnel syndrome","6600":"chronic bronchitis","8045":"TBI residuals",
"5010":"post-traumatic arthritis","5206":"limited elbow motion","6522":"allergic rhinitis","7800":"head, face, or neck scars"}

def short_names(conds, n):
    return [PLAIN.get(c["dc"], c["name"].lower()) for c in conds[:n]]

def join_words(xs):
    xs = list(xs)
    if len(xs) <= 1: return "".join(xs)
    return ", ".join(xs[:-1]) + ", and " + xs[-1]

def page(r):
    code, title, br = r["mos_code"], r["mos_title"], r["branch"]
    word = CODE_WORD[br]
    url = f"/mos/{slug(code)}.html"; canon = f"https://vareadyapp.com{url}"
    xs = exposures_for(r)
    cs = conditions_for(r)
    pact = bool(r.get("pact_presumptive_eligible"))
    xnames = [x[1].lower() for x in xs[:4]]
    top = short_names(cs, 4)

    label = f"{code} {title}"
    page_title = f"VA disability for {esc(label)}: common conditions and presumptives | VA Ready"
    desc = (f"{label} VA disability: the exposures this {br} {word} typically carried, the conditions "
            f"commonly claimed, and the PACT Act presumptive rules.")
    if len(desc) > 160: desc = desc[:157].rsplit(" ", 1)[0] + "..."

    def lc(n): return " ".join(w if re.sub(r'[^A-Za-z]', '', w).isupper() and len(re.sub(r'[^A-Za-z]', '', w)) >= 2 else w.lower() for w in n.split())
    xlinks = [(f'<a href="{lnk}">{esc(lc(n))}</a>' if lnk else esc(lc(n))) for _, n, d, lnk, _ in xs]
    if xlinks:
        intro_html = f"{esc(br)} {esc(word)}. The job usually meant {join_words(xlinks)}."
    else:
        intro_html = f"{esc(br)} {esc(word)}."

    c_html = "".join(
        f'<li><span class="cn">{esc(c["name"])}</span><span class="dc">DC {esc(c["dc"])}</span>'
        f'<span class="ctag">{PREV_LBL.get(c.get("prevalence"), "Commonly claimed")}</span>'
        f'<p>{esc(c.get("reason"))}</p></li>' for c in cs)

    linked = [c for c in cs if COND_SLUG.get(c["dc"])]
    if linked:
        links = join_words([f'<a href="/conditions/{COND_SLUG[c["dc"]]}.html">{esc(PLAIN.get(c["dc"], c["name"].lower()))}</a>' for c in linked])
        c_links = f'<p>Rating tables: {links}.</p>'
    else:
        c_links = ""

    if pact:
        pact_html = f"""<div class="pact">
        <h2>PACT Act presumptives</h2>
        <p>Many {MEMBER[br]} in this job deployed to Southwest Asia or the post-9/11 theater. Under the PACT Act, the presumption is based on where and when you served, not on your job title, and holding this job does not by itself mean you have a presumptive condition.</p>
        <p>See the full <a class="xlink" href="/exposures/burn-pits-pact-act.html">PACT Act burn pit list and locations</a> and the <a class="xlink" href="/exposures/gulf-war-illness.html">Gulf War Illness page</a>.</p>
    </div>"""
    else:
        pact_html = f"""<div class="pact">
        <h2>Presumptive conditions</h2>
        <p>Presumptive service connection depends on where and when you served, not on your job title. Earlier eras carry their own location-based presumptives, such as <a class="xlink" href="/exposures/agent-orange.html">Agent Orange</a> and <a class="xlink" href="/exposures/camp-lejeune.html">Camp Lejeune</a> water contamination. The <a class="xlink" href="/exposures.html">toxic exposures page</a> lists the locations and dates that qualify.</p>
    </div>"""

    same = [p for p in PAGES if p["branch"] == br and p["mos_code"] != code]
    others = "".join(f'<a href="/mos/{slug(p["mos_code"])}.html">{esc(p["mos_code"])} {esc(p["mos_title"])}</a>' for p in same)

    bc_ld = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"VA disability by MOS","item":"https://vareadyapp.com/mos.html"},
        {"@type":"ListItem","position":3,"name":f"{code} {title}","item":canon}]})
    art_ld = json.dumps({"@context":"https://schema.org","@type":"Article",
        "headline":f"VA disability for {label}","description":desc,"datePublished":"2026-10-07",
        "author":{"@type":"Organization","name":"JDL Software LLC"},
        "publisher":{"@type":"Organization","@id":ORG_ID,"name":"VA Ready","url":"https://vareadyapp.com/"},
        "mainEntityOfPage":canon,"inLanguage":"en-US"})

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="VA disability for {esc(label)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<script type="application/ld+json">{bc_ld}</script>
<script type="application/ld+json">{art_ld}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/mos.html">VA disability by MOS</a> / {esc(code)}</div>
    <h1>VA disability for {esc(label)}</h1>
    <p class="lede">{intro_html}</p>
    <article>
        <h2>Conditions veterans in this job claim</h2>
        <ul class="clist">{c_html}</ul>
        {c_links}
    </article>
    {pact_html}
    <p class="note">Which conditions fit you, how they combine, and what they rate together depends on your full record: every job you held, your bases, ships and aircraft.</p>
    {APP_CTA}
    <div class="btns page-cta"><a href="/va-disability-calculator.html" class="btn">Combined-rating calculator</a><a href="/find-a-vso.html" class="btn ghost">Find an accredited VSO</a></div>
    <h2 style="font-size:20px;margin-top:30px;">Other {esc(br)} jobs</h2>
    <div class="pillrow">{others}</div>
    <p class="trustline">More from VA Ready: <a href="/mos.html">all MOS pages</a> &middot; <a href="/conditions.html">ratings by condition</a> &middot; <a href="/exposures.html">toxic exposures</a></p>
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""

_COND = {c["diagnostic_code"]: c for c in json.load(open(os.path.join(HERE, "data", "conditions.json")))}

def top_two(p):
    out = []
    for c in conditions_for(p)[:2]:
        nm = PLAIN.get(c["dc"], c["name"].lower())
        nm = nm[:1].upper() + nm[1:] if not out else nm
        m = (_COND.get(c["dc"]) or {}).get("max_rating")
        out.append(f"{nm} {m}%" if m else nm)
    return ", ".join(out)

def hub():
    secs = ""
    for br in BRANCH_ORDER:
        ps = [p for p in PAGES if p["branch"] == br]
        if not ps: continue
        rows = "".join(
            f'<tr><td><a href="/mos/{slug(p["mos_code"])}.html">{esc(p["mos_code"])} {esc(p["mos_title"])}</a></td>'
            f'<td>{esc(top_two(p))}</td><td class="pct">{len(conditions_for(p))}</td></tr>' for p in ps)
        tbl = ('<div class="tbl-wrap"><table class="rt"><thead><tr><th>Job</th><th>Most claimed, highest rating</th>'
               f'<th>Listed</th></tr></thead><tbody>{rows}</tbody></table></div>')
        secs += f'<div class="hub-sec"><h2 class="branch-h">{esc(br)} {"ratings" if br == "Navy" else ("AFSCs" if br == "Air Force" else "MOS")}</h2>{tbl}</div>'
    desc = "VA disability by military job: typical exposures, commonly claimed conditions, and PACT Act notes for 11B, 68W, 0311, Navy ratings, Air Force AFSCs, and more."
    bc = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"VA disability by MOS","item":"https://vareadyapp.com/mos.html"}]})
    items = json.dumps({"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"url":f"https://vareadyapp.com/mos/{slug(p['mos_code'])}.html","name":f"{p['mos_code']} {p['mos_title']}"}
        for i, p in enumerate(PAGES)]})
    n_fmt = f"{N_PROFILES:,}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VA disability by MOS, AFSC and rating: common conditions | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="https://vareadyapp.com/mos.html">
<meta property="og:type" content="website"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="VA disability by MOS, AFSC and rating"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="https://vareadyapp.com/mos.html"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<script type="application/ld+json">{bc}</script>
<script type="application/ld+json">{items}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / VA disability by MOS</div>
    <h1>VA disability by MOS, AFSC, and rating</h1>
    <p class="lede">What each job typically exposed people to, and the conditions veterans who held it commonly claim. The VA does not keep a list of conditions by job, so these pages show the general pattern. Your own claim rests on your record.</p>
    <p class="note">This page covers {len(PAGES)} common jobs. The app carries {n_fmt} MOS, AFSC, rating, and designator profiles across every branch, including legacy codes.</p>
    {secs}
    <p class="trustline">More from VA Ready: <a href="/conditions.html">ratings by condition</a> &middot; <a href="/exposures.html">toxic exposures</a> &middot; <a href="/va-disability-calculator.html">combined-rating calculator</a></p>
    {APP_CTA}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""

for p in PAGES:
    open(os.path.join(OUT, slug(p["mos_code"]) + ".html"), "w").write(page(p))
open(os.path.join(SITE, "mos.html"), "w").write(hub())

# unmapped exposure keys are dropped silently from the page; surface them here
unmapped = sorted({k for p in PAGES for k in (p.get("exposures") or []) if k not in KEY2CAT})

sp = os.path.join(SITE, "sitemap.xml"); xml = open(sp).read(); new = []
for u, pr in [("https://vareadyapp.com/mos.html","0.8")] + [(f"https://vareadyapp.com/mos/{slug(p['mos_code'])}.html","0.7") for p in PAGES]:
    if u not in xml:
        new.append(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-10-07</lastmod>\n    <priority>{pr}</priority>\n  </url>')
if new:
    xml = xml.replace("</urlset>", "\n".join(new) + "\n</urlset>")
    open(sp, "w").write(xml)
print(f"wrote {len(PAGES)} MOS pages + hub; sitemap +{len(new)}; unmapped exposure keys: {unmapped}")
