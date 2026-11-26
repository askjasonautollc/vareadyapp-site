#!/usr/bin/env python3
"""Wear and Tear topic pages (/wear-and-tear/<slug>.html), the hub
(/wear-and-tear.html) and the app features page (/features.html).

Source: data/wear_and_tear.json, a snapshot of published rows from Supabase
`wear_and_tear` holding only what the pages show (conditions, reasons, sources)
plus counts of the proof records and statement questions, which stay in the app.
Refresh the snapshot from the app project's export before regenerating.
"""
import ast, html, json, os, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
OUT = os.path.join(SITE, "wear-and-tear")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.date.today().isoformat()

def esc(s): return html.escape(str(s) if s is not None else "", quote=True)

DATA = json.load(open(os.path.join(HERE, "data", "wear_and_tear.json")))
PAGES = DATA["pages"]
TOTAL = DATA["total_in_app"]

gtext = open(os.path.join(HERE, "gen_guides.py")).read()
CSS = re.search(r'CSS = """(.*?)"""', gtext, re.S).group(1)
ctext = open(os.path.join(HERE, "gen_conditions.py")).read()
NAV = re.search(r'NAV = """(.*?)"""', ctext, re.S).group(1)
FOOTER = re.search(r'FOOTER = """(.*?)"""', ctext, re.S).group(1)
mtext = open(os.path.join(HERE, "gen_mos.py")).read()
COND_SLUG = ast.literal_eval(re.search(r"COND_SLUG = (\{.*?\})", mtext, re.S).group(1))

CSS += """
    ul.clist { list-style:none; padding:0; margin:8px 0 18px; max-width:none; }
    ul.clist li { border-top:1px solid var(--line); padding:12px 0; margin:0; }
    ul.clist li .cn { color:var(--white); font-weight:700; }
    ul.clist li .cn a { color:var(--white); }
    ul.clist li .dc { color:var(--gray); font-size:13px; font-weight:400; margin-left:6px; }
    ul.clist li .ctag { font-size:13px; color:var(--gray); margin-left:8px; }
    ul.clist li p { color:var(--tan); font-size:15px; margin:4px 0 0; }
    ol.srcs { padding-left:20px; margin:8px 0 18px; }
    ol.srcs li { color:var(--tan); font-size:14.5px; margin:0 0 8px; max-width:72ch; }
    ol.srcs li .by { color:var(--gray); font-size:13px; }
    .pillrow { display:flex; flex-wrap:wrap; gap:4px 18px; margin:6px 0 16px; }
    .pillrow a { font-size:15px; padding:8px 0; }
    .trustline { font-size:14.5px; color:var(--tan); margin:14px 0 4px; max-width:68ch; }
    .page-cta { margin:26px 0; }
    .wrap > p:not(.lede):not(.note):not(.trustline) { color:var(--tan); margin:0 0 14px; max-width:68ch; }
    table.rt { width:100%; border-collapse:collapse; margin:8px 0 18px; }
    table.rt th, table.rt td { text-align:left; padding:11px 12px; border-bottom:1px solid var(--line); font-size:15px; vertical-align:top; color:var(--tan); }
    table.rt th { color:var(--gray); font-size:13px; font-weight:600; }
    .cat-h { font-size:21px; font-weight:800; margin:30px 0 6px; }
    .feat { display:grid; grid-template-columns:minmax(0,1fr) 260px; gap:28px; align-items:start; border-top:1px solid var(--line); padding:26px 0; }
    .feat.noimg { grid-template-columns:minmax(0,1fr); }
    .feat h2 { font-size:22px; font-weight:800; margin:0 0 8px; line-height:1.3; }
    .feat p { color:var(--tan); max-width:64ch; margin:0 0 10px; }
    .feat .tier { color:var(--gray); font-size:13px; font-weight:600; margin-left:8px; }
    .feat .phone { background:#05070d; padding:7px; border-radius:32px; border:1px solid rgba(255,255,255,0.08); }
    .feat .phone img { display:block; width:100%; height:auto; border-radius:26px; }
    @media (max-width:760px) { .feat { grid-template-columns:minmax(0,1fr); } .feat .shot { max-width:280px; } }
"""

