#!/usr/bin/env python3
"""Vet Ready for Android landing page (Google Play listing com.vaready.app).

Vet Ready is the Android edition of VA Ready (the Google Play name; never rename it).
Template parts (style, nav, footer) come from ../va-disability-pay-rates.html, like gen_windows.py.
Counts checked against Supabase 2026-11-27. Screenshots: img/android-*.jpg, from the Android 3.3.0
emulator captures (3 Feature previews/2026-11-25 Android port). Prices: Google Play, live 2026-11-24.
"""
import json, os, re, html
HERE = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(HERE)
OUT = os.path.join(SITE, "va-disability-app-for-android.html")
PLAY = "https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US"
CANON = "https://vareadyapp.com/va-disability-app-for-android.html"
PUBLISHED = "2026-11-27"
esc = lambda s: html.escape(s, quote=True)

live = open(os.path.join(SITE, "va-disability-pay-rates.html")).read()
style = re.search(r"<style>.*?</style>", live, re.S).group(0)
nav = re.search(r"<nav>.*?</nav>", live, re.S).group(0)
footer = re.search(r"<footer>.*?</body>", live, re.S).group(0)
extra = """<style>
    .phones { display:grid; grid-template-columns:repeat(3, 1fr); gap:14px; margin:22px 0 28px; }
    .phones figure { margin:0; }
    .phones img { width:100%; height:auto; display:block; border-radius:14px; border:1px solid var(--line); }
    .phones figcaption { color:var(--gray); font-size:13.5px; margin-top:8px; }
    @media (max-width:640px) { .phones { grid-template-columns:repeat(2, 1fr); } .phones figure:nth-child(3) { display:none; } }
    .facts { color:var(--tan); font-size:15px; margin:10px 0 0; max-width:68ch; }
    .btns .btn svg { width:20px; height:20px; vertical-align:-4px; margin-right:8px; }
</style>"""

title = "Vet Ready: VA Disability Calculator App for Android, Free"
desc = ("Vet Ready is the free VA disability calculator and claim app for Android: real VA rating math, "
        "your Claim File, C&P exam prep, Wear and Tear and VSO search. On Google Play, no account.")

features = [
 ("Know your rating",
  "See your combined rating with real VA math, including the bilateral factor, and your estimated monthly pay. Each of 765 conditions carries its full 38 CFR rating criteria, so you know what the examiner measures. TDIU and SMC show what each would change."),
 ("Find conditions by what you did",
  "Wear and Tear lists 226 things you did in service, from rucking and kicking in doors to flight decks and Camp Lejeune. Mark what you did and the linked conditions gather into one list, each with the studies behind it and the records that prove you did it."),
 ("Try a claim without touching yours",
  "Claim scenarios let you build up to four other versions of your claim on My Claim. Scenario 1 stays your claim and is the only one in your forms and exports."),
 ("Keep your claim in one place",
  "Scan, photograph or import every document into your Claim File. Each gets a label that matches the VA's own document types, a date and the condition it supports, and Ready for VA builds a dated folder for each condition, named the way VA.gov asks."),
 ("Get ready for your C&P exam",
  "A C&P/DBQ guideline for each condition, an exam questionnaire you answer in your own words, and peer-reviewed studies mapped to your diagnostic codes. Log symptoms on your phone as they happen, with reminders."),
 ("Find what you may be missing",
  "Claim Intel shows the conditions commonly claimed for your MOS, AFSC or rating, plus PACT Act presumptives from your bases and aircraft. 1,106 military job codes and 834 bases with exposure mapping are built in."),
 ("Find free help",
  "Search 8,959 accredited VSO offices by name, county, city or ZIP, or tap Near me. Read ratings from other veterans and hand your rep a VSO Packet."),
 ("Benefits and filing",
  "Federal and state benefits at your rating (644 state entries), the current pay chart, a back pay estimate, and 62 filing guides covering appeals, proposed reductions, protected ratings and more."),
]
free_pro = [
 ("Combined rating and estimated pay", "Full 38 CFR rating criteria for every condition"),
 ("Claim File and Ready for VA folder", "Claim Intel with Wear and Tear"),
 ("Symptom and medication logs", "Claim scenarios"),
 ("Texas state benefits", "All 50 states' benefits"),
 ("Federal benefits at every rating", "Sharing and exporting documents and packets"),
]
faqs = [
 ("Why is the Android app called Vet Ready?",
  "Vet Ready is the app's name on Google Play. It is the same product as VA Ready on iPhone, iPad, Mac and Windows, with the same features, and your backups restore across all of them."),
 ("Is there a VA disability calculator app for Android?",
  "Yes. Vet Ready on Google Play calculates your combined VA disability rating with the VA's own math, including the bilateral factor, and shows your estimated monthly pay. The calculator is free."),
 ("Does Vet Ready cost anything?",
  "The download is free, with no account. Pro is billed through Google Play: $8.99 a month, $69.99 a year, or $89.99 once."),
 ("Which Android versions does Vet Ready support?",
  "Android 8.0 or later, on phones and tablets."),
 ("Where is my claim data stored?",
  "On your phone. Vet Ready has no account and does not upload your claim, documents or notes. You can back up to a file you choose, documents included."),
 ("Is Vet Ready affiliated with the VA?",
  "No. Vet Ready is not affiliated with, endorsed by, or connected to the U.S. Department of Veterans Affairs or any government agency. Estimates are not VA decisions."),
]
ld = [
 {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
   {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
   {"@type":"ListItem","position":2,"name":"Vet Ready for Android","item":CANON}]},
 {"@context":"https://schema.org","@type":"SoftwareApplication","name":"Vet Ready","alternateName":["VA Ready for Android","Vet Ready app"],
  "description":desc,"operatingSystem":"Android 8.0 or later","applicationCategory":"UtilitiesApplication",
  "applicationSubCategory":"VA disability claim tools","softwareVersion":"3.3.0","url":CANON,"downloadUrl":PLAY,"installUrl":PLAY,
  "image":"https://vareadyapp.com/logo.png","screenshot":"https://vareadyapp.com/img/android-my-claim.jpg",
  "datePublished":PUBLISHED,"publisher":{"@type":"Organization","name":"JDL Software LLC","url":"https://vareadyapp.com/"},
  "offers":{"@type":"Offer","price":"0.00","priceCurrency":"USD","availability":"https://schema.org/InStock"}},
 {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
   {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]},
]
lds = "\n".join(f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in ld)
PLAY_SVG = '<svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M3.609 1.814L13.792 12 3.609 22.186A.997.997 0 013 21.286V2.714a.997.997 0 01.609-.9zm10.89 10.892l2.302 2.302-12.4 7.16 10.098-9.462zM18.16 9.18l2.578 1.49a1 1 0 010 1.66l-2.66 1.534-2.99-2.99 3.072-1.694zM4.398 1.815l12.4 7.16-2.282 2.282L4.398 1.815z"/></svg>'
def phone(name, alt, cap):
    return f'<figure><img src="/img/{name}.jpg" alt="{esc(alt)}" width="538" height="1200" loading="lazy"><figcaption>{esc(cap)}</figcaption></figure>'
