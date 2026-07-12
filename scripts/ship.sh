#!/usr/bin/env bash
# One-command deploy: commit sabbatical → sync portal → commit → push both.
# No PRs, no branch dance. Usage:
#   ./scripts/ship.sh "message"            # commit + sync + push
#   ./scripts/ship.sh --routes "message"   # also rebuild drive geometry first
set -euo pipefail

SAB="$(cd "$(dirname "$0")/.." && pwd)"
PORTAL="$SAB/../portal"

if [[ "${1:-}" == "--routes" ]]; then
  shift
  echo "▸ rebuilding route geometry…"
  (cd "$SAB" && python3 site/data/build_routes.py)
fi

MSG="${1:-trip update}"

echo "▸ sabbatical: commit + push"
cd "$SAB"
git add -A
git diff --cached --quiet || git commit -m "$MSG"
git push origin HEAD:main

echo "▸ portal: sync + commit + push"
cd "$PORTAL"
npm run --silent build
git add -A
git diff --cached --quiet || git commit -m "portal sync: $MSG"
git push

echo "✓ shipped — Cloudflare will auto-deploy in ~a minute."
