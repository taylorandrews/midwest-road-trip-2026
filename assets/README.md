# Assets — Disc Golf Road Trip Visual

Working materials for the digital-art visual. Keep raw inputs and exported
outputs here so the code folders (`road-trip-map/`, `data/`) stay clean.

## Folders

| Folder | What goes here |
|--------|----------------|
| `palettes/` | Color palettes, gradient definitions, style tokens for the visual. |
| `exports/` | Rendered outputs — map screenshots, SVG/PNG exports, print-res images. Name with date + scope, e.g. `route-co-mo-detroit-20260601.png`. |
| `reference/` | Inspiration, mood boards, reference maps, sketches. |

## Conventions

- **Generated, not source.** Most things here are outputs or gathered references
  — the source of truth lives in `../data/` (course rankings) and
  `../road-trip-map/` (route + map). Anything here should be reproducible or
  re-downloadable.
- Date-stamp exports (`YYYYMMDD`) so versions of the visual stay ordered.
- Big binaries (video, hi-res renders) are fine here but consider whether they
  belong in git if this folder is ever committed.

## Current state

Empty scaffolding for now — the only "asset" so far is the live map in
`../road-trip-map/`. First exports will likely be screenshots of that map once
the art direction (palette, animation) is decided.
