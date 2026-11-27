#!/usr/bin/env python3
"""Switch the pay pages from the 2027 estimate to VA's published 2027 table.

Run on the day VA posts its 2027 rates (expected around December 1, 2026).

1. Enter VA's table, copied from VA.gov, into:
     data/compensation_rates_2027.json   same schema as data/compensation_rates.json
     data/smc_rates_2027.json            same schema as data/smc_rates.json
     data/pay_2027_meta.json             {"va_published": "December 2, 2026",
                                          "va_url": "https://www.va.gov/disability/compensation-rates/veteran-rates/",
                                          "law": "<the signed COLA act, exact title>", "law_url": "<congress.gov link>",
                                          "modified": "2026-12-02"}
   Or run `python3 switch_pay_2027.py --template` to write the two rate files pre-filled with
   our estimates, then overwrite every amount with VA's figure.
2. python3 switch_pay_2027.py --check    compares VA's figures with our estimates, writes nothing
3. python3 switch_pay_2027.py            regenerates the chart, the 10 rating pages, SMC and the 2027 page
4. Review `git diff`, then push and run indexnow.py with the printed paths.
5. python3 switch_pay_2027.py --sql      writes data/pay_2027_supabase.sql so the apps switch too

Keeps data/compensation_rates.json as the 2026 table. Never writes to Supabase itself.
"""
import json, os, subprocess, sys
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
FACTOR = Decimal("1.036")
RATINGS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
PAGES = (["va-disability-pay-rates.html", "va-disability-pay-rates-2027.html",
          "va-disability-pay/special-monthly-compensation.html"] +
         [f"va-disability-pay/{p}-percent.html" for p in RATINGS])

def D(v): return Decimal(str(v))
def est(v):
    v = D(v); q = Decimal("1") if v == v.to_integral_value() else Decimal("0.01")
    return (v * FACTOR).quantize(q, rounding=ROUND_HALF_UP)
def load(n): return json.load(open(os.path.join(DATA, n)))
def amount_keys(row): return [k for k, v in row.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and k not in ("id", "rating_pct", "effective_year")]

def template():
    comp = load("compensation_rates.json"); smc = load("smc_rates.json")
    for r in comp + smc:
        for k in amount_keys(r):
            if r[k] is not None: r[k] = float(est(r[k]))
        if "effective_year" in r: r["effective_year"] = 2027
    for n, rows in (("compensation_rates_2027.json", comp), ("smc_rates_2027.json", smc)):
        p = os.path.join(DATA, n)
        if os.path.exists(p): sys.exit(f"{n} already exists, not overwriting")
        json.dump(rows, open(p, "w"), indent=1)
    print("wrote estimate-filled templates. Replace EVERY amount with VA's published figure before switching.")

def check():
    """Compare the 2027 files with our estimates. Returns the number of large gaps."""
    old = {r["rating_pct"]: r for r in load("compensation_rates.json")}
    new = {r["rating_pct"]: r for r in load("compensation_rates_2027.json")}
    smc_old = {s["smc_level"]: s for s in load("smc_rates.json")}
    smc_new = {s["smc_level"]: s for s in load("smc_rates_2027.json")}
    assert sorted(new) == sorted(old), f"ratings in 2027 file: {sorted(new)}"
    assert set(smc_new) == set(smc_old), f"SMC levels differ: {set(smc_new) ^ set(smc_old)}"
    pairs = [(f"{p}% {k}", old[p][k], new[p].get(k)) for p in sorted(old) for k in amount_keys(old[p])]
    pairs += [(f"SMC-{l} {k}", smc_old[l][k], smc_new[l].get(k)) for l in smc_old for k in amount_keys(smc_old[l])]
    exact = small = 0; big = []
    for label, a, b in pairs:
        if a is None or D(a) == 0: continue
        if b is None: big.append((label, a, "MISSING")); continue
        gap = abs(D(b) - est(a))
        if D(b) == D(a): big.append((label, a, f"{b} UNCHANGED from 2026"))
        elif gap == 0: exact += 1
        elif gap <= Decimal("3"): small += 1; print(f"  small gap {label}: estimate {est(a)}, VA {b}")
        else: big.append((label, a, f"VA {b} vs estimate {est(a)}"))
    print(f"{exact + small + len(big)} amounts: {exact} match our estimate exactly, {small} within $3, {len(big)} need a look")
    for label, a, msg in big: print("  CHECK", label, "2026", a, "|", msg)
    meta_ok = os.path.exists(os.path.join(DATA, "pay_2027_meta.json"))
    if not meta_ok: print("  data/pay_2027_meta.json missing")
    return len(big) + (0 if meta_ok else 1)

