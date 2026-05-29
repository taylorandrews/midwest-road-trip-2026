"""
Build the structured disc golf course-rankings dataset from UDisc's 2026 lists.

Source lists (all 2026, https://udisc.com/best-disc-golf-courses):
  - WORLD : 100 Best Disc Golf Courses in the World
  - US     : 100 Best Disc Golf Courses in the United States
  - STATES : per-state Top 10s for the road-trip route states only
             (CO, KS, MO, IL, IN, MI, IA, NE) per the loop:
             CO -> KS -> MO -> IL -> IN -> Detroit MI -> IA -> NE -> CO

Merges them into ONE course-centric table (one row per unique course, deduped
across lists by a normalized-name key) and writes:
  - courses_2026.json  (list of records)
  - courses_2026.csv   (same, flat)

lat/lon are left blank on purpose -- run geocode_courses.py afterward to fill
them for mapping. Standard library only.
"""

import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
YEAR = 2026

TRIP_STATES = ["Colorado", "Kansas", "Missouri", "Illinois",
               "Indiana", "Michigan", "Iowa", "Nebraska"]

# --- WORLD Top 100: (rank, name, "city, [state,] country") --------------------
WORLD = [
    (1, "Ale Disc Golf Center: White Course", "Nol, Sweden"),
    (2, "Krokhol Disc Golf Course", "Siggerud, Norway"),
    (3, "Ale Disc Golf Center: Yellow Course", "Nol, Sweden"),
    (4, "KIPPIS Pro DiscGolfPark @ kippis.org", "Heinola, Finland"),
    (5, "Maple Hill", "Leicester, Massachusetts, USA"),
    (6, "Brewster Ridge Disc Golf Course", "Cambridge, Vermont, USA"),
    (7, "Lundbyparken", "Enköping, Sweden"),
    (8, "Fox Run Meadows", "Cambridge, Vermont, USA"),
    (9, "Championship Course at Eagles Crossing", "New Truxton, Missouri, USA"),
    (10, "Uspastorp DiscGolfPark", "Nol, Sweden"),
    (11, "Åkeslund DiscGolfCenter", "Hörby, Sweden"),
    (12, "Ymergårdens Discgolfcenter: Gold Course", "Brämhult, Sweden"),
    (13, "Karidalen FrisbeeGolfPark", "Lena, Norway"),
    (14, "Blue Ribbon Pines", "East Bethel, Minnesota, USA"),
    (15, "The Diavolo DGC at New Hope Park", "Cary, North Carolina, USA"),
    (16, "Glåmos Diskgolfbane", "Glåmos, Norway"),
    (17, "Persimmon Ridge DGC", "Greenbrier, Arkansas, USA"),
    (18, "Mile Marker 63", "East Brookfield, Massachusetts, USA"),
    (19, "The Canyons at Dellwood Park", "Lockport, Illinois, USA"),
    (20, "Caliber DGC", "Sandpoint, Idaho, USA"),
    (21, "Äppelgården i Båstad", "Båstad, Sweden"),
    (22, "Idlewild", "Burlington, Kentucky, USA"),
    (23, "Järva Discgolf Park", "Kista, Sweden"),
    (24, "Häfla Bruks DiscGolfPark", "Rejmyre, Sweden"),
    (25, "Harmony Bends", "Columbia, Missouri, USA"),
    (26, "Hobb's Farm Disc Golf", "Carrollton, Georgia, USA"),
    (27, "Øverås Diskgolfpark", "Øverås, Norway"),
    (28, "Sandy Point Disc Golf Ranch", "Lac du Flambeau, Wisconsin, USA"),
    (29, "Northwood Park: Black", "Morton, Illinois, USA"),
    (30, "Faylor Lake DiscGolfPark", "Beaver Springs, Pennsylvania, USA"),
    (31, "Blue Goose", "Frankfort, Kentucky, USA"),
    (32, "Beaver Ranch Disc Golf Course", "Conifer, Colorado, USA"),
    (33, "Bryant Lake Park", "Eden Prairie, Minnesota, USA"),
    (34, "Lille Leland", "Sør-audnedal, Norway"),
    (35, "Flip City Disc Golf Park", "Shelby, Michigan, USA"),
    (36, "Meadowbrook Orchards", "Sterling, Massachusetts, USA"),
    (37, "Sabattus Disc Golf: Hawk", "Sabattus, Maine, USA"),
    (38, "Neatman Creek", "Germanton, North Carolina, USA"),
    (39, "Hillcrest Farm Disc Golf", "Bonshaw, PE, Canada"),
    (40, "Arvika Discgolf", "Åmotfors, Sweden"),
    (41, "New London Tech DGC", "Forest, Virginia, USA"),
    (42, "Echo Valley at Hoffmann Reserve", "Waynesville, Ohio, USA"),
    (43, "Rollin Ridge", "Reedsville, Wisconsin, USA"),
    (44, "Sibbe Disc Golf", "Sipoo, Finland"),
    (45, "Deer Lakes Park", "Tarentum, Pennsylvania, USA"),
    (46, "Wildcat Bluff", "Vinton, Iowa, USA"),
    (47, "BuckSnort", "Pine, Colorado, USA"),
    (48, "Stafford Woods", "Voorhees Township, New Jersey, USA"),
    (49, "Standing Rocks", "Stevens Point, Wisconsin, USA"),
    (50, "Harmon Hills", "Limestone, Tennessee, USA"),
    (51, "The Regulator at Rock Creek", "Burlington, North Carolina, USA"),
    (52, "Wild Times at Eagles Crossing", "Hawk Point, Missouri, USA"),
    (53, "Valdres Discgolfpark", "Leira i Valdres, Norway"),
    (54, "Ledgewood Disc Golf", "Northwood, New Hampshire, USA"),
    (55, "Wilcox Memorial Park", "Stanfordville, New York, USA"),
    (56, "Discgolf Terminalen Skellefteå", "Skellefteå, Sweden"),
    (57, "Olympus DGC", "Brooksville, Florida, USA"),
    (58, "The Hideaway DGR: Roadrunner", "Terrell, Texas, USA"),
    (59, "Puijo DiscGolf", "Kuopio, Finland"),
    (60, "Raptors Knoll Disc Golf Park", "Langley Township, BC, Canada"),
    (61, "Lakeview DGC at Moraine State Park", "West Liberty, Pennsylvania, USA"),
    (62, "Eastern Meadows DGC", "Östra Ryd, Sweden"),
    (63, "Kensington Toboggan", "Milford Charter Township, Michigan, USA"),
    (64, "Lula O.G.", "Lula, Georgia, USA"),
    (65, "Rolling Pines", "Wilkesboro, North Carolina, USA"),
    (66, "Westy Acres", "Greenfield, Massachusetts, USA"),
    (67, "Sugaree", "Newland, North Carolina, USA"),
    (68, "Bear Mountain", "Bailey, Colorado, USA"),
    (69, "Renegade's Trail", "Delhi Charter Township, Michigan, USA"),
    (70, "Clauder's Bogey Barn", "Paola, Kansas, USA"),
    (71, "Ørland Discgolfpark", "Brekstad, Norway"),
    (72, "Løvbergsmoen Diskgolfpark", "Elverum, Norway"),
    (73, "Beal Slough Disc Golf Course", "Lincoln, Nebraska, USA"),
    (74, "Flying Armadillo DGC: Gold Mini", "San Marcos, Texas, USA"),
    (75, "Vinbergs Discgolf", "Falkenberg, Sweden"),
    (76, "Cold Hollow Disc Golf", "Enosburg, Vermont, USA"),
    (77, "Iron Hoof", "Conyers, Georgia, USA"),
    (78, "Arvesta Sport Complex", "South Haven, Michigan, USA"),
    (79, "Milo McIver: Riverbend East", "Estacada, Oregon, USA"),
    (80, "Little Mulberry Park", "Dacula, Georgia, USA"),
    (81, "Kayak Point DGR: Red", "Stanwood, Washington, USA"),
    (82, "Fålehagen DiscGolfPark", "Motala, Sweden"),
    (83, "Cannon Ridge", "Fredericksburg, Virginia, USA"),
    (84, "North Cove Disc Golf: Boulders", "Marion, North Carolina, USA"),
    (85, "Bud Hill", "Memphis, Tennessee, USA"),
    (86, "Bradford Park", "Huntersville, North Carolina, USA"),
    (87, "Muddy Run Disc Golf Course", "Bethesda, Pennsylvania, USA"),
    (88, "Devils Grove Disc Golf: Devil", "Lewiston, Maine, USA"),
    (89, "Caesar Ford Park: Championship", "Xenia, Ohio, USA"),
    (90, "Broken Chains", "Lincoln University, Pennsylvania, USA"),
    (91, "Spa Park", "Taupō, New Zealand"),
    (92, "BC3 Disc Golf Course", "Nashville, Indiana, USA"),
    (93, "Sabattus Disc Golf: Falcon", "Sabattus, Maine, USA"),
    (94, "Rocky Hills", "Ovalo, Texas, USA"),
    (95, "Tampereen Frisbeegolfkeskus", "Tampere, Finland"),
    (96, "Mayflower Hills", "Roanoke, Virginia, USA"),
    (97, "The Preserve: Timberwolf", "Clearwater, Minnesota, USA"),
    (98, "Boylan Acres: Arduous", "Monrovia, Indiana, USA"),
    (99, "Pickard Park", "Indianola, Iowa, USA"),
    (100, "Sabattus Disc Golf: Eagle", "Sabattus, Maine, USA"),
]

