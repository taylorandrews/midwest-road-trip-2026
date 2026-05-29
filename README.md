# Sabbatical 2026 — Disc Golf Road Trip

Planning + creative tooling for a 2026 disc golf road trip sabbatical
(**Aug 8 – Sep 7, 2026**). The trip is a loop out of Colorado:

```
Colorado → Kansas → Missouri → Illinois → Indiana → Detroit, MI
        → (back through) Iowa → Nebraska → Colorado
```

Two threads: **trip logistics** (mapping the route + stops) and a **digital-art
visual** built from the route and disc golf course data.

## Layout

```
sabbatical/
├── road-trip-map/        # Interactive Leaflet map of the driving route (the app)
├── data/                 # Structured datasets for mapping
│   └── course-rankings/  # UDisc 2026 best-course rankings (world/US/route states)
├── assets/               # Working materials for the art visual (exports, palettes, refs)
└── .claude/              # Project context for Claude (living notes)
```

## The pieces

- **`road-trip-map/`** — `stops.json` → `build_route.py` → `route.geojson`/`.gpx`
  → `index.html` (dark Leaflet map, real driving geometry via OSRM, no API key).
  See its README to run it.
- **`data/course-rankings/`** — 186 unique courses deduped across UDisc's 2026
  World Top 100, US Top 100, and per-state Top 10s for the 8 route states. Has
  a build script and a geocoder. See its README for schema + how to extend.
- **`assets/`** — outputs and references for the visual; kept separate from code.

## How they connect

The course dataset (`data/course-rankings/`) is the candidate set of disc golf
stops. Geocode it, pick the courses to actually play, and add them to
`road-trip-map/stops.json` to reroute the map through them. The styled map then
becomes the basis for exports in `assets/`.
