#!/usr/bin/env python3
"""VA disability pay-rate pages (Cluster A): flagship full table + per-rating pages + SMC.
Data: data/compensation_rates.json, data/smc_rates.json (2026 = effective Dec 1, 2025).
Verified against VA.gov veteran-rates page (30/70/100% + spouse + child add) — exact match."""
import json, re, os, html
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
PAYDIR = os.path.join(SITE, "va-disability-pay")
os.makedirs(PAYDIR, exist_ok=True)

def esc(s): return html.escape(str(s) if s is not None else "", quote=True)
def money(v):
    try: return "$" + "{:,.2f}".format(float(v))
    except: return "—"

COMP = {r["rating_pct"]: r for r in json.load(open(os.path.join(HERE,"data","compensation_rates.json")))}
SMC = json.load(open(os.path.join(HERE,"data","smc_rates.json")))
RATINGS = [10,20,30,40,50,60,70,80,90,100]
EFFECTIVE = "December 1, 2025"
YEAR = "2026"

CSS = re.search(r'CSS = """(.*?)"""', open(os.path.join(HERE,"gen_guides.py")).read(), re.S).group(1) + """
    table.pt { width:100%; border-collapse:collapse; margin:10px 0 18px; font-size:15px; }
    table.pt th, table.pt td { text-align:left; padding:10px 12px; border-bottom:1px solid var(--line); }
    table.pt th { color:var(--gold); font-size:12px; text-transform:uppercase; letter-spacing:.8px; }
    table.pt td { color:var(--tan); }
    table.pt td.amt { color:var(--white); font-weight:800; white-space:nowrap; text-align:right; }
    table.pt th.amt { text-align:right; }
    table.pt tr td:first-child { color:var(--tan); }
    .bignum { font-size:40px; font-weight:900; color:var(--gold); line-height:1; margin:6px 0 2px; }
    .bignum-sub { color:var(--gray); font-size:14px; margin-bottom:14px; }
    .ratenav { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0; }
    .ratenav a { font-size:13px; font-weight:700; background:var(--card); border:1px solid var(--line); color:var(--tan); padding:7px 13px; border-radius:999px; text-decoration:none; }
    .ratenav a.cur { background:rgba(201,162,77,.16); color:var(--gold); border-color:transparent; }
    .trustline { font-size:13.5px; color:var(--tan); background:var(--card); border:1px solid var(--line); border-left:3px solid var(--gold); border-radius:10px; padding:9px 13px; margin:14px 0; }
    .trustline a { color:var(--gold); font-weight:700; text-decoration:none; }
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
    <div class="footer-social" style="display:flex;justify-content:center;gap:20px;margin:18px 0 2px;"><a href="https://www.tiktok.com/@vavet.ready" target="_blank" rel="me noopener" aria-label="VA Ready on TikTok" style="color:#d9a621;display:inline-flex;"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.6 5.82a4.28 4.28 0 0 1-1.01-2.82h-3.3v13.2a2.59 2.59 0 1 1-1.78-2.46V10.2a5.9 5.9 0 1 0 5.09 5.85V8.96a7.56 7.56 0 0 0 4.4 1.41V7.06a4.28 4.28 0 0 1-3.4-1.24Z"/></svg></a><a href="https://www.instagram.com/vareadyapp/" target="_blank" rel="me noopener" aria-label="VA Ready on Instagram" style="color:#d9a621;display:inline-flex;"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23a3.7 3.7 0 0 1-.9 1.38 3.7 3.7 0 0 1-1.38.9c-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.7 3.7 0 0 1-1.38-.9 3.7 3.7 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23-.06-1.27-.07-1.65-.07-4.85s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.17 8.8 2.16 12 2.16M12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63a5.86 5.86 0 0 0-2.12 1.38A5.86 5.86 0 0 0 .64 4.13C.34 4.9.14 5.77.08 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.28.26 2.15.56 2.91a5.86 5.86 0 0 0 1.38 2.12 5.86 5.86 0 0 0 2.12 1.38c.76.3 1.63.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.28-.06 2.15-.26 2.91-.56a5.86 5.86 0 0 0 2.12-1.38 5.86 5.86 0 0 0 1.38-2.12c.3-.76.5-1.63.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.28-.26-2.15-.56-2.91a5.86 5.86 0 0 0-1.38-2.12A5.86 5.86 0 0 0 19.87.63c-.76-.3-1.63-.5-2.91-.56C15.67.01 15.26 0 12 0Zm0 5.84A6.16 6.16 0 1 0 18.16 12 6.16 6.16 0 0 0 12 5.84Zm0 10.16A4 4 0 1 1 16 12a4 4 0 0 1-4 4Zm6.41-10.4a1.44 1.44 0 1 0 1.44 1.44 1.44 1.44 0 0 0-1.44-1.44Z"/></svg></a><a href="https://www.facebook.com/vareadyapp" target="_blank" rel="me noopener" aria-label="VA Ready on Facebook" style="color:#d9a621;display:inline-flex;"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07c0 6.03 4.39 11.03 10.13 11.93v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.69 4.53-4.69 1.31 0 2.68.24 2.68.24v2.97h-1.51c-1.49 0-1.96.93-1.96 1.89v2.25h3.33l-.53 3.49h-2.8V24C19.61 23.1 24 18.1 24 12.07Z"/></svg></a></div>
</footer>
<script defer src="/_vercel/insights/script.js"></script>
<script defer src="/track.js"></script>"""
DISCLAIMER = f"""<div class="disclaimer">Rates shown are the VA disability compensation rates effective {EFFECTIVE} (the {YEAR} rates), verified against VA.gov. VA adjusts rates annually for cost of living. Always confirm the current amount for your situation at VA.gov. VA Ready is not affiliated with the U.S. Department of Veterans Affairs, and this page is not financial or legal advice.</div>"""
APPBTNS = """<p style="margin:20px 0;"><a href="/va-disability-calculator.html" class="btn">Calculate your combined rating &rarr;</a> &nbsp; <a href="/va-disability-pay-rates.html" class="btn ghost">Full pay-rate chart &rarr;</a></p>"""

