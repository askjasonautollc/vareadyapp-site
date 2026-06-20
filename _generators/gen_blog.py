#!/usr/bin/env python3
"""Blog generator for vareadyapp.com.

Reads markdown posts from _generators/data/blog/*.md (frontmatter + body),
emits a categorized index at /blog.html and an SEO-rich page per post at
/blog/<slug>.html. Author is always "VA Ready App". Run AFTER gen_guides.py
(which rewrites sitemap.xml from scratch) so the blog URLs append cleanly.

Add a new post by dropping a .md file in data/blog/ with this header:

    ---
    title: Your Headline
    slug: your-slug
    category: Trust & Privacy
    date: 2026-06-14
    excerpt: One or two sentences for the card + meta description.
    image: /img/blog/your-slug.png
    image_alt: Describe the image.
    ---
    Markdown body...
"""
import json, re, os, html
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
BLOG_DATA = os.path.join(HERE, "data", "blog")
BLOG_OUT = os.path.join(SITE, "blog")
os.makedirs(BLOG_OUT, exist_ok=True)

def esc(s): return html.escape(s or "", quote=True)

# ---- reuse the canonical site CSS, then append blog styles ----
gtext = open(os.path.join(HERE, "gen_guides.py")).read()
m = re.search(r'CSS = """(.*?)"""', gtext, re.S)
CSS = m.group(1) if m else ""
CSS += """
    .blog-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(290px,1fr)); gap:18px; margin-bottom:6px; }
    .bcard { display:flex; background:var(--card); border:1px solid var(--line); border-radius:16px; overflow:hidden; transition:border-color .15s ease, transform .15s ease; }
    .bcard:hover { border-color:rgba(217,166,33,0.5); transform:translateY(-3px); }
    .bcard a.bc-link { color:inherit; display:flex; flex-direction:column; height:100%; width:100%; }
    .bcard .thumb { width:100%; aspect-ratio:16/9; object-fit:cover; object-position:50% 32%; display:block; }
    .bcard .thumb.ph { display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#16213b,#0c1322); }
    .bcard .thumb.ph span { font-size:24px; font-weight:900; color:rgba(217,166,33,0.5); letter-spacing:3px; }
    .bcard .bc-body { padding:15px 17px 18px; display:flex; flex-direction:column; gap:9px; flex:1; }
    .bc-tag { align-self:flex-start; font-size:10px; font-weight:800; letter-spacing:1.5px; text-transform:uppercase; color:var(--gold); background:rgba(217,166,33,0.10); border:1px solid rgba(217,166,33,0.25); padding:3px 9px; border-radius:6px; }
    .bcard h3 { font-size:17.5px; font-weight:800; color:var(--white); line-height:1.32; letter-spacing:-0.2px; }
    .bcard .bc-ex { color:var(--tan); font-size:14px; line-height:1.6; flex:1; }
    .bc-meta { font-size:12px; color:var(--gray); margin-top:1px; }
    .cat-head { display:flex; align-items:center; gap:13px; margin:32px 0 15px; }
    .cat-head h2 { font-size:13px; font-weight:800; letter-spacing:2px; text-transform:uppercase; color:var(--tan); white-space:nowrap; margin:0; }
    .cat-head::after { content:""; flex:1; height:1px; background:var(--line); }
    .post-hero { display:block; width:100%; max-width:480px; height:auto; margin:8px auto 24px; border-radius:16px; border:1px solid var(--line); }
    .post-hero.ph { aspect-ratio:1.91/1; max-width:560px; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#16213b,#0c1322); }
    .post-hero.ph span { font-size:26px; font-weight:900; color:rgba(217,166,33,0.5); letter-spacing:3px; }
    .post-sign { margin:30px 0 4px; padding-top:18px; border-top:1px solid var(--line); font-size:13px; color:var(--gray); font-style:italic; line-height:1.75; }
    article hr { border:none; border-top:1px solid var(--line); margin:26px 0; }
"""

