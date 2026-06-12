#!/usr/bin/env python3
import json, re, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
COND_DIR = os.path.join(SITE, "conditions")
os.makedirs(COND_DIR, exist_ok=True)
DATA = {c["diagnostic_code"]: c for c in json.load(open(os.path.join(HERE,"data","conditions.json")))}
STUDIES = json.load(open(os.path.join(HERE,"data","studies.json"))) if os.path.exists(os.path.join(HERE,"data","studies.json")) else {}

# DC -> (slug, friendly H1 name, intro lede). Order = most-claimed.
META = [
 ("6260","tinnitus","Tinnitus","Tinnitus &mdash; a persistent ringing, buzzing, or hissing in the ears &mdash; is the single most-claimed VA disability, common after exposure to loud weapons, aircraft, and engine noise."),
 ("9411","ptsd","PTSD","Post-traumatic stress disorder is one of the most-claimed VA mental-health conditions, rated on how much the symptoms impair your work and daily functioning."),
 ("5237","back-pain","Back Pain (Lumbosacral Strain)","Lower-back and neck strain is among the most-claimed VA conditions, rated primarily on your range of motion and flare-ups."),
 ("5260","knee-pain","Knee Pain (Limited Flexion)","Limited knee bending is one of the most-claimed VA joint conditions, rated on how far you can flex the joint."),
 ("6847","sleep-apnea","Sleep Apnea","Sleep apnea is a high-value VA claim &mdash; a CPAP requirement alone rates 50%. It is frequently service-connected, including as secondary to PTSD, sinus, or weight conditions."),
 ("8100","migraines","Migraines","Migraines are rated by how often you get prostrating attacks and whether they interfere with your ability to work."),
 ("9434","depression","Depression (MDD)","Major depressive disorder is rated on occupational and social impairment, using the same scale as other VA mental-health conditions."),
 ("5003","arthritis","Arthritis (Degenerative)","Degenerative arthritis is rated on X-ray joint involvement and the limitation of motion it causes."),
 ("5201","shoulder","Shoulder / Arm Limitation","Limited shoulder and arm motion is rated by how high you can raise the arm, with higher ratings for the dominant side."),
 ("5271","ankle","Ankle (Limited Motion)","Limited ankle motion is rated as moderate or marked based on how restricted the joint is."),
 ("5257","knee-instability","Knee Instability","Knee instability &mdash; buckling, giving way, or recurrent subluxation &mdash; is rated separately from limited motion, so many veterans can claim both."),
 ("7806","eczema","Eczema / Dermatitis","Eczema and dermatitis are rated on how much body or exposed skin is affected and the treatment required."),
 ("6602","asthma","Asthma","Bronchial asthma is rated on your pulmonary function tests (FEV-1) and the medication you require."),
 ("8520","sciatica","Sciatica","Sciatic-nerve radiculopathy is a common secondary to back conditions, rated by the severity of the nerve impairment &mdash; and it qualifies for the bilateral factor when it affects both legs."),
 ("5242","degenerative-disc-disease","Degenerative Disc Disease (Spine)","Degenerative disc disease and spinal arthritis are rated on range of motion or incapacitating episodes, whichever gives the higher rating."),
 ("6100","hearing-loss","Hearing Loss","Bilateral sensorineural hearing loss is rated from a table that combines your audiogram results and speech-recognition scores."),
 ("7101","hypertension","Hypertension","High blood pressure is rated on your diastolic and systolic readings and whether you require continuous medication."),
 ("7346","gerd-acid-reflux","GERD / Acid Reflux","GERD and hiatal hernia are rated on symptoms like reflux, regurgitation, and pain, and are a frequent secondary to other conditions and medications."),
 ("7913","diabetes","Diabetes (Type 2)","Type 2 diabetes is rated on the treatment it requires &mdash; diet, oral medication, insulin, and activity restriction &mdash; and is an Agent Orange presumptive condition."),
 ("7805","scars","Scars","Scars are rated on their size, whether they are painful or unstable, and any functional limitation they cause &mdash; and can be claimed in addition to the underlying injury."),
]

def esc(s): return html.escape(s or "", quote=True)

