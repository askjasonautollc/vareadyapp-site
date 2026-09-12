#!/usr/bin/env python3
"""Builds ../community.html, the "In the Community" trust page.

Job of the page is trust, not conversion: veteran-founded, shows up in person
(Liberty County High School Panthers sponsorship), how we support veterans.
One soft store link at the bottom, no hard CTAs.

CSS, NAV and FOOTER are read from gen_guides.py so shared chrome changes flow
through. The footer gets the page's compliance lines prepended.

Hero photo: ../img/community-liberty-county-jumbotron-{900,1600}.webp, OG image
../img/community-liberty-county-jumbotron-og.jpg. Cropped above the stands so no
spectator is identifiable, EXIF (including GPS) stripped.

community.html is in gen_guides.py's sitemap core list; this script also merges
it into ../sitemap.xml and stamps its lastmod, so it is safe to run on its own.
"""
import json, re, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
def esc(s): return html.escape(s or "", quote=True)

gtext = open(os.path.join(HERE, "gen_guides.py")).read()
def chrome(name): return re.search(name + r' = """(.*?)"""', gtext, re.S).group(1)
NAV, FOOTER = chrome("NAV"), chrome("FOOTER")

PAGE_DATE = "2026-09-11"
ORIGIN = "https://vareadyapp.com"
canon = ORIGIN + "/community.html"
title = "In the Community | VA Ready: Built by a Veteran, for Veterans"
desc = "Veteran-founded VA Ready shows up in person, sponsoring the Liberty County High School Panthers in Georgia. Free, private tools. No cut of your claim."
assert len(desc) <= 160, len(desc)

IOS = "https://apps.apple.com/app/id6761733758"
ANDROID = "https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US"

HERO_1600 = "/img/community-liberty-county-jumbotron-1600.webp"
HERO_900 = "/img/community-liberty-county-jumbotron-900.webp"
OG_IMG = "/img/community-liberty-county-jumbotron-og.jpg"
HERO_ALT = "The Liberty County High School video board at Donell Woods Stadium showing a VA Ready and Vet Ready sponsor ad during a Panthers home game"
CAPTION = "Donell Woods Stadium, Liberty County High School, September 2026. VA Ready and Vet Ready on the video board during a Panthers home game."

CSS = chrome("CSS") + """
    h1, article h2, .pull-q { font-family:Georgia,'Times New Roman',Times,serif; }
    h1 { font-size:38px; font-weight:700; letter-spacing:-0.3px; line-height:1.18; margin:4px 0 12px; }
    article h2 { font-size:26px; font-weight:700; letter-spacing:-0.2px; line-height:1.25; margin:40px 0 12px; }
    .lede { margin-bottom:6px; }
    .hero-photo { max-width:1080px; margin:26px auto 0; padding:0 22px; }
    .hero-photo img { width:100%; height:auto; aspect-ratio:1600/1000; object-fit:cover; display:block; border-radius:16px; border:1px solid var(--line); background:var(--card); }
    .hero-photo figcaption { max-width:760px; margin:10px auto 0; color:var(--gray); font-size:13px; font-style:italic; line-height:1.6; }
    .facts { display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--line); border:1px solid var(--line); border-radius:12px; overflow:hidden; margin:22px 0 6px; }
    .facts div { background:var(--card); padding:14px 16px; }
    .facts dt { font-size:10.5px; font-weight:800; letter-spacing:2px; text-transform:uppercase; color:var(--gold); line-height:1.5; }
    .facts dd { color:var(--white); font-size:14.5px; font-weight:600; line-height:1.45; margin-top:4px; }
    .pull-q { border-left:3px solid var(--gold); margin:34px 0 8px; padding:4px 0 4px 20px; color:var(--white); font-size:25px; font-style:italic; line-height:1.4; }
    .support { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:18px 0 6px; }
    .support .card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:18px 20px; }
    .support h3 { color:var(--white); font-size:16px; font-weight:800; margin:0 0 6px; }
    .support p { font-size:15px; line-height:1.65; margin:0; }
    .soft-close { text-align:center; border-top:1px solid var(--line); margin:46px 0 16px; padding:28px 0 6px; }
    .soft-close p { color:var(--tan); font-size:16px; margin-bottom:6px; }
    .soft-close .stores a { font-weight:700; }
    .soft-close .stores span { color:var(--gray); margin:0 10px; }
    .soft-close .note { color:var(--gray); font-size:13px; }
    footer .compliance { max-width:720px; margin:0 auto 14px; color:var(--tan); font-size:12.5px; line-height:1.65; }
    @media (max-width:720px){ .facts { grid-template-columns:1fr 1fr; } }
    @media (max-width:620px){ .support { grid-template-columns:1fr; } }
    @media (max-width:560px){ h1 { font-size:30px; } article h2 { font-size:23px; } .pull-q { font-size:21px; } }
"""

