#!/usr/bin/env python3
"""County VSO landing pages: /vso/<state>/<county>.html.

One page per county with at least gen_vso.COUNTY_MIN offices (DC skipped). Built
from the same office snapshot as the state pages, so it shows nothing that is not
already public on the state page: listings, VA accreditation, star average and
review count. Review comments stay in the app.

Run after gen_vso.py (which links each state page to these), then gen_vso_near.py.
"""
import glob, json, math, os, re
import gen_vso as g   # importing does not write anything (see MAIN in gen_vso.py)

esc, slug, STATES, RATINGS = g.esc, g.slug, g.STATES, g.RATINGS
TODAY = __import__("datetime").date.today().isoformat()
NEARBY = 6

CSS = g.CSS + """
    .county-cta { border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:18px 0; margin:26px 0; display:flex; gap:24px; align-items:center; }
    .county-cta p { margin:0 0 12px; max-width:68ch; }
    .county-cta .btns { display:flex; flex-wrap:wrap; gap:10px; }
    .county-cta .btn { min-height:44px; }
    .county-cta .qr { flex:none; text-align:center; color:var(--gray); font-size:13px; }
    .county-cta .qr img { width:132px; height:132px; display:block; background:#fff; padding:8px; border-radius:8px; margin-bottom:6px; }
    @media (max-width: 760px) { .county-cta .qr { display:none; } }
    .prep { max-width:68ch; }
"""

def centroid(offs):
    pts = [(o["latitude"], o["longitude"]) for o in offs if o.get("latitude") is not None and o.get("longitude") is not None]
    if not pts: return None
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

def miles(a, b):
    x = math.pi / 180
    dlat, dlng = (b[0] - a[0]) * x, (b[1] - a[1]) * x
    q = math.sin(dlat / 2) ** 2 + math.cos(a[0] * x) * math.cos(b[0] * x) * math.sin(dlng / 2) ** 2
    return 3959 * 2 * math.atan2(math.sqrt(q), math.sqrt(1 - q))

CTA = """<div class="county-cta cta" id="get-the-app">
      <div>
        <p>Meeting with a VSO in {label}? Build your claim file in VA Ready first: scan or import your records, label each one with the VA document type, and tie it to the condition it supports. Pro adds a VSO packet with an evidence index on the front page, so your rep can turn straight to each record.</p>
        <div class="btns">
          <a href="https://apps.apple.com/app/id6761733758" class="btn primary">VA Ready for iPhone, iPad and Mac</a>
          <a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US" class="btn ghost">Vet Ready for Android</a>
          <a href="https://apps.microsoft.com/detail/9p8xfcqvfjhf" class="btn ghost">VA Ready for Windows</a>
        </div>
      </div>
      <div class="qr"><img src="/img/get-qr.png" alt="QR code that opens vareadyapp.com/get" width="132" height="132" loading="lazy">Scan with your phone</div>
    </div>"""

def page(sc, county, offs, nearby, others):
    sn = STATES[sc]; label = g.county_label(sc, county)
    url = f"https://vareadyapp.com{g.county_url(sc, county)}"
    state_url = f"https://vareadyapp.com/vso/{slug(sn)}.html"
    offs = sorted(offs, key=lambda o: (o.get("city") or "zzz", o.get("office_name") or ""))
    n = len(offs)
    orgs = [x for x, _ in __import__("collections").Counter(o.get("organization") for o in offs if o.get("organization")).most_common(3)]
    cities = sorted({o.get("city") for o in offs if o.get("city")})
    n_unacc = sum(1 for o in offs if not o.get("va_accredited"))
    acc_note = ("All are VA-accredited." if not n_unacc else
                f"{n_unacc} {'is' if n_unacc == 1 else 'are'} not VA-accredited and marked as such.")
    rated = [RATINGS[str(o["id"])] for o in offs if str(o.get("id")) in RATINGS]
    n_reviews = sum(r["n"] for r in rated)
    rating_line = (f" Veterans using VA Ready have rated {len(rated)} of these offices ({n_reviews} {'review' if n_reviews == 1 else 'reviews'}); "
                   "the stars show on each card, and the reviews are in the app." if rated else "")
    desc = (f"{n} veterans service offices in {label}, {sn}"
            + (f", including {orgs[0]}" if orgs else "")
            + ". Phone, directions and VA accreditation for each. A VSO files your VA claim for free.")
    if len(desc) > 160: desc = desc[:157].rsplit(" ", 1)[0] + "..."
    title = f"VSO offices in {label}, {sc} ({n}) | VA Ready"
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://vareadyapp.com/"},
        {"@type": "ListItem", "position": 2, "name": "Find a VSO", "item": "https://vareadyapp.com/find-a-vso.html"},
        {"@type": "ListItem", "position": 3, "name": f"{sn} VSO offices", "item": state_url},
        {"@type": "ListItem", "position": 4, "name": f"{label} VSO offices", "item": url}]}
    cards = "".join(g.card(o) for o in offs)
    near_links = "".join(f'<a href="{g.county_url(sc, c)}">{esc(g.county_label(sc, c))}</a>' for c in nearby)
    other_links = "".join(f'<a href="{g.county_url(sc, c)}">{esc(g.county_label(sc, c))}</a>' for c in others)
    def join(xs):
        return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
    shown = cities[:4] + (["other cities"] if len(cities) > 4 else [])
    city_note = (f" Offices are in {esc(join(shown))}." if cities else "")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="VSO offices in {esc(label)}, {esc(sn)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<script type="application/ld+json">{json.dumps(bc)}</script>
