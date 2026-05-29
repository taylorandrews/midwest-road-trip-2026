"""
Fill lat/lon on courses_2026.json by geocoding each course with OpenStreetMap's
Nominatim service. Standard library only.

Nominatim usage policy: max 1 request/second, descriptive User-Agent required.
This script honors both. ~186 courses => ~3-4 minutes.

Usage:
    python3 geocode_courses.py            # geocode rows with empty lat/lon
    python3 geocode_courses.py --force    # re-geocode everything
    python3 geocode_courses.py --trip     # only on_trip_route courses

Re-run is safe: already-geocoded rows are skipped unless --force.
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request

from build_dataset import write_outputs  # keeps JSON + CSV in sync

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "courses_2026.json")
NOMINATIM = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "sabbatical-disc-golf-map/1.0 (personal project)"}


def geocode(query):
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    req = urllib.request.Request(f"{NOMINATIM}?{params}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        results = json.load(r)
    if results:
        return float(results[0]["lat"]), float(results[0]["lon"])
    return None


def query_variants(rec):
    """Most specific first; fall back to city/state/country."""
    loc = ", ".join(p for p in (rec["city"], rec["state_region"],
                                rec["country"]) if p)
    return [f"{rec['course_name']}, {loc}", loc]


def main():
    force = "--force" in sys.argv
    trip_only = "--trip" in sys.argv

    with open(DATA) as f:
        courses = json.load(f)

    todo = [c for c in courses
            if (force or c["lat"] == "")
            and (not trip_only or c["on_trip_route"])]
    print(f"Geocoding {len(todo)} of {len(courses)} courses "
          f"(~1/sec, be patient)...")

    hits = misses = 0
    for i, rec in enumerate(todo, 1):
        result = None
        for q in query_variants(rec):
            try:
                result = geocode(q)
            except Exception as e:
                print(f"  ! {rec['course_name']}: {e}")
            time.sleep(1.1)  # rate limit
            if result:
                break
        if result:
            rec["lat"], rec["lon"] = round(result[0], 6), round(result[1], 6)
            hits += 1
        else:
            misses += 1
            print(f"  ? no match: {rec['course_name']} ({rec['city']})")
        if i % 20 == 0:
            print(f"  ...{i}/{len(todo)}")
            write_outputs(courses)            # checkpoint (JSON + CSV)

    write_outputs(courses)
    print(f"Done. located={hits} missed={misses}. "
          f"lat/lon written to both courses_2026.json and .csv.")


if __name__ == "__main__":
    main()