# --- US Top 100: (rank, name, city, state) ------------------------------------
US = [
    (1, "Maple Hill", "Leicester", "Massachusetts"),
    (2, "Brewster Ridge Disc Golf Course", "Cambridge", "Vermont"),
    (3, "Fox Run Meadows", "Cambridge", "Vermont"),
    (4, "Championship Course at Eagles Crossing", "New Truxton", "Missouri"),
    (5, "Blue Ribbon Pines", "East Bethel", "Minnesota"),
    (6, "The Diavolo DGC at New Hope Park", "Cary", "North Carolina"),
    (7, "Persimmon Ridge DGC", "Greenbrier", "Arkansas"),
    (8, "Mile Marker 63", "East Brookfield", "Massachusetts"),
    (9, "The Canyons at Dellwood Park", "Lockport", "Illinois"),
    (10, "Caliber DGC", "Sandpoint", "Idaho"),
    (11, "Idlewild", "Burlington", "Kentucky"),
    (12, "Harmony Bends", "Columbia", "Missouri"),
    (13, "Hobb's Farm Disc Golf", "Carrollton", "Georgia"),
    (14, "Sandy Point Disc Golf Ranch", "Lac du Flambeau", "Wisconsin"),
    (15, "Northwood Park: Black", "Morton", "Illinois"),
    (16, "Faylor Lake DiscGolfPark", "Beaver Springs", "Pennsylvania"),
    (17, "Blue Goose", "Frankfort", "Kentucky"),
    (18, "Beaver Ranch Disc Golf Course", "Conifer", "Colorado"),
    (19, "Bryant Lake Park", "Eden Prairie", "Minnesota"),
    (20, "Flip City Disc Golf Park", "Shelby", "Michigan"),
    (21, "Meadowbrook Orchards", "Sterling", "Massachusetts"),
    (22, "Sabattus Disc Golf: Hawk", "Sabattus", "Maine"),
    (23, "Neatman Creek", "Germanton", "North Carolina"),
    (24, "New London Tech DGC", "Forest", "Virginia"),
    (25, "Echo Valley at Hoffmann Reserve", "Waynesville", "Ohio"),
    (26, "Rollin Ridge", "Reedsville", "Wisconsin"),
    (27, "Deer Lakes Park", "Tarentum", "Pennsylvania"),
    (28, "Wildcat Bluff", "Vinton", "Iowa"),
    (29, "BuckSnort", "Pine", "Colorado"),
    (30, "Stafford Woods", "Voorhees Township", "New Jersey"),
    (31, "Standing Rocks", "Stevens Point", "Wisconsin"),
    (32, "Harmon Hills", "Limestone", "Tennessee"),
    (33, "The Regulator at Rock Creek", "Burlington", "North Carolina"),
    (34, "Wild Times at Eagles Crossing", "Hawk Point", "Missouri"),
    (35, "Ledgewood Disc Golf", "Northwood", "New Hampshire"),
    (36, "Wilcox Memorial Park", "Stanfordville", "New York"),
    (37, "Olympus DGC", "Brooksville", "Florida"),
    (38, "The Hideaway DGR: Roadrunner", "Terrell", "Texas"),
    (39, "Lakeview DGC at Moraine State Park", "West Liberty", "Pennsylvania"),
    (40, "Kensington Toboggan", "Milford Charter Township", "Michigan"),
    (41, "Lula O.G.", "Lula", "Georgia"),
    (42, "Rolling Pines", "Wilkesboro", "North Carolina"),
    (43, "Westy Acres", "Greenfield", "Massachusetts"),
    (44, "Sugaree", "Newland", "North Carolina"),
    (45, "Bear Mountain", "Bailey", "Colorado"),
    (46, "Renegade's Trail", "Delhi Charter Township", "Michigan"),
    (47, "Clauder's Bogey Barn", "Paola", "Kansas"),
    (48, "Beal Slough Disc Golf Course", "Lincoln", "Nebraska"),
    (49, "Flying Armadillo DGC: Gold Mini", "San Marcos", "Texas"),
    (50, "Cold Hollow Disc Golf", "Enosburg", "Vermont"),
    (51, "Iron Hoof", "Conyers", "Georgia"),
    (52, "Arvesta Sport Complex", "South Haven", "Michigan"),
    (53, "Milo McIver: Riverbend East", "Estacada", "Oregon"),
    (54, "Little Mulberry Park", "Dacula", "Georgia"),
    (55, "Kayak Point DGR: Red", "Stanwood", "Washington"),
    (56, "Cannon Ridge", "Fredericksburg", "Virginia"),
    (57, "North Cove Disc Golf: Boulders", "Marion", "North Carolina"),
    (58, "Bud Hill", "Memphis", "Tennessee"),
    (59, "Bradford Park", "Huntersville", "North Carolina"),
    (60, "Muddy Run Disc Golf Course", "Bethesda", "Pennsylvania"),
    (61, "Devils Grove Disc Golf: Devil", "Lewiston", "Maine"),
    (62, "Caesar Ford Park: Championship", "Xenia", "Ohio"),
    (63, "Broken Chains", "Lincoln University", "Pennsylvania"),
    (64, "BC3 Disc Golf Course", "Nashville", "Indiana"),
    (65, "Sabattus Disc Golf: Falcon", "Sabattus", "Maine"),
    (66, "Rocky Hills", "Ovalo", "Texas"),
    (67, "Mayflower Hills", "Roanoke", "Virginia"),
    (68, "The Preserve: Timberwolf", "Clearwater", "Minnesota"),
    (69, "Boylan Acres: Arduous", "Monrovia", "Indiana"),
    (70, "Pickard Park", "Indianola", "Iowa"),
    (71, "Sabattus Disc Golf: Eagle", "Sabattus", "Maine"),
    (72, "Silver Creek Park", "Manitowoc", "Wisconsin"),
    (73, "Eagle Ridge", "Coshocton", "Ohio"),
    (74, "Kudzu Cove Cabins", "Guntersville", "Alabama"),
    (75, "Quarry Run at Augusta Disc Golf", "Augusta", "Maine"),
    (76, "Pineland Farms: The Patriot", "New Gloucester", "Maine"),
    (77, "Arrowhead Disc Golf Course", "Louisville", "Kentucky"),
    (78, "Punderson Disc Golf Course", "Newbury", "Ohio"),
    (79, "Pier Park", "Portland", "Oregon"),
    (80, "Parc des Familles DGC", "Marrero", "Louisiana"),
    (81, "Dino Hills DG Farm: Carnivore Valley", "Walnut Springs", "Texas"),
    (82, "New Melle Lakes", "Wentzville", "Missouri"),
    (83, "Tom Brown Park DGC", "Tallahassee", "Florida"),
    (84, "Top O' The Hill", "Canterbury", "New Hampshire"),
    (85, "Whistler's Bend", "Roseburg", "Oregon"),
    (86, "Woodland Valley: Black Bear", "Limerick", "Maine"),
    (87, "Black Hoof Driven by Henderson Engineers", "Lenexa", "Kansas"),
    (88, "Wilderness", "Montello", "Wisconsin"),
    (89, "DeLaveaga Disc Golf Course", "Santa Cruz", "California"),
    (90, "Tjader Acres", "Siren", "Wisconsin"),
    (91, "Cactus Rock", "Tuscaloosa", "Alabama"),
    (92, "Knockwood: Santa Fe Lake", "Augusta", "Kansas"),
    (93, "Boylan Acres: Extreme", "Monrovia", "Indiana"),
    (94, "Camp Serene", "Noti", "Oregon"),
    (95, "The Fort", "Ogden", "Utah"),
    (96, "Red Hawk Ridge", "Lula", "Georgia"),
    (97, "Ashe County Park", "Jefferson", "North Carolina"),
    (98, "North Bluff", "Gladstone", "Michigan"),
    (99, "Shelton Springs", "Shelton", "Washington"),
    (100, "The Admiral", "Semmes", "Alabama"),
]