NAV = """<nav>
    <a href="/index.html" class="nav-brand"><img src="/logo.png" alt="VA Ready logo" width="34" height="34"><span>VA READY <span style="color:var(--gray);font-weight:400;">/</span> VET READY</span></a>
    <input type="checkbox" id="nv" class="nv-cb">
    <label for="nv" class="nv-burger" aria-label="Open menu">&#9776;</label>
    <div class="nav-links"><a href="/va-disability-calculator.html">Calculator</a><a href="/conditions.html">Conditions</a><a href="/exposures.html">Exposures</a><a href="/va-disability-pay-rates.html">Pay Rates</a><a href="/states.html">State Benefits</a><a href="/federal-benefits.html">Federal Benefits</a><a href="/guides.html">Guides</a><a href="/blog.html">Blog</a><a href="/find-a-vso.html">Find a VSO</a><a href="/index.html#download">Get the App</a></div>
</nav>"""

FOOTER = """<footer>
    <p>&copy; 2026 JDL Software LLC. VA Ready (iOS) &amp; Vet Ready (Android) are not affiliated with the U.S. Department of Veterans Affairs.</p>
    <div class="footer-links"><a href="/index.html">Home</a><a href="/conditions.html">Conditions</a><a href="/exposures.html">Exposures</a><a href="/va-disability-pay-rates.html">Pay Rates</a><a href="/states.html">State Benefits</a><a href="/federal-benefits.html">Federal Benefits</a><a href="/guides.html">Guides</a><a href="/blog.html">Blog</a><a href="/va-updates.html">VA Updates</a><a href="/va-disability-calculator.html">Calculator</a><a href="/find-a-vso.html">Find a VSO</a><a href="/founders.html">Our Story</a><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a></div>
</footer>
<script defer src="/_vercel/insights/script.js"></script>
<script defer src="/track.js"></script>"""

BLOG_CTA = """<div class="cta">
    <h3>VA Ready is the app that practices what this preaches</h3>
    <p>No account, no login, no data ever leaving your phone &mdash; and real, peer-reviewed studies instead of AI guesses. The combined-rating calculator, VSO finder, and core tools are free.</p>
    <div class="btns"><a href="https://apps.apple.com/app/id6761733758" class="btn">Get VA Ready for iOS</a><a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US" class="btn ghost">Get Vet Ready for Android</a></div>
</div>"""

DISCLAIMER = """<div class="disclaimer">This article is for general informational purposes only and is not legal or medical advice. VA Ready is not affiliated with, endorsed by, or connected to the U.S. Department of Veterans Affairs. Regulations and procedures change; always verify current requirements at VA.gov and consult a VA-accredited representative for help with your claim.</div>"""

# ---------- tiny markdown -> HTML ----------
def md_inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', t)
    return t

def md_to_html(md):
    lines = md.split('\n')
    out, para, i = [], [], 0
    def flush():
        if para:
            out.append('<p>' + md_inline(' '.join(para).strip()) + '</p>')
            para.clear()
    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()
        if not s:
            flush(); i += 1; continue
        if line.startswith('### '):
            flush(); out.append('<h3>' + md_inline(line[4:]) + '</h3>'); i += 1; continue
        if line.startswith('## '):
            flush(); out.append('<h2>' + md_inline(line[3:]) + '</h2>'); i += 1; continue
        if line.startswith('# '):
            flush(); i += 1; continue  # title comes from frontmatter
        if s == '---':
            flush(); out.append('<hr>'); i += 1; continue
        if re.match(r'^\s*[-*]\s+', line):
            flush(); items = []
            while i < len(lines) and re.match(r'^\s*[-*]\s+', lines[i]):
                items.append('<li>' + md_inline(re.sub(r'^\s*[-*]\s+', '', lines[i].rstrip())) + '</li>')
                i += 1
            out.append('<ul>' + ''.join(items) + '</ul>'); continue
        para.append(s); i += 1
    flush()
    return '\n'.join(out)

# ---------- frontmatter parse ----------
def parse_post(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw, re.S)
    if not m:
        raise ValueError(f"{path}: missing frontmatter")
    fm = {}
    for line in m.group(1).split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip().strip('"')
    fm['body'] = m.group(2).strip()
    return fm

def fmt_date(d):
    dt = datetime.strptime(d, "%Y-%m-%d")
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}", dt