STORES = """<div class="btns page-cta"><a href="https://apps.apple.com/app/id6761733758" class="btn primary">VA Ready for iPhone, iPad and Mac</a><a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US" class="btn ghost">Vet Ready for Android</a><a href="https://apps.microsoft.com/detail/9p8xfcqvfjhf" class="btn ghost">VA Ready for Windows</a></div>"""
DISCLAIMER = """<div class="disclaimer">This page is for general informational purposes only and is not legal or medical advice. It lists conditions that published research and VA or DoD sources link to an activity; it does not mean any one veteran has them, and a link is not a VA presumption unless a regulation named on this page says so. The VA decides service connection and ratings from your own records, evidence, and exam. VA Ready is not affiliated with the U.S. Department of Veterans Affairs. For free help filing, work with a <a href="/find-a-vso.html">VA-accredited VSO</a>.</div>"""
ORG_ID = "https://vareadyapp.com/#organization"

EXPOSURE_PAGE = [("camp_lejeune", "camp-lejeune", "Camp Lejeune water"), ("agent_orange", "agent-orange", "Agent Orange"),
                 ("herbicide", "agent-orange", "Agent Orange"), ("burn_pit", "burn-pits-pact-act", "burn pits and the PACT Act"),
                 ("gulf_war", "gulf-war-illness", "Gulf War Illness"), ("asbestos", "asbestos", "asbestos"),
                 ("afff", "afff-pfas", "AFFF and PFAS"), ("jet_fuel", "jet-fuel-petroleum", "jet fuel and petroleum"),
                 ("depleted_uranium", "depleted-uranium", "depleted uranium"), ("k2", "k2-karshi-khanabad", "K2"),
                 ("fort_mcclellan", "fort-mcclellan", "Fort McClellan"), ("project_112", "project-112-shad", "Project 112 and SHAD"),
                 ("radiation", "radiation", "radiation"), ("ionizing", "radiation", "radiation")]

PREV = {"high": "Strong evidence", "moderate": "Documented link"}
RANK = {"high": 0, "moderate": 1}

def url_of(p): return f"/wear-and-tear/{p['slug']}.html"

def ranked(p):
    return sorted(p["common_conditions"], key=lambda c: RANK.get(c.get("prevalence"), 2))

def exposure_links(p):
    seen, out = set(), []
    for code in p.get("exposure_codes") or []:
        for key, pg, label in EXPOSURE_PAGE:
            if key in code and pg not in seen:
                seen.add(pg); out.append(f'<a href="/exposures/{pg}.html">{esc(label)}</a>')
                break
    return out

def join_words(xs):
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]

def head(title, desc, canon, lds, og_type="article"):
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in lds)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="{esc(title.split(' | ')[0])}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
{ld}
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">"""

def tail():
    return f"""</div>
{FOOTER}
</body>
</html>"""

