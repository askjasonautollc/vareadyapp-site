# Adds a "benefits by VA rating" summary to each states/*.html page and retitles
# the page for "<state> disabled veteran benefits" searches. Built from the
# badges already on the page, so the summary always matches the list below it.
# Idempotent. Re-run after gen_states.py.
import glob, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
BEN = re.compile(r'<li class="ben"><div class="ben-top"><span class="ben-name">(.*?)</span>(.*?)</div>', re.S)
BADGE = re.compile(r'<span class="badge[^"]*">([^<]*)</span>')

def tier(badges):
    for b in badges:
        if b == "100% P&amp;T": return (101, "100% permanent and total (P&amp;T)")
        if b == "100% rating": return (100, "100%")
        m = re.match(r"(\d+)%\+ rating", b)
        if m: return (int(m.group(1)), f"{m.group(1)}% or higher")
    return (0, "No rating minimum")

n = 0
for p in sorted(glob.glob(os.path.join(SITE, "states", "*.html"))):
    s = open(p).read()
    if 'class="byrating"' in s: continue
    m = re.search(r"<title>(.+?) veterans benefits \(2026\) for disabled veterans \| VA Ready</title>", s)
    if not m: print("skip", p); continue
    st = m.group(1)
    groups = {}
    for name, rest in BEN.findall(s):
        bs = BADGE.findall(rest)
        k = tier(bs)
        extra = " (combat service)" if "Combat service" in bs else ""
        groups.setdefault(k, []).append(name + extra)
    if not groups: print("no benefits", p); continue
    rows = "".join(f"<dt>{label}</dt><dd>{'; '.join(names)}</dd>"
                   for (_, label), names in sorted(groups.items(), key=lambda kv: -kv[0][0]))
    block = (f'\n    <div class="byrating"><h2>{st} benefits by VA rating</h2><dl class="tiers">{rows}</dl>'
             f'<p class="fine">Each benefit applies at its listed rating and every rating above it. Details and how to claim are below.</p></div>')
    s = re.sub(r'(<div class="meta">Last verified[^<]*</div>)', lambda mm: mm.group(1) + block, s, count=1)
    total = sum(len(v) for v in groups.values())
    desc = html.escape(f"{total} {html.unescape(st)} benefits for disabled veterans, grouped by the VA rating each one needs. Each checked against official state sources, with how to claim it.", quote=True)
    s = s.replace(m.group(0), f"<title>{st} disabled veteran benefits by VA rating (2026) | VA Ready</title>", 1)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', s, count=1)
    s = s.replace(f'<meta property="og:title" content="{st} veterans benefits (2026)">', f'<meta property="og:title" content="{st} disabled veteran benefits by VA rating (2026)">', 1)
    s = s.replace("</style>", "    .byrating .fine { font-size:13.5px; color:var(--gray); margin:6px 0 0; }\n</style>", 1)
    s = s.replace('"dateModified": "2026-06-16"', '"dateModified": "2026-10-30"', 1)
    assert 'class="byrating"' in s, p
    open(p, "w").write(s); n += 1
print(n, "state pages updated")
