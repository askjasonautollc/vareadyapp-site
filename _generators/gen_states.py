#!/usr/bin/env python3
import json, re, os, html
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
SDIR = os.path.join(SITE, "states")
os.makedirs(SDIR, exist_ok=True)
ROWS = json.load(open(os.path.join(HERE,"data","benefits.json")))
def esc(s): return html.escape(s or "", quote=True)

# top-20 states by veteran population (search-demand order)
ORDER = ["CA","TX","FL","VA","NC","GA","PA","NY","OH","WA","AZ","MI","TN","IL","CO","MO","SC","MD","IN","AL",
         "NJ","MA","MN","WI","KY","OR","OK","CT","UT","NV","IA","AR","MS","KS","NM","NE","WV","ID","HI","NH",
         "ME","RI","MT","DE","SD","ND","AK","VT","WY","LA","DC"]
NAMES = {r["state_code"]: r["state_name"] for r in ROWS}
BY = defaultdict(list)
for r in ROWS: BY[r["state_code"]].append(r)

CAT_ORDER = ["Property Tax","Income Tax","Education","Employment","Vehicle","Recreation","General"]
# Tie-break on the name itself. Categories outside CAT_ORDER all rank 99, and
# the inputs come from a set(), whose string iteration order is hash-randomized
# per process. Without the name in the key, every regeneration reshuffled those
# categories and produced spurious diffs across all 51 state pages.
def cat_rank(c): return (CAT_ORDER.index(c) if c in CAT_ORDER else 99, c)

gtext = open(os.path.join(HERE,"gen_guides.py")).read()
m = re.search(r'CSS = """(.*?)"""', gtext, re.S)
CSS = (m.group(1) if m else "") + """
    .meta { color:var(--gray); font-size:14px; margin:4px 0 14px; }
    .catblock { margin:26px 0 6px; }
    .catblock h2 { font-size:21px; font-weight:800; margin-bottom:6px; }
    ol.blist { list-style:none; padding:0; margin:0; }
    li.ben { border-top:1px solid var(--line); padding:16px 0; margin:0; }
    .ben-top { display:flex; flex-wrap:wrap; align-items:baseline; gap:2px 12px; margin-bottom:4px; }
    .ben-name { color:var(--white); font-weight:700; font-size:17px; }
    .badge { font-size:13px; color:var(--gray); }
    .ben-val { color:var(--white); font-weight:600; font-size:14.5px; margin:2px 0 6px; font-variant-numeric:tabular-nums; }
    .ben p { color:var(--tan); font-size:15px; margin:5px 0; max-width:68ch; }
    .ben .how { color:var(--tan); font-size:14.5px; }
    .ben-foot { display:flex; flex-wrap:wrap; gap:0 14px; align-items:center; margin-top:6px; font-size:13px; color:var(--gray); }
    .ben-foot a { display:inline-block; padding:8px 0; }
    .trustline { font-size:14.5px; color:var(--tan); margin:14px 0 4px; max-width:68ch; }
    .pillrow { display:flex; flex-wrap:wrap; gap:4px 18px; margin:6px 0 16px; }
    .pillrow span { font-size:15px; color:var(--tan); }
    .page-cta { margin:26px 0; }
    table.rt { width:100%; border-collapse:collapse; margin:8px 0 18px; }
    table.rt th, table.rt td { text-align:left; padding:11px 12px; border-bottom:1px solid var(--line); font-size:15px; vertical-align:top; color:var(--tan); }
    table.rt th { color:var(--gray); font-size:13px; font-weight:600; }
    table.rt td.pct { color:var(--white); font-weight:700; width:74px; font-variant-numeric:tabular-nums; }
"""