# --- Per-state Top 10s for the trip route: state -> [(rank, name, city), ...] -
STATES = {
    "Colorado": [
        (1, "Beaver Ranch Disc Golf Course", "Conifer"),
        (2, "BuckSnort", "Pine"),
        (3, "Bear Mountain", "Bailey"),
        (4, "Wondervu Disc Golf Course", "Golden"),
        (5, "Twisted Cedars Dgc", "Cokedale"),
        (6, "Glen Isle DGC", "Bailey"),
        (7, "Prickly Pines Disc Golf Course", "Elizabeth"),
        (8, "Arapahoe Basin DGC", "Keystone"),
        (9, "Ghost Town", "Central City"),
        (10, "Little Scraggy Disc Golf Course", "Sedalia"),
    ],
    "Kansas": [
        (1, "Clauder's Bogey Barn", "Paola"),
        (2, "Black Hoof Driven by Henderson Engineers", "Lenexa"),
        (3, "Knockwood: Santa Fe Lake", "Augusta"),
        (4, "Spoon Creek Disc Golf Course", "Gardner"),
        (5, "Champions Landing: Black", "Emporia"),
        (6, "Foxtail Farm", "Tonganoxie"),
        (7, "Longview", "Ozawkie"),
        (8, "Cedar Ridge", "Bonner Springs"),
        (9, "Jones Park: East", "Emporia"),
        (10, "Peter Pan Park: Optimist", "Emporia"),
    ],
    "Missouri": [
        (1, "Championship Course at Eagles Crossing", "New Truxton"),
        (2, "Harmony Bends", "Columbia"),
        (3, "Wild Times at Eagles Crossing", "Hawk Point"),
        (4, "New Melle Lakes", "Wentzville"),
        (5, "Northside DGC", "Springfield"),
        (6, "Bad Rock Creek & BRC Championship Course", "Liberty"),
        (7, "Hanna Hills Disc Golf Course", "Laquey"),
        (8, "Sunset Ridge", "Grain Valley"),
        (9, "Water Works Park DGC", "Kansas City"),
        (10, "Lake Springfield DGC", "Springfield"),
    ],
    "Illinois": [
        (1, "The Canyons at Dellwood Park", "Lockport"),
        (2, "Northwood Park: Black", "Morton"),
        (3, "Fairfield Park", "Round Lake"),
        (4, "Northwood Park: Blue", "Morton"),
        (5, "Fox Prairie", "McLeansboro"),
        (6, "Anna Page Park: West", "Rockford"),
        (7, "The Oaks", "Mokena"),
        (8, "Camden 2", "Milan"),
        (9, "Fel-Pro RRR DiscGolfPark", "Cary"),
        (10, "The Quarry at Rotary Park", "La Salle"),
    ],
    "Indiana": [
        (1, "BC3 Disc Golf Course", "Nashville"),
        (2, "Boylan Acres: Arduous", "Monrovia"),
        (3, "Boylan Acres: Extreme", "Monrovia"),
        (4, "Rogers Lakewood Park Disc Golf Course", "Valparaiso"),
        (5, "George Wilson Park Disc Golf Course", "Mishawaka"),
        (6, "Cedar Grove", "Sunman"),
        (7, "Fall Creek Disc Golf Course", "Indianapolis"),
        (8, "Lemon Lake County Park: Gold", "Crown Point"),
        (9, "Mastodon DGC at Purdue Fort Wayne", "Fort Wayne"),
        (10, "Lemon Lake County Park: Silver", "Crown Point"),
    ],
    "Michigan": [
        (1, "Flip City Disc Golf Park", "Shelby"),
        (2, "Kensington Toboggan", "Milford Charter Township"),
        (3, "Renegade's Trail", "Delhi Charter Township"),
        (4, "Arvesta Sport Complex", "South Haven"),
        (5, "North Bluff", "Gladstone"),
        (6, "Meyer Broadway: North", "Three Rivers"),
        (7, "Bald Mountain", "Orion Charter Township"),
        (8, "Green Lake DiscGolfPark", "Interlochen"),
        (9, "Black Locust: South Green", "Milford Charter Township"),
        (10, "Hammond Hills", "Hastings"),
    ],
    "Iowa": [
        (1, "Wildcat Bluff", "Vinton"),
        (2, "Pickard Park", "Indianola"),
        (3, "Shaver Park", "Cedar Rapids"),
        (4, "Coralville Disc Golf Altmaier Park", "Coralville"),
        (5, "Walnut Ridge Recreation Area", "Johnston"),
        (6, "Sunnyside", "Atlantic"),
        (7, "Southwoods Park Disc Golf Course", "West Des Moines"),
        (8, "Brookwood Park", "Waverly"),
        (9, "Treasure Cove", "Council Bluffs"),
        (10, "Ewing Park", "Des Moines"),
    ],
    "Nebraska": [
        (1, "Beal Slough Disc Golf Course", "Lincoln"),
        (2, "Lighthouse DGC", "Omaha"),
        (3, "Kelley Park", "McCook"),
        (4, "Windmill State Recreation Area", "Gibbon"),
        (5, "Cottonmill", "Kearney"),
        (6, "Lake Hastings", "Hastings"),
        (7, "Scott Whitcomb Memorial [Tierra Park]", "Lincoln"),
        (8, "Max E. Roper Interstate Park: West", "Lincoln"),
        (9, "Wildwood Disc Golf Course", "Nebraska City"),
        (10, "Seymour Smith Park", "La Vista"),
    ],
}