# Map secondary-condition names to our existing condition pages (most specific rule first).
VALID_SLUGS = {sl for _, sl, *_ in META}
SEC_RULES = [
 ("knee instability","knee-instability"),("instability","knee-instability"),
 ("degenerative disc","degenerative-disc-disease"),("disc disease","degenerative-disc-disease"),
 ("herniat","degenerative-disc-disease"),("ivds","degenerative-disc-disease"),
 ("sleep apnea","sleep-apnea"),("post-traumatic","ptsd"),("ptsd","ptsd"),
 ("major depress","depression"),("depress","depression"),("migraine","migraines"),
 ("tinnitus","tinnitus"),("hearing loss","hearing-loss"),("sciatic","sciatica"),
 ("lumbosacral","back-pain"),("lumbar strain","back-pain"),("low back","back-pain"),("back strain","back-pain"),
 ("hypertension","hypertension"),("blood pressure","hypertension"),
 ("gerd","gerd-acid-reflux"),("acid reflux","gerd-acid-reflux"),("reflux","gerd-acid-reflux"),
 ("diabet","diabetes"),("eczema","eczema"),("dermatitis","eczema"),("asthma","asthma"),
 ("shoulder","shoulder"),("ankle","ankle"),("scar","scars"),("knee","knee-pain"),("arthritis","arthritis"),
]
def sec_pill(name, current):
    n = (name or "").lower()
    for kw, sl in SEC_RULES:
        if kw in n and sl in VALID_SLUGS and sl != current:
            return f'<a href="/conditions/{sl}.html">{esc(name)}</a>'
    return f'<span>{esc(name)}</span>'

CSS = open(os.path.join(HERE,"css.txt")).read() if os.path.exists(os.path.join(HERE,"css.txt")) else ""
# Reuse the guide stylesheet by importing the constant from the guide generator.
import importlib.util
spec = importlib.util.spec_from_file_location("gguides", os.path.join(HERE,"gen_guides.py"))
# guide gen.py runs on import (writes files); avoid that — instead read its CSS via regex.
gtext = open(os.path.join(HERE,"gen_guides.py")).read()
m = re.search(r'CSS = """(.*?)"""', gtext, re.S)
CSS = m.group(1) if m else ""
# add condition-specific styles
CSS += """
    table.rt { width:100%; border-collapse:collapse; margin:8px 0 18px; }
    table.rt th, table.rt td { text-align:left; padding:11px 12px; border-bottom:1px solid var(--line); font-size:15px; vertical-align:top; }
    table.rt th { color:var(--gold); font-size:12px; text-transform:uppercase; letter-spacing:1px; }
    table.rt td.pct { color:var(--white); font-weight:800; white-space:nowrap; width:74px; }
    table.rt td { color:var(--tan); }
    .pillrow { display:flex; flex-wrap:wrap; gap:8px; margin:6px 0 16px; }
    .pillrow a, .pillrow span { font-size:13px; background:var(--card); border:1px solid var(--line); color:var(--tan); padding:6px 12px; border-radius:999px; }
    .evidence { margin:30px 0 8px; }
    .evidence > p.evintro { color:var(--tan); margin:2px 0 18px; }
    ol.evlist { list-style:none; counter-reset:ev; padding:0; margin:0; }
    ol.evlist > li.evi { position:relative; background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px 18px 16px 18px; margin:0 0 14px; }
    .evi-top { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin-bottom:7px; }
    .evi-type { font-size:11px; text-transform:uppercase; letter-spacing:.8px; color:var(--gold); border:1px solid var(--line); border-radius:999px; padding:3px 9px; }
    .evi-rel { font-size:11px; text-transform:uppercase; letter-spacing:.5px; padding:3px 9px; border-radius:999px; }
    .rel-primary { background:rgba(201,162,77,.16); color:var(--gold); }
    .rel-supporting { background:rgba(255,255,255,.06); color:var(--tan); }
    .rel-tangential { background:rgba(255,255,255,.04); color:var(--gray); }
    .evi-yr { margin-left:auto; color:var(--gray); font-size:13px; font-weight:700; }
    a.evi-title { display:block; color:var(--white); font-weight:700; font-size:16px; line-height:1.4; text-decoration:none; margin-bottom:3px; }
    a.evi-title:hover { color:var(--gold); }
    .evi-jrnl { color:var(--gray); font-size:13px; font-style:italic; margin-bottom:8px; }
    ul.evi-find { margin:6px 0 8px; padding-left:18px; }
    ul.evi-find li { color:var(--tan); font-size:14.5px; margin-bottom:4px; }
    .evi-why { color:var(--tan); font-size:14.5px; margin:6px 0 10px; }
    .evi-why strong { color:var(--white); }
    a.evi-link { display:inline-block; font-size:13px; font-weight:700; color:var(--gold); text-decoration:none; }
    a.evi-link:hover { text-decoration:underline; }
    .evi-foot { color:var(--gray); font-size:13px; margin:14px 0 4px; }
    .trustline { font-size:13.5px; color:var(--tan); background:var(--card); border:1px solid var(--line); border-left:3px solid var(--gold); border-radius:10px; padding:9px 13px; margin:14px 0 4px; }
    .trustline a { color:var(--gold); font-weight:700; text-decoration:none; }
    .trustline a:hover { text-decoration:underline; }
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
    <h3>Rate this condition in the VA Ready app</h3>
    <p>Free, no account: pick this condition, see the exact 38 CFR criteria, and watch your combined rating update with real VA math &mdash; plus the 50+ filing guides and a personalized timeline.</p>
    <div class="cta-pro"><span class="pro-pill">With Pro</span><p>Walk away with a <strong>VSO-ready Claim Summary PDF</strong> (peer-reviewed evidence appendix), an <strong>Exposure Profile PDF</strong> of every presumptive your service earned, and the full criteria for all 755 conditions.</p></div>
    <div class="btns"><a href="https://apps.apple.com/app/id6761733758" class="btn">Get VA Ready for iOS</a><a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US" class="btn ghost">Get Vet Ready for Android</a></div>
</div>"""
DISCLAIMER = """<div class="disclaimer">This page is for general informational purposes only and is not legal or medical advice. Rating criteria are summarized from 38 CFR Part 4; the VA determines actual ratings based on your evidence and exam. VA Ready is not affiliated with the U.S. Department of Veterans Affairs. Always verify current criteria at VA.gov and consult a VA-accredited representative.</div>"""

