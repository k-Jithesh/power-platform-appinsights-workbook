"""Build data/place-coordinates.csv for the Application Insights workbook map.

Source: GeoNames "cities500" (places with at least 500 people), licensed CC BY 4.0
(https://www.geonames.org/). One row per country, state and city name, keeping the most
populous place when names repeat. Names are normalised the same way as in the workbook
query: lower case, accents removed, anything that is not a letter or digit becomes one space.

Usage:  python tools/build_place_coordinates.py [--min-population 500] [--out data/place-coordinates.csv]
"""
import argparse
import csv
import io
import os
import re
import tempfile
import unicodedata
import urllib.request
import zipfile

BASE = "https://download.geonames.org/export/dump/"


def norm(text):
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def fetch(name, folder):
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        urllib.request.urlretrieve(BASE + name, path + ".part")
        os.replace(path + ".part", path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-population", type=int, default=500)
    ap.add_argument("--out", default="data/place-coordinates.csv")
    ap.add_argument("--cache", default=os.path.join(tempfile.gettempdir(), "geonames_cache"))
    args = ap.parse_args()
    os.makedirs(args.cache, exist_ok=True)

    countries = {}
    with open(fetch("countryInfo.txt", args.cache), encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            cols = line.rstrip("\n").split("\t")
            countries[cols[0]] = cols[4]

    states = {}
    with open(fetch("admin1CodesASCII.txt", args.cache), encoding="utf-8") as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")
            states[cols[0]] = cols[2]

    best = {}
    with zipfile.ZipFile(fetch("cities500.zip", args.cache)) as z, z.open("cities500.txt") as raw:
        for line in io.TextIOWrapper(raw, encoding="utf-8"):
            c = line.rstrip("\n").split("\t")
            population = int(c[14] or 0)
            if population < args.min_population:
                continue
            key = (norm(countries.get(c[8], c[8])), norm(states.get(c[8] + "." + c[10], "")), norm(c[2]))
            if not key[2]:
                continue
            if key not in best or population > best[key][2]:
                best[key] = (round(float(c[4]), 3), round(float(c[5]), 3), population)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["Country", "State", "City", "Lat", "Lon", "Pop"])
        for (country, state, city), (lat, lon, pop) in sorted(best.items()):
            w.writerow([country, state, city, lat, lon, pop])
    print("wrote %s: %d places" % (args.out, len(best)))


if __name__ == "__main__":
    main()
