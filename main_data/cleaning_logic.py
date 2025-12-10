import re

# === SYMBOL REPLACEMENTS ===
_symbol_map = {
    "@": "a",
    "0": "o",
    "!": "i",
    "#": "e",
    "'S": "'s",
    "Streetr": "Street",
    "Avenuenue": "Avenue",
    "(R1O": "(R10",
    "(R31O": "(R310",
    "1O": "10",
}

# === SUFFIX FIXES ===
_suffix_map = {
    "rd": "Road",
    "st": "Street",
    "str": "Street",
    "ave": "Avenue",
    "cl": "Close",
    "ter": "Terrace",
    "cr": "Crescent",
    "cir": "Circle",
    "sq": "Square",
    "blvd": "Boulevard",
    "la": "Lane",
    "dr": "Drive",
    "ext": "Extension",
    "pl": "Place",
    "wk": "Walk",
    "ct": "Court",
}

# Full words we should NOT re-expand
_full_words = {"street","avenue","road","drive","lane","boulevard","court","place","terrace","crescent","circle","square","close","extension","walk"}

# Ordinals we want to preserve exactly
_ordinals = {
    "1st","2nd","3rd","4th","5th","6th","7th","8th","9th",
    "10th","11th","12th","13th","14th","15th","16th","17th",
    "35th","51st"
}

def proper_case(value: str) -> str:
    """Convert to proper case (title case), preserving ordinals."""
    words = value.split()
    fixed = []
    for w in words:
        lw = w.lower()
        if lw in _ordinals:
            fixed.append(lw)  # keep ordinal exactly
        else:
            fixed.append(w.capitalize())
    return " ".join(fixed)

def replace_symbols(value: str) -> str:
    """Replace common symbol substitutions safely (case-insensitive)."""
    txt = value
    for bad, good in _symbol_map.items():
        pattern = re.compile(re.escape(bad), flags=re.IGNORECASE)
        txt = pattern.sub(good, txt)
    return txt

def fix_suffixes(value: str) -> str:
    """Replace suffix abbreviations with full words (case-insensitive), skip full words."""
    words = value.split()
    fixed = []
    for w in words:
        lw = w.lower()
        if lw in _full_words:
            fixed.append(w)  # already a full word, leave it
        elif lw in _suffix_map:
            fixed.append(_suffix_map[lw])
        else:
            fixed.append(w)
    return " ".join(fixed)

def clean_text(value: str) -> str:
    """Full cleaning pipeline for a single string."""
    if not value or str(value).strip() == "":
        return None
    txt = str(value).strip()
    # Step 1: Replace symbols inline
    txt = replace_symbols(txt)
    # Step 2: Fix suffixes (skip full words)
    txt = fix_suffixes(txt)
    # Step 3: Proper Case at the end
    txt = proper_case(txt)
    return txt