NAV = """<nav>
    <a href="/index.html" class="nav-brand"><img src="/logo-96.png" alt="VA Ready logo" width="34" height="34"><span>VA Ready <span style="color:var(--gray);font-weight:400;">/</span> Vet Ready</span></a>
    <input type="checkbox" id="nv" class="nv-cb">
    <label for="nv" class="nv-burger" aria-label="Open menu">&#9776;</label>
    <div class="nav-links"><a href="/va-disability-calculator.html">Calculator</a><a href="/conditions.html">Conditions</a><a href="/mos.html">MOS</a><a href="/va-disability-pay-rates.html">Pay Rates</a><a href="/federal-benefits.html">Federal Benefits</a><a href="/guides.html">Guides</a><a href="/blog.html">Blog</a><a href="/find-a-vso.html">Find a VSO</a><a href="/index.html#download" class="nav-cta">Get the App</a></div>
</nav>"""
FOOTER = """<footer>
    <p>&copy; 2026 JDL Software LLC. VA Ready (iOS and Windows) &amp; Vet Ready (Android) are not affiliated with the U.S. Department of Veterans Affairs.</p>
    <div class="footer-links"><a href="/index.html">Home</a><a href="/conditions.html">Conditions</a><a href="/exposures.html">Exposures</a><a href="/mos.html">By MOS</a><a href="/va-disability-pay-rates.html">Pay Rates</a><a href="/states.html">State Benefits</a><a href="/federal-benefits.html">Federal Benefits</a><a href="/guides.html">Guides</a><a href="/blog.html">Blog</a><a href="/videos.html">Videos</a><a href="/va-updates.html">VA Updates</a><a href="/va-disability-calculator.html">Calculator</a><a href="/va-back-pay-calculator.html">Back Pay</a><a href="/va-claim-evidence.html">Document Your Claim</a><a href="/reserve-national-guard-va-disability.html">Reserve &amp; Guard</a><a href="/find-a-vso.html">Find a VSO</a><a href="/va-disability-app-for-windows.html">Windows App</a><a href="/founders.html">Our Story</a><a href="/community.html">In the Community</a><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a><a href="/accessibility.html">Accessibility</a></div>
    <div class="footer-social" style="display:flex;justify-content:center;gap:0;margin:10px 0 0;"><a href="https://www.tiktok.com/@vareadyapp" target="_blank" rel="me noopener" aria-label="VA Ready on TikTok" style="color:var(--tan);display:inline-flex;padding:11px;"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.6 5.82a4.28 4.28 0 0 1-1.01-2.82h-3.3v13.2a2.59 2.59 0 1 1-1.78-2.46V10.2a5.9 5.9 0 1 0 5.09 5.85V8.96a7.56 7.56 0 0 0 4.4 1.41V7.06a4.28 4.28 0 0 1-3.4-1.24Z"/></svg></a><a href="https://www.instagram.com/vareadyapp/" target="_blank" rel="me noopener" aria-label="VA Ready on Instagram" style="color:var(--tan);display:inline-flex;padding:11px;"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23a3.7 3.7 0 0 1-.9 1.38 3.7 3.7 0 0 1-1.38.9c-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.7 3.7 0 0 1-1.38-.9 3.7 3.7 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23-.06-1.27-.07-1.65-.07-4.85s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.17 8.8 2.16 12 2.16M12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63a5.86 5.86 0 0 0-2.12 1.38A5.86 5.86 0 0 0 .64 4.13C.34 4.9.14 5.77.08 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.28.26 2.15.56 2.91a5.86 5.86 0 0 0 1.38 2.12 5.86 5.86 0 0 0 2.12 1.38c.76.3 1.63.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.28-.06 2.15-.26 2.91-.56a5.86 5.86 0 0 0 2.12-1.38 5.86 5.86 0 0 0 1.38-2.12c.3-.76.5-1.63.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.28-.26-2.15-.56-2.91a5.86 5.86 0 0 0-1.38-2.12A5.86 5.86 0 0 0 19.87.63c-.76-.3-1.63-.5-2.91-.56C15.67.01 15.26 0 12 0Zm0 5.84A6.16 6.16 0 1 0 18.16 12 6.16 6.16 0 0 0 12 5.84Zm0 10.16A4 4 0 1 1 16 12a4 4 0 0 1-4 4Zm6.41-10.4a1.44 1.44 0 1 0 1.44 1.44 1.44 1.44 0 0 0-1.44-1.44Z"/></svg></a><a href="https://www.facebook.com/vareadyapp" target="_blank" rel="me noopener" aria-label="VA Ready on Facebook" style="color:var(--tan);display:inline-flex;padding:11px;"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07c0 6.03 4.39 11.03 10.13 11.93v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.69 4.53-4.69 1.31 0 2.68.24 2.68.24v2.97h-1.51c-1.49 0-1.96.93-1.96 1.89v2.25h3.33l-.53 3.49h-2.8V24C19.61 23.1 24 18.1 24 12.07Z"/></svg></a></div>
</footer>
<script defer src="/_vercel/insights/script.js"></script>
<script defer src="/track.js"></script>"""
APP_CTA = """<div class="cta cta-line"><p>The free tier of <a href="https://apps.apple.com/app/id6761733758">VA Ready for iOS</a>, <a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US">Vet Ready for Android</a> and <a href="https://apps.microsoft.com/detail/9p8xfcqvfjhf">VA Ready for Windows</a> previews Texas benefits and shows federal benefits at every rating; Pro opens every state.</p></div>"""


