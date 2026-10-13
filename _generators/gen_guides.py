#!/usr/bin/env python3
import json, re, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
GUIDES_DIR = os.path.join(SITE, "guides")
os.makedirs(GUIDES_DIR, exist_ok=True)
DATA = json.load(open(os.path.join(HERE,"data","guides.json")))
# Site-level copy edits keyed by slug. They survive a refresh of guides.json
# from Supabase, which holds the older wording.
_EDITS = os.path.join(HERE, "data", "guides_site_edits.json")
if os.path.exists(_EDITS):
    _ed = json.load(open(_EDITS))
    for _g in DATA:
        _g.update(_ed.get(_g.get("slug") or "", {}))

# ---------- helpers ----------
def slugify(s):
    s = s.split("\u2014")[0].split("\u2013")[0].strip()        # core name before the dash
    s = s.lower().replace("&", " and ").replace("/", " ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-+", "-", s)
    return s

def esc(s): return html.escape(s, quote=True)

# Phrases that keep their capitals in sentence case: VA product names and
# proper nouns. Everything else after the first word is lowercased.
_KEEP = ["Intent to File", "Aid and Attendance", "Special Monthly Compensation", "Foreign Medical Program",
         "Federal Benefits Units", "Federal Benefits Unit", "Camp Lejeune", "Agent Orange", "PACT Act",
         "Gulf War", "Higher-Level Review", "Supplemental Claims", "Supplemental Claim", "Board Appeal",
         "Veterans Service Officers", "Veterans Service Officer", "Veterans Pension", "Vietnam", "GI Bill",
         "Chapter 31", "Chapter 35", "Social Security", "Medicare", "Medicaid", "VA Ready", "Vet Ready",
         "Fully Developed Claim", "Benefits Delivery at Discharge", "Unmistakable Error", "Vocational Rehabilitation", "VA Form", "DD Form", "Veterans Affairs"]
_SMALL = {"TO", "NOT", "IS", "OF", "AND", "OR", "THE", "IT", "A", "IN", "ON", "AN", "FOR", "BE", "DO"}

def sentence_case(s):
    """Headings and titles in sentence case. Acronyms, codes and the
    phrases in _KEEP keep their case; a new sentence after ':', '.' or '?'
    starts with a capital."""
    holes = {}
    for i, ph in enumerate(sorted(_KEEP, key=len, reverse=True)):
        tok = f"\x00{i}\x00"
        if ph in s:
            s = s.replace(ph, tok); holes[tok] = ph
    out, start = [], True
    for w in re.split(r"(\s+)", s):
        if not w.strip():
            out.append(w); continue
        if "\x00" in w:
            out.append(w); start = w.rstrip().endswith((":", "?")); continue
        def fix(part):
            core = re.sub(r"[^A-Za-z]", "", part)
            if not core: return part
            if (core.isupper() and len(core) >= 2 and core not in _SMALL) or "\u00a7" in part:
                return part
            if re.fullmatch(r"[A-Z]{2,}s", core): return part
            return part.lower()
        if re.search(r"\d", w) and re.search(r"[A-Z]{2}", w): w2 = w
        else: w2 = "-".join(fix(x) for x in w.split("-"))
        if start:
            for i, c in enumerate(w2):
                if c.isalpha():
                    w2 = w2[:i] + c.upper() + w2[i+1:]; break
        out.append(w2)
        e = w2.rstrip('"\u201d)')
        start = e.endswith((":", "?")) or (e.endswith(".") and e.lower() not in ("vs.", "etc.") and not re.fullmatch(r"(?:[A-Za-z]\.){2,}", e))
    s = "".join(out)
    for tok, ph in holes.items(): s = s.replace(tok, ph)
    return s

def _md_link(m):
    """Render a [text](url) link.

    Internal links get no rel and no target: they are our own pages, and
    nofollowing them would throw away the internal link equity that makes a
    hub-and-spoke guide set work. External links keep nofollow + new tab.
    """
    text, url = m.group(1), m.group(2)
    if url.startswith("/") or url.startswith("https://vareadyapp.com"):
        return f'<a href="{url}">{text}</a>'
    return f'<a href="{url}" rel="nofollow noopener" target="_blank">{text}</a>'

BOLD_OK = True   # set per guide in md_to_html: a page full of bold lead-ins keeps none

