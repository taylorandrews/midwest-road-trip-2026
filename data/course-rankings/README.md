# Disc Golf Course Rankings — 2026 (UDisc)

Structured dataset of UDisc's **2026** best-disc-golf-course rankings, built for
mapping the sabbatical road trip and feeding the digital-art visual.

## Files

| File | What it is |
|------|------------|
| `build_dataset.py` | Source lists (embedded) + merge logic. Run to (re)generate the dataset. |
| `geocode_courses.py` | Fills `lat`/`lon` via OpenStreetMap Nominatim. Run after building. |
| `courses_2026.json` | Generated — list of course records. Primary file. |
| `courses_2026.csv` | Generated — same data, flat. |
| `sources.md` | The exact UDisc pages each list came from. |

## What's in it

One row per **unique course**, deduped across every list it appears on:

- **World Top 100** → `world_rank`
- **US Top 100** → `us_rank`
- **Per-state Top 10s** for the road-trip route states → `state_rank`
  (Colorado, Kansas, Missouri, Illinois, Indiana, Michigan, Iowa, Nebraska)

Current totals: **186 unique courses** — 80 on the trip route, 29 international.

A course can carry several ranks at once. Example: *Beaver Ranch* is world #32,
US #18, and Colorado #1 — one row, three rank columns filled.

## Schema

| Field | Notes |
|-------|-------|
| `course_name` | Canonical name (prefers the US/world list spelling). |
| `city` | City/town. |
| `state_region` | US state, Canadian province, or foreign region. |
| `country` | `USA`, `Canada`, `Sweden`, … |
| `world_rank` | 1–100 if on the World list, else `""`. |
| `us_rank` | 1–100 if on the US list, else `""`. |
| `state_rank` | 1–10 if on a pulled state list, else `""`. |
| `scopes` | Which lists it appears on, e.g. `us;world;state:Colorado`. |
| `on_trip_route` | `True` if `state_region` is one of the 8 trip states. |
| `lat`, `lon` | Empty until `geocode_courses.py` is run. |
| `udisc_url` | Empty — slot for a future link back to UDisc. |
| `year` | `2026`. |

## Regenerate / extend

```bash
python3 build_dataset.py     # rebuild courses_2026.{json,csv}
python3 geocode_courses.py   # fill lat/lon (~3-4 min, 1 req/sec to Nominatim)
#   python3 geocode_courses.py --trip    # just the trip-route courses, faster
```

Re-running `build_dataset.py` **preserves** any `lat`/`lon`/`udisc_url` already
in `courses_2026.json`, so geocoding isn't lost on a rebuild.

**To add more states** (e.g. if the route changes): grab the list from
`https://udisc.com/best-disc-golf-courses/united-states/<state-slug>`, add a
block to the `STATES` dict in `build_dataset.py`, add the state to `TRIP_STATES`,
and rebuild. To add **countries**, the same pattern applies under
`/best-disc-golf-courses/<country-slug>` (a `COUNTRIES` dict would mirror
`STATES`).

## Provenance & caveats

- Source: UDisc 2026 rankings (6.5M+ ratings). See `sources.md` for URLs.
- Rankings are a snapshot pulled in **May 2026**; UDisc updates annually.
- Per-state lists here are **Top 10 only** and **only for the 8 route states** —
  this is intentional scope, not the full UDisc state lists.
- Coordinates come from Nominatim geocoding of name + city + state, so they
  locate the **course's town**, not necessarily the exact tee pad. Spot-check
  before using for precise navigation.
