#!/usr/bin/env python3
"""How-to pages (/how-to/<key>.html) and the features overview (/features.html).

One page per feature: what it does, where it lives, steps, real dark app
screenshots, and the questions veterans search that the feature answers, each
answer sourced to 38 CFR or VA.gov.

Inputs:
  data/howto_questions.json  {key: [{q, a, source, source_title}]}
  data/howto_manifest.json   [{feature, file, shows, pro}]
  img/howto/<file>.jpg/.webp (600 px wide, made from the app captures)
Reuses CSS/NAV/FOOTER/head/tail from gen_wear_and_tear.py's source files.
"""
import html, json, os, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
OUT = os.path.join(SITE, "how-to")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.date.today().isoformat()

def esc(s): return html.escape(str(s) if s is not None else "", quote=True)

Q = json.load(open(os.path.join(HERE, "data", "howto_questions.json")))
SHOTS = json.load(open(os.path.join(HERE, "data", "howto_manifest.json")))

gtext = open(os.path.join(HERE, "gen_guides.py")).read()
CSS = re.search(r'CSS = """(.*?)"""', gtext, re.S).group(1)
ctext = open(os.path.join(HERE, "gen_conditions.py")).read()
NAV = re.search(r'NAV = """(.*?)"""', ctext, re.S).group(1)
FOOTER = re.search(r'FOOTER = """(.*?)"""', ctext, re.S).group(1)

CSS += """
    .wrap > p:not(.lede):not(.note):not(.trustline) { color:var(--tan); margin:0 0 14px; max-width:68ch; }
    .trustline { font-size:14.5px; color:var(--tan); margin:14px 0 4px; max-width:68ch; }
    .page-cta { margin:26px 0; }
    .where { color:var(--tan); font-size:15.5px; margin:0 0 18px; max-width:68ch; }
    ol.steps { padding-left:22px; margin:8px 0 20px; }
    ol.steps li { color:var(--tan); margin:0 0 10px; max-width:66ch; }
    .shots { display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:22px; margin:10px 0 26px; }
    .shots figure { margin:0; }
    .shots figcaption { color:var(--gray); font-size:13.5px; margin-top:8px; line-height:1.45; }
    .phone { background:#05070d; padding:10px; border-radius:34px; border:1px solid rgba(255,255,255,0.08); }
    .phone img { display:block; width:100%; height:auto; border-radius:26px; }
    dl.faq { margin:8px 0 20px; }
    dl.faq dt { color:var(--white); font-weight:700; margin:18px 0 4px; font-size:16.5px; }
    dl.faq dd { margin:0; color:var(--tan); max-width:68ch; }
    dl.faq dd .src { display:block; color:var(--gray); font-size:13px; margin-top:4px; }
    dl.faq dd .src a { color:var(--gray); }
    .tier { color:var(--gray); font-size:13px; font-weight:600; margin-left:8px; }
    .grp { border-top:1px solid var(--line); padding:22px 0 6px; }
    .grp h2 { font-size:22px; font-weight:800; margin:0 0 10px; }
    ul.flist { list-style:none; padding:0; margin:0 0 10px; max-width:none; }
    ul.flist li { padding:10px 0; margin:0; border-bottom:1px solid var(--line); }
    ul.flist li a.fn { color:var(--white); font-weight:700; }
    ul.flist li p { color:var(--tan); font-size:15px; margin:3px 0 0; max-width:68ch; }
    .ov { display:grid; grid-template-columns:minmax(0,1fr) 240px; gap:28px; align-items:start; }
    @media (max-width:760px) { .ov { grid-template-columns:minmax(0,1fr); } .ov .phone { max-width:260px; } }
"""


SVG_APPLE, SVG_PLAY, SVG_WIN = '<svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>', '<svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M3.609 1.814L13.792 12 3.609 22.186A.997.997 0 013 21.286V2.714a.997.997 0 01.609-.9zm10.89 10.892l2.302 2.302-12.4 7.16 10.098-9.462zM18.16 9.18l2.578 1.49a1 1 0 010 1.66l-2.66 1.534-2.99-2.99 3.072-1.694zM4.398 1.815l12.4 7.16-2.282 2.282L4.398 1.815z"/></svg>', '<svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h8.5v8.5H3zM12.5 3H21v8.5h-8.5zM3 12.5h8.5V21H3zM12.5 12.5H21V21h-8.5z"/></svg>'
CSS += """
    .getapp { display:flex; gap:18px; align-items:center; flex-wrap:wrap; background:var(--navy2, #111a2b); border:1px solid rgba(217,166,33,0.55); border-radius:18px; padding:18px 20px; margin:6px 0 26px; }
    .getapp .gi { width:64px; height:64px; border-radius:15px; flex:none; }
    .getapp .gt { flex:1 1 260px; min-width:0; }
    .getapp .gh { color:var(--white); font-size:19px; font-weight:800; line-height:1.3; margin:0 0 4px; }
    .getapp .gp { color:var(--tan); font-size:14.5px; margin:0; }
    .getapp .gp b { color:var(--white); }
    .getapp .gb { display:flex; flex-wrap:wrap; gap:10px; flex-basis:100%; }
    .sb { display:inline-flex; align-items:center; gap:9px; background:var(--gold); color:#000 !important; font-weight:800; font-size:15.5px; padding:13px 18px; border-radius:12px; text-decoration:none !important; min-height:48px; }
    .sb svg { width:20px; height:20px; flex:none; }
    .sb:hover { filter:brightness(1.08); }
    .stickybar { position:fixed; left:0; right:0; bottom:0; z-index:50; display:flex; align-items:center; gap:12px; justify-content:center; background:rgba(8,12,22,0.96); border-top:1px solid rgba(217,166,33,0.5); padding:10px 16px calc(10px + env(safe-area-inset-bottom)); backdrop-filter:blur(8px); }
    .stickybar img { width:36px; height:36px; border-radius:9px; }
    .stickybar .st { color:var(--white); font-weight:700; font-size:15px; line-height:1.25; }
    .stickybar .st span { display:block; color:var(--tan); font-weight:400; font-size:13px; }
    .stickybar .sb { padding:10px 18px; min-height:44px; margin-left:8px; }
    body { padding-bottom:84px; }
    @media (max-width:560px) { .getapp .sb { flex:1 1 100%; justify-content:center; } }
"""