def _bold(m, s0):
    # Bold marks a defined term at the start of a list item or paragraph,
    # on pages that use it sparingly. Mid-sentence bold is emphasis and is dropped.
    if BOLD_OK and m.start() == 0 and (len(m.group(1).split()) <= 6):
        return "<strong>" + m.group(1) + "</strong>"
    return m.group(1)

def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", lambda m: _bold(m, s), s)
    # Single-asterisk italics are emphasis, which this site drops; strip the marks.
    s = re.sub(r"(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])", r"\1", s)
    # Markdown links first, so the bare-URL rule below cannot chew up the href.
    s = re.sub(r"\[([^\]]+)\]\((/[^)\s]+|https?://[^)\s]+)\)", _md_link, s)
    # Remaining bare URLs, skipping any already inside an anchor we just wrote.
    s = re.sub(r'(?<!href=")(?<!>)(https?://[^\s<]+)(?![^<]*</a>)',
               r'<a href="\1" rel="nofollow noopener" target="_blank">\1</a>', s)
    return s

def md_to_html(md):
    global BOLD_OK
    BOLD_OK = len(re.findall(r"(?m)^(?:[-*] |\d+\. )?\*\*[^*\n]+\*\*(?!:?$)", md)) <= 4
    out, para, list_type = [], [], None
    pseudo = "h3" if re.search(r"^## ", md, re.M) else "h2"
    def flush():
        if para: out.append("<p>" + inline(" ".join(para)) + "</p>"); para.clear()
    def closel():
        nonlocal list_type
        if list_type: out.append(f"</{list_type}>"); list_type = None
    for raw in md.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flush(); closel()
        elif line.startswith("### "):
            flush(); closel(); out.append("<h3>" + inline(sentence_case(line[4:])) + "</h3>")
        elif line.startswith("## "):
            flush(); closel(); out.append("<h2>" + inline(sentence_case(line[3:])) + "</h2>")
        elif re.match(r"^\*\*[^*]+?\*\*:?$", line.strip()) and not para:
            closel(); out.append(f"<{pseudo}>" + inline(sentence_case(line.strip().strip("*").rstrip(":").strip())) + f"</{pseudo}>")
        elif re.match(r"^[-*] ", line):
            flush()
            if list_type != "ul": closel(); out.append("<ul>"); list_type = "ul"
            out.append("<li>" + inline(line[2:]) + "</li>")
        elif re.match(r"^\d+\. ", line):
            flush()
            if list_type != "ol": closel(); out.append("<ol>"); list_type = "ol"
            out.append("<li>" + inline(re.sub(r"^\d+\. ", "", line)) + "</li>")
        else:
            closel(); para.append(line)
    flush(); closel()
    return "\n".join(out)

def meta_desc(s):
    s = s.strip().replace("\n", " ")
    return (s[:152].rsplit(" ", 1)[0] + "…") if len(s) > 155 else s

# ---------- enrich rows ----------
for g in DATA:
    # An explicit slug freezes the URL. Deriving it from the title meant any
    # copy edit to a title silently moved the page, which would 404 a ranking
    # URL and hand its history to a brand new one. Titles are editable; URLs
    # are not. slugify() remains only as the fallback for a brand new guide
    # that has not been given a slug yet.
    g["slug"] = (g.get("slug") or "").strip() or slugify(g["title"])
    g["is_form"] = g["sort_order"] >= 200
    g["url"] = f"/guides/{g['slug']}.html"
    g["date"] = (g.get("created_at") or "2026-06-07")[:10]
    g["title"] = sentence_case(g["title"].replace("\u2019\u2019", "\u2019").replace("''", "'"))

# unique slug guard
seen = {}
for g in DATA:
    if g["slug"] in seen:
        g["slug"] = g["slug"] + "-" + str(g["id"]); g["url"] = f"/guides/{g['slug']}.html"
    seen[g["slug"]] = True

process = [g for g in DATA if not g["is_form"]]
forms = [g for g in DATA if g["is_form"]]