# ---------- copy cleanup -------------------------------------------------
# The benefits table carries research-audit notes appended to some descriptions
# ("VERIFIED: ...", "CORRECTION TO RESEARCH: ...", "not confirmed in this
# research") and emphasis written in capitals. Neither belongs on a public page.
# The snapshot is not edited (a Supabase refresh would restore it), so the fix
# lives here, keyed by row id. Rewrites below use only facts already in the row.
DESC_FULL = {
 566: "Any honorably discharged New Mexico resident veteran (or unmarried surviving spouse) may exempt up to $10,000 of the taxable value of their property from property tax. The amount was raised from $4,000 to $10,000 by a 2024 voter-approved constitutional amendment (NM Const. Art. VIII). No VA disability rating is required. Application is made through NMDVS and filed with the county assessor. A veteran rated 100% service-connected disabled receives a full exemption on the principal residence. Under the same amendment and its enabling legislation (House Bill 47, 2025), eligibility expands to veterans rated 10% to 100%, with the exemption scaled to the disability percentage. Confirm the first tax year that applies to your rating with your county assessor.",
 621: "Honorably discharged veterans rated 100% totally disabled by the VA (including total disability based on individual unemployability) receive an enhanced homestead exemption that removes a fixed indexed amount of their home's market value from property taxation, with no age or income limit. The amount starts at $50,000 of market value and is indexed each year; the Ohio Legislative Service Commission reports $56,000 for tax year 2025. Apply via county auditor with DD214 and VA award letter showing the 100% rating. A surviving spouse may continue the benefit. Form DTE 105I states the applicant 'must be 100% disabled by or be receiving 100% compensation for service-connected injuries.' SB92 (pending, not yet law) would raise this to a full exemption of the entire homestead value.",
 772: "West Virginia offers disabled veterans the Disabled Veteran Real Property Tax Credit, first claimed for tax year 2024. Honorably discharged veterans rated 90% to 100% permanently and totally (P&T) disabled by the VA may claim a credit equal to the actual real property tax paid on a homestead used or occupied exclusively for residential purposes (used or occupied at least 6 months). It is a refundable income-tax credit, per WV Tax Division publication TSD 455 (Rev. January 2026). The credit is claimed on Form DV-1 / IT-140 Line 21(B); property taxes must be paid timely (first half before Oct 1, second half before Apr 1).",
 762: "Income-based property tax exemption for disabled veterans. Qualifying veterans get the assessed value of their residence frozen and a partial exemption scaled by income tier: full exemption from all excess (voter-approved) levies and the additional state school levy at every tier, plus a reduction of regular levies for the two lower income tiers. The veteran must own and occupy the home and meet a county-specific 'combined disposable income' threshold (based on each county's median household income); VA disability compensation and DIC are excluded from that income calculation. Under RCW 84.36.381 as amended, the qualifying combined service-connected rating is 40% or higher for taxes levied for collection in 2027 and after. Check the county assessor for the rating required on your 2026 taxes. Veterans rated 100% (or paid at the 100% rate) have always qualified. Apply through the local county assessor.",
 584: "Reduces assessed value on a veteran's primary residence: 15% reduction for wartime service, an additional 10% for service in a combat zone, and an additional reduction equal to one-half of the VA service-connected disability rating. Percentage benefits are subject to maximum dollar limits set by each local taxing jurisdiction (county/city/town/village; applies to school taxes only where the school district has opted in). Most communities require application by March 1. Separately, veterans with a 100% service-connected disability rating (or 100% via individual unemployability under VA standards) receive a full property tax exemption on the primary residence. It was established by Chapter 672 of the Laws of 2025 and made mandatory statewide, school districts included, by Chapter 77 of the Laws of 2026, and applies to assessment rolls with taxable status dates on or after October 1, 2026 (the 2027 assessment roll). The veteran must be discharged or released under honorable conditions. The partial exemptions (Alternative Veterans, Cold War, Eligible Funds) remain available for veterans below the 100% threshold.",
 666: "Rhode Island lets military retirees subtract military service pension benefits included in federal AGI from RI taxable income, with no age or income requirement. Military service pensions are fully exempt from Rhode Island personal income tax for all tax years beginning on or after January 1, 2023, with no phase-in (R.I. Gen. Laws 44-30-12(c)(11); claimed via Schedule M; RI Division of Taxation Retirement Income Guide, Pub 2026-01, Section 2). VA disability compensation is also not taxed because RI starts from federal AGI, which excludes it.",
 720: "Property tax abatement for veterans with a service-connected disability of at least 10%, applied to the primary residence (up to 1 acre) and/or personal-use tangible property. The abatement equals the disability percentage multiplied by the statutory maximum; the statutory limit was $479,504 for 2023 and rises each year with the consumer price index (Utah Code 59-2a-501), so a 100% rating exempts that indexed amount of taxable value. A veteran rated as Individually Unemployable (IU) by the VA is treated as 100% disabled regardless of the scheduled percentage. Available to the disabled veteran, an unmarried surviving spouse, or minor orphans. Apply to the county by September 1. 100%/P&T is not required to qualify.",
 751: "Subtract up to $40,000 of military retirement income (and Survivor Benefit Plan payments to surviving spouses) from Virginia taxable income. No age requirement. Income must be reported on the federal return. The cap is $40,000 for taxable years beginning on or after Jan 1, 2025 (Code of Virginia 58.1-322.02). Cannot be combined with another subtraction/deduction for the same income. Military retirement income is partly exempt, up to the cap.",
}
DESC_SUB = {
 567: [(" NMDVS materials describe the percentage-based exemption applying for the 2026 tax year and beyond.", " Confirm the first tax year that applies to your rating with your county assessor."),
      ("(per 2024 amendment, phasing in 2025-2027)", "(per 2024 amendment)")],
 287: [(" Military retirement is therefore PARTIALLY, not fully, exempt.", " Delaware therefore exempts part of military retirement pay, not all of it.")],
 365: [("IMPORTANT: Indiana does NOT exempt veteran-plated vehicles from registration fees or excise taxes, the plate confers", "Indiana does not exempt veteran-plated vehicles from registration fees or excise taxes. The plate confers")],
 741: [("NARROW benefit: A disabled", "A disabled"), ("This is NOT a general exemption", "This is not a general exemption")],
 313: [(" NOT the 2026 tax year despite some news reports.", "")],
 465: [(" NOTE: many third-party guides cite $500; the verified statutory figure in MCL 206.30(3)(b) is $250, so $250 is reported here.", " The statutory figure is in MCL 206.30(3)(b).")],
 785: [(" NOTE: 2025 SB411/AB428 would lower the threshold to 80% and prorate the credit by rating, but as of mid-2026 those are still pending proposals, not enacted law - the DOR FAQ still states 100%.", " Bills SB411 and AB428 (2025) would lower the threshold to 80% and prorate the credit by rating; as of mid-2026 they are pending proposals, not enacted law, and the DOR FAQ still states 100%.")],
 495: [(", but this specific cost tier could not be confirmed on a live official page at research time.", ".")],
 513: [("; an explicit VA rating percentage was not confirmed in the statute text, so the rating threshold is left unstated here.", " and does not state a VA rating percentage.")],
 330: [(" Exact point values under current Hawaii civil service rules were not confirmed against the statute text (older HRS 76-72/74 preference sections were repealed and replaced).", " The older HRS 76-72 and 76-74 preference sections were repealed and replaced.")],
 324: [("but the exact minimum is set by each county and was NOT confirmed as a fixed dollar figure on the official county .gov page reviewed)", "but the exact minimum is set by each county)")],
 230: [(" Dollar figures index yearly (medium confidence on amounts); verify the current-year figure with ADOR.", " Dollar figures index yearly; check the current-year figure with ADOR.")],
 523: [(" The specific VA rating/disability criteria for plate eligibility were not confirmed verbatim in this research, so confidence is medium.", "")],
 596: [(" Exact annual amount not confirmed from primary source in this research.", "")],
 684: [(" Specific per-diem cost not confirmed from a primary .gov source.", "")],
 404: [(" Specific per-diem costs were not confirmed from a primary source.", "")],
 335: [(" Exact 2026 cap not confirmed from a primary HTML page.", "")],
 840: [(" Note: an older OVA flyer cited $3,500; the current Nov 19, 2024 Summary of Local Benefits states $5,000.", " The Nov 19, 2024 Summary of Local Benefits states $5,000.")],
 520: [("Note: the Nebraska DVA/Revenue pages do not address VA disability comp explicitly; this follows from federal non-taxability flowing through Nebraska's AGI-based system, hence medium confidence.", "Nebraska's DVA and Revenue pages do not address VA disability compensation explicitly; the exclusion follows from federal non-taxability flowing through Nebraska's AGI-based system.")],
}
_EMPH = ("NOT NO FULL FULLY FREE ALL ONE ONLY ANY BOTH MUST ZERO PLUS LESS COST RATE NON EXEMPT PERMANENT TOTAL "
         "FEDERAL UNDER RETIREMENT RETIRED IS BEFORE LIVING ADDITIONAL WARTIME LONGER COMPLETE LIFETIME "
         "REGISTRATION RESIDENT ACTUAL INITIAL CURRENT SINGLE EXCLUDED PARTIALLY FLAT OPEN").split()