def run(script, env):
    subprocess.run([sys.executable, "-I", os.path.join(HERE, script)], check=True, env={**os.environ, **env})

def sql():
    """Print the Supabase inserts for the apps (owner runs them on switch day; the apps use the newest year)."""
    out = []
    # SMC rows copy description, is_additive and allows_smc_k from the 2026 row in Supabase; only amounts change.
    for r in load("smc_rates_2027.json"):
        amts = {k: v for k, v in r.items() if k not in ("id", "effective_year", "smc_level", "smc_description", "is_additive")}
        cols = ", ".join(amts)
        vals = ", ".join("null" if v is None else str(v) for v in amts.values())
        lvl = r["smc_level"].replace("'", "''")
        out.append(f"insert into public.smc_rates (effective_year, smc_level, smc_description, is_additive, allows_smc_k, {cols}) "
                   f"select 2027, smc_level, smc_description, is_additive, allows_smc_k, {vals} "
                   f"from public.smc_rates where effective_year = 2026 and smc_level = '{lvl}';")
    for table, name in (("compensation_rates", "compensation_rates_2027.json"),):
        for r in load(name):
            r = {k: v for k, v in r.items() if k != "id"}
            r["effective_year"] = 2027
            cols = ", ".join(r)
            vals = ", ".join("null" if v is None else ("true" if v is True else "false" if v is False else
                             ("'" + v.replace("'", "''") + "'") if isinstance(v, str) else str(v)) for v in r.values())
            out.append(f"insert into public.{table} ({cols}) values ({vals});")
    path = os.path.join(DATA, "pay_2027_supabase.sql")
    open(path, "w").write("begin;\n" + "\n".join(out) + "\ncommit;\n")
    print(f"wrote {path} ({len(out)} rows). Check that no 2027 rows exist first: "
          "select effective_year, count(*) from compensation_rates group by 1;")

if __name__ == "__main__":
    if "--template" in sys.argv: template(); sys.exit()
    if "--sql" in sys.argv:
        if check(): sys.exit("Stopped: fix the CHECK lines first.")
        sql(); sys.exit()
    problems = check()
    if "--check" in sys.argv: sys.exit(1 if problems else 0)
    if problems and "--force" not in sys.argv:
        sys.exit("Stopped: fix the CHECK lines above (or pass --force after confirming each against VA.gov).")
    modified = load("pay_2027_meta.json")["modified"]
    run("gen_payrates.py", {"PAY_YEAR": "2027", "PAY_MODIFIED": modified})
    run("gen_payrates_2027_official.py", {})
    # sitemap lastmod for the switched pages
    sp = os.path.join(SITE, "sitemap.xml"); xml = open(sp).read()
    import re
    for page in PAGES:
        loc = f"<loc>https://vareadyapp.com/{page}</loc>"
        xml = re.sub(re.escape(loc) + r"(\s*<lastmod>)[^<]*(</lastmod>)", lambda m: loc + m.group(1) + modified + m.group(2), xml)
    open(sp, "w").write(xml)
    leftovers = subprocess.run(["grep", "-rlE", "2027 estimate|estimated 2027|(estimated)", *PAGES], cwd=SITE,
                               capture_output=True, text=True).stdout.split()
    print("estimate wording left on:", leftovers or "none")
    others = subprocess.run(["grep", "-rlF", "$3,938.58", "--include=*.html", "."], cwd=SITE,
                            capture_output=True, text=True).stdout.split()
    others = [o[2:] for o in others if o[2:] not in PAGES]
    print("other pages still quoting the 2026 100% amount (review by hand):", others or "none")
    print("IndexNow: python3 _generators/indexnow.py " + " ".join("/" + p for p in PAGES) + " /sitemap.xml")
