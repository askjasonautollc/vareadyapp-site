#!/usr/bin/env python3
"""Builds ../community.html (the In the Community feed) and the homepage teaser.

ADDING AN ENTRY (a few minutes):
  1. Drop the photo at _generators/data/community/photos/<id>.jpg (jpg, png or heic).
     That folder is gitignored, so original photos never reach the public repo.
  2. Add an object to _generators/data/community.json (template in README.md).
     Order in the file does not matter; the feed sorts newest first by "date".
  3. Run: python3 _generators/gen_community.py   then commit and push.

The script crops each photo to 16:10, strips EXIF (including GPS), writes
../img/community/<id>-{900,1600}.webp and <id>-og.jpg, rebuilds community.html,
swaps the newest entries into ../index.html between the COMMUNITY markers, and
refreshes the sitemap lastmod. Images that already exist are kept, so another
clone can regenerate without the original photos.

CSS, NAV and FOOTER come from gen_guides.py. The footer gets the compliance lines.
community.html is also in gen_guides.py's sitemap core list.
"""
import glob, html, json, os, re, subprocess, sys, tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data", "community.json")
PHOTOS = os.path.join(HERE, "data", "community", "photos")
IMG_DIR = os.path.join(SITE, "img", "community")
HOME_TEASER_COUNT = 3

ORIGIN = "https://vareadyapp.com"
canon = ORIGIN + "/community.html"
# Page-level SEO. Revisit when the mix of entries changes.
title = "VA Ready in the Community | Veteran Flights & Georgia Football"
desc = "Veteran-founded VA Ready shows up in person in Georgia: free discovery flights for veterans with Runway One Nine Aviation and Liberty County Panthers football."
assert len(title) <= 65, len(title)
assert len(desc) <= 160, len(desc)

IOS = "https://apps.apple.com/app/id6761733758"
ANDROID = "https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US"

def esc(s): return html.escape(s or "", quote=True)
def text(s): return html.escape(s or "", quote=False).replace("'", "&rsquo;")

gtext = open(os.path.join(HERE, "gen_guides.py")).read()
def chrome(name): return re.search(name + r' = """(.*?)"""', gtext, re.S).group(1)
NAV, FOOTER = chrome("NAV"), chrome("FOOTER")

# ---------- entries ----------
REQUIRED = ("id", "date", "headline", "body", "photo_alt")
entries = json.load(open(DATA))
if not entries:
    sys.exit("community.json has no entries")
seen = set()
for e in entries:
    missing = [k for k in REQUIRED if not e.get(k)]
    if missing:
        sys.exit(f"community.json entry {e.get('id', '?')}: missing {', '.join(missing)}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", e["id"]):
        sys.exit(f"entry id {e['id']!r}: use lowercase words joined by hyphens")
    if e["id"] in seen:
        sys.exit(f"duplicate entry id {e['id']}")
    seen.add(e["id"])
    try:
        d = datetime.strptime(e["date"], "%Y-%m-%d")
    except ValueError:
        sys.exit(f"entry {e['id']}: date must be YYYY-MM-DD")
    if not e.get("when"):
        e["when"] = d.strftime("%B %Y")
    e["paras"] = [e["body"]] if isinstance(e["body"], str) else list(e["body"])
entries.sort(key=lambda e: e["date"], reverse=True)
newest = entries[0]

# ---------- photos ----------
def img_url(e, variant): return f"/img/community/{e['id']}-{variant}"

def build_photos(e):
    base = os.path.join(IMG_DIR, e["id"])
    outs = [base + "-900.webp", base + "-1600.webp", base + "-og.jpg"]
    if all(os.path.exists(p) for p in outs):
        return "kept existing images"
    stem = e.get("photo") or e["id"]
    found = sorted(glob.glob(os.path.join(PHOTOS, stem + ".*")))
    if not found:
        sys.exit(f"entry {e['id']}: no photo. Put it at _generators/data/community/photos/{stem}.jpg")
    from PIL import Image, ImageOps
    src = found[0]
    if src.lower().endswith((".heic", ".heif")):
        tmp = os.path.join(tempfile.gettempdir(), stem + "-converted.jpg")
        subprocess.run(["sips", "-s", "format", "jpeg", src, "--out", tmp], check=True, capture_output=True)
        src = tmp
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    focus = min(1.0, max(0.0, float(e.get("photo_focus", 0.5))))

    def crop(ratio):
        W, H = im.size
        if W / H > ratio:
            w = round(H * ratio); x = (W - w) // 2
            return im.crop((x, 0, x + w, H))
        h = round(W / ratio); y = round((H - h) * focus)
        return im.crop((0, y, W, y + h))

    os.makedirs(IMG_DIR, exist_ok=True)
    hero = crop(1.6)
    if hero.width < 1600:
        print(f"  note: {e['id']} photo is {hero.width}px wide after cropping and will be upscaled")
    for w in (1600, 900):  # saved without exif, so GPS and camera data are dropped
        hero.resize((w, round(w / 1.6)), Image.LANCZOS).save(base + f"-{w}.webp", "WEBP", quality=80, method=6)
    crop(1200 / 630).resize((1200, 630), Image.LANCZOS).save(base + "-og.jpg", "JPEG", quality=84, optimize=True, progressive=True)
    return "built from " + os.path.basename(found[0])