def getapp(headline):
    return (f'<div class="getapp"><img class="gi" src="/logo-96.png" alt="VA Ready app icon" width="64" height="64">'
            f'<div class="gt"><p class="gh">{esc(headline)}</p>'
            f'<p class="gp"><b>4.8</b> on the App Store, 800+ ratings &middot; <b>4.7</b> on Google Play &middot; <b>53,000+</b> downloads &middot; free to download</p></div>'
            f'<div class="gb"><a class="sb" href="https://apps.apple.com/app/id6761733758">{SVG_APPLE}App Store</a>'
            f'<a class="sb" href="https://play.google.com/store/apps/details?id=com.vaready.app&amp;hl=en_US">{SVG_PLAY}Google Play</a>'
            f'<a class="sb" href="https://apps.microsoft.com/detail/9p8xfcqvfjhf">{SVG_WIN}Microsoft Store</a></div></div>')

STICKY = ("""<div class="stickybar"><img src="/logo-96.png" alt="" width="36" height="36"><div class="st">VA Ready<span>4.8 on the App Store, free to download</span></div>"""
          """<a class="sb" id="sbget" href="https://apps.apple.com/app/id6761733758">Get the app</a></div>"""
          """<script>(function(){var u=navigator.userAgent,a=document.getElementById('sbget');if(/Android/i.test(u))a.href='https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US';else if(/Windows/i.test(u))a.href='https://apps.microsoft.com/detail/9p8xfcqvfjhf';})();</script>""")

STORES = """<div class="btns page-cta"><a href="https://apps.apple.com/app/id6761733758" class="btn primary">VA Ready for iPhone, iPad and Mac</a><a href="https://play.google.com/store/apps/details?id=com.vaready.app&hl=en_US" class="btn ghost">Vet Ready for Android</a><a href="https://apps.microsoft.com/detail/9p8xfcqvfjhf" class="btn ghost">VA Ready for Windows</a></div>"""
DISCLAIMER = """<div class="disclaimer">This page is for general informational purposes only and is not legal or medical advice. Answers summarize the regulation or VA page cited under each one; check the source for your situation. The VA decides service connection and ratings from your own records, evidence, and exam. VA Ready is not affiliated with the U.S. Department of Veterans Affairs. For free help filing, work with a <a href="/find-a-vso.html">VA-accredited VSO</a>.</div>"""
ORG_ID = "https://vareadyapp.com/#organization"