<style>{CSS}</style>
</head>
<body>
{g.NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/find-a-vso.html">Find a VSO</a> / <a href="/vso/{slug(sn)}.html">{esc(sn)}</a> / {esc(label)}</div>
    <h1>VSO offices in {esc(label)}, {esc(sn)}</h1>
    <p class="lede">{n} offices in {esc(label)} help veterans file VA claims for free. {acc_note}{city_note}{esc(rating_line)} Search by city or name, or tap Near me.</p>
    <div class="vso-tools">
        <input id="vsoFilter" type="text" placeholder="Search by city or office name&hellip;" aria-label="Filter VSO offices">
        <button id="vsoNear" type="button">Near me</button>
    </div>
    <div class="vso-meta">Showing <span id="vsoCount">{n}</span> of {n} offices{(' &middot; incl. ' + ', '.join(esc(o) for o in orgs)) if orgs else ''}{' &middot; <a href="#get-the-app">Build your claim file before you go</a>' if n > 10 else ''}</div>
    <ul id="vsoList">{cards}</ul>

    <h2 class="vso-hub-h">Before you meet your VSO</h2>
    <p class="prep">Bring your DD214, any letters from VA, and a list of your conditions with when each one started and where you were treated. If you have not filed yet, ask about an intent to file: it can hold your start date for up to a year while you gather evidence (38 CFR 3.155). See <a href="/guides/veterans-service-officers-vsos.html">what a VSO does and how to avoid claim sharks</a>.</p>

    {CTA.format(label=esc(label))}

    {f'<h2 class="vso-hub-h">Nearby counties</h2><div class="statepick">{near_links}</div>' if near_links else ''}
    {f'<h2 class="vso-hub-h">Other counties in {esc(sn)}</h2><div class="statepick">{other_links}</div>' if other_links else ''}
    <p class="trustline">See <a href="/vso/{slug(sn)}.html">every VSO office in {esc(sn)} &rarr;</a></p>
    <div class="disclaimer">Office listings are compiled from public VA accreditation data and may change; confirm details before visiting.{" Ratings reflect veterans' own opinions submitted in the VA Ready app and are not endorsements by VA Ready." if rated else ""} VA Ready is not affiliated with the U.S. Department of Veterans Affairs.</div>
</div>
{g.FOOTER}
<script defer src="/vso/finder.js"></script>
</body>
</html>"""

written = []
for sc in g.states_out:
    qs = g.qualifying_counties(sc)
    if not qs: continue
    offs_by = {c: [o for o in g.by[sc] if o.get("county") == c] for c in qs}
    cents = {c: centroid(offs_by[c]) for c in qs}
    os.makedirs(os.path.join(g.VSODIR, slug(STATES[sc])), exist_ok=True)
    for c in qs:
        others = [x for x in qs if x != c]
        nearby = []
        if cents[c]:
            nearby = sorted([x for x in others if cents[x]], key=lambda x: miles(cents[c], cents[x]))[:NEARBY]
        rest = [x for x in others if x not in nearby]
        path = os.path.join(g.SITE, g.county_url(sc, c).lstrip("/"))
        open(path, "w").write(page(sc, c, offs_by[c], nearby, rest))
        written.append(g.county_url(sc, c))

# sitemap: add new URLs, keep existing entries untouched
sp = os.path.join(g.SITE, "sitemap.xml"); xml = open(sp).read(); new = []
for u in written:
    loc = f"https://vareadyapp.com{u}"
    if loc not in xml:
        new.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <priority>0.6</priority>\n  </url>")
if new:
    xml = xml.replace("</urlset>", "\n".join(new) + "\n</urlset>"); open(sp, "w").write(xml)

# checks: JSON-LD parses, no em dash, internal county links resolve
bad = 0
for u in written:
    s = open(os.path.join(g.SITE, u.lstrip("/"))).read()
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: json.loads(b)
        except Exception as e: bad += 1; print("BAD JSON-LD", u, e)
    if "—" in s or "&mdash;" in s: bad += 1; print("EM DASH", u)
    for h in re.findall(r'href="(/vso/[^"]+\.html)"', s):
        if not os.path.exists(os.path.join(g.SITE, h.lstrip("/"))): bad += 1; print("MISSING", u, h)
print(f"wrote {len(written)} county pages in {len({u.split('/')[2] for u in written})} states; sitemap +{len(new)}; problems={bad}")