def rating_table(crit):
    rows = sorted(crit, key=lambda x: -int(x.get("percentage", 0)))
    body = "".join(f'<tr><td class="pct">{int(r["percentage"])}%</td><td>{esc(r.get("description",""))}</td></tr>' for r in rows)
    return f'<table class="rt"><thead><tr><th>Rating</th><th>When it applies</th></tr></thead><tbody>{body}</tbody></table>'

REL_LBL = {"primary":"Primary","supporting":"Supporting","tangential":"Background"}
TYPE_LBL = {"meta-analysis":"Meta-analysis","systematic-review":"Systematic review","rct":"Randomized trial",
 "cohort":"Cohort study","case-control":"Case-control","cross-sectional":"Cross-sectional",
 "narrative-review":"Review","clinical-guideline":"Clinical guideline","case-series":"Case series","other":"Study"}

def evidence_section(dc, fname, fclean):
    studs = STUDIES.get(dc) or []
    if not studs: return "", []
    items, cites = [], []
    for s in studs:
        yr = s.get("year") or ""
        tl = TYPE_LBL.get(s.get("type"), "Study")
        rel = s.get("rel") or "supporting"
        rlbl = REL_LBL.get(rel, "Supporting")
        finds = "".join(f"<li>{esc(f)}</li>" for f in (s.get("kf") or []) if f)
        finds_html = f'<ul class="evi-find">{finds}</ul>' if finds else ""
        why = s.get("why") or ""
        why_html = f'<p class="evi-why"><strong>Why it matters:</strong> {esc(why)}</p>' if why else ""
        jrnl = esc(s.get("journal") or "")
        jline = " &middot; ".join([x for x in [jrnl, str(yr)] if x])
        url = esc(s.get("url"))
        items.append(
            f'<li class="evi"><div class="evi-top"><span class="evi-type">{esc(tl)}</span>'
            f'<span class="evi-rel rel-{rel}">{rlbl}</span><span class="evi-yr">{yr}</span></div>'
            f'<a class="evi-title" href="{url}" target="_blank" rel="noopener">{esc(s.get("title"))}</a>'
            f'<div class="evi-jrnl">{jline}</div>{finds_html}{why_html}'
            f'<a class="evi-link" href="{url}" target="_blank" rel="noopener">View on PubMed &#8599;</a></li>')
        cites.append({"@type":"ScholarlyArticle","name":s.get("title"),"url":s.get("url"),
                      "datePublished":str(yr) if yr else None,
                      "publisher":{"@type":"Organization","name":s.get("journal")} if s.get("journal") else None})
    for c in cites:
        for k in [k for k,v in c.items() if v is None]: del c[k]
    html_block = (
        f'<section class="evidence"><h2>Peer-Reviewed Research on {fname}</h2>'
        f'<p class="evintro">{len(studs)} peer-reviewed studies linked to {fclean} (diagnostic code {dc}) in the VA Ready app, '
        f'sourced from PubMed and the U.S. National Library of Medicine. Every citation is real and links to the source &mdash; '
        f'bring them to your C&amp;P exam or hand them to your VSO.</p>'
        f'<ol class="evlist">{"".join(items)}</ol>'
        f'<p class="evi-foot">Citations are provided for general educational use and are not medical advice. '
        f'The VA Ready app pairs every study with its key findings and a one-tap Claim Summary PDF appendix.</p></section>')
    return html_block, cites

