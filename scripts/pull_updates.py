#!/usr/bin/env python3
"""Canonize live trip updates: fold the portal's KV overlay into git.

Fetches pending updates from the portal (/api/trip/updates), applies the
structured patches to site/data/schedule.json, appends unparsed notes to
PLANNING.md's Brain dump, archives everything to scripts/applied-updates.log,
and clears the overlay. Then commit + push (scripts/ship.sh does it in one go).

Config (env vars, or scripts/.sync-config.json with the same keys):
  PORTAL_URL        e.g. https://portal-xyz.pages.dev
  PORTAL_SYNC_TOKEN the SYNC_TOKEN you set in the Pages dashboard

Usage:
  python3 scripts/pull_updates.py            # apply + clear overlay
  python3 scripts/pull_updates.py --dry-run  # show what would happen
  python3 scripts/pull_updates.py --keep     # apply but leave overlay in place
"""
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "site" / "data" / "schedule.json"
PLANNING = ROOT / "PLANNING.md"
ARCHIVE = ROOT / "scripts" / "applied-updates.log"


def config():
    cfg = {}
    f = ROOT / "scripts" / ".sync-config.json"
    if f.exists():
        cfg = json.loads(f.read_text())
    url = os.environ.get("PORTAL_URL", cfg.get("PORTAL_URL", "")).rstrip("/")
    token = os.environ.get("PORTAL_SYNC_TOKEN", cfg.get("PORTAL_SYNC_TOKEN", ""))
    if not url or not token:
        sys.exit("Set PORTAL_URL and PORTAL_SYNC_TOKEN (env or scripts/.sync-config.json)")
    return url, token


def call(url, token, method="GET"):
    req = urllib.request.Request(url, method=method,
                                 headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def apply_ops(schedule, updates):
    """Mirror of portal functions/lib/trip.js applyUpdates, minus _live flags."""
    unplaced = []
    by_date = {d["date"]: d for d in schedule["days"]}
    for u in updates:
        ops = (u.get("patch") or {}).get("ops")
        if not ops:
            unplaced.append(u)
            continue
        placed_any = False
        for op in ops:
            day = by_date.get(op.get("date"))
            if not day:
                unplaced.append({**u, "text": op.get("note") or u["text"]})
                continue
            for k, v in (op.get("set") or {}).items():
                if v is None:
                    day.pop(k, None)
                else:
                    day[k] = v
            if op.get("note"):
                day.setdefault("notes", []).append(op["note"])
            placed_any = True
        if placed_any:
            print(f"  ✓ {u.get('patch', {}).get('summary') or u['text'][:60]}")
    return unplaced


def main():
    dry = "--dry-run" in sys.argv
    keep = "--keep" in sys.argv
    url, token = config()

    data = call(f"{url}/api/trip/updates", token)
    updates = data.get("updates", [])
    if not updates:
        print("No pending updates — overlay is empty.")
        return

    print(f"{len(updates)} update(s) pending:")
    schedule = json.loads(SCHEDULE.read_text())
    unplaced = apply_ops(schedule, updates)

    if dry:
        print(f"(dry run) would update schedule.json; {len(unplaced)} note(s) → PLANNING.md")
        return

    SCHEDULE.write_text(json.dumps(schedule, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {SCHEDULE.relative_to(ROOT)}")

    if unplaced:
        text = PLANNING.read_text()
        marker = "## Brain dump"
        lines = "".join(
            f"- ({date.today().isoformat()} via phone) {u['text']}\n" for u in unplaced)
        if marker in text:
            head, _, tail = text.partition(marker)
            # insert right after the marker line (skip its trailing newline + italics line)
            tail_lines = tail.splitlines(keepends=True)
            insert_at = 1
            if len(tail_lines) > 1 and tail_lines[1].startswith("_"):
                insert_at = 2
            tail = "".join(tail_lines[:insert_at]) + "\n" + lines + "".join(tail_lines[insert_at:])
            text = head + marker + tail
        else:
            text += f"\n{marker}\n\n{lines}"
        PLANNING.write_text(text)
        print(f"Appended {len(unplaced)} note(s) to PLANNING.md brain dump")

    with ARCHIVE.open("a") as f:
        for u in updates:
            f.write(json.dumps(u, ensure_ascii=False) + "\n")

    if not keep:
        call(f"{url}/api/trip/updates", token, method="DELETE")
        print("Cleared the live overlay.")
    print("\nNext: review the diff, then ./scripts/ship.sh \"fold in phone updates\"")


if __name__ == "__main__":
    main()