def page(p):
    name = p["activity_name"]
    canon = f"https://vareadyapp.com{url_of(p)}"
    cs = ranked(p)
    top = [c["name"] for c in cs[:3]]
    title = f"{name}: VA disability conditions linked to it | VA Ready"
    desc = f"{name} and VA disability: {len(cs)} conditions research links to it, including {join_words([t.split(',')[0] for t in top])}, with the studies behind each."
    if len(desc) > 160: desc = desc[:157].rsplit(" ", 1)[0] + "..."
    src_by_key = {s["key"]: s for s in p["sources"]}

    def cond_li(c):
        dc = c["dc"]
        nm = esc(c["name"])
        slug = COND_SLUG.get(dc.split(" ")[0])
        nm_html = f'<a href="/conditions/{slug}.html">{nm}</a>' if slug else nm
        refs = [str(i + 1) for i, s in enumerate(p["sources"]) if s["key"] in (c.get("source_keys") or [])]
        ref = f' <span class="dc">Sources {", ".join(refs)}</span>' if refs else ""
        return (f'<li><span class="cn">{nm_html}</span><span class="dc">DC {esc(dc)}</span>'
                f'<span class="ctag">{PREV.get(c.get("prevalence"), "Documented link")}</span>'
                f'<p>{esc(c.get("reason"))}{ref}</p></li>')

    def src_li(s):
        link = f"https://pubmed.ncbi.nlm.nih.gov/{s['pmid']}/" if s.get("pmid") else s.get("url")
        t = esc(s.get("title"))
        t_html = f'<a href="{esc(link)}" rel="nofollow noopener" target="_blank">{t}</a>' if link else t
        by = ", ".join(x for x in [s.get("publisher"), str(s["year"]) if s.get("year") else None] if x)
        return f'<li>{t_html} <span class="by">{esc(by)}</span></li>'

    xl = exposure_links(p)
    x_html = f'<p>Related exposure pages: {join_words(xl)}.</p>' if xl else ""
    same = [q for q in PAGES if q["category"] == p["category"] and q["slug"] != p["slug"]]
    others = "".join(f'<a href="{url_of(q)}">{esc(q["activity_name"])}</a>' for q in same)
    words = ", ".join(esc(a) for a in (p.get("search_aliases") or [])[:6])

    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://vareadyapp.com/"},
        {"@type": "ListItem", "position": 2, "name": "Wear and Tear", "item": "https://vareadyapp.com/wear-and-tear.html"},
        {"@type": "ListItem", "position": 3, "name": name, "item": canon}]}
    art = {"@context": "https://schema.org", "@type": "Article", "headline": f"{name} and VA disability",
           "description": desc, "datePublished": TODAY, "dateModified": TODAY,
           "author": {"@type": "Organization", "name": "JDL Software LLC"},
           "publisher": {"@type": "Organization", "@id": ORG_ID, "name": "VA Ready", "url": "https://vareadyapp.com/"},
           "mainEntityOfPage": canon, "inLanguage": "en-US"}

    return head(title, desc, canon, [bc, art]) + f"""
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/wear-and-tear.html">Wear and Tear</a> / {esc(name)}</div>
    <h1>{esc(name)} and VA disability</h1>
    <p class="lede">{esc(p["summary"])} Veterans also call it {words}.</p>
    <article>
        <h2>Conditions linked to it</h2>
        <ul class="clist">{"".join(cond_li(c) for c in cs)}</ul>
        <p>"Strong evidence" means studies in military or comparable groups show the link clearly. "Documented link" means published evidence exists but is thinner. Neither is a VA presumption unless a regulation is named above.</p>
        {x_html}
        <h2>Sources</h2>
        <ol class="srcs">{"".join(src_li(s) for s in p["sources"])}</ol>
    </article>
    <h2>Prove it and write it down</h2>
    <p>VA needs proof the activity happened as well as a diagnosis and a link. In VA Ready, Wear and Tear lists {p["proof_count"]} records that can show you did this, gives you {p["prompt_count"]} questions to answer for your own statement, and gathers the conditions from everything you did into one list you can add to your claim. Wear and Tear is part of Pro.</p>
    {STORES}
    <h2 style="font-size:20px;margin-top:30px;">More in {esc(p["category"].lower())}</h2>
    <div class="pillrow">{others}</div>
    <p class="trustline">More from VA Ready: <a href="/wear-and-tear.html">all Wear and Tear pages</a> &middot; <a href="/mos.html">conditions by job code</a> &middot; <a href="/exposures.html">toxic exposures</a> &middot; <a href="/features.html">what the app does</a></p>
    {DISCLAIMER}
""" + tail()

ORDER = ["Infantry and close combat", "Weapons, blast and noise", "Load, impact and training",
         "Vehicles, aircraft and ships", "Climate and terrain", "Hours and support work",
         "Medical, police and fire", "Special operations and schools", "Deployments and eras"]

def hub():
    canon = "https://vareadyapp.com/wear-and-tear.html"
    desc = "Conditions linked to what you did in service: rucking, kicking in doors, jumps, artillery, flight decks, burn pits, Camp Lejeune and more, each with its sources."
    secs = ""
    for cat in ORDER:
        ps = [p for p in PAGES if p["category"] == cat]
        if not ps: continue
        rows = "".join(f'<tr><td><a href="{url_of(p)}">{esc(p["activity_name"])}</a></td>'
                       f'<td>{esc(", ".join(c["name"].split(",")[0] for c in ranked(p)[:2]))}</td>'
                       f'<td>{len(p["common_conditions"])}</td></tr>' for p in ps)
        secs += (f'<h2 class="cat-h">{esc(cat)}</h2><div class="tbl-wrap"><table class="rt"><thead><tr>'
                 f'<th>Activity</th><th>First conditions listed</th><th>Conditions</th></tr></thead><tbody>{rows}</tbody></table></div>')
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://vareadyapp.com/"},
        {"@type": "ListItem", "position": 2, "name": "Wear and Tear", "item": canon}]}
    items = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f"https://vareadyapp.com{url_of(p)}", "name": p["activity_name"]}
        for i, p in enumerate(PAGES)]}
    return head("Wear and Tear: VA disability conditions by what you did in service | VA Ready", desc, canon, [bc, items], "website") + f"""
    <div class="crumb"><a href="/index.html">Home</a> / Wear and Tear</div>
    <h1>Conditions linked to what you did in service</h1>
    <p class="lede">A job code misses most of what service put your body through. These pages start from the activity instead: the rucks, the doors, the jumps, the ranges, the flight deck, the deployment. Each lists the conditions published research links to it, the reason for each link, and the studies behind it.</p>
    <p class="note">This page covers {len(PAGES)} activities. The app carries {TOTAL}, with the records that prove each one and questions for your own statement.</p>
    {secs}
    {STORES}
    <p class="trustline">More from VA Ready: <a href="/mos.html">conditions by job code</a> &middot; <a href="/exposures.html">toxic exposures</a> &middot; <a href="/features.html">what the app does</a></p>
    {DISCLAIMER}
""" + tail()