photo_log = {e["id"]: build_photos(e) for e in entries}

# ---------- community page ----------
CSS = chrome("CSS") + """
    h1, article h2, .entry h2 { font-family:Georgia,'Times New Roman',Times,serif; }
    h1 { font-size:38px; font-weight:700; letter-spacing:-0.3px; line-height:1.18; margin:4px 0 12px; }
    article h2 { font-size:26px; font-weight:700; letter-spacing:-0.2px; line-height:1.25; margin:40px 0 12px; }
    .lede { margin-bottom:6px; }
    .feed { margin:30px 0 8px; }
    .entry { background:var(--card); border:1px solid var(--line); border-radius:16px; overflow:hidden; margin:0 0 22px; scroll-margin-top:18px; }
    .entry img { display:block; width:100%; height:auto; aspect-ratio:1600/1000; object-fit:cover; background:#0f1524; border-bottom:1px solid var(--line); }
    .entry-body { padding:20px 24px 22px; }
    .entry-meta { display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 14px; margin-bottom:4px; }
    .entry-meta time { font-size:11.5px; font-weight:800; letter-spacing:2px; text-transform:uppercase; color:var(--gold); }
    .entry-meta .loc { font-size:13px; font-weight:600; color:var(--gray); }
    .entry h2 { font-size:25px; font-weight:700; line-height:1.25; letter-spacing:-0.2px; color:var(--white); margin:2px 0 10px; }
    .entry p { color:var(--tan); font-size:16px; margin-bottom:12px; }
    .entry p:last-child { margin-bottom:0; }
    .entry .entry-link a { font-weight:700; }
    .entry .entry-links { display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }
    .entry .entry-links a { display:inline-block; padding:8px 13px; border:1px solid rgba(217,166,33,0.35); border-radius:10px; font-size:14.5px; font-weight:700; line-height:1.3; }
    .entry .entry-links a:hover { border-color:var(--gold); }
    .support { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:18px 0 6px; }
    .support .card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:18px 20px; }
    .support h3 { color:var(--white); font-size:16px; font-weight:800; margin:0 0 6px; }
    .support p { font-size:15px; line-height:1.65; margin:0; }
    .sig { margin:34px 0 0; padding-top:16px; border-top:1px solid var(--line); }
    .sig .sig-name { color:var(--white); font-weight:800; font-size:17px; }
    .sig .sig-role { color:var(--tan); font-size:14px; }
    .soft-close { text-align:center; border-top:1px solid var(--line); margin:46px 0 16px; padding:28px 0 6px; }
    .soft-close p { color:var(--tan); font-size:16px; margin-bottom:6px; }
    .soft-close .stores a { font-weight:700; }
    .soft-close .stores span { color:var(--gray); margin:0 10px; }
    .soft-close .note { color:var(--gray); font-size:13px; }
    footer .compliance { max-width:720px; margin:0 auto 14px; color:var(--tan); font-size:12.5px; line-height:1.65; }
    @media (max-width:620px){ .support { grid-template-columns:1fr; } .entry-body { padding:18px 18px 20px; } }
    @media (max-width:560px){ h1 { font-size:30px; } article h2 { font-size:23px; } .entry h2 { font-size:22px; } }
"""

COMPLIANCE = ('<p class="compliance">The app is educational. It does not give claims advice, legal guidance, '
              'or predict ratings, and it points veterans to free accredited representatives. '
              'VA Ready is not affiliated with the U.S. Department of Veterans Affairs.</p>')
FOOTER_PAGE = FOOTER.replace("<footer>", "<footer>\n    " + COMPLIANCE, 1)
assert COMPLIANCE in FOOTER_PAGE