_EMPH_RE = re.compile(r"(?<![A-Za-z0-9/'-])(PERMANENT AND TOTAL|NON(?=-)|(?:" + "|".join(_EMPH) + r"|OR(?= [a-z(0-9])|AND(?= [a-z(0-9]))(?![A-Za-z0-9/'-]))")
def clean_text(t, bid=None, full=False):
    if not t: return t
    if full and bid in DESC_FULL: t = DESC_FULL[bid]
    for a, b in DESC_SUB.get(bid, []):
        t = t.replace(a, b)
    t = re.sub(r"(\(?)Note: (\w)", lambda m: m.group(1) + (m.group(2) if m.group(1) else m.group(2).upper()), t, flags=re.I)
    def low(m):
        w = m.group(0).lower()
        before = t_[:m.start()].rstrip(" (")
        if not before or before[-1] in ".:?!": w = w[:1].upper() + w[1:]
        return w
    # quoted spans ('DISABLED VETERAN') keep their case
    parts = re.split(r"('[^']*')", t)
    out = []
    for p in parts:
        if p.startswith("'") and p.endswith("'") and len(p) > 2:
            out.append(p); continue
        t_ = p
        out.append(_EMPH_RE.sub(low, p))
    t = "".join(out)
    return t

def slug(name): return re.sub(r"[^a-z0-9]+","-", name.lower()).strip("-")

