#!/usr/bin/env python3
"""2027 VA disability pay-rate page, OFFICIAL version (replaces the estimate page at the same URL).

Run only through switch_pay_2027.py, after VA publishes its 2027 table.
Inputs:
  data/compensation_rates.json       2026 table (effective Dec 1, 2025), the prior year
  data/compensation_rates_2027.json  VA's published 2027 table, same schema
  data/smc_rates.json / data/smc_rates_2027.json
  data/pay_2027_meta.json            {"va_published": "December 2, 2026", "va_url": "...",
                                      "law": "...", "law_url": "...", "modified": "2026-12-02"}
Template: the head, nav and footer of ../va-disability-pay-rates.html.
"""
import json, os, re, html
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
OUT = os.path.join(SITE, "va-disability-pay-rates-2027.html")
RATINGS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
DATA = os.path.join(HERE, "data")

def esc(s): return html.escape(str(s), quote=True)
def D(v): return Decimal(str(v))
def money(v): return "${:,.2f}".format(D(v))
def load(name): return json.load(open(os.path.join(DATA, name)))

OLD = {r["rating_pct"]: r for r in load("compensation_rates.json")}
NEW = {r["rating_pct"]: r for r in load("compensation_rates_2027.json")}
SMC_OLD = {s["smc_level"]: s for s in load("smc_rates.json")}
SMC_NEW = load("smc_rates_2027.json")
META = load("pay_2027_meta.json")
for k in ("va_published", "va_url", "law", "law_url", "modified"):
    assert META.get(k), f"pay_2027_meta.json is missing {k}"

live = open(os.path.join(SITE, "va-disability-pay-rates.html")).read()
style = re.search(r"<style>.*?</style>", live, re.S).group(0)
nav = re.search(r"<nav>.*?</nav>", live, re.S).group(0)
footer = re.search(r"<footer>.*?</body>", live, re.S).group(0)
cta = re.search(r'<div class="cta cta-line">.*?</div>', live, re.S).group(0)
btns = re.search(r'<div class="btns page-cta">.*?</div>', live, re.S).group(0)
extra_css = """<style>
    table.pt caption { text-align:left; color:var(--gray); font-size:13px; padding:0 12px 8px; }
</style>"""

def table(caption, head_cells, rows):
    th = "".join(f'<th class="{c}">{esc(t)}</th>' if c else f"<th>{esc(t)}</th>" for t, c in head_cells)
    tb = "".join("<tr>" + "".join(f'<td class="{c}">{v}</td>' if c else f"<td>{v}</td>" for v, c in row) + "</tr>"
                 for row in rows)
    return (f'<div class="tbl-wrap"><table class="pt"><caption>{esc(caption)}</caption>'
            f"<thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>")

def link(p): return f'<a href="/va-disability-pay/{p}-percent.html">{p}%</a>'

rows = []
for p in RATINGS:
    a, b = OLD[p]["veteran_alone"], NEW[p]["veteran_alone"]
    rows.append([(link(p), ""), (money(a), "amt"), (money(b), "amt"), ("+" + money(D(b) - D(a)), "amt")])
t_alone = table("Veteran alone, monthly, tax-free.",
                [("Rating", ""), ("2026", "amt"), ("2027", "amt"), ("Change", "amt")], rows)

cols = [("Alone", "veteran_alone"), ("With spouse", "veteran_spouse"),
        ("Spouse and 1 child", "veteran_spouse_1child"), ("Spouse and 2 children", "veteran_spouse_2child")]
t_dep = table("2027 monthly amounts. Dependent amounts start at 30%.",
              [("Rating", "")] + [(n, "amt") for n, _ in cols],
              [[(link(p), "")] + [(money(NEW[p][k]), "amt") for _, k in cols] for p in RATINGS])

t_add = table("2027 added amounts, per person.",
              [("Rating", ""), ("Each child under 18", "amt"), ("Each child 18+ in school", "amt"),
               ("Spouse on Aid & Attendance", "amt")],
              [[(f"{p}%", ""), ("+" + money(NEW[p]["add_child_under18"]), "amt"),
                ("+" + money(NEW[p]["add_child_school_over18"]), "amt"),
                ("+" + money(NEW[p]["add_spouse_aid_attendance"]), "amt")] for p in RATINGS if p >= 30])