phones = ('<div class="phones">'
    + phone("android-my-claim", "Vet Ready on Android, My Claim: a 50% combined rating and $1,376.90 estimated monthly pay.", "My Claim: your combined rating and estimated pay.")
    + phone("android-wear-and-tear", "Vet Ready on Android, Claim Intel Wear and Tear: close quarters battle marked, with 6 linked conditions.", "Wear and Tear: conditions from what you did.")
    + phone("android-scenarios", "Vet Ready on Android, My Claim with Scenario 2 open, marked as a scenario, not your claim.", "Claim scenarios: try a claim without touching yours.")
    + "</div>")
feat = "".join(f'<div class="faq-item"><h3>{esc(t)}</h3><p>{esc(p)}</p></div>' for t, p in features)
rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in free_pro)
# NO_SLOP W1: no question headings, so each question is bold text, not an h3
faq_html = "".join(f'<div class="faq-item"><p><strong>{esc(q)}</strong></p><p>{esc(a)}</p></div>' for q, a in faqs)
cta = f'<div class="btns page-cta"><a href="{PLAY}" class="btn">{PLAY_SVG}Get Vet Ready on Google Play</a><a href="/va-disability-calculator.html" class="btn ghost">Free rating calculator in your browser</a></div>'

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
<meta property="og:type" content="website">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{CANON}">
<meta property="og:image" content="https://vareadyapp.com/img/android-my-claim.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
{lds}
{style}
{extra}
</head>
<body>
{nav}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / Vet Ready for Android</div>
    <h1>Vet Ready for Android</h1>
    <p class="lede">Vet Ready is VA Ready on Android. Calculate your combined VA disability rating, build your claim and keep your evidence in order on your phone. Free on Google Play, no account.</p>
    {cta}
    <p class="facts">4.7 on Google Play. Android 8.0 or later, phones and tablets.</p>
    {phones}
    <article>
        <h2>What you can do on Android</h2>
        {feat}
        <h2>Free and Pro</h2>
        <div class="tbl-wrap"><table class="pt"><thead><tr><th>Free</th><th>Pro</th></tr></thead><tbody>{rows}</tbody></table></div>
        <p>Pro is billed through Google Play: $8.99 a month, $69.99 a year, or $89.99 once.</p>
        <h2>Your data stays on your phone</h2>
        <p>Vet Ready has no account. Your claim, documents and notes live on your phone, and you can back them up to a file you choose, documents included. A backup made on Android restores in VA Ready on iPhone, iPad, Mac or Windows.</p>
        <h2>Questions</h2>
        {faq_html}
    </article>
    {cta}
    <p class="trustline">Also on <a href="https://apps.apple.com/app/id6761733758">iPhone, iPad and Mac</a> and <a href="/va-disability-app-for-windows.html">Windows</a>. See <a href="/features.html">every feature and how to use it</a>, or try the <a href="/va-disability-calculator.html">free calculator in your browser</a>.</p>
    <div class="disclaimer">Vet Ready and VA Ready are not affiliated with, endorsed by, or connected to the U.S. Department of Veterans Affairs or any government agency. Estimates are not VA decisions. This page is not financial or legal advice.</div>
</div>
{footer}
"""
assert "—" not in page, "em dash"
assert len(re.findall(r"<h1", page)) == 1
open(OUT, "w").write(page)
sp = os.path.join(SITE, "sitemap.xml"); xml = open(sp).read()
if CANON not in xml:
    open(sp, "w").write(xml.replace("</urlset>", f"  <url>\n    <loc>{CANON}</loc>\n    <lastmod>{PUBLISHED}</lastmod>\n    <priority>0.9</priority>\n  </url>\n</urlset>"))
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S): json.loads(b)
print("wrote", OUT)
