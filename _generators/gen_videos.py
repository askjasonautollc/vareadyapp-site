#!/usr/bin/env python3
"""
Builds /videos.html, the video hub that ties the @vareadyapp TikTok channel to
the vareadyapp.com domain.

Why this page exists, in order of what actually earns traffic:

1. It is a genuine topic hub. Google ranks original text, not embeds. Every
   section here is original copy that links down into the deep pages we already
   have, so the page carries its own weight even before a single video is added.
2. It gives a TikTok viewer somewhere useful to land instead of the homepage.
3. It puts the TikTok channel on a crawlable page on our own domain, which
   reinforces the sameAs entity signal already in the homepage Organization
   schema.

DELIBERATELY NOT DONE: no TikTok captions or titles are copied onto this page.
Duplicating them creates thin duplicate content and would hurt the page. Each
video gets an original one-line description written for search, not scraped.

TO ADD VIDEOS: paste entries into VIDEOS below. The page renders fine with an
empty list; sections simply show their copy and links until videos exist.

SITEMAP WARNING: gen_guides.py rewrites sitemap.xml FROM SCRATCH; every other
generator appends. This script appends like the others, AND /videos.html has
been added to the `core` list in gen_guides.py so a from-scratch rebuild cannot
silently drop it. Run order stays: gen_guides.py first, then the rest.
"""
import os, re, json, html

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
URL = "https://vareadyapp.com/videos.html"
TIKTOK = "https://www.tiktok.com/@vareadyapp"


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------------------
# Videos. Empty is fine. Add as they are published.
#   topic:  must match a TOPICS key below
#   title:  ORIGINAL wording for our site. Not the TikTok caption.
#   url:    full TikTok video URL
#   blurb:  one original sentence describing what the video covers
# ---------------------------------------------------------------------------
VIDEOS = [
    {"topic": "intent-to-file",
     "title": "Where to start a VA disability claim",
     "url": "https://www.tiktok.com/@vareadyapp/video/7669961095230049566",
     "blurb": "The first steps of a VA disability claim, in order, and what is worth doing before you file anything."},

    {"topic": "rating-math",
     "title": "Why VA rating math does not add up",
     "url": "https://www.tiktok.com/@vareadyapp/video/7666989245663415583",
     "blurb": "How the VA combines ratings, and why two ratings never total what you would expect."},

    {"topic": "appeals",
     "title": "The VA decision letter most vets never read",
     "url": "https://www.tiktok.com/@vareadyapp/video/7666158490422922526",
     "blurb": "What is inside your rating decision, and the part that explains why each condition landed where it did."},

    {"topic": "intent-to-file",
     "title": "Your claim starts before you separate",
     "url": "https://www.tiktok.com/@vareadyapp/video/7665800074575826207",
     "blurb": "Why the strongest claims begin while you are still in, and what to line up ahead of your separation date."},
]