def head(title, desc, canon, ld_blocks):
    lds = "\n".join(f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in ld_blocks)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="/logo.png">
{lds}
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">"""

def article_ld(title, desc, canon):
    return {"@context":"https://schema.org","@type":"Article","headline":title,"description":desc,
        "datePublished":"2026-06-09","dateModified":"2026-06-09",
        "author":{"@type":"Organization","name":"JDL Software LLC"},"publisher":{"@type":"Organization","name":"VA Ready"},
        "mainEntityOfPage":canon,"inLanguage":"en-US"}
def faq_ld(faqs):
    return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
def bc_ld(items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":u} for i,(n,u) in enumerate(items)]}

def ratenav(cur):
    links = "".join(f'<a class="cur">{p}%</a>' if p==cur else f'<a href="/va-disability-pay/{p}-percent.html">{p}%</a>' for p in RATINGS)
    return f'<div class="ratenav">{links}</div>'

# ---------- per-rating page ----------
def rating_page(p):
    r = COMP[p]
    canon = f"https://vareadyapp.com/va-disability-pay/{p}-percent.html"
    alone = money(r["veteran_alone"])
    has_dep = p >= 30
    title = f"{p}% VA Disability Pay ({YEAR}) — Monthly Amount With & Without Dependents"
    if has_dep:
        desc = f"{p}% VA disability pays {alone}/month for a veteran alone in {YEAR} (effective Dec 1, 2025), more with dependents. Full {p}% rate table by spouse, children, and parents."
    else:
        desc = f"{p}% VA disability pays {alone}/month in {YEAR} (effective Dec 1, 2025). Dependent amounts don't start until 30%. See the full VA pay chart."
    desc = desc[:160]
    # table rows
    rows = [("Veteran alone (no dependents)", r["veteran_alone"])]
    if has_dep:
        rows += [
            ("With spouse (no children)", r["veteran_spouse"]),
            ("With spouse and 1 child", r["veteran_spouse_1child"]),
            ("With spouse and 2 children", r["veteran_spouse_2child"]),
            ("With 1 child (no spouse)", r["veteran_1child"]),
            ("With 1 dependent parent", r["veteran_1parent"]),
            ("With 2 dependent parents", r["veteran_2parents"]),
            ("With spouse and 1 parent", r["veteran_spouse_1parent"]),
        ]
    body = "".join(f'<tr><td>{esc(label)}</td><td class="amt">{money(v)}</td></tr>' for label,v in rows if v is not None)
    table = f'<table class="pt"><thead><tr><th>Your situation</th><th class="amt">Monthly (tax-free)</th></tr></thead><tbody>{body}</tbody></table>'
    added = ""
    if has_dep:
        added = ('<h2>Added amounts (on top of the above)</h2><table class="pt"><tbody>'
            f'<tr><td>Each additional child under 18</td><td class="amt">+{money(r["add_child_under18"])}</td></tr>'
            f'<tr><td>Each child 18+ in a qualifying school program</td><td class="amt">+{money(r["add_child_school_over18"])}</td></tr>'
            f'<tr><td>Spouse receiving Aid &amp; Attendance</td><td class="amt">+{money(r["add_spouse_aid_attendance"])}</td></tr>'
            '</tbody></table>')
    dep_note = ("" if has_dep else
        f'<p><strong>Note:</strong> VA only adds money for dependents once your rating reaches <strong>30%</strong>. At {p}% the amount is the same whether or not you have a spouse, children, or dependent parents.</p>')
    faqs = [
        (f"How much is {p}% VA disability per month in {YEAR}?",
         f"{p}% VA disability pays {alone} per month for a veteran with no dependents, effective December 1, 2025. "
         + (f"With dependents it is higher — for example {money(r['veteran_spouse'])} with a spouse." if has_dep else "Dependent amounts do not apply below 30%.")),
        ("Is VA disability compensation taxable?",
         "No. VA disability compensation is not taxed by the federal government or by states."),
        ("When did these rates take effect?",
         f"These are the {YEAR} rates, effective December 1, 2025. VA adjusts them each year for cost of living (COLA)."),
    ]
    if has_dep:
        faqs.append((f"Does {p}% VA disability include money for a spouse and kids?",
                     f"Yes. At {p}% VA adds dependent amounts — {money(r['veteran_spouse'])} with a spouse, {money(r['veteran_spouse_1child'])} with a spouse and one child, plus {money(r['add_child_under18'])} for each additional child under 18."))
    faq_visible = "".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q,a in faqs)
    lds = [bc_ld([("Home","https://vareadyapp.com/"),("VA Disability Pay Rates","https://vareadyapp.com/va-disability-pay-rates.html"),(f"{p}% VA Disability Pay",canon)]),
           article_ld(title,desc,canon), faq_ld(faqs)]
    out = head(title, desc, canon, lds)
    out += f"""
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/va-disability-pay-rates.html">Pay Rates</a> / {p}%</div>
    <div class="eyebrow">{YEAR} VA Disability Compensation</div>
    <h1>{p}% VA Disability Pay</h1>
    <p class="lede">A {p}% VA disability rating pays the amounts below each month, tax-free. These are the {YEAR} rates, effective {EFFECTIVE}.</p>
    {ratenav(p)}
    <div class="bignum">{alone}<span style="font-size:18px;color:var(--gray);font-weight:600;">/mo</span></div>
    <div class="bignum-sub">{p}% &mdash; veteran with no dependents</div>
    <article>
        <h2>{p}% VA disability monthly pay by dependents</h2>
        {table}
        {dep_note}
        {added}
        <h2>How VA pays your rating</h2>
        <p>VA pays compensation in 10% steps from 10% to 100%, and the amount is the same nationwide. If you have <strong>multiple conditions</strong>, VA combines them with its own math (not simple addition) and rounds to the nearest 10% — so a combined 75% pays at the {('80' )}% rate. Use the calculator to see where your conditions land.</p>
    </article>
    {APPBTNS}
    {APP_CTA}
    <p class="trustline">Wondering what your rating unlocks beyond the check? See <a href="/states.html">your state's veteran benefits</a> and whether you may be <a href="/guides/permanent-and-total-disability.html">Permanent &amp; Total</a>.</p>
    <h2 style="font-size:20px;margin-top:26px;">Common questions</h2>
    {faq_visible}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""
    return out

# ---------- flagship full chart ----------
def flagship():
    canon = "https://vareadyapp.com/va-disability-pay-rates.html"
    title = f"{YEAR} VA Disability Pay Rates — Full Monthly Compensation Chart"
    desc = f"The {YEAR} VA disability pay chart (effective Dec 1, 2025): monthly compensation for every rating 10%–100%, alone and with dependents. Verified against VA.gov."
    desc = desc[:160]
    # main table: ratings x key dependent columns
    cols = [("Alone","veteran_alone"),("+ Spouse","veteran_spouse"),("+ Spouse, 1 child","veteran_spouse_1child"),("+ Spouse, 2 children","veteran_spouse_2child")]
    head_cells = "".join(f'<th class="amt">{esc(c[0])}</th>' for c in cols)
    body = ""
    for p in RATINGS:
        r = COMP[p]
        cells = "".join(f'<td class="amt">{money(r[c[1]])}</td>' for c in cols)
        body += f'<tr><td><a href="/va-disability-pay/{p}-percent.html" style="color:var(--gold);font-weight:700;">{p}%</a></td>{cells}</tr>'
    table = f'<table class="pt"><thead><tr><th>Rating</th>{head_cells}</tr></thead><tbody>{body}</tbody></table>'
    faqs = [
        (f"How much does VA disability pay in {YEAR}?",
         f"For a veteran with no dependents, monthly compensation ranges from {money(COMP[10]['veteran_alone'])} at 10% to {money(COMP[100]['veteran_alone'])} at 100%, effective December 1, 2025. Dependents increase the amount starting at 30%."),
        ("How much is 100% VA disability per month?",
         f"100% VA disability pays {money(COMP[100]['veteran_alone'])} per month for a veteran alone, and {money(COMP[100]['veteran_spouse'])} with a spouse (no children), in {YEAR}."),
        ("Is VA disability pay taxable?", "No — VA disability compensation is not taxable at the federal or state level."),
        ("How does VA combine multiple ratings?",
         "VA does not add ratings together. It combines them with a formula and rounds to the nearest 10%, so a combined 75% is paid at the 80% rate. The VA Ready calculator does this math for you."),
    ]
    faq_visible = "".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q,a in faqs)
    lds = [bc_ld([("Home","https://vareadyapp.com/"),("VA Disability Pay Rates",canon)]), article_ld(title,desc,canon), faq_ld(faqs)]
    out = head(title, desc, canon, lds)
    out += f"""
    <div class="crumb"><a href="/index.html">Home</a> / VA Disability Pay Rates</div>
    <div class="eyebrow">{YEAR} Rates &middot; effective {EFFECTIVE}</div>
    <h1>{YEAR} VA Disability Pay Rates</h1>
    <p class="lede">How much VA disability compensation pays each month, tax-free, for every rating from 10% to 100% &mdash; alone and with dependents. These are the {YEAR} rates (effective {EFFECTIVE}), verified against VA.gov. Tap a rating for the full breakdown.</p>
    {ratenav(None)}
    <article>
        <h2>Monthly VA disability compensation by rating</h2>
        {table}
        <p>Dependent amounts apply at <strong>30% and above</strong>. At 10% and 20%, the amount is the same with or without dependents. Each page below also lists added amounts for extra children, school-age children, and a spouse receiving Aid &amp; Attendance.</p>
        <h2>Per-rating pay pages</h2>
        <div class="ratenav">{''.join(f'<a href="/va-disability-pay/{p}-percent.html">{p}% pay</a>' for p in RATINGS)}<a href="/va-disability-pay/special-monthly-compensation.html">SMC rates</a></div>
        <h2>How combined ratings work</h2>
        <p>If you have more than one service-connected condition, VA combines them with its own formula (not simple addition) and rounds to the nearest 10%. That's why two 30% conditions don't make 60%. The free calculator shows exactly where your conditions land and what it pays.</p>
    </article>
    {APPBTNS}
    {APP_CTA}
    <p class="trustline">More from VA Ready: <a href="/va-disability-pay/special-monthly-compensation.html">SMC rates</a> &middot; <a href="/conditions.html">VA ratings by condition</a> &middot; <a href="/states.html">State benefits</a></p>
    <h2 style="font-size:20px;margin-top:26px;">Common questions</h2>
    {faq_visible}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""
    return out

