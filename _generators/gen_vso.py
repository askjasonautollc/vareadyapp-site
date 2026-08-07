#!/usr/bin/env python3
"""VSO finder vertical (Cluster C): a crawlable, searchable page per state from vso_offices.
Build-time baked. NO Supabase key on the site. Public = aggregate star ratings only
(comments stay in-app). Each state page bakes its offices as HTML + a JS filter + geo 'near me'."""
import json, re, os, html
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
VSODIR = os.path.join(SITE, "vso")
os.makedirs(VSODIR, exist_ok=True)
def esc(s): return html.escape(str(s) if s is not None else "", quote=True)

OFFICES = json.load(open(os.path.join(HERE,"data","vso_offices.json")))
RATINGS = json.load(open(os.path.join(HERE,"data","vso_ratings.json")))

STATES = {
"AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut",
"DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois",
"IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts",
"MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada",
"NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota",
"OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota",
"TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia",
"WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico","GU":"Guam","VI":"U.S. Virgin Islands","AS":"American Samoa","MP":"Northern Mariana Islands",
}
def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")

# group offices by valid state
by = {}
for o in OFFICES:
    sc = o.get("state_code")
    if sc in STATES: by.setdefault(sc, []).append(o)

CSS = re.search(r'CSS = """(.*?)"""', open(os.path.join(HERE,"gen_guides.py")).read(), re.S).group(1) + """
    .vso-tools { display:flex; flex-wrap:wrap; gap:10px; margin:14px 0 6px; align-items:center; }
    #vsoFilter { flex:1; min-width:200px; background:var(--card); border:1px solid var(--line); color:var(--white); border-radius:10px; padding:11px 14px; font-size:15px; }
    #vsoNear { background:rgba(201,162,77,.16); color:var(--gold); border:1px solid transparent; border-radius:10px; padding:11px 14px; font-size:14px; font-weight:700; cursor:pointer; }
    .vso-meta { color:var(--gray); font-size:13.5px; margin:6px 0 14px; }
    .vso-meta strong { color:var(--white); }
    #vsoList { list-style:none; padding:0; margin:0; }
    /* content-visibility lets the browser skip layout and paint for cards that
       are off screen. On a big state like Texas that is 800+ cards it never has
       to render until scrolled to. contain-intrinsic-size keeps the scrollbar
       honest by reserving each card's approximate height. */
    .vso-card { background:var(--card); border:1px solid var(--line); border-radius:13px; padding:13px 15px; margin:0 0 11px;
                content-visibility:auto; contain-intrinsic-size:auto 118px; }
    .vso-card[hidden] { display:none; }
    .faq-item { border-top:1px solid var(--line); padding:16px 0; }
    .faq-item:first-of-type { border-top:none; }
    .faq-item h3 { font-size:16px; font-weight:800; color:var(--gold); margin-bottom:6px; }
    .faq-item p { font-size:14.5px; color:var(--tan); margin:0; }
    .vso-top { display:flex; flex-wrap:wrap; align-items:center; gap:8px; }
    .vso-name { color:var(--white); font-weight:800; font-size:16px; }
    .vso-acc { font-size:10.5px; font-weight:800; text-transform:uppercase; letter-spacing:.5px; background:rgba(52,168,83,.16); color:var(--green); padding:3px 8px; border-radius:999px; }
    .vso-rate { font-size:13px; color:var(--gold); font-weight:700; }
    .vso-dist { margin-left:auto; font-size:12px; color:var(--gray); font-weight:700; }
    .vso-org { color:var(--tan); font-size:14px; margin-top:3px; }
    .vso-loc { color:var(--gray); font-size:13px; margin-top:2px; }
    .vso-actions { display:flex; flex-wrap:wrap; gap:14px; margin-top:8px; }
    .vso-actions a { color:var(--gold); font-size:13px; font-weight:700; text-decoration:none; }
    .vso-actions a:hover { text-decoration:underline; }
    .trustline { font-size:13.5px; color:var(--tan); background:var(--card); border:1px solid var(--line); border-left:3px solid var(--gold); border-radius:10px; padding:9px 13px; margin:14px 0; }
    .trustline a { color:var(--gold); font-weight:700; text-decoration:none; }
    .statepick { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0; }
    .statepick a { font-size:14px; background:var(--card); border:1px solid var(--line); color:var(--tan); padding:8px 13px; border-radius:10px; text-decoration:none; }
    .statepick a b { color:var(--white); } .statepick a span { color:var(--gray); font-size:12px; }
"""
NAV = re.search(r'NAV = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)
FOOTER = re.search(r'FOOTER = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)
APP_CTA = re.search(r'APP_CTA = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)

def maps_link(o):
    if o.get("latitude") and o.get("longitude"):
        return f"https://www.google.com/maps/search/?api=1&query={o['latitude']},{o['longitude']}"
    q = ", ".join([x for x in [o.get("office_name"), o.get("address"), o.get("city"), o.get("state_code")] if x])
    return "https://www.google.com/maps/search/?api=1&query=" + esc(q).replace(" ", "+")

def card(o):
    oid = str(o.get("id"))
    name = esc(o.get("office_name") or o.get("organization") or "VSO office")
    org = esc(o.get("organization") or ""); otype = esc(o.get("organization_type") or "")
    city = o.get("city"); county = o.get("county"); zc = o.get("zip"); sc = o.get("state_code")
    loc = ", ".join([x for x in [esc(city), sc] if x]) + (f" {esc(zc)}" if zc else "")
    if county: loc += f" &middot; {esc(county)} County"
    phone = o.get("phone") or o.get("toll_free_phone")
    web = o.get("website")
    acc = '<span class="vso-acc">VA-accredited</span>' if o.get("va_accredited") else ""
    r = RATINGS.get(oid)
    rate = f'<span class="vso-rate">&#9733; {r["avg"]} ({r["n"]})</span>' if r else ""
    search = " ".join([str(x) for x in [o.get("office_name"),o.get("organization"),o.get("organization_type"),city,county,zc] if x]).lower()
    search = re.sub(r'\s+',' ',search).replace('"',"")
    lat = o.get("latitude") if o.get("latitude") is not None else ""
    lng = o.get("longitude") if o.get("longitude") is not None else ""
    acts = []
    if phone: acts.append(f'<a href="tel:{esc(re.sub(r"[^0-9+]","",str(phone)))}">&#128222; Call</a>')
    if web:
        w = web if str(web).startswith("http") else "https://"+str(web)
        acts.append(f'<a href="{esc(w)}" target="_blank" rel="noopener nofollow">Website</a>')
    acts.append(f'<a href="{maps_link(o)}" target="_blank" rel="noopener nofollow">Directions</a>')
    org_line = " &middot; ".join([x for x in [org, otype] if x])
    return (f'<li class="vso-card" data-search="{esc(search)}" data-lat="{lat}" data-lng="{lng}">'
            f'<div class="vso-top"><span class="vso-name">{name}</span>{acc}{rate}<span class="vso-dist"></span></div>'
            + (f'<div class="vso-org">{org_line}</div>' if org_line else '')
            + (f'<div class="vso-loc">{loc}</div>' if loc.strip() else '')
            + f'<div class="vso-actions">{"".join(acts)}</div></li>')

def page(sc):
    sn = STATES[sc]; offs = by[sc]; sl = slug(sn)
    offs = sorted(offs, key=lambda o:(o.get("city") or "zzz", o.get("office_name") or ""))
    norgs = len({o.get("organization") for o in offs if o.get("organization")})
    ncities = len({o.get("city") for o in offs if o.get("city")})
    canon = f"https://vareadyapp.com/vso/{sl}.html"
    top_orgs = [x for x,_ in __import__("collections").Counter(o.get("organization") for o in offs if o.get("organization")).most_common(5)]
    desc = f"Find a free, VA-accredited Veterans Service Officer (VSO) in {sn}. {len(offs)} accredited offices across {norgs} organizations and {ncities} cities. Search, call, and get free claim help."
    desc = desc[:160]
    cards = "".join(card(o) for o in offs)
    faqs = [
        (f"Is a VSO free in {sn}?", f"Yes. Accredited Veterans Service Officers in {sn} help you file your VA claim at no charge. You never pay a VSO to prepare or file your claim."),
        (f"How do I find a VSO near me in {sn}?", f"Use the search above to filter {len(offs)} accredited {sn} offices by city or name, or tap 'Near me' to sort by distance. You can also use the free locator in the VA Ready app."),
        ("What does a VSO do?", "A VSO helps you file your claim, gather evidence, becomes your representative (VA Form 21-22), and represents you through appeals, all free. They help you avoid paying a 'claim shark' for help you can get at no cost."),
    ]
    faq_v = "".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q,a in faqs)
    lds = [
        {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
            {"@type":"ListItem","position":2,"name":"Find a VSO","item":"https://vareadyapp.com/find-a-vso.html"},
            {"@type":"ListItem","position":3,"name":f"{sn} VSO offices","item":canon}]},
        {"@context":"https://schema.org","@type":"Article","headline":f"Find a Free Accredited VSO in {sn}","description":desc,"datePublished":"2026-06-12","dateModified":"2026-06-12","author":{"@type":"Organization","name":"JDL Software LLC"},"publisher":{"@type":"Organization","name":"VA Ready"},"mainEntityOfPage":canon,"inLanguage":"en-US"},
        {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]},
    ]
    lds_html = "\n".join(f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in lds)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Find a Free Accredited VSO in {esc(sn)} ({len(offs)} offices) | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="Find a Free Accredited VSO in {esc(sn)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" href="/logo.png">
{lds_html}
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/find-a-vso.html">Find a VSO</a> / {esc(sn)}</div>
    <div class="eyebrow">Free Accredited VSO Finder</div>
    <h1>Find a Free, Accredited VSO in {esc(sn)}</h1>
    <p class="lede">A Veterans Service Officer (VSO) helps you file your VA claim, <strong>for free</strong>. Below are <strong>{len(offs)}</strong> accredited offices across {esc(sn)}. Search by city or name, or tap <em>Near me</em>. Never pay a claim shark for help you can get at no cost.</p>
    <div class="vso-tools">
        <input id="vsoFilter" type="text" placeholder="Search by city, county, or office name&hellip;" aria-label="Filter VSO offices">
        <button id="vsoNear" type="button">&#128205; Near me</button>
    </div>
    <div class="vso-meta">Showing <strong id="vsoCount">{len(offs)}</strong> of {len(offs)} accredited offices &middot; {norgs} organizations &middot; {ncities} cities{(' &middot; incl. ' + ', '.join(esc(o) for o in top_orgs[:3])) if top_orgs else ''}</div>
    <ul id="vsoList">{cards}</ul>
    <p class="trustline">New to VSOs? See <a href="/guides/veterans-service-officers-vsos.html">what a VSO does and how to avoid claim sharks &rarr;</a></p>
    {APP_CTA}
    <h2 style="font-size:20px;margin-top:26px;">Common questions</h2>
    {faq_v}
    <p class="trustline">Find a VSO in another state: <a href="/find-a-vso.html">browse all states &rarr;</a></p>
    <div class="disclaimer">Office listings are compiled from public VA accreditation data and may change; confirm details before visiting. Ratings reflect veterans' own opinions submitted in the VA Ready app and are not endorsements by VA Ready. VA Ready is not affiliated with the U.S. Department of Veterans Affairs.</div>