# key, page title (H1), SEO title, meta description, tier, where it lives,
# intro, steps, related links [(href, label)], overview one-liner, group
F = [
 dict(key="claim-denied", h1="How to appeal a denied VA claim with the Claim Navigator",
  seo="Denied VA claim: your appeal options, step by step", tier="Pro", group="decision",
  desc="VA denied your claim. See your three appeal lanes, the one-year window and what each lane needs, step by step in the VA Ready Claim Navigator.",
  where="Filing tab, Tools, Claim Navigator.",
  intro="A denial starts a one-year clock. The Claim Navigator turns the decision into a route: which of the three appeal lanes fits what went wrong, what to gather for it, and a reminder before the year runs out.",
  steps=["Open the Filing tab and tap Claim Navigator under Tools.",
         "Pick I was denied from the starting points.",
         "Read the next step and the route map. Each lane (Supplemental Claim, Higher-Level Review, Board Appeal) shows when it fits and the typical days VA takes.",
         "Turn on the one-year deadline reminder.",
         "Tap Share this route as PDF to take the plan to your VSO."],
  links=[("/guides/denied-your-appeal-options-explained.html", "appeal options explained"), ("/guides/supplemental-claims.html", "Supplemental Claims"), ("/guides/va-form-20-0996.html", "VA Form 20-0996")],
  blurb="Pick I was denied and get the appeal lane that fits, the one-year deadline and what to gather."),
 dict(key="rating-increase", h1="How to file for a VA rating increase",
  seo="VA rating increase: how to file and what VA looks for", tier="Pro", group="decision",
  desc="Think your condition got worse? See the rating criteria for each percent, the re-exam risk and the steps to file for a VA increase in VA Ready.",
  where="Filing tab, Tools, Claim Navigator. Rating criteria open from Edit rating on any condition in My Claim.",
  intro="An increase is won on evidence that the condition now meets the next level of the rating schedule. VA Ready shows the criteria for every level of your condition and walks the increase route, including the chance that a new exam lowers the rating.",
  steps=["On My Claim, open the condition and tap Edit rating to read the 38 CFR criteria for each percent.",
         "Compare your symptoms with the next level up.",
         "On the Filing tab, open Claim Navigator and pick I want to increase an existing rating.",
         "Follow the route: gather worsening evidence, read the re-exam risk detour, then file.",
         "Keep logging symptoms so the record shows the change over time."],
  links=[("/guides/filing-for-an-increase.html", "filing for an increase"), ("/guides/protected-ratings.html", "protected ratings"), ("/conditions.html", "rating criteria by condition")],
  blurb="Read the criteria for the next level, check the re-exam risk, and follow the increase route."),
 dict(key="cp-exam-prep", h1="How to prepare for your C&P exam",
  seo="C&P exam prep: the questions examiners ask, by condition", tier="Pro", group="evidence",
  desc="Prepare for your VA C&P exam: answer the questions the examiner works from for your condition, in your own words, then export them as a PDF.",
  where="My Claim, open a condition, C&P exam questionnaire.",
  intro="Examiners fill out a set form for each condition. The questionnaire puts those questions in front of you at home, so you can think through onset, frequency, flare-ups and how the condition affects work before you are in the room.",
  steps=["On My Claim, open the condition with the exam.",
         "Tap C&P exam questionnaire.",
         "Read Why this matters, then answer each question in your own words.",
         "Tap Export my answers as PDF and save or print it.",
         "Bring the printout to the exam and give a copy to your VSO."],
  links=[("/guides/c-and-p-exam-preparation.html", "C&P exam preparation"), ("/guides/10-mistakes-that-get-claims-denied.html", "mistakes that get claims denied")],
  blurb="Answer the examiner's questions for your condition at home, then export them as a PDF."),
 dict(key="what-to-claim", h1="How to find what to claim from your job and duties",
  seo="What to claim for VA disability by MOS, AFSC or rating", tier="Pro", group="start",
  desc="What should I claim? See conditions common for your MOS, AFSC or Navy rating, your extra duties and the top conditions VA rates, in VA Ready Claim Intel.",
  where="Claim Intel tab, MOS view. Top VA claims opens from the Claim Intel tab and is free.",
  intro="Most veterans under-claim. Claim Intel starts from your job code (1,106 across every branch, including legacy codes) and your additional duties, and lists the conditions common for them, with PACT Act presumptives called out. Top VA claims adds VA's own counts of what it rates most.",
  steps=["Set your branch and job code in your profile.",
         "Open the Claim Intel tab. The MOS view ranks conditions common for your job.",
         "Scroll to Additional duties and mark the ones you held.",
         "Open Top VA claims to see VA's counts by era, by body system and for veterans newly rated.",
         "Add any condition to your claim to see what it does to your rating."],
  links=[("/mos.html", "conditions by job code"), ("/what-helps-and-hurts-va-claims.html", "what helps and hurts claims")],
  blurb="Conditions common for your job code and duties, plus VA's own list of what it rates most."),
 dict(key="toxic-exposures", h1="How to check toxic exposures and PACT Act presumptives",
  seo="PACT Act presumptives by base: check your toxic exposures", tier="Pro", group="start",
  desc="Add the bases and aircraft you served on and see the PACT Act and other presumptive conditions they qualify you for, with the exposure and law behind each.",
  where="Claim Intel tab, Exposures view.",
  intro="A presumptive condition skips the hardest part of a claim: proving the link to service. Add where you served and VA Ready matches 834 bases and 148 airframes against 56 exposures, then lists the presumptive conditions with the window and the authority for each.",
  steps=["Open the Claim Intel tab and switch to Exposures.",
         "Add each base or ship and the dates you were there, and any aircraft you worked on.",
         "Read the list of possible presumptive matches.",
         "Tap a condition to see why it is listed: the exposure, the dates and the law.",
         "Add the ones you have to your claim."],
  links=[("/exposures.html", "toxic exposure pages"), ("/guides/pact-act.html", "the PACT Act"), ("/exposures/burn-pits-pact-act.html", "burn pits")],
  blurb="Add where you served and see the presumptive conditions, with the dates and law behind each."),
 dict(key="wear-and-tear", h1="How to claim wear and tear from what you did in service",
  seo="Wear and tear VA claims: conditions linked to what you did", tier="Pro", group="start",
  desc="Rucking, kicking in doors, jumps, ranges, flight decks: see the conditions linked to what you did in service, the studies behind each and how to prove it.",
  where="Claim Intel tab, Wear and Tear view.",
  intro="A job code misses most of what service put your body through. Wear and Tear starts from the activity instead, across 226 of them, and lists the conditions published research links to each, the records that prove you did it, and questions for your own statement.",
  steps=["Open the Claim Intel tab and switch to Wear and Tear.",
         "Search an activity (ruck, doors, jumps) or browse the categories.",
         "Open an activity and mark I did this. The conditions from everything you mark gather into one ranked list.",
         "Read How to prove you did this for the records that show it.",
         "Answer the statement questions, then copy or share your statement, or ask a buddy for one."],
  links=[("/wear-and-tear.html", "Wear and Tear pages"), ("/guides/buddy-statements.html", "buddy statements")],
  blurb="Mark what you did, from rucking to flight decks, and see the conditions and the proof for each."),
 dict(key="secondary-conditions", h1="How to find secondary conditions and test them with What-If",
  seo="Secondary conditions to your service-connected rating", tier="Pro", group="start",
  desc="Find conditions secondary to the ones you are rated for, like depression or sleep apnea secondary to PTSD, and see what each would do to your rating.",
  where="My Claim, Suggestions and What-If.",
  intro="A rated condition often causes or worsens another one, and VA pays for that second condition too. Suggestions lists likely secondaries for what you already have, along with presumptives for your job, and What-If shows what each would do to your combined rating and pay.",
  steps=["Add your rated conditions on My Claim.",
         "Open Suggestions to see conditions secondary to each one and presumptives for your job code.",
         "Tap Add on any that apply to you.",
         "Open What-If to try a condition at a rating and see the new combined rating and monthly pay.",
         "Check which condition gets you closest to the next level."],
  links=[("/guides/secondary-service-connection.html", "secondary service connection"), ("/guides/nexus-letters.html", "nexus letters"), ("/va-disability-calculator.html", "combined-rating calculator")],
  blurb="Likely secondaries for what you are rated for, and what each would do to your rating."),
 dict(key="back-pay", h1="How to estimate your VA back pay",
  seo="VA back pay estimate from your Intent to File date", tier=None, group="money",
  desc="Estimate VA back pay from your Intent to File or claim date, by condition and expected rating, with what could reduce it.",
  where="Filing tab, Tools, Back pay estimate. Also on My Claim.",
  intro="Back pay usually runs from your effective date, often the Intent to File date. The estimator adds up each month from that date using the rate tables for each year, for the ratings you expect, and lists what could lower the total.",
  steps=["Open the Filing tab and tap Back pay estimate under Tools.",
         "Tap Start an estimate and enter your Intent to File or claim date.",
         "Check the conditions and the expected rating for each. The low rating shows a cautious estimate.",
         "Read What could reduce my back pay."],
  links=[("/va-back-pay-calculator.html", "back pay calculator"), ("/guides/intent-to-file.html", "Intent to File"), ("/va-disability-pay-rates.html", "VA pay rates")],
  blurb="Back pay from your effective date, by condition, with what could reduce it."),
 dict(key="benefits-by-rating", h1="How to see every benefit for your VA rating",
  seo="VA benefits by disability rating, federal and state", tier=None, group="money",
  desc="See federal and state benefits for your VA rating, from 0 to 100 percent and P&T, with the amounts and how to apply.",
  where="Benefits tab.",
  intro="Your rating unlocks benefits beyond the monthly payment, and many depend on hitting a set percent or P&T status. The Benefits tab lists 32 federal benefits and 644 state benefits by rating. Free shows Texas; Pro shows every state.",
  steps=["Open the Benefits tab.",
         "Pick your rating and turn on P&T or TDIU if they apply.",
         "Open a federal category to see each benefit, its amount and how to apply.",
         "Open your state's benefits by category."],
  links=[("/federal-benefits.html", "federal benefits"), ("/states.html", "state benefits"), ("/guides/permanent-and-total-disability.html", "P&T status")],
  blurb="Federal and state benefits for your rating, with P&T and TDIU switches."),
 dict(key="buddy-statement", h1="How to write a buddy statement for a VA claim",
  seo="Buddy statement for VA: templates and how to write one", tier=None, group="evidence",
  desc="Write a buddy statement for your VA claim from five guided templates: in-service event, spouse or family, behavior change, physical limitation and general.",
  where="Filing tab, Tools, Buddy statements.",
  intro="A statement from someone who saw the event or lives with the effects can fill a gap in your records. Five templates guide the writer through what VA needs to read: who they are, what they saw, when, and how they know.",
  steps=["Open the Filing tab and tap Buddy statements.",
         "Tap New statement from a template and pick one.",
         "Fill in the details with the witness, or send it for them to complete.",
         "Print it, have the witness sign and date it, then submit it with VA Form 21-10210 or as a signed statement."],
  links=[("/guides/buddy-statements.html", "buddy statements"), ("/guides/va-form-21-10210.html", "VA Form 21-10210"), ("/guides/va-form-21-4138.html", "VA Form 21-4138")],
  blurb="Five guided templates for the people who saw what happened."),
 dict(key="symptom-log", h1="How to keep a symptom log for your VA claim",
  seo="Symptom log for VA claims: daily check-ins and medications", tier=None, group="evidence",
  desc="Log symptoms and flare-ups by condition with a severity and a note, track medications, and export the log for your claim or C&P exam.",
  where="My Claim, Symptom log and Medications.",
  intro="Ratings turn on frequency, severity and how a condition limits you. A log written as it happens is better evidence than memory at an exam. Check in for each condition, note what happened, and keep your medications in one list. Pro adds unlimited history, reminders and PDF exports.",
  steps=["On My Claim, open Symptom log.",
         "Tap a condition to check in. Set the severity and add a note.",
         "Log flare-ups when they happen, not after.",
         "Add your medications from Medications on My Claim.",
         "Export the log before your exam or claim."],
  links=[("/guides/building-your-evidence-package.html", "building your evidence package"), ("/guides/c-and-p-exam-preparation.html", "C&P exam preparation")],
  blurb="Daily check-ins by condition, severity and notes, plus your medications."),
 dict(key="claim-evidence", h1="How to organize your claim evidence for VA",
  seo="Organize VA claim evidence and upload it to VA.gov", tier=None, group="evidence",
  desc="Scan and label your records by VA document type and condition, rename them for VA.gov upload, and build a VSO packet with an evidence index.",
  where="Filing tab, Tools, Claim file. The VSO packet is on the My VSO tab.",
  intro="VA decides on what is in the file. The claim file keeps every record on your device, labeled by document type and tied to the condition it supports. Ready for VA (Pro) renames files with the upload category to pick on VA.gov, and the VSO packet (Pro) puts everything in one PDF with an index.",
  steps=["Open the Filing tab and tap Claim file.",
         "Scan or import a record, label its type and pick the condition it supports.",
         "Tap Ready for VA to create renamed copies, each with its VA.gov upload category.",
         "On the My VSO tab, open VSO packet and tap Build the packet."],
  links=[("/va-claim-evidence.html", "claim evidence"), ("/guides/building-your-evidence-package.html", "building your evidence package"), ("/guides/nexus-letters.html", "nexus letters")],
  blurb="Label records by type and condition, rename them for VA.gov and build a VSO packet."),
 dict(key="intent-to-file", h1="How to track your Intent to File date",
  seo="Intent to File: track the date and get reminders", tier=None, group="track",
  desc="Save your VA Intent to File date and get reminders 60 and 14 days before the one-year window closes, so you keep your effective date.",
  where="Filing tab, Claim status. Deadlines show under Upcoming.",
  intro="An Intent to File holds your effective date for one year. Miss the window and the back pay from that date is gone. Save the date and VA Ready reminds you 60 and 14 days before it expires.",
  steps=["File your Intent to File with VA (online, by phone or on VA Form 21-0966).",
         "On the Filing tab, open Claim status and tap Add Intent to File date.",
         "Check the date it holds your effective date through.",
         "Leave reminders on. The end date shows under Upcoming."],
  links=[("/guides/intent-to-file.html", "Intent to File"), ("/guides/va-form-21-0966.html", "VA Form 21-0966")],
  blurb="Save the date and get reminders 60 and 14 days before the year ends."),
 dict(key="tdiu", h1="How to check if you qualify for TDIU",
  seo="TDIU: do you qualify and what it pays", tier=None, group="money",
  desc="Check the TDIU percentage rules under 38 CFR 4.16(a) against your ratings and see the monthly difference between your rating and the 100 percent rate.",
  where="My Claim, Compensation, TDIU card.",
  intro="TDIU pays at the 100 percent rate when service-connected conditions keep you from steady work. The card checks your ratings against the 38 CFR 4.16(a) thresholds and shows what TDIU would add each month.",
  steps=["Add your rated conditions on My Claim.",
         "Scroll to Compensation and find the TDIU card.",
         "Tap See if I qualify to check the 38 CFR 4.16(a) thresholds.",
         "Read what the decision turns on, then follow the TDIU route in Claim Navigator if it fits."],
  links=[("/guides/tdiu.html", "TDIU"), ("/guides/va-form-21-8940.html", "VA Form 21-8940"), ("/guides/va-form-21-4192.html", "VA Form 21-4192")],
  blurb="Your ratings against the 4.16(a) thresholds and the monthly difference TDIU makes."),
 dict(key="smc", h1="How to see what Special Monthly Compensation pays",
  seo="Special Monthly Compensation (SMC): levels and rates", tier=None, group="money",
  desc="See SMC levels K through S, which ones add to your rate and which replace it, with the current monthly rate for each.",
  where="My Claim, Compensation, Special monthly compensation.",
  intro="SMC pays more than the 100 percent rate for specific losses, like loss of use or the need for aid and attendance. SMC-K adds to your rate. The other levels replace it. Pick a level to see what your monthly pay would be.",
  steps=["On My Claim, scroll to Compensation.",
         "Tap Check under Special monthly compensation.",
         "Add SMC-K if it applies, then pick the level that fits.",
         "Compare the monthly rate with your current pay."],
  links=[("/guides/special-monthly-compensation-smc.html", "SMC explained"), ("/va-disability-pay-rates.html", "VA pay rates")],
  blurb="SMC levels K through S with the monthly rate for each."),
 dict(key="track-claim", h1="How to track your VA claim status",
  seo="VA claim status: the 10 steps and what happens next", tier=None, group="track",
  desc="Track your VA claim through each step, see what to do next and what VA is doing now, and keep a dated claim journal.",
  where="Filing tab, Claim status. The Claim Journal is on My Claim.",
  intro="VA.gov shows a step number. VA Ready explains it: what VA is doing at this step, what you can do, and what comes next. The Claim Journal keeps every call, letter, exam and upload in one dated timeline.",
  steps=["On the Filing tab, tap Claim status and set the step VA.gov shows.",
         "Read what is happening now and what to do next.",
         "Open All steps to see where you are in the process.",
         "On My Claim, open Claim Journal and add each event as it happens."],
  links=[("/guides/how-long-does-a-va-claim-take.html", "how long a claim takes"), ("/guides/fdc-vs-standard-claim.html", "FDC or standard claim")],
  blurb="What each claim step means, what to do next, and a dated journal."),
 dict(key="rating-reduction", h1="How to respond to a proposed VA rating reduction",
  seo="Proposed VA rating reduction: the 60-day window", tier="Pro", group="decision",
  desc="Got a proposed reduction? See the 60-day window to respond, the protected-rating rules and your appeal options, step by step.",
  where="Filing tab, Tools, Claim Navigator. Protected Ratings is under Filing guides.",
  intro="A proposed reduction gives you 60 days to send evidence before VA acts. Some ratings are protected by how long you have held them. The reduction route walks the window, and the Protected Ratings guide covers the 5, 10 and 20-year rules.",
  steps=["On the Filing tab, open Claim Navigator and pick My rating was reduced (or proposed).",
         "Note the 60-day response date and set the reminder.",
         "Check the Protected Ratings guide under Filing guides.",
         "Read the proposed reduction notice guide and gather current evidence.",
         "If VA reduces the rating, follow the appeal guide."],
  links=[("/guides/proposed-reduction-notice.html", "proposed reduction notice"), ("/guides/protected-ratings.html", "protected ratings"), ("/guides/due-process-rights-under-3-103.html", "due process rights")],
  blurb="The 60-day window, protected ratings and what to send VA."),
 dict(key="board-cases", h1="How to see what decided Board cases on your condition",
  seo="What wins BVA appeals: Board decisions by condition", tier="Pro", group="decision",
  desc="See what helped and what hurt in real Board of Veterans' Appeals decisions on your condition, with the decision numbers behind each finding.",
  where="My Claim, open a condition, What decided Board cases.",
  intro="The Board of Veterans' Appeals publishes its decisions. VA Ready reads them by condition and sorts what helped a veteran win and what hurt, with the decision number behind each point, so you can see what evidence the judges weighed.",
  steps=["On My Claim, open a condition.",
         "Tap What decided Board cases.",
         "Read what helped and what hurt.",
         "Tap Preview and share to send the summary to your VSO."],
  links=[("/what-helps-and-hurts-va-claims.html", "what helps and hurts claims"), ("/guides/va-form-10182.html", "VA Form 10182")],
  blurb="What helped and hurt in real Board decisions on your condition."),
 dict(key="claim-scenarios", h1="How to try different claims with claim scenarios",
  seo="Compare VA claim scenarios without changing your claim", tier="Pro", group="money",
  desc="Try up to four other claims on My Claim and compare the combined rating and pay. Scenario 1 stays your claim; scenarios never reach your forms or exports.",
  where="My Claim, scenario menu at the top.",
  intro="Scenario 1 is your claim. Scenarios 2 to 5 let you try other sets of conditions and ratings and compare the result. They never touch your claim, forms, VSO packet or exports.",
  steps=["On My Claim, tap the scenario menu at the top.",
         "Pick Scenario 2 to 5.",
         "Choose Copy my claim or start empty.",
         "Add, remove or re-rate conditions and watch the combined rating.",
         "Tap Back to my claim to return to Scenario 1."],
  links=[("/va-disability-calculator.html", "combined-rating calculator")],
  blurb="Try up to four other claims; Scenario 1 stays your claim."),
 dict(key="combined-rating", h1="How VA combines ratings, step by step",
  seo="How VA combined ratings work, step by step", tier=None, group="money",
  desc="See how VA combines your ratings with the whole-person math, step by step, with the bilateral factor and the monthly pay for your dependents.",
  where="My Claim.",
  intro="VA does not add ratings. Each one applies to what is left of a whole person, the result rounds to the nearest 10, and paired limbs get a bilateral factor. My Claim shows the math one step at a time and the monthly pay for your dependents.",
  steps=["Open My Claim and add each condition with its rating.",
         "Add your dependents so the pay matches your household.",
         "Read the combined rating and monthly pay at the top.",
         "Open How the VA combines them to see each step and the rounding."],
  links=[("/va-disability-calculator.html", "combined-rating calculator"), ("/va-disability-pay-rates.html", "VA pay rates")],
  blurb="The whole-person math one step at a time, with your monthly pay."),
 dict(key="find-vso", h1="How to find a free VA-accredited VSO near you",
  seo="Find a free VSO near you: VA-accredited offices", tier=None, group="track",
  desc="Find free VA-accredited VSO offices near your ZIP code, from 8,959 offices, with distance, phone, email and reviews from other veterans.",
  where="My VSO tab.",
  intro="An accredited Veterans Service Officer files and argues your claim for free. The My VSO tab searches 8,959 offices by ZIP code, with distance, phone, email and ratings from veterans who used them.",
  steps=["Open the My VSO tab.",
         "Search your ZIP code or city.",
         "Open an office to see its contact details and reviews.",
         "Tap Make this my VSO and set a visit reminder.",
         "Build the VSO packet before your visit."],
  links=[("/find-a-vso.html", "find a VSO"), ("/guides/veterans-service-officers-vsos.html", "what a VSO does"), ("/guides/va-form-21-22.html", "VA Form 21-22")],
  blurb="Free accredited offices near your ZIP code, with reviews from veterans."),
]

