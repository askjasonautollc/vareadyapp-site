# _generators — VA Ready site page generators

DB-driven static-page generators for the SEO sections of vareadyapp.com.
Versioned in git but **excluded from the Vercel deploy** (see `/.vercelignore`),
so nothing here is served publicly.

Each script writes its HTML into the site root (one level up) and merges its URLs
into `../sitemap.xml`. Paths are resolved relative to this folder, so they run
from anywhere after a clone — no hardcoded `/tmp` or absolute paths.

## Scripts

| Script | Builds | Data source |
|---|---|---|
| `gen_guides.py` | 50 filing/claim guide pages → `../guides/*.html` + `../guides.html` | `data/guides.json` |
| `gen_conditions.py` | 20 top-condition pages → `../conditions/*.html` + `../conditions.html` | `data/conditions.json`, `data/studies.json` |
| `gen_states.py` | 20 state-benefit pages → `../states/*.html` + `../states.html` | `data/benefits.json` |
| `gen_founders.py` | `../founders.html` | none (uses `../img/jason_*.jpg`, `wocs_grad.jpg`) |
| `gen_community.py` | `../community.html` (In the Community) | none (uses `../img/community-liberty-county-jumbotron-*`) |

## How to run

```bash
cd _generators
python3 gen_guides.py        # run FIRST — it rewrites sitemap.xml from scratch
python3 gen_conditions.py    # these merge their URLs into the sitemap
python3 gen_states.py
python3 gen_founders.py
python3 gen_community.py
```

Run `gen_guides.py` first: it regenerates `../sitemap.xml` from the core pages +
guides, and the others append their URLs to it. Running all four reproduces the
current live site exactly (verified byte-for-byte).

The shared CSS, `<nav>`, `<footer>`, and the Vercel analytics + `/track.js`
snippets live as constants inside `gen_guides.py`; `gen_conditions.py`,
`gen_states.py`, and `gen_founders.py` read the CSS from it, so edit the look in
one place (`gen_guides.py`) and re-run all four.

## Refreshing the data

The `data/*.json` files are snapshots pulled from Supabase via the REST API
(anon key). To refresh (e.g., the January state-benefits re-sweep), re-fetch the
relevant table to the matching JSON and re-run that generator. Example:

```bash
KEY="<supabase anon key>"; URL="https://fmgyxwxaxqxtbpwqehab.supabase.co/rest/v1"
curl -s "$URL/state_benefits?state_code=in.(CA,TX,FL,...)&select=*" \
  -H "apikey: $KEY" -H "Authorization: Bearer $KEY" -o data/benefits.json
```

(See CHANGELOG entries dated 2026-06-07/08/09 for the original build details.)

## Adding a community entry (In the Community feed)

`gen_community.py` builds `../community.html` and the homepage teaser from
`data/community.json`. To add an entry:

1. Save the photo as `data/community/photos/<id>.jpg` (jpg, png or heic). This
   folder is gitignored so originals, which can carry GPS or bystanders, never
   reach the public repo. The script crops to 16:10 and strips EXIF.
2. Add an object to `data/community.json`. File order does not matter, the feed
   sorts newest first by `date`:

```json
{
  "id": "short-lowercase-slug-2026",
  "date": "2026-10-04",
  "when": "October 2026",
  "headline": "What happened, in a few words",
  "location": "Place, City, GA",
  "body": ["First paragraph.", "Optional second paragraph."],
  "photo_alt": "Plain description of what is in the photo",
  "photo_focus": 0.5,
  "teaser": "Optional one-liner for the homepage card",
  "link": { "url": "https://partner.example/", "label": "Partner name" }
}
```

   For more than one contact, use `links` instead of `link`; they render as buttons:

```json
"links": [
  { "url": "https://www.facebook.com/vareadyapp", "label": "Message us on Facebook" },
  { "url": "mailto:support@vareadyapp.com", "label": "Email support@vareadyapp.com" }
]
```

   Required: `id`, `date`, `headline`, `body`, `photo_alt`. Everything else is
   optional. `photo_focus` moves the crop from 0 (keep the top) to 1 (keep the
   bottom). An optional `sponsored` object (schema.org, e.g. a SportsTeam)
   marks the thing we sponsor in the page's structured data.
3. `python3 gen_community.py`, check `community.html` locally, commit, push.

The homepage shows the newest 3 entries between the `COMMUNITY:START` and
`COMMUNITY:END` markers in `index.html`. Do not hand-edit that block.
