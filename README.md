# Sabbatical 2026 — Disc Golf Road Trip

Planning + creative tooling for a 2026 disc golf road trip sabbatical
(**Aug 8 – Sep 7, 2026**). The trip is a loop out of Colorado:

```
Colorado → Kansas → Missouri → Illinois → Indiana → Detroit, MI
        → (back through) Iowa → Nebraska → Colorado
```

Two threads: **trip logistics** (mapping the route + stops) and a **digital-art
visual** built from the route and disc golf course data.

## The trip guide

The phone-facing guide lives in **`site/`** as one self-contained bundle (the
whole folder copies into the portal as a unit). `site/index.html` is the
mobile-first guide: a Schedule tab (each day: route, courses, where you sleep
with a 📍 Directions link, tee times) and a Map tab (drive lines, course baskets,
campsite tents). It reads one data source, `site/data/`.

To view it locally (the guide uses `fetch`, so it needs a static server, not
`file://`):

```bash
cd site && python3 -m http.server 8000   # then open http://localhost:8000/
```

## The planning workflow

Free-form notes live in **`PLANNING.md`** (repo root) — a plain text file. There
is no app or server for planning; it's just a file.

1. **Plan in your editor** — open `PLANNING.md`, type anything (ideas, to-dos,
   per-day notes). Save. It's version-controlled, so nothing gets lost.
2. **Hand Claude the rest in the terminal** — paste emails/screenshots and say
   "fold in my planning notes." Claude reads `PLANNING.md` + your materials and
   promotes the settled stuff into `site/data/schedule.json`.
3. **See it on your phone** — the guide renders the current trip from that one
   data source. No copies, never stale.

## Data (source of truth)

```
site/data/
├── schedule.json          # the trip: days, route, courses, stays, tee times (Claude maintains)
├── segments.json          # per-day driving waypoints (courses + booked campgrounds)
├── route_segments.geojson # generated — drive geometry + markers (build_routes.py)
└── itinerary.md           # human-readable itinerary
```

Regenerate routes after editing `segments.json` (real driving geometry via OSRM,
no API key):

```bash
python3 site/data/build_routes.py
```

## Layout

```
sabbatical/
├── site/                 # The web bundle (served + shipped to the portal)
│   ├── index.html        # Mobile-first trip guide
│   ├── leaflet.css/.js   # bundled map lib (offline-friendly)
│   └── data/             # source of truth (see above)
├── PLANNING.md           # free-form planning scratchpad (you type, Claude reads)
├── portal.json           # portal manifest → site/index.html
├── course-map/           # Leaflet map of all courses (basket pins) for research
├── data/course-rankings/ # UDisc 2026 best-course rankings (world/US/route states)
├── assets/               # Working materials for the art visual
└── .claude/              # Project context for Claude (living notes)
```

## How it connects

`data/course-rankings/` (186 courses deduped across UDisc's 2026 World/US/state
lists) is the candidate set of disc golf stops. Pick the ones to play and add
them to `site/data/segments.json` (+ a `course` on the day in `schedule.json`),
then re-run `build_routes.py`. The styled map can still feed exports in `assets/`.
