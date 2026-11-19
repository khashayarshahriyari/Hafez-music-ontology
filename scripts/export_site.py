#!/usr/bin/env python3
"""Build the files to upload to the personal website.

Writes into site/:
  hafez-music-ontology.html        the page (a copy of index.html with paths pointing into hafez/)
  hafez/app.js, style.css,
        lines.js, background.jpg   everything the page loads

Upload the contents of site/ to the root of the website repository.
Run this after build_lines.py whenever the couplets, translations, text or styles change.

Usage: python3 -I scripts/export_site.py
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
FOLDER = SITE / "hafez"

REWRITE = [
    ('href="assets/style.css"', 'href="hafez/style.css"'),
    ('src="assets/app.js"', 'src="hafez/app.js"'),
    ('src="data/lines.js"', 'src="hafez/lines.js"'),
]


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for old, new in REWRITE:
        if old not in html:
            raise SystemExit(f"index.html no longer contains {old!r}; update REWRITE in export_site.py")
        html = html.replace(old, new)
    if FOLDER.exists():
        shutil.rmtree(FOLDER)
    FOLDER.mkdir(parents=True)
    (SITE / "hafez-music-ontology.html").write_text(html, encoding="utf-8")
    for src, name in [("assets/app.js", "app.js"), ("assets/style.css", "style.css"),
                      ("assets/background.jpg", "background.jpg"), ("data/lines.js", "lines.js")]:
        shutil.copy2(ROOT / src, FOLDER / name)
    print("wrote", SITE / "hafez-music-ontology.html")
    for f in sorted(FOLDER.iterdir()):
        print("wrote", f, f"({f.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
