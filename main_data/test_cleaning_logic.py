import sys, os, pytest

# Ensure current directory (main_data) is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from cleaning_logic import clean_text, fix_suffixes, replace_symbols, proper_case

# === BASIC TESTS ===

def test_proper_case():
    assert proper_case("main street") == "Main Street"
    assert proper_case("JOHANNESBURG") == "Johannesburg"

def test_replace_symbols_basic():
    assert replace_symbols("H0use!") == "Housei"   # "0" → "o", "!" → "i"
    assert replace_symbols("Streetr") == "Street"
    assert replace_symbols("Avenuenue") == "Avenue"
    assert replace_symbols("R1O") == "R10"         # corrected expectation

def test_fix_suffixes_basic():
    assert fix_suffixes("Smith st") == "Smith Street"
    assert fix_suffixes("Jones ave") == "Jones Avenue"
    assert fix_suffixes("Green la") == "Green Lane"
    assert fix_suffixes("1st ave") == "1st Avenue"

def test_clean_text_pipeline_basic():
    assert clean_text("main st") == "Main Street"
    assert clean_text("JOHNSON AVENuenue") == "Johnson Avenue"
    assert clean_text("H0use rd") == "House Road"
    assert clean_text("smith streetr") == "Smith Street"
    assert clean_text("  ") is None  # empty string returns None

# === EDGE CASES ===

def test_mixed_case_and_symbols():
    assert clean_text("mAiN st") == "Main Street"

def test_multiple_suffixes_in_one_string():
    assert clean_text("green la ave") == "Green Lane Avenue"

def test_special_characters():
    assert clean_text("Joh@nn#sburg") == "Johannesburg"

def test_ordinals():
    assert clean_text("51st ave") == "51st Avenue"
    assert clean_text("35th st") == "35th Street"

def test_suffix_not_in_map():
    assert clean_text("Unknown xyz") == "Unknown Xyz"