def shot(img, alt):
    return (f'<div class="shot"><div class="phone"><picture><source srcset="/img/{img}.webp" type="image/webp">'
            f'<img src="/img/{img}.jpg" alt="{esc(alt)}" width="600" height="1304" loading="lazy" decoding="async"></picture></div></div>')

FEATURES = [
    ("My Claim and the combined rating", "Free",
     ["Add each condition and its rating, and VA Ready works out your combined rating the way VA does, step by step, with the bilateral factor, and shows the monthly pay for your dependents.",
      "Each condition keeps its evidence count, exam status and notes on your device."],
     ("v3-rating", "VA Ready My Claim screen showing a sample combined rating and monthly payment with a body figure.")),
    ("Claim scenarios", "Pro",
     ["Pick a scenario at the top of My Claim to try a different claim. Scenario 1 is your claim. Scenarios 2 to 5 start as a copy or empty, and they never reach your forms, VSO packet or exports."],
     ("v3-scenarios", "VA Ready My Claim screen with Scenario 2 open and a note that it is a scenario, not the claim.")),
    ("What-If", None,
     ["Test a possible claim against your rating before you decide what to pursue, with suggestions from your job code, exposures and duties."],
     ("v3-what-if", "VA Ready What-If screen testing an added condition against a sample rating.")),
    ("Claim Intel: your job code and exposures", "Pro",
     ["Conditions common for your MOS, AFSC or rating, ranked, with PACT Act presumptives and the conditions suggested by your exposures, bases and aircraft. It covers 1,106 job codes across every branch, including legacy codes."],
     ("v3-claim-intel-conditions", "VA Ready Claim Intel screen listing common conditions for an Army 11B, ranked by prevalence.")),
    ("Wear and Tear", "Pro",
     [f"Search {TOTAL} things you did in service, from kicking in doors and rucking to flight decks and Camp Lejeune. Each one lists the conditions linked to it, the studies behind each link, the records that prove you did it, and questions for your own statement. Mark what you did and the conditions gather into one list.",
      'Read the conditions and sources for the most searched activities on the <a href="/wear-and-tear.html">Wear and Tear pages</a>.'],
     ("v3-wear-and-tear", "VA Ready Wear and Tear screen listing the conditions from what a veteran did, ranked by how many activities point to each.")),
    ("Top VA claims", "Free",
     ["The most common conditions VA rates, from VA's 2025 Annual Benefits Report: for all veterans, for veterans newly rated this year, by era, after 9/11, and by body system, with VA's count for each."],
     ("v3-top-claims", "VA Ready Top VA claims screen listing the ten most common rated conditions with VA's counts.")),
    ("What decided Board cases", "Pro",
     ["What helped and what hurt in real Board of Veterans' Appeals decisions on your condition, with the decision numbers behind each finding."], None),
    ("C&P exam prep", "Pro",
     ["Answer the questions an examiner works from, at home and in your own words, then export them as a PDF to bring with you."], None),
    ("Claim Navigator", "Pro",
     ["Step-by-step directions from where you are in the claim to a decision, with a guide for each step, including increases, TDIU and a proposed reduction."], None),
    ("Claim file and VSO packet", None,
     ["Scan or import your records, label each one with the VA document type, and tie it to the condition it supports. Pro adds a VSO packet with an evidence index on the front page."],
     ("v3-claim-file", "VA Ready claim file screen listing documents labeled by type and condition.")),
    ("Symptom log and buddy statements", None,
     ["Log flare-ups as they happen and build buddy statements from guided templates. Pro adds unlimited history, reminders and PDF exports."],
     ("v3-symptom-log", "VA Ready symptom log screen with dated entries.")),
    ("Benefits and finding a VSO", None,
     ["Federal benefits by rating, state benefits for every state with Pro, and a map of VA-accredited VSO offices near you."], None),
]