CTA = {
 "claim-denied": "Denied? Get your appeal route in VA Ready",
 "rating-increase": "See what the next rating level takes, in VA Ready",
 "cp-exam-prep": "Walk into your C&P exam ready, with VA Ready",
 "what-to-claim": "See what to claim for your job code in VA Ready",
 "toxic-exposures": "Check your bases for PACT Act presumptives in VA Ready",
 "wear-and-tear": "Turn what you did in service into a claim list, in VA Ready",
 "secondary-conditions": "Find the secondaries you are missing, in VA Ready",
 "back-pay": "Estimate your back pay in VA Ready",
 "benefits-by-rating": "See every benefit your rating unlocks, in VA Ready",
 "buddy-statement": "Write a buddy statement in minutes with VA Ready",
 "symptom-log": "Start your symptom log today in VA Ready",
 "claim-evidence": "Get your evidence VA-ready with VA Ready",
 "intent-to-file": "Never lose your Intent to File date: track it in VA Ready",
 "tdiu": "Check if you qualify for TDIU in VA Ready",
 "smc": "See what SMC would pay you, in VA Ready",
 "track-claim": "Know what every claim step means, in VA Ready",
 "rating-reduction": "Fight a proposed reduction with VA Ready",
 "board-cases": "See what won Board cases on your condition, in VA Ready",
 "claim-scenarios": "Try different claims side by side in VA Ready",
 "combined-rating": "Get your combined rating and pay in VA Ready",
 "find-vso": "Find a free VSO near you with VA Ready",
}
for _f in F: _f["cta"] = CTA[_f["key"]]