def cond_page(dc, slug, fname, intro):
    c = DATA[dc]
    cn, cfr, bsys = c["condition_name"], c.get("cfr_section") or "", c.get("body_system") or ""
    maxr = c.get("max_rating")
    crit = c.get("rating_criteria") or []
    secs = c.get("secondary_conditions") or []
    notes = c.get("notes")
    url = f"/conditions/{slug}.html"; canon = f"https://vareadyapp.com{url}"
    fclean = re.sub("<.*?>", "", fname)
    nstud = len(STUDIES.get(dc) or [])
    stud_bit = f" Plus {nstud} peer-reviewed studies." if nstud else ""
    desc = f"How the VA rates {fclean} (diagnostic code {dc}): the {len(crit)} rating breakpoints, the {cfr} criteria, secondary conditions, and how to claim it.{stud_bit} Free calculator."
    desc = desc[:160]
    secs_html = ""
    if secs:
        pills = "".join(sec_pill(s, slug) for s in secs[:10])
        secs_html = f'<h2>Conditions commonly connected to {fname}</h2><p>{fclean} is frequently claimed alongside, or as a secondary to, these conditions. If you have any of them, they may be separately ratable:</p><div class="pillrow">{pills}</div>'
    notes_html = f'<h2>Good to know</h2><p>{esc(notes)}</p>' if notes else ""
    # FAQ (visible + schema)
    faqs = [
      (f"What is the VA rating for {fclean}?",
       f"The VA rates {cn} under diagnostic code {dc} ({cfr}). Ratings run up to {maxr}%, assigned from the criteria in the table above based on the severity of your condition."),
      (f"What diagnostic code does the VA use for {fclean}?",
       f"Diagnostic code {dc}, rated under {cfr} of the VA Schedule for Rating Disabilities."),
    ]
    if secs:
        faqs.append((f"Can {fclean} be claimed as a secondary condition?",
                     f"Yes. {fclean} is commonly connected to conditions like {', '.join(secs[:3])}. A secondary claim needs a medical nexus linking it to your service-connected condition."))
    faq_visible = "".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q,a in faqs)
    faq_ld = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]})
    bc_ld = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"VA Ratings by Condition","item":"https://vareadyapp.com/conditions.html"},
        {"@type":"ListItem","position":3,"name":f"VA Rating for {fclean}","item":canon}]})
    ev_html, ev_cites = evidence_section(dc, fname, fclean)
    art_obj = {"@context":"https://schema.org","@type":"Article",
        "headline":f"VA Disability Rating for {fclean}","description":desc,"datePublished":"2026-06-07",
        "author":{"@type":"Organization","name":"JDL Software LLC"},"publisher":{"@type":"Organization","name":"VA Ready"},
        "mainEntityOfPage":canon,"inLanguage":"en-US"}
    if ev_cites: art_obj["citation"] = ev_cites
    art_ld = json.dumps(art_obj)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VA Rating for {fclean} (DC {dc}) &mdash; Criteria &amp; Pay | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="VA Disability Rating for {fclean} (DC {dc})">
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
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/conditions.html">VA Ratings by Condition</a> / {esc(fclean)}</div>
    <div class="eyebrow">VA Disability Rating</div>
    <h1>VA Disability Rating for {fname}</h1>
    <p class="lede">{intro}</p>
    <div class="meta"><strong>Diagnostic code {dc}</strong> &middot; {esc(cfr)} &middot; {esc(bsys)} &middot; up to {maxr}%</div>
    <p class="trustline">Built by a veteran who filed his own claim to 100&#37; P&amp;T &mdash; then built the tool he wished he&rsquo;d had. <a href="/founders.html">Read our story &rarr;</a></p>
    <article>
        <h2>How the VA rates {fname}</h2>
        <p>The VA assigns one of these ratings for {esc(cn)}, based on the severity of your condition. These criteria are summarized from {esc(cfr)}:</p>
        {rating_table(crit)}
        {notes_html}
        {secs_html}
        <h2>How to strengthen a {fname} claim</h2>
        <p>The rating you receive depends almost entirely on your evidence and your C&amp;P exam. To put your best claim forward:</p>
        <ul>
            <li>Get a current diagnosis and make sure your symptoms are documented at their worst, not your best day.</li>
            <li>Prepare for your <a href="/guides/c-and-p-exam-preparation.html">C&amp;P exam</a> &mdash; the examiner's report usually decides your rating.</li>
            <li>If service connection isn't obvious, a <a href="/guides/nexus-letters.html">nexus letter</a> can link the condition to your service.</li>
            <li>If this condition was caused by another rated condition, file it as a <a href="/guides/secondary-service-connection.html">secondary claim</a>.</li>
        </ul>
    </article>
    {ev_html}
    <p style="margin:22px 0;"><a href="/va-disability-calculator.html" class="btn">Estimate your combined rating &rarr;</a> &nbsp; <a href="/states.html" class="btn ghost">Veterans benefits by state &rarr;</a></p>
    {APP_CTA}
    <h2 style="font-size:20px;margin-top:30px;">Common questions</h2>
    {faq_visible}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""

