# Builds vso/near.json for the "Near me" button on find-a-vso.html.
# Reads the published state pages so the hub never lists an office the state
# pages do not. Run after gen_vso.py.
import glob, html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
VSODIR = os.path.join(SITE, "vso")

CARD = re.compile(r'<li class="vso-card"[^>]*data-lat="([^"]*)" data-lng="([^"]*)">(.*?)</li>', re.S)
def text(rx, s):
    m = re.search(rx, s, re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""

rows = []
for f in sorted(glob.glob(os.path.join(VSODIR, "*.html"))):
    st = os.path.basename(f)[:-5]
    for la, lo, body in CARD.findall(open(f).read()):
        try: la, lo = round(float(la), 4), round(float(lo), 4)
        except ValueError: continue
        tel = re.search(r'href="tel:([^"]+)"', body)
        rows.append({"n": text(r'class="vso-name">(.*?)</span>', body),
                     "o": text(r'class="vso-org">(.*?)</div>', body),
                     "l": text(r'class="vso-loc">(.*?)</div>', body),
                     "t": tel.group(1) if tel else "",
                     "a": la, "g": lo, "s": st})

json.dump(rows, open(os.path.join(VSODIR, "near.json"), "w"), separators=(",", ":"), ensure_ascii=False)
print(len(rows), "offices with coordinates")