GROUPS = [("start", "Find what to claim"), ("evidence", "Prove it"), ("money", "Your rating and pay"),
          ("track", "Deadlines, status and help"), ("decision", "After a decision")]

# Shots that do not go on the site: a real veteran's review of a named VSO.
SKIP = {"find-vso-2.png"}
def shots_for(key):
    extra = ["top-claims"] if key == "what-to-claim" else []
    return [s for s in SHOTS if (s["feature"] == key or s["feature"] in extra) and s["file"] not in SKIP]

def img(s):
    b = s["file"].rsplit(".", 1)[0]
    return (f'<div class="phone"><picture><source srcset="/img/howto/{b}.webp" type="image/webp">'
            f'<img src="/img/howto/{b}.jpg" alt="{esc("VA Ready app: " + s["shows"])}" width="600" height="1303" loading="lazy" decoding="async"></picture></div>')

def url_of(f): return f"/how-to/{f['key']}.html"

def head(title, desc, canon, lds, og_type="article", ogimg="https://vareadyapp.com/logo.png"):
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in lds)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#0a0f1a">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="VA Ready">
<meta property="og:title" content="{esc(title.split(' | ')[0])}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{ogimg}">
<meta name="twitter:card" content="summary"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
{ld}
<style>{CSS}</style>
</head>
<body>
{NAV}
<div class="wrap">"""

def tail():
    return f"""</div>
{FOOTER}
{STICKY}
</body>
</html>"""

def tier_tag(t): return f'&nbsp;<span class="tier">{t}</span>' if t else ""

def page(f):
    canon = f"https://vareadyapp.com{url_of(f)}"
    shots = shots_for(f["key"])
    qs = Q.get(f["key"], [])
    figs = "".join(f'<figure>{img(s)}<figcaption>{esc(s["shows"])}</figcaption></figure>' for s in shots)
    steps = "".join(f"<li>{esc(x)}</li>" for x in f["steps"])
    faq = "".join(f'<dt>{esc(x["q"])}</dt><dd>{esc(x["a"])}<span class="src">Source: <a href="{esc(x["source"])}" rel="nofollow noopener" target="_blank">{esc(x["source_title"])}</a></span></dd>' for x in qs)
    rel = " &middot; ".join(f'<a href="{h}">{esc(l)}</a>' for h, l in f["links"])
    grp = next(g for g in GROUPS if g[0] == f["group"])
    same = [o for o in F if o["group"] == f["group"] and o["key"] != f["key"]]
    more = " &middot; ".join(f'<a href="{url_of(o)}">{esc((lambda t: t[:1].upper() + t[1:])(o["h1"].replace("How to ", "")))}</a>' for o in same)
    tier_line = {"Pro": "Part of VA Ready Pro.", None: "Free in VA Ready."}[f["tier"]]
    if f["key"] in ("symptom-log",): tier_line = "Free in VA Ready; Pro adds unlimited history, reminders and PDF exports."
    if f["key"] == "claim-evidence": tier_line = "The claim file is free; Ready for VA and the VSO packet are part of Pro."
    if f["key"] == "benefits-by-rating": tier_line = "Free with Texas state benefits; Pro shows every state."
    if f["key"] == "what-to-claim": tier_line = "Claim Intel is part of Pro; Top VA claims is free."
    if f["key"] == "wear-and-tear": tier_line = "Part of VA Ready Pro, with a free preview."
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://vareadyapp.com/"},
        {"@type": "ListItem", "position": 2, "name": "Features", "item": "https://vareadyapp.com/features.html"},
        {"@type": "ListItem", "position": 3, "name": f["h1"], "item": canon}]}
    howto = {"@context": "https://schema.org", "@type": "HowTo", "name": f["h1"], "description": f["desc"],
             "step": [{"@type": "HowToStep", "position": i + 1, "text": x} for i, x in enumerate(f["steps"])],
             "tool": [{"@type": "HowToTool", "name": "VA Ready app"}]}
    if shots: howto["image"] = f"https://vareadyapp.com/img/howto/{shots[0]['file'].rsplit('.', 1)[0]}.jpg"
    lds = [bc, howto]
    if qs:
        lds.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": x["q"], "acceptedAnswer": {"@type": "Answer", "text": x["a"]}} for x in qs]})
    ogimg = f"https://vareadyapp.com/img/howto/{shots[0]['file'].rsplit('.', 1)[0]}.jpg" if shots else "https://vareadyapp.com/logo.png"
    faq_block = f'<h2>Questions this answers</h2><dl class="faq">{faq}</dl>' if qs else ""
    return head(f"{f['seo']} | VA Ready", f["desc"], canon, lds, ogimg=ogimg) + f"""
    <div class="crumb"><a href="/index.html">Home</a> / <a href="/features.html">Features</a> / {esc(grp[1])}</div>
    <h1>{esc(f["h1"])}</h1>
    <p class="lede">{esc(f["intro"])}</p>
    {getapp(f["cta"])}
    <p class="where">Where it is in the app: {esc(f["where"])} {esc(tier_line)}</p>
    <article>
        <h2>Steps</h2>
        <ol class="steps">{steps}</ol>
        <h2>In the app</h2>
        <div class="shots">{figs}</div>
        {faq_block}
    </article>
    {STORES}
    <p class="trustline">Read more: {rel}</p>
    <p class="trustline">More in {esc(grp[1].lower())}: {more} &middot; <a href="/features.html">every feature</a></p>
    {DISCLAIMER}
