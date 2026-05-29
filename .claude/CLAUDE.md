# Sabbatical 2026 — Project Context

Living notes about this project for Claude (and future-me). Add to this over time
as the work grows. Keep it factual and current — delete what's no longer true.

## What this is

Planning + creative tooling for a **2026 disc golf road trip sabbatical**
(Aug 8 – Sep 7, 2026). A day-by-day template lives in the Apple Notes note
"Sabbatical 2026" (Trips folder).

**Route is a loop out of Colorado:**
CO → KS → MO → IL → IN → Detroit, MI → back through IA → NE → CO.
(The original map was a one-way Buena Vista → Kansas City; that's now just the
first leg.)

The coding side has two threads:
1. **Trip logistics** — mapping the route and stops.
2. **Digital art** — the route map is meant to grow into a visual art piece
   about the road trip.

## Folder layout

```
road-trip-map/   # Leaflet map of the active driving route (KC→Detroit leg)
course-map/      # Leaflet map of all courses (basket pins, no route) for research
data/            # structured datasets for mapping
  course-rankings/   # UDisc 2026 rankings, deduped (world/US/route-state), geocoded
trip-plan/       # itinerary.md — canonical schedule (transferred from Apple Notes)
assets/          # working materials for the visual (exports/palettes/reference)
.claude/         # this file
README.md        # top-level overview tying it together
```

## Subprojects

### `road-trip-map/`
Interactive map of the active driving route. Now set to the **KC → Detroit disc
golf leg** (Aug 17–25): 9 stops through chosen top courses, ~1,254 mi / ~25 hr,
ending at Kensington Toboggan (Worlds venue). `stops.json` carries each course's
ranks + camping notes. (Earlier draft was a one-way Buena Vista → Kansas City.)

- **Stack:** Leaflet (no API key) + the public OSRM routing API for real
  driving geometry. Python **standard library only** — `build_route.py` needs
  no `pip install`, just an internet connection to reach OSRM.
- **Lineage:** same GPX/GeoJSON backbone as the sibling `sloans-lake` project,
  but Leaflet instead of gmplot/Google Maps — chosen for no-key setup and full
  CSS control for the eventual art piece.
- **Data flow:** `stops.json` (source of truth) → `build_route.py` →
  `route.geojson` + `route.gpx` → `index.html` renders it.
- **Run it:** `cd road-trip-map && python3 -m http.server 8000`, open
  <http://localhost:8000>. Opening `index.html` via `file://` won't work
  (browsers block `fetch()` of local files).
- **Edit loop:** change `stops.json` → `python3 build_route.py` → reload browser
  (no server restart needed).
- See `road-trip-map/README.md` for full details and art-direction notes.

### `data/course-rankings/`
Structured UDisc **2026** course-ranking dataset, built for mapping.

- **Stack:** stdlib-only Python. `build_dataset.py` holds the source lists and
  merges them into one course-centric table; `geocode_courses.py` fills lat/lon
  via OSM Nominatim (1 req/sec).
- **Contents:** 186 unique courses deduped across World Top 100, US Top 100, and
  per-state Top 10s for the 8 route states (CO/KS/MO/IL/IN/MI/IA/NE). Fields
  include `world_rank`/`us_rank`/`state_rank`, `on_trip_route`, lat/lon.
- **Outputs:** `courses_2026.json` (primary) + `courses_2026.csv`.
- `build_dataset.py` **preserves** existing lat/lon/udisc_url on rebuild, so
  geocoding isn't lost. See its README for schema + how to add states/countries.
- Trip-route headliner: Championship Course at Eagles Crossing (New Truxton, MO)
  = World #9 / US #4 / Missouri #1.

## Status / decisions so far

- **Overall trip = loop** (CO→KS→MO→IL→IN→MI→IA→NE→CO), Aug 8 – Sep 7. Full
  schedule lives in `trip-plan/itinerary.md` (transferred from Apple Notes; that
  note can be archived). Worlds (spectating) is Aug 26–30 near Detroit.
- **Active mapped route = KC→Detroit disc golf leg** (Aug 17–25). Per-state
  ranking lists were pulled for the 8 route states only (intentional scope).
- Course stops chosen for the leg: Harmony Bends, Eagles Crossing (play both
  courses), BC3, Idlewild, a 2-night Lake Michigan camp (Rogers Lakewood /
  Lemon Lake, near Indiana Dunes), Arvesta, Flip City, Kensington Toboggan.
- Map kept **static** for now (no draw-on-load animation) until the art
  direction is clearer.
- Course dataset **geocoded** (185/186 located; only "Lille Leland", Norway
  missed). lat/lon live in `courses_2026.json` + `.csv`.
- **`course-map/`** added: Leaflet map of all geocoded courses, basket-icon
  markers, hover tooltips with name/location/ranks, filter buttons (All / route
  states / World 100 / US 100). No route lines — it's for trip research. Reads
  `../data/course-rankings/courses_2026.json`, so **serve from the sabbatical
  root**: `python3 -m http.server 8000` → <http://localhost:8000/course-map/>.

## Conventions

- Personal-use tool first; pragmatic, data-driven (matches Taylor's usual style).
- stdlib-only Python where possible; no pip installs required to run things.
- Generated files (`route.geojson`, `route.gpx`, `courses_2026.*`) are committed
  for convenience but are reproducible from their source + build script.
- `data/` = source-of-truth datasets; `assets/` = outputs/references for the
  visual (keep them out of the code folders).

## Ideas / backlog

- Geocode the course dataset, then add chosen courses to `stops.json` as stops.
- Update `road-trip-map` to the full loop route (currently just leg 1).
- Animated "draw the route" reveal for the art version.
- Per-day route segmentation/coloring (`stops.json` already carries `day`).
- Print/SVG export for large-format art.
- Possible future: overlay the course-ranking points on the route map.