def entry_html(e, first):
    paras = "\n".join(f"      <p>{text(p)}</p>" for p in e["paras"])
    link = ""
    links = e.get("links") or ([e["link"]] if e.get("link") else [])
    if len(links) == 1:
        link = f'\n      <p class="entry-link"><a href="{esc(links[0]["url"])}">{text(links[0]["label"])} &rarr;</a></p>'
    elif links:
        link = '\n      <p class="entry-links">' + "".join(f'<a href="{esc(l["url"])}">{text(l["label"])}</a>' for l in links) + "</p>"
    loc = f'<span class="loc">{text(e["location"])}</span>' if e.get("location") else ""
    load = 'loading="eager" fetchpriority="high"' if first else 'loading="lazy"'
    return f'''  <article class="entry" id="{e["id"]}">
    <img src="{img_url(e, "1600.webp")}" srcset="{img_url(e, "900.webp")} 900w, {img_url(e, "1600.webp")} 1600w" sizes="(max-width:760px) 100vw, 716px" alt="{esc(e["photo_alt"])}" width="1600" height="1000" {load} decoding="async">
    <div class="entry-body">
      <div class="entry-meta"><time datetime="{e["date"]}">{text(e["when"])}</time>{loc}</div>
      <h2>{text(e["headline"])}</h2>
{paras}{link}
    </div>
  </article>'''

FEED = '<div class="feed">\n' + "\n".join(entry_html(e, i == 0) for i, e in enumerate(entries)) + "\n  </div>"

BODY_TOP = '''<div class="crumb"><a href="/index.html">Home</a> / In the Community</div>
    <div class="eyebrow">VA Ready &amp; Vet Ready in the Community</div>
    <h1>I built this for veterans, so I show up in person.</h1>
    <p class="lede">I&rsquo;m a retired Army Chief Warrant Officer, and I built VA Ready with a team of fellow veterans and people who know the VA claims process inside and out. This is where you&rsquo;ll find us off the screen, newest first.</p>'''

ABOUT = f'''<article>
    <h2>I&rsquo;m a veteran, not a marketing company</h2>
    <p>No agency went looking for a veteran angle here. I served twenty years in the U.S. Army, retired as a Chief Warrant Officer, and went through the VA claims process myself.</p>
    <p>I dug through scattered rules, made my own checklists, and figured out the steps the hard way. Then I built the tool I wish someone had handed me. <a href="/founders.html">Read my story</a>.</p>
    <p>I don&rsquo;t do it alone. I built VA Ready with <strong>a team of fellow veterans and people with years of hands-on experience in the VA claims process</strong>, including helping other veterans through it. They keep the app honest about what claims really look like on the ground.</p>

    <h2>How we support veterans</h2>
    <div class="support">
      <div class="card">
        <h3>Free accredited help comes first</h3>
        <p>I built the app to point veterans to accredited Veterans Service Organizations like the DAV, the VFW, and county veterans service offices. Their help is free. <a href="/find-a-vso.html">Find a VSO near you</a>.</p>
      </div>
      <div class="card">
        <h3>Free and private</h3>
        <p>The core tools are free, with no account. Your claim information stays on your phone. I don&rsquo;t sell your data, I don&rsquo;t take a cut of your claim, and nothing I charge is tied to your benefits.</p>
      </div>
      <div class="card">
        <h3>I show up in person</h3>
        <p>I&rsquo;d rather meet veterans where they already gather, in the stands and on the flight line, than chase them with ads.</p>
      </div>
      <div class="card">
        <h3>Built from veteran feedback</h3>
        <p>Veterans send reports straight from the app. My team and I read them, check them against the primary sources, and ship the fixes. A lot of every update started as a message from a veteran.</p>
      </div>
    </div>

    <div class="sig">
      <div class="sig-name">Jason, CW2, U.S. Army (Retired)</div>
      <div class="sig-role">Founder, VA Ready &amp; Vet Ready</div>
    </div>
  </article>

  <div class="soft-close">
    <p>Free to download on iPhone and Android.</p>
    <p class="stores"><a href="{IOS}">VA Ready on the App Store</a><span aria-hidden="true">&middot;</span><a href="{esc(ANDROID)}">Vet Ready on Google Play</a></p>
    <p class="note">Same app, two names: VA Ready on iPhone, Vet Ready on Android.</p>
  </div>'''