def reading_min(body):
    return max(1, round(len(re.findall(r'\w+', body)) / 200))

def img_exists(path):
    return path and os.path.exists(os.path.join(SITE, path.lstrip('/')))

# ---------- load posts (newest first) ----------
posts = []
for fn in sorted(os.listdir(BLOG_DATA)):
    if fn.endswith(".md"):
        p = parse_post(os.path.join(BLOG_DATA, fn))
        p["url"] = f'/blog/{p["slug"]}.html'
        p["date_label"], p["_dt"] = fmt_date(p["date"])
        p["reading"] = reading_min(p["body"])
        posts.append(p)
posts.sort(key=lambda p: p["_dt"], reverse=True)

# ---------- post page ----------
def post_page(p, related):
    body = md_to_html(p["body"])
    canon = f'https://vareadyapp.com{p["url"]}'
    desc = esc(p["excerpt"][:160])
    img_url = f'https://vareadyapp.com{p["image"]}' if p.get("image") else "https://vareadyapp.com/logo.png"
    if img_exists(p.get("image")):
        hero = f'<img class="post-hero" src="{esc(p["image"])}" alt="{esc(p.get("image_alt",""))}" loading="eager">'
    else:
        hero = '<div class="post-hero ph"><span>VA READY</span></div>'
    rel_html = ""
    if related:
        items = "".join(
            f'<a href="{r["url"]}">{esc(r["title"])}<span>{esc(r["excerpt"][:90])}</span></a>'
            for r in related)
        rel_html = f'<div class="related"><h2>More from the blog</h2>{items}</div>'
    breadcrumb = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"Blog","item":"https://vareadyapp.com/blog.html"},
        {"@type":"ListItem","position":3,"name":p["title"],"item":canon}]})
    # Optional per-post byline (frontmatter `author` / `author_url`). When absent,
    # the post is published under the app's name, as before.
    author_name = p.get("author", "VA Ready App")
    author_url = p.get("author_url") or ("/founders.html" if p.get("author") else "https://vareadyapp.com/")
    author_url_abs = author_url if author_url.startswith("http") else f"https://vareadyapp.com{author_url}"
    author_ld = ({"@type":"Person","name":author_name,"url":author_url_abs} if p.get("author")
                 else {"@type":"Organization","name":"VA Ready App","url":"https://vareadyapp.com/"})
    article_ld = json.dumps({
        "@context":"https://schema.org","@type":"BlogPosting","headline":p["title"][:110],
        "description":p["excerpt"],"datePublished":p["date"],"dateModified":p["date"],
        "image":img_url,"articleSection":p["category"],
        "author":author_ld,
        "publisher":{"@type":"Organization","name":"VA Ready","logo":{"@type":"ImageObject","url":"https://vareadyapp.com/logo.png"}},
        "mainEntityOfPage":canon,"inLanguage":"en-US"})
    byline = (f'<a href="{esc(author_url)}">{esc(author_name)}</a>' if p.get("author") else "<strong>VA Ready App</strong>")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(p['title'])} | VA Ready Blog</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="{esc(p['title'])}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{img_url}">
<meta property="article:published_time" content="{p['date']}">
<meta property="article:section" content="{esc(p['category'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(p['title'])}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img_url}">
<link rel="icon" type="image/png" href="/logo.png">
<script type="application/ld+json">{breadcrumb}</script>
<script type="application/ld+json">{article_ld}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/blog.html">Blog</a> / {esc(p['category'])}</div>
    <div class="eyebrow">{esc(p['category'])}</div>
    <h1>{esc(p['title'])}</h1>
    <p class="lede">{esc(p['excerpt'])}</p>
    <div class="meta">{byline} &middot; {p['date_label']} &middot; {p['reading']} min read</div>
    {hero}
    <article>
{body}
    </article>
    <div class="post-sign">VA Ready is built by veterans, for veterans. It is not affiliated with the U.S. Department of Veterans Affairs. Information is sourced from public VA regulations (38 CFR) and peer-reviewed medical literature, and is provided for educational purposes only. Consult a VA-accredited VSO, agent, or attorney before filing.<br>VA Ready on iPhone &amp; iPad &middot; Vet Ready on Android &middot; vareadyapp.com</div>
    {BLOG_CTA}
    {rel_html}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""

