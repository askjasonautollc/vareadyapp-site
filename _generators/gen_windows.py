#!/usr/bin/env python3
"""VA Ready for Windows landing page (Microsoft Store listing 9P8XFCQVFJHF).

Template parts (style, nav, footer, closing CTA) come from ../va-disability-pay-rates.html so the
page tracks the shared look. Counts match dist/store-listing/LISTING.txt in the Windows project
(checked against Supabase 2026-10-13). Screenshots: img/windows-*.jpg, resized from the Store shots.
"""
import json, os, re, html
HERE = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(HERE)
OUT = os.path.join(SITE, "va-disability-app-for-windows.html")
MS = "https://apps.microsoft.com/detail/9p8xfcqvfjhf"
CANON = "https://vareadyapp.com/va-disability-app-for-windows.html"
PUBLISHED = "2026-10-18"
esc = lambda s: html.escape(s, quote=True)

live = open(os.path.join(SITE, "va-disability-pay-rates.html")).read()
style = re.search(r"<style>.*?</style>", live, re.S).group(0)
nav = re.search(r"<nav>.*?</nav>", live, re.S).group(0)
footer = re.search(r"<footer>.*?</body>", live, re.S).group(0)
extra = """<style>
    .shot { margin:22px 0 28px; }
    .shot img { width:100%; height:auto; display:block; border-radius:8px; border:0; }
    .shot figcaption { color:var(--gray); font-size:13.5px; margin-top:8px; max-width:68ch; }
    .facts { color:var(--tan); font-size:15px; margin:10px 0 0; max-width:68ch; }
    .btns .btn svg { width:20px; height:20px; vertical-align:-4px; margin-right:8px; }
</style>"""

title = "VA Ready for Windows: VA disability calculator and claim organizer for PC"
desc = ("VA Ready for Windows is a free VA disability calculator and claim organizer for Windows 10 and 11. "
        "Real VA rating math, a Claim File, C&P exam prep and VSO search. On the Microsoft Store.")

features = [
 ("Know your rating",
  "See your combined rating with real VA math, including the bilateral factor, and your estimated monthly pay. Each of 765 conditions carries its full 38 CFR rating criteria, so you know what the examiner measures. TDIU and SMC calculators show what each would change."),
 ("Keep your claim in one place",
  "Import every document into your Claim File. Each gets a label that matches the VA's own document types, a date and the condition it supports, and your evidence checklist ticks itself. Drag and drop files, or save them to the VA Ready Documents folder and they import on their own."),
 ("Ready for VA",
  "One click builds a dated folder for each condition: your records, signed buddy statements, symptom logs and an optional claim journal. Every file is named with the document type to pick on VA.gov, with an upload checklist on top."),
 ("Get ready for your C&P exam",
  "A C&P/DBQ Guideline for each condition, an exam questionnaire you answer in your own words before the exam, and peer-reviewed studies mapped to your diagnostic codes, all exportable to PDF."),
 ("Find what you may be missing",
  "Claim Intel shows the conditions commonly claimed for your MOS, AFSC or rating, plus PACT Act presumptives from the bases you served at and the aircraft you worked on. 1,102 military job codes and 827 bases with exposure mapping are built in."),
 ("Never miss a VA date",
  "One Upcoming list for your Intent to File expiration, VA evidence requests, decision review windows, C&P exams and VSO visits. Print the schedule for the fridge."),
 ("Find free help",
  "Search 8,957 VSO offices, read ratings from other veterans, track visits, and hand your rep a VSO Packet. VA Ready saves the visit and a reminder on your PC. It does not book or confirm an appointment."),
 ("Benefits and back pay",
  "Federal and state benefits at your rating (644 state entries), the current pay rate chart, and a back pay estimate from your effective date. 60 filing guides cover appeals, proposed reductions, protected ratings and more."),
]
free_pro = [
 ("Combined rating and estimated pay", "Full 38 CFR rating criteria for every condition"),
 ("Claim File and Ready for VA folder", "All 50 states' benefits"),
 ("Texas state benefits", "Claim Intel"),
 ("Federal benefits at every rating", "Sharing and exporting documents and packets"),
]
faqs = [
 ("Is VA Ready available for Windows?",
  "Yes. VA Ready is on the Microsoft Store for Windows 10 (version 1809 or later) and Windows 11, 64-bit. It is the same product as VA Ready on iPhone, iPad and Mac and Vet Ready on Android."),
 ("Does VA Ready for Windows cost anything?",
  "The download is free, with no account. Pro adds full rating criteria, all 50 states, Claim Intel and sharing or exporting documents. Pro is billed through your Microsoft account: $4.99 a month, $39.99 a year, or $59.99 once."),
 ("Where is my claim data stored?",
  "On your PC. VA Ready has no account and does not upload your claim, documents or notes. You can back up to a folder you choose, documents included."),
 ("Does it need an internet connection?",
  "Yes, for the conditions, benefits and VSO data it loads. Your own claim and documents stay on your PC."),
 ("Is VA Ready affiliated with the VA?",
  "No. VA Ready is not affiliated with, endorsed by, or connected to the U.S. Department of Veterans Affairs or any government agency. Estimates are not VA decisions."),
]
ld = [
 {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
   {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
   {"@type":"ListItem","position":2,"name":"VA Ready for Windows","item":CANON}]},
 {"@context":"https://schema.org","@type":"SoftwareApplication","name":"VA Ready for Windows","alternateName":"VA Ready",
  "description":desc,"operatingSystem":"Windows 10, Windows 11","applicationCategory":"UtilitiesApplication",
  "applicationSubCategory":"VA disability claim tools","softwareVersion":"3.0.1","url":CANON,"downloadUrl":MS,"installUrl":MS,
  "image":"https://vareadyapp.com/logo.png","screenshot":"https://vareadyapp.com/img/windows-my-claim.jpg",
  "datePublished":PUBLISHED,"publisher":{"@type":"Organization","name":"JDL Software LLC","url":"https://vareadyapp.com/"},
  "offers":{"@type":"Offer","price":"0.00","priceCurrency":"USD","availability":"https://schema.org/InStock"}},
 {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
   {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]},
]
lds = "\n".join(f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in ld)
WIN = '<svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h8.5v8.5H3zM12.5 3H21v8.5h-8.5zM3 12.5h8.5V21H3zM12.5 12.5H21V21h-8.5z"/></svg>'
def shot(name, alt, cap):
    return f'<figure class="shot"><img src="/img/{name}.jpg" alt="{esc(alt)}" width="1400" height="787" loading="lazy"><figcaption>{esc(cap)}</figcaption></figure>'
