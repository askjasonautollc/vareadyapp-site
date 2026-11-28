#!/usr/bin/env python3
"""Named author on every article page. Idempotent; run after any generator.

1. JSON-LD: Article / BlogPosting author Organization -> the founder Person (@id on founders.html).
2. Visible byline after the first </h1>: "By Jason, CW2 (R), U.S. Army · Updated <date>".
   Date = the page's dateModified, else its sitemap lastmod.
Skips the VSO directory pages (listings, not articles) and pages without an Article block.
Usage: python3 _generators/apply_byline.py [--dry]
"""
import glob, json, os, re, sys
from datetime import date

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSON = {"@type": "Person", "@id": "https://vareadyapp.com/founders.html#jason", "name": "Jason",
          "honorificSuffix": "CW2 (R), U.S. Army", "jobTitle": "Founder and developer of VA Ready",
          "url": "https://vareadyapp.com/founders.html"}
ARTICLE_TYPES = {"Article", "BlogPosting", "NewsArticle", "TechArticle"}
SKIP_DIRS = ("vso/",)
LD = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)

lastmod = dict(re.findall(r"<loc>https://vareadyapp\.com/([^<]*)</loc>\s*<lastmod>([^<]+)</lastmod>",
                          open(os.path.join(SITE, "sitemap.xml")).read()))

def fmt(d):
    y, m, dd = map(int, d[:10].split("-"))
    return date(y, m, dd).strftime("%b %-d, %Y")

def fix_block(obj, found):
    if isinstance(obj, list):
        for o in obj: fix_block(o, found)
    elif isinstance(obj, dict):
        t = obj.get("@type")
        if (set(t) if isinstance(t, list) else {t}) & ARTICLE_TYPES:
            found["article"] = True
            found["modified"] = obj.get("dateModified") or found.get("modified")
            a = obj.get("author")
            if not (isinstance(a, dict) and a.get("@id") == PERSON["@id"]):
                if a is None or (isinstance(a, dict) and a.get("@type") == "Organization") or \
                   (isinstance(a, dict) and a.get("@type") == "Person" and "Jason" in a.get("name", "")):
                    obj["author"] = dict(PERSON); found["changed"] = True
        for k in ("@graph",):
            if k in obj: fix_block(obj[k], found)

def main(dry):
    pages = changed = bylines = 0
    for path in sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(path, SITE)
        if rel.startswith(SKIP_DIRS) or rel.startswith("_"): continue
        s = open(path).read()
        found = {}
        def sub(m):
            obj = json.loads(m.group(2))
            f = {}
            fix_block(obj, f)
            found.update({k: v for k, v in f.items() if v})
            return m.group(1) + (json.dumps(obj) if f.get("changed") else m.group(2)) + m.group(3)
        new = LD.sub(sub, s)
        if not found.get("article"): continue
        pages += 1
        if new != s: changed += 1
        if 'class="byline"' not in new and "</h1>" in new and not rel.startswith("blog/"):
            d = found.get("modified") or lastmod.get(rel)
            upd = f" &middot; Updated {fmt(d)}" if d else ""
            line = ('\n<p class="byline" style="color:#8a94a6;font-size:13px;margin:6px 0 14px">'
                    f'By <a href="/founders.html" style="color:inherit">Jason, CW2 (R), U.S. Army</a>{upd}</p>')
            new = new.replace("</h1>", "</h1>" + line, 1); bylines += 1
        if new != s and not dry: open(path, "w").write(new)
    print(f"article pages {pages}, schema author changed {changed}, bylines added {bylines}{' (dry run)' if dry else ''}")

if __name__ == "__main__":
    main("--dry" in sys.argv)