# ---------------------------------------------------------------------------
# Topics. Each one is a real thing vets search for, mapped to the pages we
# already rank with. The `links` are the whole point: this hub exists partly to
# push authority down into those pages.
# ---------------------------------------------------------------------------
TOPICS = [
    {
        "id": "rating-math",
        "h2": "Combined rating math",
        "copy": "VA does not add your ratings together. It applies each one to whatever is left of you after the last, which is why 50% and 30% comes out at 70% and not 80%. Once you see the order the math runs in, your own rating decision stops looking like a typo.",
        "links": [("Combined rating calculator", "/va-disability-calculator.html"),
                  ("2026 pay rates by rating", "/va-disability-pay-rates.html"),
                  ("What each rating pays", "/va-disability-pay/")],
    },
    {
        "id": "cp-exams",
        "h2": "C&P exams",
        "copy": "The exam is the part of a claim that most often decides it, and it is over in twenty minutes. Examiners ask how you are today; the rating schedule asks how you are on an average day and a bad one. Knowing the difference before you walk in is most of the battle.",
        "links": [("C&P exam preparation guide", "/guides/c-and-p-exam-preparation.html"),
                  ("Building your evidence package", "/guides/building-your-evidence-package.html"),
                  ("10 mistakes that get claims denied", "/guides/10-mistakes-that-get-claims-denied.html")],
    },
    {
        "id": "intent-to-file",
        "h2": "Intent to File and effective dates",
        "copy": "An Intent to File holds your effective date for one year while you get the rest together. It is one of the few free wins in the whole process, and the one most people find out about after they have already lost months of back pay.",
        "links": [("Intent to File guide", "/guides/intent-to-file.html"),
                  ("VA Form 21-0966", "/guides/va-form-21-0966.html"),
                  ("Back pay calculator", "/va-back-pay-calculator.html"),
                  ("Filing within 1 year of discharge", "/guides/filing-within-1-year-of-discharge.html")],
    },
    {
        "id": "appeals",
        "h2": "Appeals and denials",
        "copy": "A denial is not the end of the claim, it is a fork in it. There are three lanes and they are not interchangeable: one takes new evidence, one does not, and one goes to a judge. Picking the wrong lane costs you months.",
        "links": [("Supplemental claims", "/guides/supplemental-claims.html"),
                  ("Denied your appeal, options explained", "/guides/denied-your-appeal-options-explained.html"),
                  ("VA Form 20-0995, Supplemental Claim", "/guides/va-form-20-0995.html"),
                  ("VA Form 20-0996, Higher-Level Review", "/guides/va-form-20-0996.html"),
                  ("VA Form 10182, Board Appeal", "/guides/va-form-10182.html")],
    },
    {
        "id": "tdiu",
        "h2": "TDIU and 100%",
        "copy": "TDIU pays at the 100% rate without a 100% schedular rating, when service-connected conditions keep you from holding steady work. Plenty of vets qualify for years without knowing the option exists.",
        "links": [("TDIU guide", "/guides/tdiu.html"),
                  ("VA Form 21-8940", "/guides/va-form-21-8940.html"),
                  ("Permanent and total disability", "/guides/permanent-and-total-disability.html"),
                  ("Special Monthly Compensation", "/guides/special-monthly-compensation-smc.html")],
    },
    {
        "id": "secondary",
        "h2": "Secondary conditions",
        "copy": "One rated condition can cause another, and the second one is claimable on its own. Sleep apnea from PTSD, a bad knee from the other knee, depression from chronic pain. These are some of the most commonly missed points on the whole schedule.",
        "links": [("Secondary service connection", "/guides/secondary-service-connection.html"),
                  ("Nexus letters", "/guides/nexus-letters.html"),
                  ("Browse conditions by body system", "/conditions.html")],
    },
    {
        "id": "exposures",
        "h2": "Toxic exposure and the PACT Act",
        "copy": "Where you served can make a condition presumptive, which means you do not have to prove the link. Burn pits, Agent Orange, Camp Lejeune, radiation. If your service touched one of these lists, the evidence bar for certain conditions drops sharply.",
        "links": [("PACT Act guide", "/guides/pact-act.html"),
                  ("Exposure library", "/exposures.html"),
                  ("Conditions by exposure", "/conditions.html")],
    },
    {
        "id": "vso",
        "h2": "Working with a VSO",
        "copy": "A VSO is a VA-accredited rep who files and manages your claim, and they do it for free. Nobody accredited can charge you to file an initial claim. If someone is asking for a cut of your back pay, that is the signal to walk.",
        "links": [("Find a VSO near you", "/find-a-vso.html"),
                  ("What VSOs do", "/guides/veterans-service-officers-vsos.html"),
                  ("Changing your VSO", "/guides/changing-your-vso.html"),
                  ("VA Form 21-22", "/guides/va-form-21-22.html")],
    },
]


def topic_section(t):
    vids = [v for v in VIDEOS if v.get("topic") == t["id"]]
    cards = ""
    if vids:
        items = "".join(
            f'<li><a href="{esc(v["url"])}" target="_blank" rel="noopener">{esc(v["title"])}</a>'
            f'<span style="display:block;color:var(--gray);font-size:14px;margin-top:2px;">{esc(v["blurb"])}</span></li>'
            for v in vids
        )
        cards = f'<ul class="vid-list">{items}</ul>'
    links = "".join(f'<a href="{esc(u)}">{esc(l)}</a>' for l, u in t["links"])
    return f"""    <section id="{t['id']}">
      <h2>{esc(t['h2'])}</h2>
      <p>{esc(t['copy'])}</p>
      {cards}
      <div class="topic-links">{links}</div>
    </section>
"""