CSS = """
    * { margin:0; padding:0; box-sizing:border-box; }
    :root { --navy:#0a0f1a; --card:#141b2d; --gold:#d9a621; --tan:#c8bda5; --white:#fff; --green:#34a853; --gray:#8a93a6; --line:rgba(255,255,255,0.08); }
    html { -webkit-text-size-adjust:100%; }
    body { font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display','Segoe UI',sans-serif; background:var(--navy); color:var(--white); line-height:1.75; -webkit-font-smoothing:antialiased; overflow-wrap:break-word; }
    a { color:var(--white); text-decoration:underline; text-decoration-color:rgba(255,255,255,0.35); text-underline-offset:3px; }
    a:hover { text-decoration-color:var(--gold); }
    img { max-width:100%; height:auto; }
    .wrap { max-width:760px; margin:0 auto; padding:0 22px; }
    nav { display:flex; align-items:center; justify-content:space-between; padding:18px 22px; max-width:1080px; margin:0 auto; }
    .nav-brand { display:flex; align-items:center; gap:10px; text-decoration:none; color:var(--white); }
    .nav-brand img { width:34px; height:34px; border-radius:9px; }
    .nav-brand span { font-size:15px; font-weight:800; white-space:nowrap; }
    .nav-links a { font-size:13px; color:var(--tan); margin-left:16px; font-weight:600; white-space:nowrap; text-decoration:none; display:inline-block; padding:10px 0; }
    .crumb { font-size:13px; color:var(--gray); padding:26px 0 4px; }
    .crumb a { color:var(--tan); text-decoration:none; display:inline-block; padding:8px 0; }
    .eyebrow { font-size:14px; color:var(--gray); margin:14px 0 6px; }
    h1 { font-size:32px; line-height:1.2; font-weight:800; margin-bottom:14px; }
    .lede { font-size:18px; color:var(--tan); margin-bottom:18px; max-width:68ch; }
    .meta { font-size:13px; color:var(--gray); border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:12px 0; margin-bottom:26px; }
    article h2 { font-size:22px; font-weight:800; color:var(--white); margin:32px 0 10px; line-height:1.3; }
    article h3 { font-size:17px; font-weight:700; color:var(--white); margin:22px 0 8px; }
    article p { color:var(--tan); margin-bottom:14px; font-size:16px; max-width:68ch; }
    article strong { color:var(--white); }
    article ul, article ol { margin:0 0 16px 4px; padding-left:22px; max-width:68ch; }
    article li { color:var(--tan); margin-bottom:7px; font-size:16px; }
    article a { word-break:break-word; }
    .cta { border-top:1px solid var(--line); padding-top:24px; margin:36px 0; }
    .cta.cta-line { margin:28px 0; padding-top:18px; }
    .cta.cta-line p { margin:0; }
    .cta h3 { font-size:19px; font-weight:800; color:var(--white); margin-bottom:8px; }
    .cta p { color:var(--tan); font-size:15px; margin-bottom:12px; max-width:68ch; }
    .tiers { margin:0 0 18px; max-width:68ch; }
    .tiers dt { color:var(--white); font-weight:700; font-size:15px; margin-top:10px; }
    .tiers dd { color:var(--tan); font-size:15px; margin:2px 0 0; }
    .btns { display:flex; gap:10px; flex-wrap:wrap; }
    .btn { display:inline-flex; align-items:center; min-height:44px; background:var(--gold); color:#1a1205; font-weight:800; font-size:14px; padding:10px 18px; border-radius:11px; text-decoration:none; }
    .btn:hover { color:#1a1205; }
    .btn.ghost { background:transparent; color:var(--tan); border:1px solid rgba(255,255,255,0.22); }
    .btn.ghost:hover { color:var(--white); }
    .related { margin:34px 0; }
    .related h2 { font-size:19px; font-weight:800; margin-bottom:6px; }
    .related a { display:block; border-top:1px solid var(--line); padding:13px 0; color:var(--white); font-weight:700; font-size:15px; text-decoration:none; }
    .related a span { display:block; color:var(--gray); font-weight:400; font-size:13px; margin-top:2px; }
    .disclaimer { font-size:12.5px; color:var(--gray); line-height:1.7; border-top:1px solid var(--line); padding:22px 0; margin-top:10px; }
    .disclaimer a { color:var(--tan); }
    .faq-item { border-top:1px solid var(--line); padding:16px 0; }
    .faq-item h3 { font-size:16px; font-weight:700; color:var(--white); margin-bottom:6px; }
    .faq-item p { font-size:15px; color:var(--tan); margin:0; max-width:68ch; }
    .note { font-size:14.5px; color:var(--tan); margin:14px 0; max-width:68ch; }
    footer { text-align:center; padding:40px 22px; border-top:1px solid var(--line); margin-top:10px; }
    footer p { font-size:12.5px; color:var(--gray); }
    .footer-links a { display:inline-block; color:var(--tan); font-size:13px; padding:12px 8px; text-decoration:none; }
    /* hub */
    .hub-sec { margin:34px 0; }
    .hub-sec > h2 { font-size:21px; font-weight:800; margin-bottom:8px; }
    .hub-grid { display:block; }
    .hub-card { border-top:1px solid var(--line); padding:13px 0; }
    .hub-card a { color:var(--white); font-weight:700; font-size:16px; text-decoration:none; }
    .hub-card a:hover { text-decoration:underline; }
    .hub-card p { color:var(--tan); font-size:14px; margin-top:4px; max-width:68ch; }
    .tbl-wrap { overflow-x:auto; -webkit-overflow-scrolling:touch; margin:8px 0 18px; }
    @media (max-width:560px){ h1{font-size:27px;} }
    .nv-burger { display:none; font-size:25px; color:var(--tan); cursor:pointer; line-height:1; padding:9px 12px; user-select:none; min-width:44px; min-height:44px; text-align:center; }
    .nv-cb { display:none; }
    .nav-links a.nav-cta { background:var(--gold); color:#000; padding:9px 16px; border-radius:8px; font-weight:800; }
    .nav-links a.nav-cta:hover { color:#000; }
    @media (max-width:1100px){ .nav-links a.nav-cta { margin-top:10px; text-align:center; border-top:none; padding:12px; } }
    @media (max-width:1100px){
      nav { flex-wrap:wrap; }
      .nv-burger { display:block; }
      .nav-links { display:none; flex-basis:100%; flex-direction:column; align-items:stretch; gap:0; margin-top:10px; }
      .nv-cb:checked ~ .nav-links { display:flex; }
      .nav-links a { margin-left:0; padding:13px 2px; border-top:1px solid var(--line); font-size:15px; white-space:normal; }
    }
"""

