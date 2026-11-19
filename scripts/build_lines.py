#!/usr/bin/env python3
"""Build data/lines.json (the file the web page loads) from the curation ledger.

Inputs
  scripts/cache/candidates.json   (from find_candidates.py)
  scripts/curation_ledger.txt     (human decisions: 1 musical / 0 not / 2 borderline)
  scripts/translations.json       (optional: {"<couplet id>": "English translation"})
  scripts/notes.json              (optional: {"<couplet id>": "short note on wordplay"})

Outputs
  data/lines.json                 only couplets decided as musical (code 1)
  scripts/REVIEW.md               borderline (2) and excluded (0) couplets, for checking

To promote a borderline couplet: change its code from 2 to 1 in the ledger
and re-run this script.

Usage: python3 -I scripts/build_lines.py
"""
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lexicon import BASE_WORDS, FORMS  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "data" / "lines.json"
PINNED_COMMIT = "616e4042699fb2ac9a148b17c7b61221bd3edfe8"

DIAC = re.compile("[ً-ٰٟـ]")
FOLD = {"ي": "ی", "ك": "ک", "ۀ": "ه", "أ": "ا", "إ": "ا", "آ": "ا"}


def read_ledger(path):
    decisions = OrderedDict()  # index -> (id, code, [lemmas], note)
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        parts = raw.split(" ", 4)
        idx, cid, code, lem = int(parts[0]), parts[1], int(parts[2]), parts[3]
        note = parts[4] if len(parts) > 4 else ""
        lemmas = [] if lem == "-" else lem.split(",")
        decisions[idx] = (cid, code, lemmas, note)  # later lines override earlier ones
    return decisions


def highlight_spans(text, lemmas):
    """Character ranges (in the original text) of tokens that are musical hits."""
    norm, pos = [], []
    for i, ch in enumerate(text):
        if DIAC.match(ch):
            continue
        if ch == "ا" and i + 1 < len(text) and text[i + 1] == "ٓ":
            ch = "ا"
        ch = FOLD.get(ch, ch)
        if not (ch.isalnum() or ch == "_"):
            ch = " "
        norm.append(ch)
        pos.append(i)
    spans, start = [], None
    for k in range(len(norm) + 1):
        inside = k < len(norm) and norm[k] != " "
        if inside and start is None:
            start = k
        if not inside and start is not None:
            tok = "".join(norm[start:k])
            lemma = FORMS.get(tok)
            if not lemma and tok.startswith("و") and len(tok) > 4:
                lemma = FORMS.get(tok[1:])
            if lemma and lemma in lemmas:
                s, e = pos[start], pos[k - 1] + 1
                while e < len(text) and DIAC.match(text[e]):
                    e += 1
                spans.append([s, e])
            start = None
    return spans


def work_label(work):
    return {"ghazal": "Ghazal", "ghete": "Qet'e", "robaee": "Ruba'i", "ghaside": "Qasida",
            "masnavi": "Masnavi", "saghiname": "Saqi-nameh"}[work]


def main():
    cands = json.loads((ROOT / "cache" / "candidates.json").read_text(encoding="utf-8"))
    decisions = read_ledger(ROOT / "curation_ledger.txt")
    trans_path = ROOT / "translations.json"
    translations = json.loads(trans_path.read_text(encoding="utf-8")) if trans_path.exists() else {}
    notes_path = ROOT / "notes.json"
    notes = json.loads(notes_path.read_text(encoding="utf-8")) if notes_path.exists() else {}

    lines, borderline, excluded = [], [], []
    missing = [i for i in range(len(cands)) if i not in decisions]
    if missing:
        sys.exit(f"ledger has no decision for candidate indexes: {missing[:10]} ...")
    for i, cand in enumerate(cands):
        cid, code, lemmas, note = decisions[i]
        if cid != cand["id"]:
            sys.exit(f"ledger index {i} is {cid} but candidate is {cand['id']} - re-check the ledger")
        if code == 1:
            m = re.search(r"(\d+)$", cand["slug"])
            rec = OrderedDict()
            rec["id"] = cand["id"]
            rec["work"] = cand["work"]
            rec["poem"] = int(m.group(1)) if m and cand["work"] in ("ghazal", "ghete", "robaee", "ghaside") else None
            rec["couplet"] = cand["couplet"]
            rec["v"] = cand["verses"]
            rec["w"] = lemmas
            rec["hl"] = [highlight_spans(v, lemmas) for v in cand["verses"]]
            rec["url"] = cand["url"]
            rec["en"] = translations.get(cand["id"])
            if notes.get(cand["id"]):
                rec["note"] = notes[cand["id"]]
            lines.append(rec)
        elif code == 2:
            borderline.append((cand, lemmas, note))
        else:
            excluded.append((cand, note))

    lexicon = OrderedDict((k, {"en": v[0], "cat": v[1]}) for k, v in BASE_WORDS.items())
    counts = Counter(l for r in lines for l in r["w"])
    data = OrderedDict()
    data["meta"] = OrderedDict([
        ("title", "Hafez Music Ontology"),
        ("source", "Ganjoor (ganjoor.net) - public data export github.com/ganjoor/ganjoor-data"),
        ("sourceCommit", PINNED_COMMIT),
        ("count", len(lines)),
        ("translated", sum(1 for r in lines if r["en"])),
    ])
    data["lexicon"] = lexicon
    data["counts"] = OrderedDict(counts.most_common())
    data["lines"] = lines
    OUT.parent.mkdir(exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text(payload, encoding="utf-8")
    # same data as a script, so index.html also works when opened straight from disk
    OUT.with_suffix(".js").write_text("window.HMO_DATA=" + payload + ";\n", encoding="utf-8")

    # review file
    def block(c, extra):
        t = [f"- **{work_label(c['work'])} {c['title']}**, couplet {c['couplet']}  (`{c['id']}`) — {extra}",
             f"  - {c['verses'][0]}", f"  - {c['verses'][1] if len(c['verses']) > 1 else ''}"]
        return "\n".join(t)

    with open(ROOT / "REVIEW.md", "w", encoding="utf-8") as fh:
        fh.write("# Curation review\n\n")
        fh.write("Generated by `build_lines.py`. Decisions live in `curation_ledger.txt`; "
                 "change a code there and re-run the build.\n\n")
        fh.write(f"## Borderline — held out of the page ({len(borderline)})\n\n"
                 "The listed word is present, but its sense is general joy, a plain voice, a bell, or an "
                 "idiom rather than clearly music. Promote any you want by changing `2` to `1`.\n\n")
        for c, lemmas, note in borderline:
            fh.write(block(c, f"{'،'.join(lemmas)}: {note}") + "\n\n")
        fh.write(f"## Excluded as non-musical ({len(excluded)})\n\n")
        for c, note in excluded:
            fh.write(block(c, note) + "\n\n")

    print(f"musical (in page): {len(lines)} | borderline: {len(borderline)} | excluded: {len(excluded)}")
    print("by work:", dict(Counter(r['work'] for r in lines)))
    print("by lemma:", dict(counts.most_common()))
    print(f"wrote {OUT} ({OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