COMPLIANCE = ('<p class="compliance">The app is educational. It does not give claims advice, legal guidance, '
              'or predict ratings, and it points veterans to free accredited representatives. '
              'VA Ready is not affiliated with the U.S. Department of Veterans Affairs.</p>')
FOOTER_PAGE = FOOTER.replace("<footer>", "<footer>\n    " + COMPLIANCE, 1)
assert COMPLIANCE in FOOTER_PAGE

# ---------- JSON-LD ----------
ORG_ID, TEAM_ID, IMG_ID, BC_ID = ORIGIN + "/#organization", canon + "#liberty-county-panthers", canon + "#hero", canon + "#breadcrumb"
org = {"@type": "Organization", "@id": ORG_ID, "name": "JDL Software LLC", "alternateName": ["VA Ready", "Vet Ready"],
       "url": ORIGIN + "/", "logo": ORIGIN + "/logo.png", "email": "support@vareadyapp.com",
       "description": "Veteran-founded maker of VA Ready (iOS) and Vet Ready (Android), educational apps for veterans working through the VA disability claims process.",
       "founder": {"@type": "Person", "name": "Jason", "jobTitle": "Founder", "honorificSuffix": "CW2, U.S. Army (Retired)", "url": ORIGIN + "/founders.html"},
       "knowsAbout": ["VA disability compensation claims", "38 CFR Part 4, Schedule for Rating Disabilities",
                      "PACT Act presumptive conditions", "Accredited Veterans Service Organizations", "State and federal veterans benefits"],
       "sameAs": [IOS, "https://play.google.com/store/apps/details?id=com.vaready.app", "https://www.tiktok.com/@vareadyapp",
                  "https://www.facebook.com/vareadyapp", "https://www.instagram.com/vareadyapp/"]}
team = {"@type": "SportsTeam", "@id": TEAM_ID, "name": "Liberty County High School Panthers", "sport": "American football",
        "parentOrganization": {"@type": "HighSchool", "name": "Liberty County High School",
                               "address": {"@type": "PostalAddress", "addressRegion": "GA", "addressCountry": "US"}},
        "location": {"@type": "StadiumOrArena", "name": "Donell Woods Stadium",
                     "containedInPlace": {"@type": "AdministrativeArea", "name": "Liberty County, Georgia"}},
        "sponsor": {"@id": ORG_ID}}
image = {"@type": "ImageObject", "@id": IMG_ID, "url": ORIGIN + HERO_1600, "contentUrl": ORIGIN + HERO_1600,
         "width": 1600, "height": 1000, "caption": CAPTION}
bc = {"@type": "BreadcrumbList", "@id": BC_ID, "itemListElement": [
      {"@type": "ListItem", "position": 1, "name": "Home", "item": ORIGIN + "/"},
      {"@type": "ListItem", "position": 2, "name": "In the Community", "item": canon}]}
page = {"@type": "WebPage", "@id": canon, "url": canon, "name": title, "description": desc, "inLanguage": "en-US",
        "datePublished": PAGE_DATE, "isPartOf": {"@type": "WebSite", "name": "VA Ready", "url": ORIGIN + "/"},
        "about": {"@id": ORG_ID}, "mentions": {"@id": TEAM_ID}, "primaryImageOfPage": {"@id": IMG_ID}, "breadcrumb": {"@id": BC_ID}}
LD = {"@context": "https://schema.org", "@graph": [page, org, team, image, bc]}

# ---------- body ----------
BODY_TOP = '''<div class="crumb"><a href="/index.html">Home</a> / In the Community</div>
    <div class="eyebrow">In the Community</div>
    <h1>We show up in person, not just on your phone.</h1>
    <p class="lede">VA Ready is a veteran-founded company. This season, that means Friday nights in Liberty County, Georgia, with our name on the board at Donell Woods Stadium.</p>'''

HERO = f'''<figure class="hero-photo">
    <img src="{HERO_1600}" srcset="{HERO_900} 900w, {HERO_1600} 1600w" sizes="(max-width:1080px) 100vw, 1036px" alt="{esc(HERO_ALT)}" width="1600" height="1000" loading="eager" fetchpriority="high" decoding="async">
    <figcaption>{esc(CAPTION)}</figcaption>
</figure>'''

