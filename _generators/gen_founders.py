#!/usr/bin/env python3
import json, re, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
def esc(s): return html.escape(s or "", quote=True)

gtext = open(os.path.join(HERE,"gen_guides.py")).read()
m = re.search(r'CSS = """(.*?)"""', gtext, re.S)
CSS = m.group(1) if m else ""
CSS += """
    .founder-hero { display:flex; gap:26px; align-items:flex-start; flex-wrap:wrap; margin:6px 0 10px; }
    .founder-hero .fh-text { flex:1; min-width:260px; }
    .pphoto { width:150px; height:150px; border-radius:50%; flex-shrink:0; border:2px solid var(--gold);
        background:var(--card); display:flex; align-items:center; justify-content:center; overflow:hidden; }
    .pphoto img { width:100%; height:100%; object-fit:cover; }
    .pphoto .mono { font-size:54px; font-weight:800; color:var(--gold); font-family:Georgia,serif; }
    .pphoto img { object-position:50% 28%; }
    .fimg { width:100%; max-width:520px; height:auto; border-radius:14px; border:1px solid var(--line); margin:14px 0 6px; display:block; }
    .photo-row { display:flex; gap:14px; flex-wrap:wrap; margin:16px 0 6px; }
    .photo-row figure { flex:1; min-width:200px; margin:0; }
    .photo-row img { width:100%; height:260px; object-fit:cover; object-position:50% 35%; border-radius:14px; border:1px solid var(--line); display:block; }
    .photo-row img.crop-top { object-position:50% 0; }
    figure.fig { margin:16px 0 6px; max-width:430px; }
    figure.fig img { width:100%; height:auto; border-radius:14px; border:1px solid var(--line); display:block; }
    figcaption { color:var(--gray); font-size:13px; font-style:italic; margin-top:7px; }
    .sig { margin:26px 0 6px; padding-top:16px; border-top:1px solid var(--line); }
    .sig .sig-name { color:var(--white); font-weight:800; font-size:17px; }
    .sig .sig-role { color:var(--tan); font-size:14px; }
    article h2 { margin-top:28px; }
    .pull { border-left:3px solid var(--gold); padding:4px 0 4px 16px; margin:18px 0; color:var(--white); font-size:18px; font-weight:600; line-height:1.5; }
"""

NAV = """<nav>
    <a href="/index.html" class="nav-brand"><img src="/logo.png" alt="VA Ready logo" width="34" height="34"><span>VA READY <span style="color:var(--gray);font-weight:400;">/</span> VET READY</span></a>
    <div class="nav-links"><a href="/va-disability-calculator.html">Calculator</a><a href="/conditions.html">Conditions</a><a href="/states.html">State Benefits</a><a href="/guides.html">Guides</a><a href="/founders.html">Our Story</a><a href="/index.html#download">Get the App</a></div>
</nav>"""
FOOTER = """<footer>
    <p>&copy; 2026 JDL Software LLC. VA Ready (iOS) &amp; Vet Ready (Android) are not affiliated with the U.S. Department of Veterans Affairs.</p>
    <div class="footer-links"><a href="/index.html">Home</a><a href="/conditions.html">Conditions</a><a href="/states.html">State Benefits</a><a href="/guides.html">Guides</a><a href="/va-disability-calculator.html">Calculator</a><a href="/founders.html">Our Story</a><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a></div>
</footer>
<script defer src="/_vercel/insights/script.js"></script>
<script defer src="/track.js"></script>"""

DLBTNS = """<div class="btns"><a href="https://apps.apple.com/app/id6761733758" class="btn">Get VA Ready for iOS</a><a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US" class="btn ghost">Get Vet Ready for Android</a></div>"""

canon = "https://vareadyapp.com/founders.html"
title = "About VA Ready &mdash; Built by a Retired Army Chief Who Filed His Own Claim"
desc = "VA Ready was built by Jason — a retired U.S. Army Chief Warrant Officer who filed his own claim to 100% P&T. The story behind the app, chief to soldier."
desc = desc[:160]