NAV = """<nav>
    <a href="/index.html" class="nav-brand"><img src="/logo-96.png" alt="VA Ready logo" width="34" height="34"><span>VA Ready <span style="color:var(--gray);font-weight:400;">/</span> Vet Ready</span></a>
    <input type="checkbox" id="nv" class="nv-cb">
    <label for="nv" class="nv-burger" aria-label="Open menu">&#9776;</label>
    <div class="nav-links"><a href="/va-disability-calculator.html">Calculator</a><a href="/conditions.html">Conditions</a><a href="/mos.html">MOS</a><a href="/va-disability-pay-rates.html">Pay Rates</a><a href="/federal-benefits.html">Federal Benefits</a><a href="/guides.html">Guides</a><a href="/blog.html">Blog</a><a href="/find-a-vso.html">Find a VSO</a><a href="/index.html#download" class="nav-cta">Get the App</a></div>
</nav>"""

FOOTER = """<footer>
    <p>&copy; 2026 JDL Software LLC. VA Ready (iOS) &amp; Vet Ready (Android) are not affiliated with the U.S. Department of Veterans Affairs.</p>
    <div class="footer-links"><a href="/index.html">Home</a><a href="/conditions.html">Conditions</a><a href="/exposures.html">Exposures</a><a href="/mos.html">By MOS</a><a href="/va-disability-pay-rates.html">Pay Rates</a><a href="/states.html">State Benefits</a><a href="/federal-benefits.html">Federal Benefits</a><a href="/guides.html">Guides</a><a href="/blog.html">Blog</a><a href="/videos.html">Videos</a><a href="/va-updates.html">VA Updates</a><a href="/va-disability-calculator.html">Calculator</a><a href="/va-back-pay-calculator.html">Back Pay</a><a href="/va-claim-evidence.html">Document Your Claim</a><a href="/reserve-national-guard-va-disability.html">Reserve &amp; Guard</a><a href="/find-a-vso.html">Find a VSO</a><a href="/founders.html">Our Story</a><a href="/community.html">In the Community</a><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a><a href="/accessibility.html">Accessibility</a></div>
    <div class="footer-social" style="display:flex;justify-content:center;gap:0;margin:10px 0 0;"><a href="https://www.tiktok.com/@vareadyapp" target="_blank" rel="me noopener" aria-label="VA Ready on TikTok" style="color:var(--tan);display:inline-flex;padding:11px;"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.6 5.82a4.28 4.28 0 0 1-1.01-2.82h-3.3v13.2a2.59 2.59 0 1 1-1.78-2.46V10.2a5.9 5.9 0 1 0 5.09 5.85V8.96a7.56 7.56 0 0 0 4.4 1.41V7.06a4.28 4.28 0 0 1-3.4-1.24Z"/></svg></a><a href="https://www.instagram.com/vareadyapp/" target="_blank" rel="me noopener" aria-label="VA Ready on Instagram" style="color:var(--tan);display:inline-flex;padding:11px;"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23a3.7 3.7 0 0 1-.9 1.38 3.7 3.7 0 0 1-1.38.9c-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.7 3.7 0 0 1-1.38-.9 3.7 3.7 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23-.06-1.27-.07-1.65-.07-4.85s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.17 8.8 2.16 12 2.16M12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63a5.86 5.86 0 0 0-2.12 1.38A5.86 5.86 0 0 0 .64 4.13C.34 4.9.14 5.77.08 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.28.26 2.15.56 2.91a5.86 5.86 0 0 0 1.38 2.12 5.86 5.86 0 0 0 2.12 1.38c.76.3 1.63.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.28-.06 2.15-.26 2.91-.56a5.86 5.86 0 0 0 2.12-1.38 5.86 5.86 0 0 0 1.38-2.12c.3-.76.5-1.63.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.28-.26-2.15-.56-2.91a5.86 5.86 0 0 0-1.38-2.12A5.86 5.86 0 0 0 19.87.63c-.76-.3-1.63-.5-2.91-.56C15.67.01 15.26 0 12 0Zm0 5.84A6.16 6.16 0 1 0 18.16 12 6.16 6.16 0 0 0 12 5.84Zm0 10.16A4 4 0 1 1 16 12a4 4 0 0 1-4 4Zm6.41-10.4a1.44 1.44 0 1 0 1.44 1.44 1.44 1.44 0 0 0-1.44-1.44Z"/></svg></a><a href="https://www.facebook.com/vareadyapp" target="_blank" rel="me noopener" aria-label="VA Ready on Facebook" style="color:var(--tan);display:inline-flex;padding:11px;"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07c0 6.03 4.39 11.03 10.13 11.93v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.69 4.53-4.69 1.31 0 2.68.24 2.68.24v2.97h-1.51c-1.49 0-1.96.93-1.96 1.89v2.25h3.33l-.53 3.49h-2.8V24C19.61 23.1 24 18.1 24 12.07Z"/></svg></a></div>
</footer>
<script defer src="/_vercel/insights/script.js"></script>
<script defer src="/track.js"></script>"""