def norm(name):
    """Normalized key so the same course matches across lists despite
    punctuation differences (e.g. 'Knockwood: Santa Fe Lake' vs
    'Knockwood - Santa Fe Lake')."""
    return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()


def parse_world_location(loc):
    """'Leicester, Massachusetts, USA' -> (city, state_region, country)."""
    parts = [p.strip() for p in loc.split(",")]
    country = parts[-1]
    if len(parts) >= 3:
        return ", ".join(parts[:-2]), parts[-2], country
    if len(parts) == 2:
        return parts[0], "", country
    return parts[0], "", ""


def blank_record(name):
    return {
        "course_name": name,
        "city": "",
        "state_region": "",
        "country": "",
        "world_rank": "",
        "us_rank": "",
        "state_rank": "",
        "scopes": [],          # which lists this course appears on
        "on_trip_route": False,
        "lat": "",
        "lon": "",
        "udisc_url": "",
        "year": YEAR,
    }


def build():
    records = {}  # norm-key -> record

    # 1) US national list (clean city/state; sets canonical name for US courses)
    for rank, name, city, state in US:
        rec = records.setdefault(norm(name), blank_record(name))
        rec.update(city=city, state_region=state, country="USA", us_rank=rank)
        rec["scopes"].append("us")

    # 2) World list (adds world_rank; creates international courses)
    for rank, name, loc in WORLD:
        rec = records.get(norm(name))
        if rec is None:
            rec = records.setdefault(norm(name), blank_record(name))
            city, region, country = parse_world_location(loc)
            rec.update(city=city, state_region=region, country=country)
        rec["world_rank"] = rank
        rec["scopes"].append("world")

    # 3) Per-state trip lists (adds state_rank; creates state-only courses)
    for state, rows in STATES.items():
        for rank, name, city in rows:
            rec = records.get(norm(name))
            if rec is None:
                rec = records.setdefault(norm(name), blank_record(name))
                rec.update(city=city, state_region=state, country="USA")
            rec["state_rank"] = rank
            rec["scopes"].append(f"state:{state}")

    # preserve enrichment (lat/lon/udisc_url) from a prior build if present,
    # so re-running this script doesn't wipe geocoding done by geocode_courses.py
    prior_path = os.path.join(HERE, "courses_2026.json")
    if os.path.exists(prior_path):
        with open(prior_path) as f:
            prior = {norm(r["course_name"]): r for r in json.load(f)}
        for key, rec in records.items():
            old = prior.get(key)
            if old:
                for field in ("lat", "lon", "udisc_url"):
                    if old.get(field) not in ("", None):
                        rec[field] = old[field]

    # finalize derived fields
    out = []
    for rec in records.values():
        rec["on_trip_route"] = rec["state_region"] in TRIP_STATES
        rec["scopes"] = ";".join(rec["scopes"])
        out.append(rec)

    # stable, useful sort: trip-route first, then by best available rank
    def sort_key(r):
        ranks = [v for v in (r["world_rank"], r["us_rank"], r["state_rank"])
                 if v != ""]
        best = min(ranks) if ranks else 9999
        return (not r["on_trip_route"], best, r["course_name"])

    out.sort(key=sort_key)
    return out


def write_outputs(records):
    json_path = os.path.join(HERE, "courses_2026.json")
    with open(json_path, "w") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    csv_path = os.path.join(HERE, "courses_2026.csv")
    fields = ["course_name", "city", "state_region", "country", "world_rank",
              "us_rank", "state_rank", "scopes", "on_trip_route", "lat", "lon",
              "udisc_url", "year"]
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(records)
    return json_path, csv_path


if __name__ == "__main__":
    recs = build()
    jp, cp = write_outputs(recs)
    trip = sum(1 for r in recs if r["on_trip_route"])
    intl = sum(1 for r in recs if r["country"] not in ("USA", ""))
    print(f"Total unique courses: {len(recs)}")
    print(f"  on trip route (CO/KS/MO/IL/IN/MI/IA/NE): {trip}")
    print(f"  international (non-US): {intl}")
    print(f"Wrote {os.path.basename(jp)} and {os.path.basename(cp)}")