def cat_label(c):
    """Category names come Title Case from the table; headings are sentence case."""
    return c[:1] + c[1:].lower()

_MONTHS = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def human_date(d):
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", d or "")
    return f"{_MONTHS[int(m.group(2))]} {int(m.group(3))}, {m.group(1)}" if m else (d or "")

def money(v):
    try:
        n = float(v)
        if n <= 0: return None
        return "${:,.0f}".format(n)
    except: return None

def badges(r):
    out = []
    if r.get("requires_pt"): out.append('<span class="badge req">100% P&amp;T</span>')
    pct = r.get("min_rating_pct")
    if pct and int(pct) > 0 and not r.get("requires_pt"): out.append(f'<span class="badge req">{int(pct)}%{"+" if int(pct) < 100 else ""} rating</span>')
    if r.get("requires_combat"): out.append('<span class="badge req">Combat service</span>')
    if not out: out.append('<span class="badge">All veterans</span>')
    return "".join(out)

def benefit_li(r):
    bid = r.get("id")
    val = money(r.get("estimated_annual_value")); vd = clean_text(r.get("value_description"), bid)
    if val and vd: vline = f'<div class="ben-val">Est. {val}/yr &middot; {esc(vd)}</div>'
    elif val: vline = f'<div class="ben-val">Est. value: {val}/yr</div>'
    elif vd: vline = f'<div class="ben-val">{esc(vd)}</div>'
    else: vline = ""
    how = f'<p class="how">How to claim: {esc(clean_text(r["how_to_claim"], bid))}</p>' if r.get("how_to_claim") else ""
    foot = []
    if r.get("agency"): foot.append(esc(r["agency"]))
    if r.get("form_name"): foot.append("Form " + esc(r["form_name"]))
    foot_html = " &middot; ".join(foot)
    return (f'<li class="ben"><div class="ben-top"><span class="ben-name">{esc(r["benefit_name"])}</span>{badges(r)}</div>'
            f'{vline}<p>{esc(clean_text(r.get("description"), bid, True))}</p>{how}'
            + (f'<div class="ben-foot">{foot_html}</div>' if foot_html else '') + '</li>')