feat = "".join(f'<div class="faq-item"><h3>{esc(t)}</h3><p>{esc(p)}</p></div>' for t, p in features)
rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in free_pro)
faq_html = "".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q, a in faqs)
cta = f'<div class="btns page-cta"><a href="{MS}" class="btn">{WIN}Get VA Ready on the Microsoft Store</a><a href="/va-disability-calculator.html" class="btn ghost">Free rating calculator in your browser</a></div>'

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
<meta property="og:image" content="https://vareadyapp.com/img/windows-my-claim.jpg">
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
    <div class="crumb"><a href="/index.html">Home</a> / VA Ready for Windows</div>
    <h1>VA Ready for Windows</h1>
    <p class="lede">Calculate your combined VA disability rating, build your claim and keep your evidence in order on a Windows PC. Free on the Microsoft Store, no account.</p>
    {cta}
    <p class="facts">Windows 10 (version 1809 or later) and Windows 11, 64-bit.</p>
    {shot("windows-my-claim", "VA Ready on Windows, My Claim tab: combined rating, estimated monthly pay and the list of claimed conditions.", "My Claim shows your combined rating and estimated monthly pay from the conditions you add.")}
    <article>
        <h2>What you can do on a PC</h2>
        {feat}
        {shot("windows-claim-intel", "VA Ready on Windows, Claim Intel tab listing conditions commonly claimed for an Army 11B.", "Claim Intel lists the conditions commonly claimed for your job code, with PACT Act presumptives for your bases.")}
        <h2>Free and Pro</h2>
        <div class="tbl-wrap"><table class="pt"><thead><tr><th>Free</th><th>Pro</th></tr></thead><tbody>{rows}</tbody></table></div>
        <p>Pro is billed through your Microsoft account: $4.99 a month, $39.99 a year, or $59.99 once.</p>
        {shot("windows-filing", "VA Ready on Windows, Filing tab with step-by-step filing guides.", "Filing is a task list: eight plain steps that tick themselves off, plus guides for each VA form.")}
        <h2>Your data stays on your PC</h2>
        <p>VA Ready has no account. Your claim, documents and notes live on your PC, and you can back them up to a folder you choose, documents included. Light and dark mode follow your Windows setting.</p>
        <h2>Questions</h2>
        {faq_html}
    </article>
    {cta}
    <p class="trustline">Also on <a href="https://apps.apple.com/app/id6761733758">iPhone, iPad and Mac</a> and <a href="https://play.google.com/store/apps/details?id=com.vaready.app&amp;hl=en_US">Android</a>. Not on a PC? <a href="/va-disability-calculator.html">Use the free calculator in your browser</a>, or see the <a href="/va-disability-pay-rates.html">VA pay rates</a>.</p>
    <div class="disclaimer">VA Ready is not affiliated with, endorsed by, or connected to the U.S. Department of Veterans Affairs or any government agency. Estimates are not VA decisions. This page is not financial or legal advice.</div>
</div>
{footer}
"""
open(OUT, "w").write(page)
sp = os.path.join(SITE, "sitemap.xml"); xml = open(sp).read()
if CANON not in xml:
    open(sp, "w").write(xml.replace("</urlset>", f"  <url>\n    <loc>{CANON}</loc>\n    <lastmod>{PUBLISHED}</lastmod>\n    <priority>0.9</priority>\n  </url>\n</urlset>"))
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S): json.loads(b)
print("wrote", OUT)
