#!/usr/bin/env python3
"""VA Updates / Federal Register Rule Tracker for vareadyapp.com.

Pulls VA regulatory actions from the Federal Register public API (no key,
primary source) and bakes a single rich hub at /va-updates.html — original
framing + the official government abstract + Proposed/Final flag + a link to
the primary source. NOT a raw feed republish: one curated, regularly-rebuilt
page (run on a schedule via CI) so it's fresh without thin/duplicate pages.

Filters to Rules + Proposed Rules whose title/abstract touch claim-relevant
topics, so the page surfaces rate-schedule / presumptive / PACT / rating
changes — not Privacy-Act notices and info-collection chatter.
"""
import json, re, os, html, urllib.request, urllib.parse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
def esc(s): return html.escape(s or "", quote=True)

# reuse canonical CSS + add a little for the updates list
gtext = open(os.path.join(HERE, "gen_guides.py")).read()
CSS = re.search(r'CSS = """(.*?)"""', gtext, re.S).group(1)
CSS += """
    .upd { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px 20px; margin-bottom:14px; }
    .upd-top { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:8px; }
    .badge { font-size:10px; font-weight:900; letter-spacing:1px; text-transform:uppercase; padding:3px 9px; border-radius:6px; }
    .b-prop { color:#1a1205; background:var(--gold); }
    .b-final { color:#06210f; background:var(--green); }
    .b-notice { color:var(--tan); background:rgba(255,255,255,0.08); }
    .upd-date { font-size:12px; color:var(--gray); }
    .upd h3 { font-size:17px; font-weight:800; color:var(--white); line-height:1.35; margin-bottom:6px; }
    .upd p { color:var(--tan); font-size:14px; line-height:1.6; margin-bottom:8px; }
    .upd .why { color:var(--white); font-size:13.5px; border-left:3px solid var(--gold); padding-left:12px; margin:8px 0; }
    .upd a.src { font-size:13px; font-weight:700; }
    .upd-note { font-size:12.5px; color:var(--gray); line-height:1.7; background:rgba(217,166,33,0.06); border:1px solid rgba(217,166,33,0.22); border-radius:11px; padding:13px 15px; margin:16px 0; }
"""
NAV = re.search(r'NAV = """(.*?)"""', gtext, re.S).group(1)
FOOTER = re.search(r'FOOTER = """(.*?)"""', gtext, re.S).group(1)

# ---------- fetch Federal Register (VA) ----------
API = ("https://www.federalregister.gov/api/v1/documents.json?"
       "conditions[agencies][]=veterans-affairs-department"
       "&conditions[type][]=RULE&conditions[type][]=PRORULE"
       "&conditions[publication_date][gte]=2022-06-01&order=newest&per_page=400"
       "&fields[]=title&fields[]=type&fields[]=publication_date&fields[]=abstract"
       "&fields[]=html_url&fields[]=document_number&fields[]=action")

KEYWORDS = ["disabilit", "rating", "ratings", "compensation", "presumpt", "pension",
            "herbicide", "agent orange", "pact", "burn pit", "radiation", "schedule for rating",
            "examination", "dbq", "tinnitus", "mental disorder", "musculoskeletal", "neurolog",
            "convulsive", "respiratory", "sleep apnea", "hearing loss", "service connection",
            "toxic exposure", "camp lejeune", "gulf war", "special monthly", "evaluation of",
            "cost-of-living", "cost of living", "1151", "effective date", "nehmer"]

def relevant(doc):
    t = doc.get("type", "")
    if t not in ("Rule", "Proposed Rule"):
        return False
    blob = ((doc.get("title") or "") + " " + (doc.get("abstract") or "")).lower()
    return any(k in blob for k in KEYWORDS)

