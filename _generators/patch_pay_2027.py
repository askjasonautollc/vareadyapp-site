# Adds the estimated 2027 amount to each va-disability-pay/NN-percent.html page.
# Figures come from va-disability-pay-rates-2027.html so the two never disagree.
# Idempotent. Re-run after gen_payrates.py; delete once VA publishes its 2027 table.
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
src = open(os.path.join(SITE, "va-disability-pay-rates-2027.html")).read()
i = src.index("Veteran alone, monthly, tax-free. 2027")
tbl = src[i:src.index("</table>", i)]
rows = re.findall(r'(\d+)-percent\.html">\d+%</a></td><td class="amt">([^<]+)</td><td class="amt">([^<]+)</td>', tbl)
assert len(rows) == 10, rows

for pct, y26, y27 in rows:
    p = os.path.join(SITE, "va-disability-pay", f"{pct}-percent.html")
    s = open(p).read()
    s = re.sub(r"<title>\d+% VA disability pay \(2026, 2027 estimate\): monthly amount with and without dependents \| VA Ready</title>",
               f"<title>{pct}% VA disability pay: {y26} a month in 2026, plus 2027 estimate | VA Ready</title>", s)
    if 'class="est27 ' in s:
        open(p, "w").write(s)
        continue
    assert y26 in s, (pct, y26)  # 2026 figure on the page must match the 2027 page's base
    note = (f'\n    <p class="est27 lede">2027 estimate: about <strong>{y27}</strong> a month for a veteran alone, '
            f'after the 3.6% COLA announced October 14, 2026. The increase starts December 1, 2026, in the payment '
            f'that arrives in early January. VA has not published its 2027 table yet. '
            f'<a href="/va-disability-pay-rates-2027.html">See every estimated 2027 amount &rarr;</a></p>')
    s = re.sub(r'(<p class="lede">[^\n]*?</p>)', lambda m: m.group(1) + note, s, count=1)
    s = s.replace(f"<title>{pct}% VA disability pay (2026): monthly amount with and without dependents | VA Ready</title>",
                  f"<title>{pct}% VA disability pay: {y26} a month in 2026, plus 2027 estimate | VA Ready</title>", 1)
    s = s.replace('"dateModified": "2026-06-09"', '"dateModified": "2026-10-30"')
    assert 'class="est27 ' in s and "plus 2027 estimate" in s, pct
    open(p, "w").write(s)
    print(pct, y26, "->", y27)