person = {"@type":"Person","name":"Jason","honorificSuffix":"CW2, U.S. Army (Retired)",
  "jobTitle":"Founder","worksFor":{"@type":"Organization","name":"JDL Software LLC"},
  "image":"https://vareadyapp.com/img/jason_drill.jpg",
  "description":"Retired U.S. Army Chief Warrant Officer (CW2). Served as a 19D Cavalry Scout (enlisted, to E-7) and a 131A Field Artillery Targeting Technician. Deployed to Iraq and Afghanistan. Founder of the VA Ready / Vet Ready disability-claims app."}
org = {"@type":"Organization","name":"VA Ready","alternateName":"Vet Ready","url":"https://vareadyapp.com/",
  "logo":"https://vareadyapp.com/logo.png","parentOrganization":{"@type":"Organization","name":"JDL Software LLC"},
  "founder":{"@type":"Person","name":"Jason"}}
aboutpage = {"@context":"https://schema.org","@type":"AboutPage","name":"About VA Ready",
  "url":canon,"description":re.sub("&mdash;","-",desc),"mainEntity":person,"about":org,"inLanguage":"en-US"}
bc = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
  {"@type":"ListItem","position":2,"name":"Our Story","item":canon}]}

PHOTO_HERO = '''<div class="pphoto"><img src="/img/jason_drill.jpg" alt="Jason, founder of VA Ready, as an Army Drill Sergeant in dress blues" width="150" height="150" loading="eager"></div>'''