def build():
    # Pull the shared chrome by regex rather than importing, because gen_guides
    # runs its entire build at import time and would rewrite the sitemap.
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen_guides.py")).read()
    def block(name):
        m = re.search(rf'^{name} = """(.*?)"""', src, re.S | re.M)
        if not m:
            raise SystemExit(f"could not find {name} in gen_guides.py")
        return m.group(1)

    CSS, NAV, FOOTER = block("CSS"), block("NAV"), block("FOOTER")
    APP_CTA, DISCLAIMER = block("APP_CTA"), block("DISCLAIMER")

    sections = "".join(topic_section(t) for t in TOPICS)
    toc = "".join(f'<a href="#{t["id"]}">{esc(t["h2"])}</a>' for t in TOPICS)

    # Schema. ItemList of the topics is honest whether or not videos exist yet.
    # VideoObject entries are only emitted for videos that actually exist, so we
    # never claim media we do not have.
    graph = [{
        "@type": "CollectionPage",
        "@id": URL,
        "url": URL,
        "name": "VA Claim Help Videos",
        "description": "Free educational videos about the VA disability claims process, made by a retired Army veteran.",
        "isPartOf": {"@type": "WebSite", "url": "https://vareadyapp.com"},
        "publisher": {"@type": "Organization", "name": "VA Ready",
                      "url": "https://vareadyapp.com", "sameAs": [TIKTOK]},
    }, {
        "@type": "ItemList",
        "name": "VA claim video topics",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": t["h2"],
             "url": f"{URL}#{t['id']}"} for i, t in enumerate(TOPICS)
        ],
    }]
    for v in VIDEOS:
        graph.append({"@type": "VideoObject", "name": v["title"],
                      "description": v["blurb"], "contentUrl": v["url"],
                      "publisher": {"@type": "Organization", "name": "VA Ready"}})
    schema = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2)

    extra_css = """
    .vid-list { list-style:none; padding:0; margin:14px 0; }
    .vid-list li { padding:10px 0; border-top:1px solid var(--line); }
    .topic-links { display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }
    .topic-links a { font-size:14px; padding:6px 12px; border:1px solid var(--line); border-radius:20px; text-decoration:none; }
    .toc { display:flex; flex-wrap:wrap; gap:8px; margin:18px 0 26px; }
    .toc a { font-size:14px; padding:6px 12px; background:rgba(217,166,33,.10); border-radius:20px; text-decoration:none; }
    """

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VA Claim Help Videos: Free Guides for Vets | VA Ready</title>
<meta name="description" content="Free short videos on VA disability claims: combined rating math, C&amp;P exams, Intent to File, appeals, TDIU, and finding a VSO. Made by a retired Army vet. No claim sharks, no referral fees.">
<link rel="canonical" href="{URL}">
<meta property="og:title" content="VA Claim Help Videos: Free Guides for Vets">
<meta property="og:description" content="Short, plain-language videos on the VA claims process from a retired Army vet.">
<meta property="og:url" content="{URL}">
<meta property="og:type" content="website">
<link rel="icon" href="/logo.png">
<style>{CSS}{extra_css}</style>
<script type="application/ld+json">
{schema}
</script>
</head>
<body>
{NAV}
<div class="wrap">
    <h1>VA Claim Help Videos: Free Guides from VA Ready</h1>
    <p class="lede">Short, plain-language videos about how VA disability claims actually work, made by a retired Army vet who has been through the process. No referral fees, no cut of your back pay, no claim shark pitch.</p>
    <p>Every topic below links to the full written guide on this site, so you can watch the short version or read the long one. Both are free.</p>

    <div class="toc">{toc}</div>

    <div class="cta" style="margin-bottom:30px;">
        <h3>Watch on TikTok</h3>
        <p>New videos go up on <a href="{TIKTOK}" target="_blank" rel="me noopener">@vareadyapp</a>. Follow there for the short version; the guides on this site go deeper and cite the regulation.</p>
        <div class="btns"><a href="{TIKTOK}" class="btn" target="_blank" rel="me noopener">Follow @vareadyapp on TikTok</a></div>
    </div>

{sections}
    {APP_CTA}
    {DISCLAIMER}
</div>
{FOOTER}
</body>
</html>"""

    open(os.path.join(SITE, "videos.html"), "w").write(page)

    # Append to sitemap if missing. Same merge pattern the other nine use.
    sp = os.path.join(SITE, "sitemap.xml")
    xml = open(sp).read()
    if URL not in xml:
        entry = (f'  <url>\n    <loc>{URL}</loc>\n'
                 f'    <lastmod>2026-08-09</lastmod>\n    <priority>0.7</priority>\n  </url>\n')
        xml = xml.replace("</urlset>", entry + "</urlset>")
        open(sp, "w").write(xml)
        print("sitemap: added /videos.html")
    else:
        print("sitemap: /videos.html already present")

    print(f"generated videos.html | topics: {len(TOPICS)} | videos: {len(VIDEOS)}")


if __name__ == "__main__":
    build()