# write pages
for dc, slug, fname, intro in META:
    if dc not in DATA: continue
    open(os.path.join(COND_DIR, slug + ".html"), "w").write(cond_page(dc, slug, fname, intro))

# hub
def hub():
    cards = "".join(
        f'<div class="hub-card"><a href="/conditions/{slug}.html">VA Rating for {esc(re.sub("<.*?>","",fname))}</a><p>Diagnostic code {dc} &middot; up to {DATA[dc].get("max_rating")}%' + (f' &middot; {len(STUDIES.get(dc) or [])} studies' if STUDIES.get(dc) else '') + f'</p></div>'
        for dc, slug, fname, intro in META if dc in DATA)
    desc = "VA disability ratings for the most-claimed conditions: tinnitus, PTSD, back pain, sleep apnea, migraines, hearing loss, and more. Rating criteria, diagnostic codes, and how to claim each."
    bc = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"VA Ratings by Condition","item":"https://vareadyapp.com/conditions.html"}]})
    items = json.dumps({"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"url":f"https://vareadyapp.com/conditions/{slug}.html","name":f"VA Rating for {re.sub('<.*?>','',fname)}"}
        for i,(dc,slug,fname,intro) in enumerate(META) if dc in DATA]})
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VA Disability Ratings by Condition &mdash; The Most-Claimed Conditions | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="https://vareadyapp.com/conditions.html">
<meta property="og:type" content="website"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="VA Disability Ratings by Condition"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="https://vareadyapp.com/conditions.html"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" href="/logo.png">
<script type="application/ld+json">{bc}</script>
<script type="application/ld+json">{items}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / VA Ratings by Condition</div>
    <div class="eyebrow">By Condition</div>
    <h1>VA Disability Ratings by Condition</h1>
    <p class="lede">Plain-language rating breakdowns for the conditions veterans claim most &mdash; the exact 38 CFR breakpoints, diagnostic codes, secondary conditions, and how to claim each. Every page now includes the <strong style="color:var(--white);">real peer-reviewed studies</strong> linked to that condition, with a direct PubMed link for each. All sourced from the regulations and the U.S. National Library of Medicine.</p>
    <div class="hub-sec"><div class="hub-grid">{cards}</div></div>
    <p class="trustline">More from VA Ready: <a href="/states.html">Veterans benefits by state</a> &middot; <a href="/guides.html">VA claim guides</a> &middot; <a href="/va-disability-calculator.html">Combined-rating calculator</a></p>
    {APP_CTA}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""
open(os.path.join(SITE, "conditions.html"), "w").write(hub())

# merge into sitemap.xml (add hub + condition pages if missing)
sp = os.path.join(SITE, "sitemap.xml")
xml = open(sp).read()
new = []
for u,p in [("https://vareadyapp.com/conditions.html","0.8")] + \
           [(f"https://vareadyapp.com/conditions/{slug}.html","0.7") for dc,slug,fname,intro in META if dc in DATA]:
    if u not in xml:
        new.append(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-06-07</lastmod>\n    <priority>{p}</priority>\n  </url>')
if new:
    xml = xml.replace("</urlset>", "\n".join(new) + "\n</urlset>")
    open(sp, "w").write(xml)

print(f"generated {len([1 for dc,_,_,_ in META if dc in DATA])} condition pages + hub; sitemap +{len(new)} urls")
