# cleaning_logic.py

import re

# ANSI colors (normal intensity)
ANSI_RESET = "\033[0m"
ANSI_CYAN = "\033[36m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN = "\033[32m"
ANSI_MAGENTA = "\033[35m"
ANSI_RED = "\033[31m"

# -------------------------
# Debug helpers (Phase 5 only)
# -------------------------

def dbg_header(phase_name):
    print(f"{ANSI_CYAN}-------------------------{ANSI_RESET}")
    print(f"{ANSI_CYAN}{phase_name}{ANSI_RESET}")

def dbg_before(text):
    print(f"{ANSI_YELLOW}BEFORE:{ANSI_RESET} {text}")

def dbg_after(text):
    print(f"{ANSI_GREEN}AFTER:{ANSI_RESET} {text}")
    print()

def dbg_rule(rule_desc, before, after):
    print(f"{ANSI_MAGENTA}RULE MATCHED:{ANSI_RESET} {rule_desc}")
    print(f"{ANSI_YELLOW}  BEFORE:{ANSI_RESET} {before}")
    print(f"{ANSI_GREEN}  AFTER:{ANSI_RESET} {after}")
    print()

# -------------------------
# Helper: case-insensitive literal replace
# -------------------------

def _ci_replace(text, old, new):
    pattern = re.compile(re.escape(old), flags=re.IGNORECASE)
    return pattern.sub(new, text)

# -------------------------
# Phase 1 -- NO DEBUG
# -------------------------

def phase1_symbols(text):
    t = text
    t = re.sub(r"\s{2,}", " ", t)
    t = re.sub(r"\s*,\s*", ", ", t)
    return t

# -------------------------
# Phase 2 -- NO DEBUG
# -------------------------

def phase2_suffixes(text):
    t = text
    t = re.sub(r"\bRd\b", "Road", t, flags=re.IGNORECASE)
    t = re.sub(r"\bSt\b", "Street", t, flags=re.IGNORECASE)
    return t

# -------------------------
# Phase 3 -- NO DEBUG
# -------------------------

def phase3_propercase(text):
    def proper_word(w):
        if not w:
            return w
        return w[0].upper() + w[1:].lower()
    return " ".join(proper_word(w) for w in text.split())

# -------------------------
# Phase 4 -- NO DEBUG
# -------------------------

def phase4_prefixes(text):
    return re.sub(r"\bN\b", "North", text, flags=re.IGNORECASE)

# -------------------------
# Phase 5 -- DEBUG ENABLED
# -------------------------

def phase5_literals(text):
    dbg_header("PHASE 5 -- LITERAL / SPECIAL-CASE FIXES")
    dbg_before(text)

    t = text

    # (m ==> (M
    new_t = re.sub(r"\(m", "(M", t, flags=re.IGNORECASE)
    if new_t != t:
        dbg_rule("(m ==> (M", t, new_t)
        t = new_t

    # (n ==> (N
    new_t = re.sub(r"\(n", "(N", t, flags=re.IGNORECASE)
    if new_t != t:
        dbg_rule("(n ==> (N)", t, new_t)
        t = new_t

    # (r ==> (R
    new_t = re.sub(r"\(r", "(R", t, flags=re.IGNORECASE)
    if new_t != t:
        dbg_rule("(r ==> (R)", t, new_t)
        t = new_t

    # -------------------------
    # NEW Mt.<letter> RULE
    # -------------------------
    new_t = re.sub(
        r"\bMt\.([a-z])",
        lambda m: "Mt." + m.group(1).upper(),
        t,
        flags=re.IGNORECASE
    )
    if new_t != t:
        dbg_rule("Mt.<letter> ==> Mt.<Uppercase letter>", t, new_t)
        t = new_t

    # -------------------------
    # NEW RULES (24/12/2025)
    # -------------------------

    # (Mi2) ==> (M12)
    new_t = re.sub(r"\(mi2\)", "(M12)", t, flags=re.IGNORECASE)
    if new_t != t:
        dbg_rule("(Mi2) ==> (M12)", t, new_t)
        t = new_t

    # (Ni) ==> (N1)
    new_t = re.sub(r"\(ni\)", "(N1)", t, flags=re.IGNORECASE)
    if new_t != t:
        dbg_rule("(Ni) ==> (N1)", t, new_t)
        t = new_t

    # N2/m3 ==> N2/M3
    new_t = re.sub(r"\bN2/m3\b", "N2/M3", t, flags=re.IGNORECASE)
    if new_t != t:
        dbg_rule("N2/m3 ==> N2/M3", t, new_t)
        t = new_t

    # Ni ==> N1 (standalone)
    new_t = re.sub(r"\bNi\b", "N1", t, flags=re.IGNORECASE)
    if new_t != t:
        dbg_rule("Ni ==> N1", t, new_t)
        t = new_t

    # Pres.brand ==> Pres.Brand
    new_t = _ci_replace(t, "Pres.brand", "Pres.Brand")
    if new_t != t:
        dbg_rule("Pres.brand ==> Pres.Brand", t, new_t)
        t = new_t

    # Pres.steyn ==> Pres.Steyn
    new_t = _ci_replace(t, "Pres.steyn", "Pres.Steyn")
    if new_t != t:
        dbg_rule("Pres.steyn ==> Pres.Steyn", t, new_t)
        t = new_t

    # -------------------------
    # Existing literal rules
    # -------------------------

    new_t = _ci_replace(t, "Pres.reitz Street", "Pres.Reitz Street")
    if new_t != t:
        dbg_rule("Pres.reitz Street ==> Pres.Reitz Street", t, new_t)
        t = new_t

    new_t = _ci_replace(t, "D.f.malan", "D.F. Malan")
    if new_t != t:
        dbg_rule("D.f.malan ==> D.F. Malan", t, new_t)
        t = new_t

    new_t = _ci_replace(t, "Stormvoel", "Stormvoel")
    if new_t != t:
        dbg_rule("Stormvoel ==> Stormvoel", t, new_t)
        t = new_t

    dbg_after(t)
    return t

# -------------------------
# Phase 6 -- NO DEBUG
# -------------------------

def phase6_ordinals(text):
    return re.sub(
        r"\b([0-9]+)(St|Nd|Rd|Th)\b",
        lambda m: m.group(1) + m.group(2).lower(),
        text,
        flags=re.IGNORECASE
    )

# -------------------------
# Phase 7 -- NO DEBUG
# -------------------------

def phase7_finalize(text):
    return text.strip()

# -------------------------
# Public API
# -------------------------

def clean_str_name(text):
    t = text if text is not None else ""

    # Correct pipeline order
    t = phase1_symbols(t)
    t = phase2_suffixes(t)
    t = phase3_propercase(t)
    t = phase4_prefixes(t)
    t = phase5_literals(t)   # ONLY PHASE WITH DEBUG
    t = phase6_ordinals(t)
    t = phase7_finalize(t)

    return t

def clean_suburb(text):
    t = text if text is not None else ""
    t = t.strip()

    def proper_word(w):
        if not w:
            return w
        return w[0].upper() + w[1:].lower()

    return " ".join(proper_word(w) for w in t.split())