def sources_line(rows):
    """One sources line per page: each distinct site once, linked to its first URL."""
    seen, out = set(), []
    for r in rows:
        u = r.get("source_url") or r.get("website_url")
        if not u or not u.startswith("http"): continue
        host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", u).split("/")[0].lower())
        if host in seen: continue
        seen.add(host); out.append(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(host)}</a>')
    return f'<p class="trustline">Sources: {", ".join(out)}.</p>' if out else ""

def state_page(sc):
    rows = sorted(BY[sc], key=lambda r:(cat_rank(r["benefit_category"]), r["benefit_name"]))
    sn = NAMES[sc]; sl = slug(sn)
    cats = []
    for c in sorted(set(r["benefit_category"] for r in rows), key=cat_rank): cats.append(c)
    lastv = max((r.get("last_verified") or "") for r in rows) or ""
    url = f"/states/{sl}.html"; canon = f"https://vareadyapp.com{url}"
    catlist = ", ".join(cats).lower()
    desc = f"{sn} veterans benefits: property tax exemptions, education, vehicle, and recreation perks for disabled veterans. What you qualify for and how to claim it. Free VA tools."
    desc = desc[:158]
    # category blocks
    blocks = ""
    for c in cats:
        crows = [r for r in rows if r["benefit_category"] == c]
        items = "".join(benefit_li(r) for r in crows)
        blocks += f'<div class="catblock"><h2>{esc(cat_label(c))}</h2><ol class="blist">{items}</ol></div>'
    bc_ld = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"Veterans benefits by state","item":"https://vareadyapp.com/states.html"},
        {"@type":"ListItem","position":3,"name":f"{sn} veterans benefits","item":canon}]})
    art_ld = json.dumps({"@context":"https://schema.org","@type":"Article",
        "headline":f"{sn} veterans benefits","description":desc,"datePublished":"2026-06-08",
        "dateModified": lastv or "2026-06-08",
        "author":{"@type":"Organization","name":"JDL Software LLC"},"publisher":{"@type":"Organization","name":"VA Ready"},
        "mainEntityOfPage":canon,"inLanguage":"en-US"})
    _cc = {}
    for r in rows: _cc[r["benefit_category"]] = _cc.get(r["benefit_category"], 0) + 1
    cat_counts = ", ".join(f"{_cc[c]} {cat_label(c).lower()}" for c in cats)
    lastv_str = f"Last verified {human_date(lastv)}" if lastv else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(sn)} veterans benefits (2026) for disabled veterans | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="{esc(sn)} veterans benefits (2026)">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<script type="application/ld+json">{bc_ld}</script>
<script type="application/ld+json">{art_ld}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/states.html">State benefits</a> / {esc(sn)}</div>
    <h1>{esc(sn)} veterans benefits</h1>
    <p class="lede">{esc(sn)} lists {len(rows)} veteran benefits: {esc(cat_counts)}.</p>
    {('<div class="meta">' + lastv_str + '</div>') if lastv_str else ''}
    {blocks}
    {sources_line(rows)}
    <div class="btns page-cta"><a href="/va-disability-calculator.html" class="btn">Estimate your combined rating</a><a href="/conditions.html" class="btn ghost">Browse conditions</a></div>
    {APP_CTA}
    <div class="disclaimer">State benefit rules, amounts, and eligibility change and vary by county or municipality. Estimated values are approximate. Always confirm current details with the state agency or the official source linked above before relying on a benefit. VA Ready is not affiliated with the U.S. Department of Veterans Affairs or any state agency, and this page is not legal, tax, or financial advice.</div>
