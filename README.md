# Sabbatical 2026 — Disc Golf Road Trip

Planning + creative tooling for a 2026 disc golf road trip sabbatical
(**Aug 8 – Sep 7, 2026**). The trip is a loop out of Colorado:

```
Colorado → Kansas → Missouri → Illinois → Indiana → Detroit, MI
        → (back through) Iowa → Nebraska → Colorado
```

Two threads: **trip logistics** (mapping the route + stops) and a **digital-art
visual** built from the route and disc golf course data.

## The site

Everything served lives in **`site/`** as one self-contained bundle (so the
whole folder copies into the portal as a unit). Two surfaces, one data source:

- **`site/index.html`** — the **mobile-first trip guide** (portal entry). A
  Schedule tab (each day: route, courses, where you sleep with a 📍 Directions
  link, tee times) and a Map tab (drive lines, course baskets, campsite tents).
- **`site/plan.html`** — the **laptop planning page**. Read-only established info
  per day plus a notes box. Notes **autosave to `site/data/planning-notes.json`**
  so they live in the repo (Claude reads them and folds the durable bits into
  `schedule.json`). Autosave needs the local server below.

**To plan: double-click `plan.command`** (or run `python3 serve.py`). It starts
the local server and opens the planning page in your browser. Leave it running
while you plan; Ctrl+C to stop. The portal hosts `site/` statically — this
write-back server only runs on the laptop, which is where planning happens.

```bash
python3 serve.py            # opens http://localhost:8000/plan.html (planning)
                            #        http://localhost:8000/         (trip guide)
```

## The workflow

1. **Plan on the laptop** — double-click `plan.command`, type free-form ideas
   into the scratchpad / per-day boxes. Everything autosaves to
   `site/data/planning-notes.json`.
2. **Hand Claude the rest in the terminal** — paste emails/screenshots and say
   "fold in my planning notes." Claude reads `planning-notes.json` + your
   materials and promotes the settled stuff into `site/data/schedule.json`.
3. **See it on your phone** — the guide renders the current trip from that one
   data source. No copies, never stale.

## Data (source of truth)

```
site/data/
├── schedule.json          # the trip: days, route, courses, stays, tee times (Claude maintains)
├── segments.json          # per-day driving waypoints (courses + booked campgrounds)
├── route_segments.geojson # generated — drive geometry + markers (build_routes.py)
├── planning-notes.json    # YOUR typed notes (written by serve.py, read by Claude)
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
│   ├── plan.html         # Laptop planning page (autosaves notes)
│   ├── leaflet.css/.js   # bundled map lib (offline-friendly)
│   └── data/             # source of truth (see above)
├── serve.py              # dev server: serves site/ + notes write-back
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