# ---------- JSON-LD ----------
ORG_ID, FEED_ID, IMG_ID, BC_ID = ORIGIN + "/#organization", canon + "#feed", canon + "#primary-image", canon + "#breadcrumb"
org = {"@type": "Organization", "@id": ORG_ID, "name": "JDL Software LLC", "alternateName": ["VA Ready", "Vet Ready"],
       "url": ORIGIN + "/", "logo": ORIGIN + "/logo.png", "email": "support@vareadyapp.com",
       "description": "Veteran-founded maker of VA Ready (iOS) and Vet Ready (Android), educational apps for veterans working through the VA disability claims process.",
       "founder": {"@type": "Person", "name": "Jason", "jobTitle": "Founder", "honorificSuffix": "CW2, U.S. Army (Retired)", "url": ORIGIN + "/founders.html"},
       "knowsAbout": ["VA disability compensation claims", "38 CFR Part 4, Schedule for Rating Disabilities",
                      "PACT Act presumptive conditions", "Accredited Veterans Service Organizations", "State and federal veterans benefits"],
       "sameAs": [IOS, "https://play.google.com/store/apps/details?id=com.vaready.app", "https://www.tiktok.com/@vareadyapp",
                  "https://www.facebook.com/vareadyapp", "https://www.instagram.com/vareadyapp/"]}
items, sponsored = [], []
for i, e in enumerate(entries, 1):
    anchor = f"{canon}#{e['id']}"
    items.append({"@type": "ListItem", "position": i, "url": anchor, "name": e["headline"]})
    if e.get("sponsored"):
        node = dict(e["sponsored"])
        node.setdefault("@id", anchor + "-sponsored")
        node["sponsor"] = {"@id": ORG_ID}
        if node.get("@type") in ("Project", "Grant"):
            node["funder"] = {"@id": ORG_ID}
        sponsored.append(node)
feed_ld = {"@type": "ItemList", "@id": FEED_ID, "name": "VA Ready in the Community", "numberOfItems": len(items),
           "itemListOrder": "https://schema.org/ItemListOrderDescending", "itemListElement": items}
image = {"@type": "ImageObject", "@id": IMG_ID, "url": ORIGIN + img_url(newest, "1600.webp"),
         "contentUrl": ORIGIN + img_url(newest, "1600.webp"), "width": 1600, "height": 1000, "caption": newest["photo_alt"]}
bc = {"@type": "BreadcrumbList", "@id": BC_ID, "itemListElement": [
      {"@type": "ListItem", "position": 1, "name": "Home", "item": ORIGIN + "/"},
      {"@type": "ListItem", "position": 2, "name": "In the Community", "item": canon}]}
page = {"@type": "CollectionPage", "@id": canon, "url": canon, "name": title, "description": desc, "inLanguage": "en-US",
        "datePublished": "2026-09-11", "dateModified": newest["date"],
        "isPartOf": {"@type": "WebSite", "name": "VA Ready", "url": ORIGIN + "/"},
        "about": {"@id": ORG_ID}, "mainEntity": {"@id": FEED_ID}, "primaryImageOfPage": {"@id": IMG_ID}, "breadcrumb": {"@id": BC_ID}}
LD = {"@context": "https://schema.org", "@graph": [page, org, feed_ld, image, bc] + sponsored}

OG_TITLE = "VA Ready in the Community: Veteran Flights and Georgia Football"
OG_IMG = ORIGIN + img_url(newest, "og.jpg")

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
<meta property="og:title" content="{esc(OG_TITLE)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{OG_IMG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(newest["photo_alt"])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(OG_TITLE)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{OG_IMG}">
<meta name="twitter:image:alt" content="{esc(newest["photo_alt"])}">
<link rel="icon" type="image/png" href="/logo.png">
<link rel="apple-touch-icon" sizes="180x180" href="/logo.png">
<link rel="preload" as="image" href="{img_url(newest, "1600.webp")}" imagesrcset="{img_url(newest, "900.webp")} 900w, {img_url(newest, "1600.webp")} 1600w" imagesizes="(max-width:760px) 100vw, 716px">
<script type="application/ld+json">{json.dumps(LD)}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    {BODY_TOP}
  {FEED}
  {ABOUT}