BODY = f'''<article>
    <h2>Friday nights in Liberty County</h2>
    <p>We sponsor the <strong>Liberty County High School Panthers</strong> football team for the full 2026 season. Every home game, our name runs on the video board at Donell Woods Stadium.</p>
    <p>Liberty County is home to Fort Stewart. A lot of the families in those stands are military families. Plenty of the parents have served, and plenty are serving now. Those are the people we built this for, so that is where we wanted to be.</p>
    <dl class="facts">
      <div><dt>Team</dt><dd>Liberty County High School Panthers</dd></div>
      <div><dt>Stadium</dt><dd>Donell Woods Stadium</dd></div>
      <div><dt>Where</dt><dd>Liberty County, Georgia</dd></div>
      <div><dt>Sponsorship</dt><dd>Full 2026 season</dd></div>
    </dl>
    <p class="pull-q">We&rsquo;d rather earn trust in the stands than buy it in an ad.</p>

    <h2>Built by a veteran, not a marketing company</h2>
    <p>VA Ready was not built by an agency that found a veteran angle. It was built by a retired U.S. Army Chief Warrant Officer who went through the VA claims process himself.</p>
    <p>He dug through scattered rules, made his own checklists, and figured out the steps the hard way. Then he built the tool he wished someone had handed him. <a href="/founders.html">Read our story</a>.</p>

    <h2>How we support veterans</h2>
    <div class="support">
      <div class="card">
        <h3>Free accredited help comes first</h3>
        <p>The app points veterans to accredited Veterans Service Organizations like the DAV, the VFW, and county veterans service offices. Their help is free. <a href="/find-a-vso.html">Find a VSO near you</a>.</p>
      </div>
      <div class="card">
        <h3>Free and private</h3>
        <p>The core tools are free, with no account. Your claim information stays on your phone. We don&rsquo;t sell your data, we don&rsquo;t take a cut of your claim, and nothing we charge is tied to your benefits.</p>
      </div>
      <div class="card">
        <h3>We show up in person</h3>
        <p>Liberty County is where we started. We would rather meet veterans where they already gather than chase them with ads.</p>
      </div>
      <div class="card">
        <h3>Built from veteran feedback</h3>
        <p>Veterans send reports straight from the app. We read them, check them against the primary sources, and ship the fixes. A lot of every update started as a message from a veteran.</p>
      </div>
    </div>
  </article>

  <div class="soft-close">
    <p>Free to download on iPhone and Android.</p>
    <p class="stores"><a href="{IOS}">VA Ready on the App Store</a><span aria-hidden="true">&middot;</span><a href="{esc(ANDROID)}">Vet Ready on Google Play</a></p>
    <p class="note">Same app, two names: VA Ready on iPhone, Vet Ready on Android.</p>
  </div>'''

PAGE = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="JDL Software LLC">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="VA Ready">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="In the Community: VA Ready, Built by a Veteran, for Veterans">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{ORIGIN}{OG_IMG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(HERO_ALT)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="In the Community: VA Ready, Built by a Veteran, for Veterans">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{ORIGIN}{OG_IMG}">
<meta name="twitter:image:alt" content="{esc(HERO_ALT)}">
<link rel="icon" type="image/png" href="/logo.png">
<link rel="apple-touch-icon" sizes="180x180" href="/logo.png">
<link rel="preload" as="image" href="{HERO_1600}" imagesrcset="{HERO_900} 900w, {HERO_1600} 1600w" imagesizes="(max-width:1080px) 100vw, 1036px">
<script type="application/ld+json">{json.dumps(LD)}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    {BODY_TOP}
</div>
{HERO}
<div class="wrap">
  {BODY}
</div>
{FOOTER_PAGE}
</body>
</html>'''

# house rules: no em dashes, no AI language, never "prep"/"practice"
assert "—" not in PAGE and "&mdash;" not in PAGE, "em dash"
assert not re.search(r"\bAI\b", PAGE), "AI language"
assert not re.search(r"prep|practice", PAGE, re.I), "prep/practice"
for f in (HERO_1600, HERO_900, OG_IMG):
    assert os.path.exists(os.path.join(SITE, f.lstrip("/"))), "missing image " + f

open(os.path.join(SITE, "community.html"), "w").write(PAGE)

# merge into sitemap and stamp lastmod
sp = os.path.join(SITE, "sitemap.xml")
xml = open(sp).read()
entry = f'  <url>\n    <loc>{canon}</loc>\n    <lastmod>{PAGE_DATE}</lastmod>\n    <priority>0.7</priority>\n  </url>\n'
if canon in xml:
    xml = re.sub(r'  <url>\n    <loc>' + re.escape(canon) + r'</loc>\n.*?  </url>\n', lambda m: entry, xml, count=1, flags=re.S)
    note = "sitemap entry refreshed"
else:
    xml = xml.replace("</urlset>", entry + "</urlset>")
    note = "sitemap +1"
open(sp, "w").write(xml)

for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', PAGE, re.S):
    json.loads(blk)
print(f"community.html written; {note}; JSON-LD valid; page bytes: {len(PAGE)}")