</div>
{FOOTER}
<script defer src="/vso/finder.js"></script>
</body>
</html>"""

# write state pages
states_out = [sc for sc in STATES if sc in by]
states_out.sort(key=lambda sc: -len(by[sc]))
for sc in states_out:
    open(os.path.join(VSODIR, slug(STATES[sc])+".html"),"w").write(page(sc))

# finder.js
open(os.path.join(VSODIR,"finder.js"),"w").write(
"""(function(){var i=document.getElementById('vsoFilter'),l=document.getElementById('vsoList');if(!l)return;
var cards=[].slice.call(l.querySelectorAll('.vso-card')),cnt=document.getElementById('vsoCount'),raf=0;
/* Cache the haystack once. Reading a data attribute per card per keystroke was
   forcing a DOM read on 800+ nodes for every character typed. */
var hay=cards.map(function(c){return (c.getAttribute('data-search')||'').toLowerCase();});
/* Toggle the hidden attribute instead of writing style.display, and only when
   the state actually changes. Writing display on every card every keystroke was
   the layout thrash that made a big state feel stuck while typing. */
function apply(){raf=0;var q=(i.value||'').toLowerCase().trim(),s=0;
for(var n=0;n<cards.length;n++){var m=!q||hay[n].indexOf(q)>-1;if(m)s++;
if(cards[n].hidden===m)cards[n].hidden=!m;}
if(cnt)cnt.textContent=s;}
/* Coalesce to one pass per frame, so holding a key down cannot queue work. */
function f(){if(raf)return;raf=requestAnimationFrame(apply);}
if(i)i.addEventListener('input',f);
var b=document.getElementById('vsoNear');
if(b&&navigator.geolocation){b.addEventListener('click',function(){b.textContent='Locating\\u2026';navigator.geolocation.getCurrentPosition(function(p){var la=p.coords.latitude,lo=p.coords.longitude;
function d(a,b2,c2,d2){var R=3959,x=Math.PI/180,u=(c2-a)*x,v=(d2-b2)*x,q=Math.sin(u/2)*Math.sin(u/2)+Math.cos(a*x)*Math.cos(c2*x)*Math.sin(v/2)*Math.sin(v/2);return R*2*Math.atan2(Math.sqrt(q),Math.sqrt(1-q));}
var order=cards.map(function(c,n){var la2=parseFloat(c.getAttribute('data-lat')),lo2=parseFloat(c.getAttribute('data-lng')),dd=(!isNaN(la2)&&!isNaN(lo2))?d(la,lo,la2,lo2):1e9;var bd=c.querySelector('.vso-dist');if(bd&&dd<1e9)bd.textContent=dd.toFixed(0)+' mi';return{c:c,d:dd,n:n};});
order.sort(function(a,b3){return a.d-b3.d||a.n-b3.n;});
/* One fragment, one reflow, instead of 800 appendChild calls against the live list. */
var fr=document.createDocumentFragment();order.forEach(function(o){fr.appendChild(o.c);});l.appendChild(fr);
cards=order.map(function(o){return o.c;});hay=cards.map(function(c){return (c.getAttribute('data-search')||'').toLowerCase();});
b.textContent='\\u2713 Nearest first';},function(){b.textContent='Location unavailable';});});}
})();""")

# hub
def hub():
    canon="https://vareadyapp.com/find-a-vso.html"
    total=sum(len(by[sc]) for sc in states_out)
    picks="".join(f'<a href="/vso/{slug(STATES[sc])}.html"><b>{esc(STATES[sc])}</b> <span>{len(by[sc])}</span></a>' for sc in sorted(states_out, key=lambda s:STATES[s]))
    desc=f"Looking for a VSO near me? Search {total:,} free VA-accredited Veterans Service Officer offices across {len(states_out)} states and territories. They file your claim at no cost."
    desc=desc[:160]
    bc={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},{"@type":"ListItem","position":2,"name":"Find a VSO","item":canon}]}
    # ItemList of the state pages. Legitimate: these are our own pages and this
    # is literally a list of them. Deliberately NOT LocalBusiness, which would
    # claim we operate these offices; we do not, and marking them up as ours
    # would be schema spam.
    il={"@context":"https://schema.org","@type":"ItemList",
        "name":"Free accredited VSO offices by state",
        "numberOfItems":len(states_out),
        "itemListElement":[{"@type":"ListItem","position":n+1,"name":f"VSOs in {STATES[sc]}",
                            "url":f"https://vareadyapp.com/vso/{slug(STATES[sc])}.html"}
                           for n,sc in enumerate(sorted(states_out, key=lambda s:STATES[s]))]}
    faqs=[("What is a VSO?",
           "A Veterans Service Officer is a representative accredited by the VA to prepare, file, and track your disability claim. They are trained on the rating schedule and on VA procedure, and they can act as your representative with VA."),
          ("Are VSOs really free?",
           "Yes. A VA-accredited VSO prepares and files your claim at no cost, including your very first claim. Nobody may legally charge you a fee to file an original claim, and only accredited attorneys, claims agents, and VSO representatives may charge a fee at all, and only after VA has issued a decision."),
          ("How do I find a VSO near me?",
           f"Pick your state below to see the accredited offices in it, then sort by distance or search by city, county, or ZIP. We track {total:,} offices across {len(states_out)} states and territories, with phone numbers and directions for each."),
          ("Can a VSO help me if I live or serve overseas?",
           "Yes. Accreditation is not tied to where you live, so a VSO in your home state can represent you while you are stationed or living abroad. Overseas filers can also use a Federal Benefits Unit at a U.S. embassy or consulate."),
          ("What is the difference between a VSO and a claim shark?",
           "A VSO is accredited and free. An unaccredited consultant is neither, and typically wants a percentage of your back pay. Fees on a VA claim may only ever come out of past-due benefits, which is why fee-seekers concentrate on that lump sum.")]
    faq_ld={"@context":"https://schema.org","@type":"FAQPage",
            "mainEntity":[{"@type":"Question","name":q,
                           "acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    faq_html="".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q,a in faqs)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Find a VSO Near Me: {total:,} Free Accredited Offices | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="Find a VSO Near Me: Free Accredited Help"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" href="/logo.png">
<script type="application/ld+json">{json.dumps(bc)}</script>
<script type="application/ld+json">{json.dumps(il)}</script>
<script type="application/ld+json">{json.dumps(faq_ld)}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / Find a VSO</div>
    <div class="eyebrow">Free Accredited VSO Finder</div>
    <h1>Find a Free, Accredited VSO Near Me</h1>
    <p class="lede">Looking for a VSO near me? A <strong>Veterans Service Officer</strong> is a VA-accredited rep who will prepare and file your disability claim <strong>for free</strong>, including your very first one. We track <strong>{total:,}</strong> accredited offices across {len(states_out)} states and territories. Pick your state below to find the ones near you, get a phone number, and call.</p>
    <p class="lede">No vet should hand over a slice of their back pay for work a VSO does at no cost.</p>
    <p class="trustline">First time? Start with <a href="/guides/veterans-service-officers-vsos.html">what a VSO is, what they do, and how they keep you from paying a claim shark &rarr;</a></p>
    <h2>Choose your state</h2>
    <div class="statepick">{picks}</div>

    <h2>Stationed or living overseas?</h2>
    <p>Accreditation is not tied to where you live, so a VSO in your home state can represent you while you are stationed or living abroad. Pick the state you claim as your residence and work with them by phone and email; plenty of vets file their whole claim that way from Germany, Japan, Korea, or the Philippines.</p>
    <p>Two things worth knowing if you file from outside the United States. <strong>Federal Benefits Units</strong> at U.S. embassies and consulates handle VA benefits questions overseas and can point you at the right office. And VA can arrange an exam abroad through the Foreign Medical Program, so being OCONUS does not stop a claim from moving.</p>
    <p class="trustline">Filing from outside the U.S.? Read <a href="/guides/va-benefits-while-abroad.html">VA benefits while abroad: foreign claims, FMP, overseas exams, and international direct deposit &rarr;</a></p>

    <h2>Common questions</h2>
    {faq_html}

    {APP_CTA}
    <div class="disclaimer">Office listings are compiled from public VA accreditation data and may change; confirm details before visiting. Ratings reflect veterans' own opinions submitted in the VA Ready app, not endorsements by VA Ready. VA Ready is not affiliated with the U.S. Department of Veterans Affairs.</div>
</div>
{FOOTER}
</body>
</html>"""
open(os.path.join(SITE,"find-a-vso.html"),"w").write(hub())

# sitemap
sp=os.path.join(SITE,"sitemap.xml"); xml=open(sp).read(); new=[]
urls=[("https://vareadyapp.com/find-a-vso.html","0.8")]+[(f"https://vareadyapp.com/vso/{slug(STATES[sc])}.html","0.7") for sc in states_out]
for u,pr in urls:
    if u not in xml: new.append(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-06-12</lastmod>\n    <priority>{pr}</priority>\n  </url>')
if new: xml=xml.replace("</urlset>","\n".join(new)+"\n</urlset>"); open(sp,"w").write(xml)

import glob
bad=0
for f in [os.path.join(SITE,"find-a-vso.html")]+glob.glob(os.path.join(VSODIR,"*.html")):
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>',open(f).read(),re.S):
        try: json.loads(b)
        except Exception as e: bad+=1;print("BAD",f,e)
print(f"wrote {len(states_out)} state pages + hub + finder.js; total offices {sum(len(by[sc]) for sc in states_out)}; sitemap +{len(new)}; JSON-LD bad={bad}")