APP_CTA = """<div class="cta cta-line"><p>The in-depth filing guides are Pro in <a href="https://apps.apple.com/app/id6761733758">VA Ready for iOS</a> and <a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US">Vet Ready for Android</a>; the combined-rating calculator, claim list, exposure catalog, VSO finder and symptom tracker are free.</p></div>"""

DISCLAIMER = """<div class="disclaimer">This guide is for general informational purposes only and is not legal or medical advice. VA Ready is not affiliated with, endorsed by, or connected to the U.S. Department of Veterans Affairs. Regulations and procedures change; always verify current requirements at VA.gov and consult a VA-accredited representative for help with your claim.</div>"""

def guide_page(g, related):
    body = md_to_html(g["content"])
    cat = "VA forms" if g["is_form"] else "Filing guides"
    cfr = esc(g["cfr_reference"]) if g.get("cfr_reference") else ""
    rel_html = ""
    if related:
        items = "".join(
            f'<a href="{r["url"]}">{esc(r["title"].split("—")[0].strip())}<span>{esc(meta_desc(r["summary"]))}</span></a>'
            for r in related)
        rel_html = f'<div class="related"><h2>Related guides</h2>{items}</div>'
    desc = meta_desc(g["summary"])
    title_tag = f'{esc(g["title"])} | VA Ready'
    canon = f'https://vareadyapp.com{g["url"]}'
    breadcrumb = json.dumps({
        "@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
            {"@type":"ListItem","position":2,"name":"VA claim guides","item":"https://vareadyapp.com/guides.html"},
            {"@type":"ListItem","position":3,"name":g["title"],"item":canon}]})
    article_ld = json.dumps({
        "@context":"https://schema.org","@type":"Article","headline":g["title"][:110],
        "description":g["summary"],"datePublished":g["date"],"dateModified":g["date"],
        "author":{"@type":"Organization","name":"JDL Software LLC"},
        "publisher":{"@type":"Organization","name":"VA Ready"},
        "mainEntityOfPage":canon, "inLanguage":"en-US"})
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_tag}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="{esc(g['title'])}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{esc(g['title'])}">
<meta name="twitter:description" content="{esc(desc)}">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<script type="application/ld+json">{breadcrumb}</script>
<script type="application/ld+json">{article_ld}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/guides.html">VA claim guides</a> / {esc(cat)}</div>
    <h1>{esc(g['title'])}</h1>
    <p class="lede">{esc(g['summary'])}</p>
    {('<div class="meta">' + cfr + '</div>') if cfr else ''}
    <article>
{body}
    </article>
    {APP_CTA}
    {rel_html}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""