# ---------- SMC page ----------
def smc_page():
    canon = "https://vareadyapp.com/va-disability-pay/special-monthly-compensation.html"
    title = f"VA Special Monthly Compensation (SMC) Rates {YEAR}"
    desc = f"{YEAR} VA Special Monthly Compensation (SMC) rates, effective Dec 1, 2025: what SMC is, the SMC levels (K through R), and the monthly amounts. Verified against VA.gov."
    desc = desc[:160]
    rows = ""
    for s in SMC:
        amt = money(s.get("veteran_alone"))
        lvl = esc(s.get("smc_level")); d = esc(s.get("smc_description"))
        rows += f'<tr><td><strong style="color:var(--white);">{lvl}</strong></td><td>{d}</td><td class="amt">{amt}</td></tr>'
    table = f'<table class="pt"><thead><tr><th>SMC level</th><th>What it covers</th><th class="amt">Veteran alone / mo</th></tr></thead><tbody>{rows}</tbody></table>'
    faqs = [
        ("What is VA Special Monthly Compensation (SMC)?",
         "SMC is additional, higher-than-100% tax-free compensation for veterans with especially serious disabilities — such as loss or loss of use of a limb, blindness, being housebound, or needing Aid and Attendance — paid on top of or in place of the standard rating amount."),
        ("Who qualifies for SMC?",
         "Veterans with qualifying conditions like loss or loss of use of a hand, foot, eye, or reproductive organ; being permanently bedridden or housebound; or requiring the regular aid and attendance of another person. SMC-K is an add-on; higher levels replace the base rate."),
        ("When did these SMC rates take effect?",
         f"These are the {YEAR} SMC rates, effective December 1, 2025."),
    ]
    faq_visible = "".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q,a in faqs)
    lds = [bc_ld([("Home","https://vareadyapp.com/"),("VA Disability Pay Rates","https://vareadyapp.com/va-disability-pay-rates.html"),("Special Monthly Compensation",canon)]),
           article_ld(title,desc,canon), faq_ld(faqs)]
    out = head(title, desc, canon, lds)
    out += f"""
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/va-disability-pay-rates.html">Pay Rates</a> / SMC</div>
    <div class="eyebrow">{YEAR} Rates &middot; effective {EFFECTIVE}</div>
    <h1>VA Special Monthly Compensation (SMC) Rates</h1>
    <p class="lede">Special Monthly Compensation (SMC) is extra, tax-free compensation above the normal rating schedule for the most serious service-connected disabilities. These are the {YEAR} SMC rates (effective {EFFECTIVE}).</p>
    <article>
        <h2>What SMC is</h2>
        <p>SMC recognizes disabilities that go beyond what a percentage rating captures &mdash; loss or loss of use of a limb, eye, or reproductive organ; deafness or blindness; being housebound; or needing the regular <strong>Aid and Attendance</strong> of another person. Some SMC levels (like SMC-K) are <em>added</em> to your regular compensation; higher levels <em>replace</em> the base 100% amount with a larger one.</p>
        <h2>{YEAR} SMC rate levels (veteran alone)</h2>
        {table}
        <p>SMC amounts also increase with dependents. The figures above are for a veteran alone; check VA.gov or ask a VSO for your exact amount.</p>
    </article>
    {APPBTNS}
    {APP_CTA}
    <p class="trustline">Related: <a href="/va-disability-pay-rates.html">full VA pay chart</a> &middot; <a href="/guides/permanent-and-total-disability.html">Permanent &amp; Total</a> &middot; <a href="/conditions.html">ratings by condition</a></p>
    <h2 style="font-size:20px;margin-top:26px;">Common questions</h2>
    {faq_visible}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""
    return out

# import APP_CTA from gen_states constant by reading it (keeps one source)
APP_CTA = re.search(r'APP_CTA = """(.*?)"""', open(os.path.join(HERE,"gen_states.py")).read(), re.S).group(1)

# write pages
open(os.path.join(SITE,"va-disability-pay-rates.html"),"w").write(flagship())
for p in RATINGS:
    open(os.path.join(PAYDIR,f"{p}-percent.html"),"w").write(rating_page(p))
open(os.path.join(PAYDIR,"special-monthly-compensation.html"),"w").write(smc_page())

# sitemap merge
sp = os.path.join(SITE,"sitemap.xml"); xml = open(sp).read(); new=[]
urls = [("https://vareadyapp.com/va-disability-pay-rates.html","0.8")]
urls += [(f"https://vareadyapp.com/va-disability-pay/{p}-percent.html","0.7") for p in RATINGS]
urls += [("https://vareadyapp.com/va-disability-pay/special-monthly-compensation.html","0.6")]
for u,pr in urls:
    if u not in xml: new.append(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-06-09</lastmod>\n    <priority>{pr}</priority>\n  </url>')
if new:
    xml = xml.replace("</urlset>", "\n".join(new)+"\n</urlset>"); open(sp,"w").write(xml)

# validate JSON-LD
import glob
bad=0
for f in [os.path.join(SITE,"va-disability-pay-rates.html")]+glob.glob(os.path.join(PAYDIR,"*.html")):
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', open(f).read(), re.S):
        try: json.loads(blk)
        except Exception as e: bad+=1; print("BAD JSON-LD",f,e)
print(f"wrote flagship + {len(RATINGS)} rating pages + SMC; sitemap +{len(new)}; JSON-LD bad={bad}")