</div>
{FOOTER}
</body>
</html>"""

written = 0
for sc in ORDER:
    if sc in BY:
        open(os.path.join(SDIR, slug(NAMES[sc]) + ".html"), "w").write(state_page(sc))
        written += 1

# hub
def hub():
    import collections
    df = collections.Counter()
    def toks(n): return {w for w in re.findall(r"[a-z]{4,}", re.sub(r"\([^)]*\)", "", n).lower())}
    for sc in ORDER:
        if sc in BY:
            for t in set().union(*[toks(r["benefit_name"]) for r in BY[sc]]): df[t] += 1
    GENERIC = {"veteran","veterans","disabled","exemption","property","license","service","tuition","state","benefit"}
    def notable(rows):
        best, bs = None, 9
        for r in rows:
            if r["benefit_category"] in ("Veterans Home",): continue
            tk = toks(r["benefit_name"]) - GENERIC
            if not tk: continue
            sc_ = sum(df[t] for t in tk) / len(tk)
            if sc_ < bs: best, bs = r, sc_
        n = re.sub(r"\s*\([^)]*\)", "", best["benefit_name"]) if best else ""
        return n.strip()
    body = ""
    for sc in ORDER:
        if sc not in BY: continue
        sn = NAMES[sc]; rows = BY[sc]
        body += (f'<tr><td><a href="/states/{slug(sn)}.html">{esc(sn)}</a></td><td class="pct">{len(rows)}</td>'
                 f'<td>{esc(notable(rows))}</td></tr>')
    cards = ('<div class="tbl-wrap"><table class="rt"><thead><tr><th>State</th><th>Benefits</th>'
             f'<th>Most distinctive</th></tr></thead><tbody>{body}</tbody></table></div>')
    desc = "Veteran benefits for all 50 states plus DC: property tax exemptions, tuition waivers, vehicle and recreation perks, and how military-retirement pay is taxed. What disabled veterans qualify for in your state and how to claim it."
    bc = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://vareadyapp.com/"},
        {"@type":"ListItem","position":2,"name":"Veterans benefits by state","item":"https://vareadyapp.com/states.html"}]})
    items = json.dumps({"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"url":f"https://vareadyapp.com/states/{slug(NAMES[sc])}.html","name":f"{NAMES[sc]} veterans benefits"}
        for i,sc in enumerate(ORDER) if sc in BY]})
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Veterans benefits by state (2026): property tax, education and more | VA Ready</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="https://vareadyapp.com/states.html">
<meta property="og:type" content="website"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="Veterans benefits by state"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="https://vareadyapp.com/states.html"><meta property="og:image" content="https://vareadyapp.com/logo.png">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<script type="application/ld+json">{bc}</script>
<script type="application/ld+json">{items}</script>
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">
    <div class="crumb"><a href="/index.html">Home</a> / Veterans benefits by state</div>
    <h1>Veterans benefits by state</h1>
    <p class="lede">Most states add their own benefits for veterans with a VA rating: property-tax exemptions, free or reduced tuition, vehicle and license breaks, and hunting and fishing perks. Pick a state below. Each page was checked against official state sources and says how to claim every benefit.</p>
    <div class="hub-sec"><h2>All 50 states and DC</h2>{cards}</div>
    <p class="trustline">More from VA Ready: <a href="/conditions.html">VA ratings by condition</a> &middot; <a href="/guides.html">VA claim guides</a> &middot; <a href="/va-disability-calculator.html">Combined-rating calculator</a></p>
    {APP_CTA}
    <div class="disclaimer">State benefit rules and amounts change and vary locally. Always confirm with the state agency before relying on a benefit. VA Ready is not affiliated with the U.S. Department of Veterans Affairs.</div>
</div>
{FOOTER}
</body>
</html>"""
open(os.path.join(SITE, "states.html"), "w").write(hub())

# sitemap merge
sp = os.path.join(SITE, "sitemap.xml")
xml = open(sp).read(); new = []
urls = [("https://vareadyapp.com/states.html","0.8")] + [(f"https://vareadyapp.com/states/{slug(NAMES[sc])}.html","0.7") for sc in ORDER if sc in BY]
for u,p in urls:
    if u not in xml:
        new.append(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-06-08</lastmod>\n    <priority>{p}</priority>\n  </url>')
if new:
    xml = xml.replace("</urlset>", "\n".join(new) + "\n</urlset>"); open(sp,"w").write(xml)

# validate all JSON-LD
import glob
bad = 0
for f in [os.path.join(SITE,"states.html")] + glob.glob(os.path.join(SDIR,"*.html")):
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', open(f).read(), re.S):
        try: json.loads(blk)
        except Exception as e: bad += 1; print("BAD JSON-LD", f, e)
print(f"wrote {written} state pages + hub; sitemap +{len(new)} urls; JSON-LD bad={bad}")