</div>
{FOOTER_PAGE}
</body>
</html>'''

# ---------- homepage teaser ----------
def excerpt(e, n=150):
    if e.get("teaser"):
        return e["teaser"]
    t = e["paras"][0]
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0].rstrip(",;:.") + "…"

def home_card(e):
    loc = f'\n                <span class="cm-loc">{text(e["location"])}</span>' if e.get("location") else ""
    return f'''            <a class="cm-card" href="community.html#{e["id"]}">
                <img src="img/community/{e["id"]}-900.webp" alt="{esc(e["photo_alt"])}" width="900" height="562" loading="lazy" decoding="async">
                <span class="cm-meta">{text(e["when"])}</span>
                <strong>{text(e["headline"])}</strong>{loc}
                <span class="cm-ex">{text(excerpt(e))}</span>
            </a>'''

START, END = "<!-- COMMUNITY:START", "<!-- COMMUNITY:END -->"
HOME = f'''{START} generated by _generators/gen_community.py from data/community.json. Edit the data, not this block. -->
    <style>
        .cm-home {{ margin-top: 44px; }}
        .cm-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 340px)); justify-content: center; gap: 20px; margin: 0 auto 22px; }}
        .cm-card {{ display: flex; flex-direction: column; background: var(--card); border: 1px solid var(--line); border-radius: 18px; overflow: hidden; text-align: left; color: inherit; text-decoration: none; transition: border-color .2s, transform .2s; }}
        .cm-card:hover {{ border-color: rgba(217,166,33,.55); transform: translateY(-2px); }}
        .cm-card img {{ display: block; width: 100%; height: auto; aspect-ratio: 16 / 10; object-fit: cover; border-bottom: 1px solid var(--line); }}
        .cm-card .cm-meta {{ padding: 14px 16px 0; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; color: var(--gold); }}
        .cm-card strong {{ padding: 5px 16px 0; font-size: 17px; line-height: 1.3; color: var(--white); }}
        .cm-card .cm-loc {{ padding: 3px 16px 0; font-size: 12.5px; color: var(--gray); }}
        .cm-card .cm-ex {{ padding: 8px 16px 16px; font-size: 13.5px; line-height: 1.6; color: var(--tan); }}
    </style>
    <section class="calc-show cm-home" aria-labelledby="cm-home-title">
        <div class="eyebrow-v">VA Ready &amp; Vet Ready in the Community</div>
        <h2 id="cm-home-title">We show up in person.<br><span class="gold">Not just on your phone.</span></h2>
        <p class="cs-sub">Veteran-founded and veteran-run. Here&rsquo;s where you&rsquo;ll find us off the screen.</p>
        <div class="cm-grid">
{chr(10).join(home_card(e) for e in entries[:HOME_TEASER_COUNT])}
        </div>
        <div class="cs-cta"><a href="community.html" class="btn-secondary">See everything we&rsquo;re doing &rarr;</a></div>
    </section>
    {END}'''

# house rules: no em dashes, no AI language, never "prep"/"practice"
for blob, label in ((PAGE, "community.html"), (HOME, "homepage teaser")):
    for needle in ("—", "&mdash;", "\\u2014"):
        assert needle not in blob, f"em dash in {label}"
    assert not re.search(r"\bAI\b", blob), f"'AI' in {label}"
    assert not re.search(r"prep|practice", blob, re.I), f"prep/practice in {label}"
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', PAGE, re.S):
    json.loads(blk)

open(os.path.join(SITE, "community.html"), "w").write(PAGE)

ip = os.path.join(SITE, "index.html")
s = open(ip).read()
if START in s and END in s:
    s = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: HOME, s, count=1, flags=re.S)
    home_note = "homepage teaser refreshed"
else:
    anchor = "    <!-- BY THE NUMBERS -->"
    assert s.count(anchor) == 1, "homepage anchor <!-- BY THE NUMBERS --> not found exactly once"
    s = s.replace(anchor, "    " + HOME + "\n\n" + anchor)
    home_note = "homepage teaser inserted"
open(ip, "w").write(s)

sp = os.path.join(SITE, "sitemap.xml")
xml = open(sp).read()
entry = f'  <url>\n    <loc>{canon}</loc>\n    <lastmod>{newest["date"]}</lastmod>\n    <priority>0.7</priority>\n  </url>\n'
if canon in xml:
    xml = re.sub(r'  <url>\n    <loc>' + re.escape(canon) + r'</loc>\n.*?  </url>\n', lambda m: entry, xml, count=1, flags=re.S)
else:
    xml = xml.replace("</urlset>", entry + "</urlset>")
open(sp, "w").write(xml)

for e in entries:
    print(f"  {e['date']}  {e['id']}: {photo_log[e['id']]}")
print(f"community.html written ({len(entries)} entries); {home_note} (newest {min(len(entries), HOME_TEASER_COUNT)}); sitemap lastmod {newest['date']}; JSON-LD valid")