""" + tail()

def features():
    canon = "https://vareadyapp.com/features.html"
    desc = "Every VA Ready feature with a how-to: claim denied, rating increases, C&P exam prep, what to claim, PACT Act, wear and tear, back pay, benefits, TDIU, SMC and more."
    lead_shot = {"start": "wear-and-tear-1.png", "evidence": "cp-exam-prep-1.png", "money": "combined-rating-2.png",
                 "track": "track-claim-1.png", "decision": "claim-denied-2.png"}
    secs = ""
    for gk, gt in GROUPS:
        items = "".join(f'<li><a class="fn" href="{url_of(f)}">{esc(f["h1"])}</a>{tier_tag(f["tier"])}<p>{esc(f["blurb"])}</p></li>'
                        for f in F if f["group"] == gk)
        s = next(x for x in SHOTS if x["file"] == lead_shot[gk])
        secs += f'<section class="grp"><h2>{esc(gt)}</h2><div class="ov"><ul class="flist">{items}</ul>{img(s)}</div></section>'
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://vareadyapp.com/"},
        {"@type": "ListItem", "position": 2, "name": "Features", "item": canon}]}
    app = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "VA Ready",
           "applicationCategory": "UtilitiesApplication", "operatingSystem": "iOS, iPadOS, macOS, Android, Windows",
           "publisher": {"@type": "Organization", "@id": ORG_ID, "name": "VA Ready"}, "url": canon}
    items = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f"https://vareadyapp.com{url_of(f)}", "name": f["h1"]} for i, f in enumerate(F)]}
    return head("What VA Ready does: every feature, with how-to guides | VA Ready", desc, canon, [bc, app, items], "website") + f"""
    <div class="crumb"><a href="/index.html">Home</a> / Features</div>
    <h1>What VA Ready does</h1>
    <p class="lede">VA Ready helps you build a VA disability claim from start to finish: what to claim, how it rates, how to prove it, and where you are in the process. Everything stays on your device. Each feature below links to a page with the steps, screenshots from the app and the questions it answers.</p>
    {getapp("Get VA Ready: every feature below, on your phone, tablet or computer")}
    {secs}
    {STORES}
    <p class="trustline">More from VA Ready: <a href="/wear-and-tear.html">Wear and Tear pages</a> &middot; <a href="/mos.html">conditions by job code</a> &middot; <a href="/guides.html">filing guides</a> &middot; <a href="/conditions.html">conditions</a></p>
    <div class="disclaimer">VA Ready is not affiliated with the U.S. Department of Veterans Affairs. It is an organizing and education tool, not legal or medical advice. For free help filing, work with a <a href="/find-a-vso.html">VA-accredited VSO</a>.</div>
