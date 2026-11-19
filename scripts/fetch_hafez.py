#!/usr/bin/env python3
"""Download Hafez's poems from the public ganjoor-data repository.

Source:  https://github.com/ganjoor/ganjoor-data  (poets/hafez/...)
Output:  scripts/cache/hafez/<work>/<slug>.json   (git-ignored, re-creatable)

The data are pinned to one commit so that the build is reproducible.
Change PINNED_COMMIT to move to a newer snapshot.

Usage:  python3 scripts/fetch_hafez.py [--with-attributed]
"""
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PINNED_COMMIT = "616e4042699fb2ac9a148b17c7b61221bd3edfe8"
RAW = f"https://raw.githubusercontent.com/ganjoor/ganjoor-data/{PINNED_COMMIT}/poets/hafez/"

# work key -> (category folder or None for a poem at the poet root, human label)
WORKS = {
    "ghazal":   ("ghazal",   "Ghazals"),
    "ghete":    ("ghete",    "Qet'at"),
    "robaee":   ("robaee2",  "Ruba'iyat"),
    "ghaside":  ("ghaside",  "Qasidas"),
}
ROOT_POEMS = {"masnavi": "Masnavi", "saghiname": "Saqi-nameh"}
ATTRIBUTED = ("montasab", "Attributed poems")  # not certainly Hafez; off by default

CACHE = Path(__file__).resolve().parent / "cache" / "hafez"


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def fetch_to(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(get(url))


def main():
    works = dict(WORKS)
    if "--with-attributed" in sys.argv:
        works["montasab"] = (ATTRIBUTED[0], ATTRIBUTED[1])
    jobs = []
    for key, (folder, _label) in works.items():
        cat = json.loads(get(RAW + f"{folder}/_cat.json"))
        for p in cat["Poems"]:
            slug = p["FullUrl"].rstrip("/").split("/")[-1]
            jobs.append((RAW + f"{folder}/{slug}.json", CACHE / key / f"{slug}.json"))
    for slug in ROOT_POEMS:
        jobs.append((RAW + f"{slug}.json", CACHE / slug / f"{slug}.json"))
    with ThreadPoolExecutor(max_workers=12) as ex:
        list(ex.map(lambda j: fetch_to(*j), jobs))
    print(f"fetched {len(jobs)} poems into {CACHE}")


if __name__ == "__main__":
    main()