def fetch():
    req = urllib.request.Request(API, headers={"Accept": "application/json", "User-Agent": "vareadyapp-news/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("results", [])

def trim(s, n=320):
    s = re.sub(r"\s+", " ", (s or "").strip())
    return (s[:n].rsplit(" ", 1)[0] + "…") if len(s) > n else s

def fmt_date(d):
    try:
        dt = datetime.strptime(d, "%Y-%m-%d")
        return f"{dt.strftime('%B')} {dt.day}, {dt.year}", d
    except Exception:
        return d, d

def badge(t):
    if t == "Proposed Rule": return '<span class="badge b-prop">Proposed Rule</span>'
    if t == "Rule": return '<span class="badge b-final">Final Rule</span>'
    return '<span class="badge b-notice">Notice</span>'

def why_line(doc):
    t = doc.get("type")
    if t == "Proposed Rule":
        return ("<strong>This is a proposal, not law yet.</strong> Nothing changes for your claim "
                "until (and unless) it's finalized. You can't claim under a proposed rule.")
    return ("<strong>This is a final rule.</strong> It's in effect as of its stated date — worth checking "
            "if it touches a condition or exposure on your claim.")

def updates_page(docs, generated):
    cards = ""
    for d in docs:
        label, iso = fmt_date(d.get("publication_date"))
        cards += f"""<div class="upd">
    <div class="upd-top">{badge(d.get('type'))}<span class="upd-date">Federal Register &middot; {esc(label)}</span></div>
    <h3>{esc(d.get('title'))}</h3>
    <p>{esc(trim(d.get('abstract')) or 'No summary provided by the Federal Register for this action.')}</p>
    <div class="why">{why_line(d)}</div>
    <a class="src" href="{esc(d.get('html_url'))}" rel="nofollow noopener" target="_blank">Read the official document on FederalRegister.gov &rarr;</a>
</div>"""
    desc = ("Track the latest U.S. Department of Veterans Affairs regulatory actions — proposed and final "
            "rules on disability ratings, presumptive conditions, the PACT Act, and toxic exposure — in plain "
            "language, pulled straight from the Federal Register.")
    breadcrumb = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"VA Updates","item":"https://vareadyapp.com/va-updates.html"}]})
    collection = json.dumps({"@context":"https://schema.org","@type":"CollectionPage",
        "name":"VA Rule & Policy Updates","url":"https://vareadyapp.com/va-updates.html",
        "description":desc,"dateModified":generated,
        "publisher":{"@type":"Organization","name":"VA Ready","logo":{"@type":"ImageObject","url":"https://vareadyapp.com/logo.png"}}})
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VA Rule &amp; Policy Updates — Disability, PACT Act &amp; Presumptive Changes | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="https://vareadyapp.com/va-updates.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="VA Rule &amp; Policy Updates">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="https://vareadyapp.com/va-updates.html">
<meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="/logo.png">
<script type="application/ld+json">{breadcrumb}</script>
<script type="application/ld+json">{collection}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / VA Updates</div>
    <div class="eyebrow">VA Updates</div>
    <h1>VA Rule &amp; Policy Updates</h1>
    <p class="lede">The latest VA regulatory actions that can affect your claim — disability ratings, presumptive conditions, the PACT Act, and toxic exposure — in plain language, pulled straight from the Federal Register.</p>
    <div class="upd-note">These updates come directly from the <strong>Federal Register</strong>, the U.S. government's official record of rules and proposed rules. We summarize and link to the source; we never change what it says. Remember: a <strong>proposed</strong> rule is not law and you can't claim under it until it's finalized. Always verify current rules at VA.gov and with an accredited VSO.</div>
    {cards if cards else '<p class="lede">No qualifying VA rule actions found in the latest pull. Check back soon.</p>'}
    <p class="upd-note">Last updated {esc(fmt_date(generated)[0])}. This page refreshes automatically.</p>
</div>
{FOOTER}
</body>
</html>"""

# ---------- run ----------
generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
try:
    raw = fetch()
except Exception as e:
    raise SystemExit(f"Federal Register fetch failed: {e}")
docs = [d for d in raw if relevant(d)][:20]
open(os.path.join(SITE, "va-updates.html"), "w", encoding="utf-8").write(updates_page(docs, generated))

# sitemap append
sp = os.path.join(SITE, "sitemap.xml")
xml = open(sp).read()
u = "https://vareadyapp.com/va-updates.html"
if u not in xml:
    xml = xml.replace("</urlset>", f'  <url>\n    <loc>{u}</loc>\n    <lastmod>{generated}</lastmod>\n    <priority>0.7</priority>\n  </url>\n</urlset>')
    open(sp, "w").write(xml)

# validate JSON-LD
page = open(os.path.join(SITE, "va-updates.html")).read()
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
    json.loads(blk)
print(f"va-updates.html: {len(docs)} claim-relevant VA rules from {len(raw)} fetched; JSON-LD valid")
print("sample:", [ (d['type'], d['title'][:50]) for d in docs[:3] ])
