"""Tell Bing (and other IndexNow engines) which pages changed, so they recrawl
within hours. Run after a push is live:

    python3 indexnow.py                      # every URL in ../sitemap.xml
    python3 indexnow.py /va-disability-calculator.html /index.html

The key file ../a85851f2c83d6a33c6295b2ab99899d1.txt must stay in the site root."""
import json, os, re, sys, urllib.request

KEY = "a85851f2c83d6a33c6295b2ab99899d1"
HOST = "vareadyapp.com"
SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

if len(sys.argv) > 1:
    urls = ["https://" + HOST + (p if p.startswith("/") else "/" + p) for p in sys.argv[1:]]
else:
    urls = re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(SITE, "sitemap.xml")).read())

body = json.dumps({"host": HOST, "key": KEY,
                   "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls[:10000]}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req, timeout=30) as r:
    print(r.status, f"{len(urls)} URLs submitted")
