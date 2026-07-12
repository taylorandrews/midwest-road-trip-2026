# Live trip updates — design & setup

The old loop was: edit `PLANNING.md` / paste emails → Claude edits
`schedule.json` → PR → manual merge → portal `npm run build` → commit → push.
Fine in June; useless from a campground in Michigan.

The new loop splits **capture** from **canonize**:

```
phone ✏️ ──POST /api/trip/update──▶ KV overlay ──▶ /api/trip/schedule (merged, live)
                                        │
   Mac, whenever ◀── pull_updates.py ───┘   folds overlay → schedule.json + PLANNING.md
                     ship.sh                commits main + syncs portal + pushes
```

## Capture (phone, seconds)

The guide (`site/index.html`) shows an ✏️ button when it's served from the
portal. Type anything: *"staying in Denver the 15th"*, *"playing Birdland Wed
instead of Eagles Crossing"*. It POSTs to `/api/trip/update` (behind the
portal's Face ID session):

1. The raw note is stored in KV **first** — a thought is never lost.
2. If `ANTHROPIC_API_KEY` is set on the Pages project, Claude (Haiku) parses
   the note against the *current merged schedule* into a small patch:
   `{summary, ops:[{date, set:{…}, note}]}`. Parsed patches take effect
   immediately — the day card gets a `LIVE` badge.
3. No key / can't parse confidently → the note shows up as a 📌 sticky on the
   day (or a "pending updates" card up top). Still instant, just unstructured.

The updates sheet lists everything in the overlay; ✕ removes a bad one.

## Serve (merged, no build)

`GET /api/trip/schedule` = committed `schedule.json` (fetched from the
deployed static assets) + overlay patches applied in order. The guide prefers
the API and falls back to the static file, so `python3 -m http.server` local
dev still works, and if the API ever breaks the page degrades to the committed
plan.

## Canonize (Mac, occasionally)

```bash
python3 scripts/pull_updates.py    # overlay → schedule.json + PLANNING.md, then clears it
./scripts/ship.sh "fold in phone updates"   # commit main + portal sync + push, both repos
```

`pull_updates.py` mirrors the server merge, appends unplaced notes to the
Brain dump in `PLANNING.md`, and archives every processed update to
`scripts/applied-updates.log` (gitignored) before clearing KV. Git remains the
long-term source of truth; it's just no longer the bottleneck. **No PRs** —
`ship.sh` commits straight to `main`.

Note: the first `pull_updates.py` run rewrites `schedule.json` with
`json.dumps(indent=2)`, so the hand-aligned formatting becomes standard
two-space indent in that one diff.

## One-time setup (Cloudflare Pages dashboard)

Settings → Environment variables (Production):

| var | required | value |
|---|---|---|
| `SYNC_TOKEN` | for `pull_updates.py` | any long random string (`openssl rand -hex 24`) |
| `ANTHROPIC_API_KEY` | for live parsing | console.anthropic.com key |
| `TRIP_MODEL` | no | defaults to `claude-haiku-4-5` |

Locally: `scripts/.sync-config.json` (gitignored) →
`{"PORTAL_URL": "https://<your-portal>.pages.dev", "PORTAL_SYNC_TOKEN": "<same token>"}`

Then push both repos once so the new Functions deploy.

## Files

- portal `functions/api/trip/{schedule,update,updates}.js` + `functions/lib/trip.js`
- portal `functions/_middleware.js` — `/api/trip/updates` exempted (it checks
  session **or** `Authorization: Bearer $SYNC_TOKEN` itself)
- sabbatical `site/index.html` — API-first loading, ✏️ sheet, LIVE badges, 📌 stickies
- sabbatical `scripts/pull_updates.py`, `scripts/ship.sh`

## Later ideas

- **Voice**: an iOS Shortcut ("Hey Siri, trip update") that POSTs dictated
  text to `/api/trip/update` with a stored token — same pipeline, zero typing.
- **Email ingestion**: forward a reservation email to a worker address; the
  same parse step files it as a booked stay + drops the PDF in `reservations/`.
- **Scheduled canonize**: a Cowork scheduled task that runs `pull_updates.py`
  + `ship.sh` weekly during the trip, so git never drifts far.
- **Course intelligence**: the parse prompt already knows the schedule; give
  it `data/course-rankings/` too and "find me a course near Wednesday's drive"
  becomes an update that answers back.