BODY = f'''<div class="founder-hero">
    {PHOTO_HERO}
    <div class="fh-text">
      <div class="eyebrow">Our Story</div>
      <h1 style="margin:6px 0 10px;">I built VA Ready after filing my own claim.</h1>
      <p class="lede">I&rsquo;m Jason &mdash; a retired Army Chief Warrant Officer. After twenty years in uniform and my own trip through the VA claims process, I built the tool I wish someone had handed me. Here&rsquo;s the why.</p>
    </div>
  </div>
  <article>
    <h2>Twenty years, then the paperwork</h2>
    <p>I spent two decades in the Army. I came up enlisted as a <strong>19D Cavalry Scout</strong>, made it to Sergeant First Class (E-7), and then earned my appointment as a <strong>131A Field Artillery Targeting Technician</strong> &mdash; a warrant officer. A Chief. The job took me to Iraq in 2006 and again in 2008&ndash;2009, to Afghanistan in 2011&ndash;2012, plus rotations through Europe, South Korea, and Kuwait. I retired in 2026.</p>
    <div class="photo-row">
      <figure><img class="crop-top" src="/img/jason_private.jpg" alt="Jason as a young soldier deployed overseas" width="600" height="833" loading="lazy"><figcaption>Where it started &mdash; a young Scout, downrange.</figcaption></figure>
      <figure><img src="/img/jason_afghan.jpg" alt="Jason resting during a deployment to Afghanistan" width="600" height="398" loading="lazy"><figcaption>Afghanistan, 2011&ndash;2012. The grind never made the brochure.</figcaption></figure>
    </div>
    <p>When it was my turn to transition out, I filed my own claim through the <strong>Benefits Delivery at Discharge (BDD)</strong> program. I was rated <strong>100% Permanent &amp; Total on the first pass</strong>. I&rsquo;m proud of that &mdash; but I&rsquo;ll be straight with you about what it took: I had to build my own checklists, dig through an overwhelming pile of scattered information, and figure out most of the steps on my own. That result came from my service and my evidence. It wasn&rsquo;t handed to me, and it isn&rsquo;t a promise to anyone else &mdash; every claim stands on its own.</p>

    <h2>The knowledge no one handed me</h2>
    <p>Here&rsquo;s something I noticed along the way. As an enlisted soldier &mdash; all the way up to E-7 &mdash; nobody really talked about the VA. It wasn&rsquo;t until I put on the warrant officer&rsquo;s bars that I found a different culture. <strong>Chiefs mentor.</strong> They talk openly about the things that matter later, and they take care of their people. That &ldquo;chief knowledge&rdquo; changed how I left the service.</p>
    <figure class="fig"><img src="/img/wocs_grad.jpg" alt="Jason at his Warrant Officer Candidate School graduation in Army Service Uniform" width="528" height="528" loading="lazy"><figcaption>Warrant Officer Candidate School graduation &mdash; pinning on the bars, and stepping into the Chief community.</figcaption></figure>
    <p class="pull">VA Ready is my way of handing that knowledge down &mdash; to every soldier, regardless of rank. Chief to soldier.</p>

    <h2>How it actually started</h2>
    <p>The honest version: I&rsquo;d already tried building apps during my transition. They flopped. But I learned how to ship. Last year, in a passing conversation with a good friend and fellow retired Chief &mdash; <strong>Pablo</strong> &mdash; we floated the idea that something like this could really help. Then it just sat there for a while.</p>
    <p>One Easter morning I woke up wanting to be productive, so I started wireframing it out. It got addicting fast, and it looked right. I put my head down for two weeks, shipped it &mdash; and I&rsquo;ve been improving it almost every day since.</p>

    <h2>I&rsquo;m not doing this alone</h2>
    <p>To make sure VA Ready grows around what veterans actually need &mdash; not just what I think they need &mdash; I brought on <strong>Andrew</strong>, a battle buddy with extensive experience navigating the VA claims process and helping others through it. He keeps us honest about the real world: what claims look like on the ground, and what veterans are actually asking for.</p>

    <h2>What VA Ready is &mdash; and what it isn&rsquo;t</h2>
    <p>It&rsquo;s <strong>free</strong>, and it&rsquo;s <strong>private</strong>. No account just to look around. We don&rsquo;t sell your data, and we don&rsquo;t track you the way most sites do. We&rsquo;re independent &mdash; not a big claims company taking a cut of your back pay, and not affiliated with the Department of Veterans Affairs.</p>
    <p>The app won&rsquo;t file for you, and it won&rsquo;t promise you a rating. What it <em>does</em> is give you the map I had to draw for myself: your conditions and the real rating criteria, the presumptives your service may have earned, the peer-reviewed research behind your conditions, every-state benefits, and a clear path to file <em>ready</em>. The goal is simple &mdash; that you walk in better prepared than I was.</p>

    <h2>If something&rsquo;s missing, tell me</h2>
    <p>If this helps even one veteran walk into their claim more prepared than I was, it did its job. Download it, put it to work &mdash; and if there&rsquo;s something missing or something we can do better, reach out. I&rsquo;m listening.</p>
    {DLBTNS}

    <div class="sig">
      <div class="sig-name">&mdash; Jason, CW2, U.S. Army (Retired)</div>
      <div class="sig-role">Founder, VA Ready &amp; Vet Ready &middot; JDL Software LLC</div>
    </div>
  </article>
  <div class="disclaimer">VA Ready and Vet Ready are products of JDL Software LLC and are not affiliated with, endorsed by, or sponsored by the U.S. Department of Veterans Affairs. The founder&rsquo;s 100% P&amp;T rating reflects his own service and evidence and is not a prediction or guarantee of any result &mdash; your claim depends entirely on your own circumstances, documentation, and exam. This page and the app are for general informational purposes only and are not legal or medical advice. Always verify current criteria at VA.gov and consider consulting a VA-accredited representative.</div>'''

PAGE = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="About VA Ready &mdash; Built by a Retired Army Chief">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://vareadyapp.com/img/jason_drill.jpg">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="/logo.png">
<script type="application/ld+json">{json.dumps(bc)}</script>
<script type="application/ld+json">{json.dumps(aboutpage)}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / Our Story</div>
    {BODY}
</div>
{FOOTER}
</body>
</html>'''

open(os.path.join(SITE, "founders.html"), "w").write(PAGE)

# add to sitemap if missing
sp = os.path.join(SITE, "sitemap.xml")
xml = open(sp).read()
if canon not in xml:
    xml = xml.replace("</urlset>", f'  <url>\n    <loc>{canon}</loc>\n    <lastmod>2026-06-08</lastmod>\n    <priority>0.7</priority>\n  </url>\n</urlset>')
    open(sp, "w").write(xml)
    print("founders.html written; sitemap +1")
else:
    print("founders.html written; sitemap already had it")
# validate JSON-LD
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', PAGE, re.S):
    json.loads(blk)
print("JSON-LD valid; page bytes:", len(PAGE))
