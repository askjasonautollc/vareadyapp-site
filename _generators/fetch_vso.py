#!/usr/bin/env python3
"""Refresh the VSO snapshots used by gen_vso.py and gen_vso_county.py.

Writes data/vso_offices.json (every office, paginated past the 1,000-row cap)
and data/vso_ratings.json ({office_id: {"avg": 4.5, "n": 2}}, stars and counts
only: review comments never leave the app).

Needs the public anon key in the environment, never in the repo:
    SUPABASE_ANON_KEY=... python3 fetch_vso.py
"""
import json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "https://fmgyxwxaxqxtbpwqehab.supabase.co/rest/v1"
KEY = os.environ.get("SUPABASE_ANON_KEY")
if not KEY:
    sys.exit("Set SUPABASE_ANON_KEY")

COLS = ("id,office_name,organization,organization_type,city,state_code,zip,county,"
        "phone,toll_free_phone,website,va_accredited,address,latitude,longitude")

def get(path):
    req = urllib.request.Request(f"{URL}/{path}", headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

offices, page = [], 1000
while True:
    rows = get(f"vso_offices?select={COLS}&order=id&limit={page}&offset={len(offices)}")
    offices += rows
    if len(rows) < page:
        break

stats = get("vso_office_review_stats?select=vso_office_id,review_count,avg_rating")
ratings = {str(s["vso_office_id"]): {"avg": round(float(s["avg_rating"]), 1), "n": int(s["review_count"])}
           for s in stats if s.get("review_count")}

json.dump(offices, open(os.path.join(HERE, "data", "vso_offices.json"), "w"), ensure_ascii=False)
json.dump(ratings, open(os.path.join(HERE, "data", "vso_ratings.json"), "w"), ensure_ascii=False)
print(f"{len(offices)} offices, {len(ratings)} rated offices")
