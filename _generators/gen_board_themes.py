#!/usr/bin/env python3
"""What helps and hurts a VA claim, from Board of Veterans' Appeals decisions (one page, cross-condition).

Data: data/board_themes.json (themes and totals built from the board_evidence cards; bullets are copied
verbatim from the cards that also render on the condition pages). Template parts come from the live
pay-rates page like gen_windows.py. Page: /what-helps-and-hurts-va-claims.html.
Re-run after gen_guides.py (it rebuilds the sitemap).
"""
import json, os, re, html
HERE = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(HERE)
OUT = os.path.join(SITE, "what-helps-and-hurts-va-claims.html")
CANON = "https://vareadyapp.com/what-helps-and-hurts-va-claims.html"
PUBLISHED = "2026-11-15"
esc = lambda s: html.escape(s, quote=True)

D = json.load(open(os.path.join(HERE, "data", "board_themes.json")))
T, themes = D["totals"], D["themes"]
# condition pages that carry the full Board section
src = open(os.path.join(HERE, "gen_conditions.py")).read()
SLUG = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\s*\("(\d{4})","([a-z0-9-]+)","', src, re.M))
def cond_link(dc, name):
    s = SLUG.get(dc)
    return f'<a href="/conditions/{s}.html#board-cases">{esc(name)}</a>' if s else esc(name)

live = open(os.path.join(SITE, "va-disability-pay-rates.html")).read()
style = re.search(r"<style>.*?</style>", live, re.S).group(0)
nav = re.search(r"<nav>.*?</nav>", live, re.S).group(0)
footer = re.search(r"<footer>.*?</body>", live, re.S).group(0)
extra = """<style>
    .theme { margin:0 0 26px; padding:0 0 4px; }
    .theme h3 { margin:0 0 6px; }
    .theme .seen { color:var(--gray); font-size:13.5px; margin:0 0 8px; }
    .theme ul { margin:8px 0 0; padding-left:20px; max-width:68ch; }
    .theme li { margin:0 0 6px; }
    .theme li .on { color:var(--gray); font-size:13.5px; display:block; }
    .toc { max-width:68ch; margin:14px 0 24px; padding-left:20px; }
    .tags { color:var(--tan); font-size:15px; max-width:68ch; }
</style>"""

N = T["cards"]
title = "What Helps and Hurts a VA Claim: Patterns From Board Decisions"
desc = (f"What the Board of Veterans' Appeals pointed to when it helped or hurt a VA disability claim, across {N} conditions: "
        f"medical opinions, VA exams, service records, lay statements and more. Cases differ.")

helped = [t for t in themes if t["direction"] == "helped"]
hurt = [t for t in themes if t["direction"] == "hurt"]
def slug(t): return re.sub(r"[^a-z0-9]+", "-", t["title"].lower()).strip("-")
def theme_html(t):
    ex = "".join(f'<li>{esc(e["bullet"])}<span class="on">{cond_link(e["dc"], e["condition"])}</span></li>' for e in t["examples"])
    return (f'<div class="theme" id="{slug(t)}"><h3>{esc(t["title"])}</h3>'
            f'<p>{esc(t["summary"])}</p><p class="seen">Seen on {t["card_count"]} conditions.</p><ul>{ex}</ul></div>')
toc = lambda L: "".join(f'<li><a href="#{slug(t)}">{esc(t["title"])}</a></li>' for t in L)

faqs = [
 ("Where do these patterns come from?",
  f"From decisions of the Board of Veterans' Appeals, which VA publishes. For {N} conditions we read the decisions and kept only patterns that showed up in at least three different decisions. Every finding in the app lists the decision numbers behind it."),
 ("Does a pattern here mean my claim will be granted or denied?",
  "No. These are patterns in past decisions, not odds. Each case turns on its own records, and the Board decides on the whole file."),
 ("What does a sent-back decision mean?",
  "The Board returned the claim for a new exam or medical opinion. It is not a grant, and it is not a denial. It means the earlier exam or opinion was not enough to decide."),
 ("Why do VA opinions that skip your records lose weight?",
  "Across many conditions the Board found negative VA opinions inadequate when they ignored the veteran's account, relied on missing records, gave no reasons or used wrong facts. Opinions with a clear reason tied to the record carried weight."),
 ("Where can I see the findings for my condition?",
  "The most-claimed conditions have their own page with the full helped and hurt list and the decision numbers. VA Ready shows the same breakdown on your condition cards in the app."),
 ("Is this legal advice?",
  "No. VA Ready is not a law firm and is not affiliated with the U.S. Department of Veterans Affairs. For help with a claim, an accredited VSO is free."),
]
guides = [
 ("/guides/nexus-letters.html", "Nexus letters: what a medical opinion needs to say"),
 ("/guides/c-and-p-exam-preparation.html", "C&P exam preparation"),
 ("/guides/building-your-evidence-package.html", "Building your evidence package"),
 ("/guides/buddy-statements.html", "Buddy statements"),
 ("/guides/secondary-service-connection.html", "Secondary service connection"),
 ("/guides/10-mistakes-that-get-claims-denied.html", "10 mistakes that get claims denied"),
 ("/guides/denied-your-appeal-options-explained.html", "Denied? Your appeal options explained"),
 ("/guides/supplemental-claims.html", "Supplemental claims"),
 ("/va-claim-evidence.html", "How to document a VA claim: symptom log and VSO packet"),
 ("/find-a-vso.html", "Find an accredited VSO near you (free)"),
]
IOS = "https://apps.apple.com/app/id6761733758"; AND = "https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US"
cta = (f'<div class="btns page-cta"><a href="/index.html#download" class="btn">Get VA Ready</a>'
       f'<a href="/conditions.html" class="btn ghost">See your condition</a></div>')
ld = [
 {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
   {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
   {"@type":"ListItem","position":2,"name":"What helps and hurts a VA claim","item":CANON}]},
 {"@context":"https://schema.org","@type":"Article","headline":title,"description":desc,"url":CANON,
  "datePublished":PUBLISHED,"dateModified":PUBLISHED,"mainEntityOfPage":CANON,
  "image":"https://vareadyapp.com/logo.png",
  "author":{"@type":"Organization","name":"VA Ready","url":"https://vareadyapp.com/"},
  "publisher":{"@type":"Organization","name":"JDL Software LLC","url":"https://vareadyapp.com/"}},
 {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
   {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]},
]
lds = "\n".join(f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in ld)
faq_html = "".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q, a in faqs)
glist = "".join(f'<li><a href="{u}">{esc(t)}</a></li>' for u, t in guides)

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{CANON}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{CANON}">
<meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
{lds}
{style}
{extra}
</head>
<body>
{nav}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / What helps and hurts a VA claim</div>
    <h1>What helps and hurts a VA claim, according to Board decisions</h1>
    <p class="lede">We read thousands of decisions of the Board of Veterans&rsquo; Appeals across {N} conditions and kept the patterns that repeat. Here is what the Board pointed to when it helped a veteran&rsquo;s claim, and what it pointed to when it did not.</p>
    <p class="tags">From Board of Veterans&rsquo; Appeals decisions. Cases differ. These are patterns, not odds.</p>
    <article>
        <h2>How to read this page</h2>
        <p>Each pattern below showed up in at least three different Board decisions, usually on many conditions. We list the Board&rsquo;s own reasoning in plain words, not a prediction. A decision that sent a claim back for a new exam is not a win, and we say so where it applies. The most-claimed conditions have a page with every finding and the decision numbers; the others are in the VA Ready app.</p>
        <h2>What helped claims</h2>
        <ol class="toc">{toc(helped)}</ol>
        {"".join(theme_html(t) for t in helped)}
        <h2>What hurt claims</h2>
        <ol class="toc">{toc(hurt)}</ol>
        {"".join(theme_html(t) for t in hurt)}
        <h2>Use it on your own claim</h2>
        <p>Match these patterns to what is in your file: a reasoned medical opinion, an exam that covered your symptoms, records from service, a dated symptom log. Then ask an accredited VSO to review it, for free.</p>
        <ul class="toc">{glist}</ul>
        <p>Looking for your condition? <a href="/conditions.html">Browse the most-claimed conditions</a>, each with its full Board findings. In the app, the same breakdown sits on your condition cards, with the decision numbers behind each finding. Get it on <a href="{IOS}">iPhone and iPad</a>, <a href="{AND}">Android</a> or <a href="/va-disability-app-for-windows.html">Windows</a>.</p>
        <h2>Questions</h2>
        {faq_html}
    </article>
    {cta}
    <div class="disclaimer">VA Ready is not affiliated with, endorsed by, or connected to the U.S. Department of Veterans Affairs or any government agency. This page summarizes public Board of Veterans&rsquo; Appeals decisions. It is not legal advice and does not predict how any claim will be decided.</div>
</div>
{footer}
"""
open(OUT, "w").write(page)
sp = os.path.join(SITE, "sitemap.xml"); xml = open(sp).read()
if CANON not in xml:
    open(sp, "w").write(xml.replace("</urlset>", f"  <url>\n    <loc>{CANON}</loc>\n    <lastmod>{PUBLISHED}</lastmod>\n    <priority>0.8</priority>\n  </url>\n</urlset>"))
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S): json.loads(b)
print("wrote", OUT, len(page))