def hub_page():
    def cards(items):
        return "".join(
            f'<div class="hub-card"><a href="{g["url"]}">{esc(g["title"].split("—")[0].strip())}</a><p>{esc(meta_desc(g["summary"]))}</p></div>'
            for g in items)
    desc = "Guides on filing a VA disability claim, C&P exam preparation, nexus letters, the PACT Act, TDIU and appeals, plus an explainer for each VA form."
    breadcrumb = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"VA claim guides","item":"https://vareadyapp.com/guides.html"}]})
    itemlist = json.dumps({"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"url":f'https://vareadyapp.com{g["url"]}',"name":g["title"]} for i,g in enumerate(DATA)]})
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VA claim guides: filing steps and every VA form explained | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="https://vareadyapp.com/guides.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="VA claim guides: filing steps and every VA form explained">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="https://vareadyapp.com/guides.html">
<meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<script type="application/ld+json">{breadcrumb}</script>
<script type="application/ld+json">{itemlist}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / VA claim guides</div>
    <h1>VA claim guides</h1>
    <p class="lede">{len(DATA)} guides on this site: {len(process)} on filing and appeals, and {len(forms)} explainers for individual VA forms. They are free to read and cite 38 CFR and VA.gov.</p>
    <div class="hub-sec">
        <h2>Filing and appeals</h2>
        <div class="hub-grid">{cards(process)}</div>
    </div>
    <div class="hub-sec">
        <h2>VA forms</h2>
        <div class="hub-grid">{cards(forms)}</div>
    </div>
    {APP_CTA}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""

# ---------- write pages ----------
n = 0
for g in DATA:
    pool = process if not g["is_form"] else forms
    related = [r for r in pool if r["id"] != g["id"]]
    # nearest by sort_order
    related.sort(key=lambda r: abs(r["sort_order"] - g["sort_order"]))
    open(os.path.join(GUIDES_DIR, g["slug"] + ".html"), "w").write(guide_page(g, related[:4]))
    n += 1
open(os.path.join(SITE, "guides.html"), "w").write(hub_page())

# ---------- sitemap ----------
core = [("https://vareadyapp.com/","1.0"),
        ("https://vareadyapp.com/va-disability-calculator.html","0.9"),
        ("https://vareadyapp.com/va-back-pay-calculator.html","0.9"),
        ("https://vareadyapp.com/va-claim-evidence.html","0.9"),
        ("https://vareadyapp.com/guides.html","0.8"),
        ("https://vareadyapp.com/videos.html","0.7"),
        ("https://vareadyapp.com/the-va-ready-difference.html","0.8"),
        ("https://vareadyapp.com/community.html","0.7"),
        ("https://vareadyapp.com/privacy.html","0.5"),
        ("https://vareadyapp.com/terms.html","0.5"),
        ("https://vareadyapp.com/accessibility.html","0.4")]
urls = "".join(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-06-07</lastmod>\n    <priority>{p}</priority>\n  </url>\n' for u,p in core)
for g in DATA:
    urls += f'  <url>\n    <loc>https://vareadyapp.com{g["url"]}</loc>\n    <lastmod>2026-06-07</lastmod>\n    <priority>0.7</priority>\n  </url>\n'
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n'
open(os.path.join(SITE, "sitemap.xml"), "w").write(sitemap)

print(f"generated {n} guide pages + hub")
print("process:", len(process), "| forms:", len(forms))
print("sample slugs:", [g["slug"] for g in DATA[:5]])
print("sitemap urls:", len(core) + len(DATA))
