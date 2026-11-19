#!/usr/bin/env python3
"""Find couplets that contain any of the music words (or their inflections).

Reads  scripts/cache/hafez/**.json   (run fetch_hafez.py first)
Writes scripts/cache/candidates.json     all candidate couplets, with context
       scripts/cache/near_misses.txt     tokens that *start with* a lemma but
                                         were not matched (to spot missing forms)

Usage: python3 -I scripts/find_candidates.py
"""
import collections
import glob
import json
import re
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lexicon import FORMS, STEMS, norm_text, tokens, BASE_WORDS  # noqa: E402

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache" / "hafez"
WORK_ORDER = ["ghazal", "ghete", "robaee", "ghaside", "masnavi", "saghiname", "montasab"]
WORK_LABEL = {
    "ghazal": "Ghazal", "ghete": "Qet'e", "robaee": "Ruba'i", "ghaside": "Qasida",
    "masnavi": "Masnavi", "saghiname": "Saqi-nameh", "montasab": "Attributed",
}


def poem_sort_key(p):
    m = re.search(r"(\d+)$", p)
    return (0, int(m.group(1))) if m else (1, p)


def main():
    cands = []
    near = collections.Counter()
    near_ex = {}
    n_couplets = 0
    for work in WORK_ORDER:
        files = glob.glob(str(CACHE / work / "*.json"))
        for f in sorted(files, key=lambda x: poem_sort_key(Path(x).stem)):
            d = json.load(open(f, encoding="utf-8"))
            slug = Path(f).stem
            couplets = collections.OrderedDict()
            for v in d["Verses"]:
                couplets.setdefault(v["CoupletIndex"], []).append(v)
            n_couplets += len(couplets)
            for ci, vs in couplets.items():
                hits = []
                for v in vs:
                    for tok in tokens(v["Text"]):
                        lemma = FORMS.get(tok)
                        # "وآهنگ": the conjunction و written fused to the word
                        if not lemma and tok.startswith("و") and len(tok) > 4:
                            lemma = FORMS.get(tok[1:])
                        if lemma:
                            hits.append({"lemma": lemma, "token": tok})
                        else:
                            for stem, lem in STEMS.items():
                                if len(stem) >= 3 and tok.startswith(stem) and tok != stem:
                                    near[(lem, tok)] += 1
                                    near_ex.setdefault((lem, tok), (work, slug, ci))
                if hits:
                    cands.append({
                        "id": f"{work}/{slug}#{ci + 1}",
                        "work": work,
                        "slug": slug,
                        "title": d["Title"],
                        "url": d["FullUrl"],
                        "couplet": ci + 1,
                        "verses": [v["Text"] for v in vs],
                        "paraphrase": next((v.get("CoupletSummary") for v in vs if v.get("CoupletSummary")), None),
                        "hits": hits,
                    })
    (ROOT / "cache").mkdir(exist_ok=True)
    json.dump(cands, open(ROOT / "cache" / "candidates.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with open(ROOT / "cache" / "near_misses.txt", "w", encoding="utf-8") as fh:
        for (lem, tok), n in sorted(near.items(), key=lambda x: (x[0][0], -x[1])):
            fh.write(f"{lem}\t{tok}\t{n}\t{near_ex[(lem, tok)]}\n")
    by_work = collections.Counter(c["work"] for c in cands)
    by_lemma = collections.Counter(h["lemma"] for c in cands for h in c["hits"])
    print("couplets scanned:", n_couplets, "| candidate couplets:", len(cands))
    print("by work:", dict(by_work))
    print("by lemma (hit count):", dict(by_lemma.most_common()))


if __name__ == "__main__":
    main()