""" + tail()

written = []
for f in F:
    open(os.path.join(OUT, f["key"] + ".html"), "w").write(page(f)); written.append(url_of(f))
open(os.path.join(SITE, "features.html"), "w").write(features()); written.append("/features.html")

sp = os.path.join(SITE, "sitemap.xml"); xml = open(sp).read(); new = []
for u in written:
    loc = f"https://vareadyapp.com{u}"
    if loc not in xml:
        new.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <priority>0.7</priority>\n  </url>")
if new:
    xml = xml.replace("</urlset>", "\n".join(new) + "\n</urlset>"); open(sp, "w").write(xml)

bad = 0
missing_q = [f["key"] for f in F if not Q.get(f["key"])]
if missing_q: print("NO QUESTIONS", missing_q)
for u in written:
    s = open(os.path.join(SITE, u.lstrip("/"))).read()
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: json.loads(b)
        except Exception as e: bad += 1; print("BAD JSON-LD", u, e)
    if "—" in s or "&mdash;" in s: bad += 1; print("EM DASH", u)
    if s.count("<h1") != 1: bad += 1; print("H1 COUNT", u)
    for h in re.findall(r"<h[1-3][^>]*>(.*?)</h[1-3]>", s):
        if "?" in h: bad += 1; print("QUESTION HEADING", u, h)
    if "!" in re.sub(r"<!DOCTYPE|<!--.*?-->", "", s.split("<body>")[1].split("<footer")[0], flags=re.S).replace("!important", ""):
        print("NOTE: '!' in body", u)
    for h in re.findall(r'href="(/[^"#]+\.html)"', s):
        if not os.path.exists(os.path.join(SITE, h.lstrip("/"))): bad += 1; print("MISSING", u, h)
    for im in re.findall(r'(?:src|srcset)="(/img/[^"]+)"', s):
        if not os.path.exists(os.path.join(SITE, im.lstrip("/"))): bad += 1; print("NO IMAGE", u, im)
print(f"wrote {len(F)} how-to pages + features; sitemap +{len(new)}; problems={bad}")