def features():
    canon = "https://vareadyapp.com/features.html"
    desc = "What VA Ready does: combined rating, claim scenarios, Claim Intel by job code and exposure, Wear and Tear, Board cases, C&P exam prep, Claim Navigator and more."
    secs = ""
    for t, tier, paras, img in FEATURES:
        tg = f'<span class="tier">{tier}</span>' if tier else ""
        body = "".join(f"<p>{x}</p>" for x in paras)
        if img:
            secs += f'<section class="feat"><div><h2>{esc(t)}{tg}</h2>{body}</div>{shot(*img)}</section>'
        else:
            secs += f'<section class="feat noimg"><div><h2>{esc(t)}{tg}</h2>{body}</div></section>'
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://vareadyapp.com/"},
        {"@type": "ListItem", "position": 2, "name": "Features", "item": canon}]}
    app = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "VA Ready",
           "applicationCategory": "UtilitiesApplication", "operatingSystem": "iOS, iPadOS, macOS, Android, Windows",
           "publisher": {"@type": "Organization", "@id": ORG_ID, "name": "VA Ready"}, "url": canon}
    return head("What VA Ready does: every feature | VA Ready", desc, canon, [bc, app], "website") + f"""
    <div class="crumb"><a href="/index.html">Home</a> / Features</div>
    <h1>What VA Ready does</h1>
    <p class="lede">VA Ready helps you build a VA disability claim from start to finish: what to claim, how it rates, how to prove it, and where you are in the process. Everything stays on your device. Free covers the rating and the basics; Pro adds the research and the exports.</p>
    {secs}
    {STORES}
    <p class="trustline">More from VA Ready: <a href="/va-disability-calculator.html">combined-rating calculator</a> &middot; <a href="/wear-and-tear.html">Wear and Tear pages</a> &middot; <a href="/mos.html">conditions by job code</a> &middot; <a href="/find-a-vso.html">find a VSO</a></p>
    <div class="disclaimer">VA Ready is not affiliated with the U.S. Department of Veterans Affairs. It is an organizing and education tool, not legal or medical advice. For free help filing, work with a <a href="/find-a-vso.html">VA-accredited VSO</a>.</div>
""" + tail()

written = []
for p in PAGES:
    open(os.path.join(OUT, p["slug"] + ".html"), "w").write(page(p)); written.append(url_of(p))
open(os.path.join(SITE, "wear-and-tear.html"), "w").write(hub()); written.append("/wear-and-tear.html")
# /features.html is written by gen_howto.py (overview of every feature).

sp = os.path.join(SITE, "sitemap.xml"); xml = open(sp).read(); new = []
for u in written:
    loc = f"https://vareadyapp.com{u}"
    if loc not in xml:
        pr = "0.8" if u in ("/wear-and-tear.html", "/features.html") else "0.7"
        new.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <priority>{pr}</priority>\n  </url>")
if new:
    xml = xml.replace("</urlset>", "\n".join(new) + "\n</urlset>"); open(sp, "w").write(xml)

bad = 0
for u in written:
    s = open(os.path.join(SITE, u.lstrip("/"))).read()
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: json.loads(b)
        except Exception as e: bad += 1; print("BAD JSON-LD", u, e)
    if "—" in s or "&mdash;" in s: bad += 1; print("EM DASH", u)
    if s.count("<h1") != 1: bad += 1; print("H1 COUNT", u)
    for h in re.findall(r'href="(/[^"#]+\.html)"', s):
        if not os.path.exists(os.path.join(SITE, h.lstrip("/"))): bad += 1; print("MISSING", u, h)
    for im in re.findall(r'(?:src|srcset)="(/img/[^"]+)"', s):
        if not os.path.exists(os.path.join(SITE, im.lstrip("/"))): bad += 1; print("NO IMAGE", u, im)
print(f"wrote {len(PAGES)} activity pages + hub + features; sitemap +{len(new)}; problems={bad}")
