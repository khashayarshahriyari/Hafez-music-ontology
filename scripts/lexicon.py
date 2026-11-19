"""Music vocabulary and the forms we accept for each word.

BASE_WORDS is the user's list of 20 words. For each we generate common
inflections (plurals, clitics, vocative, adjective/compound endings) and
a few spelling variants. Matching is done on normalised tokens, so
diacritics, ZWNJ and the alef-madda difference do not matter.

Every hit is only a *candidate*: whether the word is used in a musical
sense in that couplet is decided by a human reading it (scripts/curation.json).
"""
import re

_DIAC = re.compile("[ً-ٰٟـ]")


def norm_text(s):
    """Normalise Persian text for matching (not for display)."""
    s = s.replace("آ", "آ")
    s = _DIAC.sub("", s)
    s = (s.replace("ي", "ی").replace("ك", "ک").replace("ۀ", "ه")
           .replace("أ", "ا").replace("إ", "ا").replace("آ", "ا"))
    s = s.replace("‌", " ").replace("‏", " ").replace("‎", " ")
    s = re.sub(r"[^\w\s]", " ", s)
    return s


def tokens(s):
    return norm_text(s).split()


# lemma -> (English gloss, ontology category)
BASE_WORDS = {
    "مطرب":   ("minstrel / musician",            "performer"),
    "طرب":    ("mirth, music-making, rapture",   "practice"),
    "بربط":   ("barbat (lute)",                  "instrument"),
    "پرده":   ("mode / fret / tune (lit. veil)", "structure"),
    "چنگ":    ("chang (harp)",                   "instrument"),
    "رباب":   ("rubab (lute)",                   "instrument"),
    "بانگ":   ("cry, call, sound",               "sound"),
    "آهنگ":   ("melody, tune",                   "structure"),
    "صوت":    ("sound, voice, chant",            "sound"),
    "ساز":    ("instrument, music",              "instrument"),
    "آواز":   ("song, voice",                    "sound"),
    "نی":     ("ney (reed flute)",               "instrument"),
    "رود":    ("rud (stringed instrument)",      "instrument"),
    "دف":     ("daf (frame drum)",               "instrument"),
    "رقص":    ("dance",                          "practice"),
    "سماع":   ("sama' (mystic audition / dance)", "practice"),
    "دستان":  ("tune, song (dastan)",            "structure"),
    "کمانچه": ("kamancheh (bowed fiddle)",       "instrument"),
    "نغمه":   ("melody, song",                   "structure"),
    "سرود":   ("song, hymn; sang",               "sound"),
}

# ending sets
_N = ["", "ها", "ی", "ای", "یی", "ان", "ا", "ام", "ت", "ش", "م", "مان", "تان", "شان"]

# lemma -> extra explicit forms (beyond suffixes) and which suffixes apply
_SUFFIXES = {
    "مطرب":   ["", "ان", "ا", "ی", "ها", "م", "ش", "ت", "ای", "انه", "بچه", "بچگان", "بچگی"],
    "طرب":    ["", "ها", "ی", "ای", "یی", "ش", "م", "ت", "ناک", "انگیز", "خانه", "گاه", "فزا", "افزا", "نامه"],
    "بربط":   ["", "ها", "ی", "ای", "ش", "م", "زن", "ان"],
    "پرده":   ["", "ها", "ی", "ای", "یی", "ش", "م", "ت", "ان", "سرا", "ساز"],
    "چنگ":    ["", "ها", "ی", "ای", "یی", "ش", "م", "ت", "ان", "زن", "نواز", "مان"],
    "رباب":   ["", "ها", "ی", "ای", "ش", "م", "ت", "ان", "زن"],
    "بانگ":   ["", "ها", "ی", "ای", "یی", "ش", "م", "ت"],
    "آهنگ":   ["", "ها", "ی", "ای", "یی", "ش", "م", "ت", "ین", "ساز", "ان"],
    "صوت":    ["", "ها", "ی", "ش", "م", "ت", "ی"],
    "ساز":    ["", "ها", "ی", "ای", "یی", "ان"],  # no verb endings on purpose
    "آواز":   ["", "ها", "ی", "ای", "یی", "ش", "م", "ت", "ان", "خوان", "خوانی", "گر"],
    "نی":     ["", "ها", "ی"],  # handled specially below
    "رود":    ["", "ها", "ی", "ای", "ش", "م", "ت", "ان", "نواز", "زن"],
    "دف":     ["", "ها", "ی", "ای", "ش", "م", "ت", "ان", "زن", "زنان", "نواز", "کوب"],
    "رقص":    ["", "ها", "ی", "ای", "یی", "ان", "کنان", "ش", "م", "ت", "ید", "یدن", "ید", "یم", "ند", "د", "نده", "اندن"],
    "سماع":   ["", "ها", "ی", "ای", "ات", "ش", "م", "ت", "ان", "خانه"],
    "دستان":  ["", "ها", "ی", "ای", "سرا", "زن", "ش", "م", "ت", "ان"],
    "کمانچه": ["", "ها", "ی", "ای", "ش", "م", "ت", "زن", "کش"],
    "نغمه":   ["", "ها", "ی", "ای", "یی", "ات", "ش", "م", "ت", "سرا", "سرایی", "پرداز", "خوان", "ساز", "زن", "گر"],
    "سرود":   ["", "ها", "ی", "ای", "یی", "ش", "م", "ت", "ن", "ند", "ه", "یم", "ید", "ان", "خوان", "گو"],
}

# explicit extra surface forms (Arabic plurals, spelling variants, verbs, etc.)
_EXTRA = {
    "مطرب":  ["مطربا", "مطربان", "مطربی"],
    "بربط":  ["بربت", "بربتی", "بربطی"],
    "بانگ":  ["گلبانگ"],
    "صوت":   ["اصوات", "صوتی"],
    "نغمه":  ["نغمات"],
    "نی":    ["نی", "نای", "نایی", "نای‌ها", "نیها", "نایها", "نیی"],
    "رقص":   ["برقص", "برقصد", "برقصم", "برقصی", "برقصند", "برقصید", "رقاص", "رقاصی", "رقاصه", "رقصی"],
    "سماع":  ["سماعی"],
    "آواز":  ["آوازی"],
}


def build_forms():
    """Return {normalised form: lemma}."""
    forms = {}
    for lemma in BASE_WORDS:
        stem = norm_text(lemma).strip()
        for suf in _SUFFIXES[lemma]:
            f = norm_text(stem + suf).replace(" ", "")
            forms.setdefault(f, lemma)
        for extra in _EXTRA.get(lemma, []):
            f = norm_text(extra).replace(" ", "")
            forms.setdefault(f, lemma)
    # "نی" must be tightly controlled: only these tokens count.
    for f in list(forms):
        if forms[f] == "نی" and f not in {"نی", "نای", "نایی", "نیها", "نایها", "نیی", "ني"}:
            del forms[f]
    forms.setdefault("نی", "نی")
    forms.setdefault("نای", "نی")
    return forms


FORMS = build_forms()
STEMS = {norm_text(l).strip(): l for l in BASE_WORDS}