rows = []
for s in SMC_NEW:
    if s["smc_level"] == "Q": continue
    lvl = s["smc_level"].replace("_half", " 1/2").replace("_", "/")
    rows.append([(esc("SMC-" + lvl), ""), (money(SMC_OLD[s["smc_level"]]["veteran_alone"]), "amt"),
                 (money(s["veteran_alone"]), "amt")])
t_smc = table("Special monthly compensation, veteran alone, monthly.",
              [("SMC level", ""), ("2026", "amt"), ("2027", "amt")], rows)

a100, b100 = OLD[100]["veteran_alone"], NEW[100]["veteran_alone"]
title = "2027 VA disability pay rates: official monthly amounts, 3.6% COLA"
desc = (f"VA's 2027 disability pay rates, effective Dec 1, 2026: 100% pays {money(b100)} a month alone. "
        "Every rating, with dependents and SMC, beside the 2026 amount.")[:160]
canon = "https://vareadyapp.com/va-disability-pay-rates-2027.html"
faqs = [
    ("How much did VA disability go up for 2027?",
     f"3.6 percent, the same cost-of-living increase as Social Security. A veteran rated 100% with no dependents goes from {money(a100)} to {money(b100)} a month."),
    ("When do the 2027 VA disability rates take effect?",
     "December 1, 2026. VA pays a month behind, so the first payment at the new rate arrives in early January 2027."),
    ("Where do these 2027 amounts come from?",
     f"VA's published compensation rate tables ({META['va_published']}). The 2026 amounts beside them are the rates effective December 1, 2025."),
]
ld = [
    {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://vareadyapp.com/"},
        {"@type": "ListItem", "position": 2, "name": "VA disability pay rates", "item": "https://vareadyapp.com/va-disability-pay-rates.html"},
        {"@type": "ListItem", "position": 3, "name": "2027 rates", "item": canon}]},
    {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
     "datePublished": "2026-10-15", "dateModified": META["modified"],
     "author": {"@type": "Organization", "name": "JDL Software LLC"},
     "publisher": {"@type": "Organization", "name": "VA Ready"}, "mainEntityOfPage": canon, "inLanguage": "en-US"},
    {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
]
lds = "\n".join(f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in ld)
faq_html = "".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q, a in faqs)

page = f"""<!DOCTYPE html>
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
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
{lds}
{style}
{extra_css}
</head>
<body>
{nav}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/va-disability-pay-rates.html">Pay Rates</a> / 2027</div>
    <h1>2027 VA disability pay rates</h1>
    <p class="lede">VA disability compensation rose 3.6% for 2027, effective December 1, 2026. The first payment at the new rate arrives in early January 2027. Each table puts the 2027 amount beside the 2026 one.</p>
    <article>
        <h2>2027 pay, veteran alone</h2>
        <p>A veteran rated 100% with no dependents goes from {money(a100)} to {money(b100)} a month.</p>
        {t_alone}
        <h2>2027 pay with dependents</h2>
        {t_dep}
        <h2>2027 added amounts for dependents</h2>
        {t_add}
        <h2>2027 special monthly compensation</h2>
        <p>SMC-Q is a protected rate and is not shown. What each level covers is on our <a href="/va-disability-pay/special-monthly-compensation.html">SMC page</a>.</p>
        {t_smc}
        <h2>Questions</h2>
        {faq_html}
        <h2>Sources</h2>
        <p><a href="{esc(META['va_url'])}">VA.gov, veterans disability compensation rates ({esc(META['va_published'])})</a><br><a href="{esc(META['law_url'])}">{esc(META['law'])}</a><br><a href="https://www.ssa.gov/news/en/press/releases/2026-10-14.html">Social Security Administration, 3.6 percent benefit increase for 2027 (October 14, 2026)</a></p>
    </article>
    {btns}
    {cta}
    <div class="disclaimer">Rates shown are VA's published 2027 disability compensation rates, effective December 1, 2026. Confirm your amount at VA.gov. VA Ready is not affiliated with the U.S. Department of Veterans Affairs, and this page is not financial or legal advice.</div>
</div>
{footer}
"""
assert "\u2014" not in page, "em dash"
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
    json.loads(blk)
open(OUT, "w").write(page)
print("wrote", OUT, "100% alone", money(a100), "->", money(b100))