# ---------- index page ----------
def card(p):
    if img_exists(p.get("image")):
        thumb = f'<img class="thumb" src="{esc(p["image"])}" alt="{esc(p.get("image_alt",""))}" loading="lazy">'
    else:
        thumb = '<div class="thumb ph"><span>VA READY</span></div>'
    return (f'<div class="bcard"><a class="bc-link" href="{p["url"]}">{thumb}'
            f'<div class="bc-body"><span class="bc-tag">{esc(p["category"])}</span>'
            f'<h3>{esc(p["title"])}</h3><p class="bc-ex">{esc(p["excerpt"][:140])}</p>'
            f'<div class="bc-meta">{p["date_label"]} &middot; {p["reading"]} min read</div></div></a></div>')

def index_page():
    cats = {}
    for p in posts:
        cats.setdefault(p["category"], []).append(p)
    sections = ""
    for cat, items in cats.items():
        cards = "".join(card(p) for p in items)
        sections += f'<div class="cat-head"><h2>{esc(cat)}</h2></div><div class="blog-grid">{cards}</div>'
    desc = "Straight-talk reads for veterans filing VA disability claims — filing smarter, protecting your information, and getting the rating you earned. From the team behind VA Ready."
    breadcrumb = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"Blog","item":"https://vareadyapp.com/blog.html"}]})
    blog_ld = json.dumps({"@context":"https://schema.org","@type":"Blog","name":"VA Ready Blog",
        "url":"https://vareadyapp.com/blog.html","description":desc,
        "publisher":{"@type":"Organization","name":"VA Ready","logo":{"@type":"ImageObject","url":"https://vareadyapp.com/logo.png"}},
        "blogPost":[{"@type":"BlogPosting","headline":p["title"],"url":f'https://vareadyapp.com{p["url"]}',"datePublished":p["date"]} for p in posts]})
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VA Ready Blog — Straight Talk for Veterans Filing VA Claims</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="https://vareadyapp.com/blog.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="VA Ready Blog — Straight Talk for Veterans">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="https://vareadyapp.com/blog.html">
<meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="/logo.png">
<script type="application/ld+json">{breadcrumb}</script>
<script type="application/ld+json">{blog_ld}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / Blog</div>
    <div class="eyebrow">VA Ready Blog</div>
    <h1>Straight Talk for Veterans Filing VA Claims</h1>
    <p class="lede">Plain-language reads on filing smarter, protecting your information, and getting the rating you earned &mdash; from the team behind VA Ready.</p>
    {sections}
    {BLOG_CTA}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""

# ---------- write ----------
for p in posts:
    related = [r for r in posts if r["slug"] != p["slug"]][:4]
    open(os.path.join(BLOG_OUT, p["slug"] + ".html"), "w", encoding="utf-8").write(post_page(p, related))
open(os.path.join(SITE, "blog.html"), "w", encoding="utf-8").write(index_page())

# ---------- sitemap append ----------
sp = os.path.join(SITE, "sitemap.xml")
xml = open(sp).read()
add = []
if "https://vareadyapp.com/blog.html" not in xml:
    add.append(("https://vareadyapp.com/blog.html", "0.8"))
for p in posts:
    u = f'https://vareadyapp.com{p["url"]}'
    if u not in xml:
        add.append((u, "0.7"))
if add:
    block = "".join(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-06-14</lastmod>\n    <priority>{pri}</priority>\n  </url>\n' for u, pri in add)
    xml = xml.replace("</urlset>", block + "</urlset>")
    open(sp, "w").write(xml)

# ---------- validate JSON-LD ----------
allhtml = open(os.path.join(SITE, "blog.html")).read()
for p in posts:
    allhtml += open(os.path.join(BLOG_OUT, p["slug"] + ".html")).read()
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', allhtml, re.S):
    json.loads(blk)

print(f"generated {len(posts)} blog post(s) + index")
print("categories:", sorted({p['category'] for p in posts}))
print("sitemap +", len(add), "url(s)")
print("JSON-LD valid")
