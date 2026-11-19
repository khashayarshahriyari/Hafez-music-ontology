# Hafez Music Ontology

A small web project that finds couplets (beyts) of Hafez that speak of music, and lets you read them in three ways:

1. **A couplet at random**, with a button for another.
2. **In English**: a translation of whichever couplet is selected, whether it came from the random draw or from the list.
3. **All couplets**: a browsable, searchable index. Filter by word, group by poem or by word, and click any couplet to read it in section 2.

It is plain HTML, CSS and JavaScript with no build step and no server. Open `index.html` in a browser, or host the folder on GitHub Pages.

The Persian text comes from [Ganjoor](https://ganjoor.net) (public data export, pinned to one commit). Every couplet links back to its Ganjoor page. The English renderings are working translations prepared with Claude: literal rather than poetic, and open to correction. The Ganjoor data repository does not state a data licence, so keep the credit and the per-couplet links in place.

## The twenty words

مطرب، طرب، بربط، پرده، چنگ، رباب، بانگ، آهنگ، صوت، ساز، آواز، نی، رود، دف، رقص، سماع، دستان، کمانچه، نغمه، سرود

Common inflections and variants are matched through an explicit list in `scripts/lexicon.py` (not blind prefix matching), for example plurals, `-ی` forms, compounds such as گلبانگ, and fused forms such as وآهنگ.

## How the couplets were chosen

Several of the words have non-musical meanings (`رود` river or "goes", `پرده` veil, `نی` "not", `ساز` "make", `دستان` Zal's epithet, and so on). The pipeline is:

1. `scripts/fetch_hafez.py` downloads Hafez's ghazals, qet'e, ruba'i, qasidas and the Saqi-nameh from the pinned Ganjoor snapshot into `scripts/cache/hafez/`. The attributed poems (montasab) are skipped unless you pass `--with-attributed`.
2. `scripts/find_candidates.py` finds every couplet containing a listed word or form (350 candidates) and writes `scripts/cache/candidates.json`.
3. Each candidate was read in context and recorded in `scripts/curation_ledger.txt`:
   - `1` musical, included on the page (162 couplets)
   - `2` borderline, held out and listed in `scripts/REVIEW.md` (36)
   - `0` non-musical sense, excluded (152)
4. `scripts/build_lines.py` merges the ledger with `scripts/translations.json` and `scripts/notes.json` and writes `data/lines.json` and `data/lines.js`, which the page loads.

The borderline group is mostly `طرب` used as plain "joy" and `آواز` as an ordinary voice. To include a borderline couplet, change its code from `2` to `1` in the ledger, then rebuild.

## Rebuilding

```bash
python3 scripts/fetch_hafez.py          # only needed if scripts/cache/hafez/ is missing
python3 scripts/find_candidates.py      # only needed if you change the lexicon
python3 scripts/build_lines.py          # regenerates data/lines.json, data/lines.js, scripts/REVIEW.md
```

Add or correct a translation by editing `scripts/translations.json` (keyed by couplet id such as `ghazal/sh2#3`, with a newline between the two hemistichs). Add a short note on wordplay (shown under the translation) in `scripts/notes.json`. Then run `build_lines.py` again.

## Deep links

Selecting a couplet updates the address, for example `index.html#ghazal/sh2/3` (work, poem number, couplet number). Opening such a link selects that couplet in section 2 and scrolls to it.

## Hosting on GitHub Pages

1. Create the repository and push this folder to it.
2. In the repository, open Settings, then Pages, and publish from the `main` branch (root).
3. The project page will be at `https://<user>.github.io/<repo>/`. The "← Home" link at the top of `index.html` points to `/`; change it if the project lives at a different path on your site.

## Linking from your home page

Add one line below the Temporal Entanglements link, for example:

```html
<a href="https://<user>.github.io/<repo>/">Hafez Music Ontology</a>
```

## Live translation (optional, later)

The page ships with pre-translated couplets, so nothing needs configuring and nothing can break at runtime. If you later want translation of arbitrary text, a small Cloudflare Worker (free plan) holding an API key can sit between the page and a translation service; `transText` in `assets/app.js` is where the page reads the English text.

## Layout

```
index.html            the page
assets/style.css      styles (light and dark themes)
assets/app.js         random draw, selection, list, search, filters
data/lines.json       built data (also data/lines.js, so the page works from file://)
scripts/              fetch, candidate search, lexicon, curation ledger, build, translations, notes
```
