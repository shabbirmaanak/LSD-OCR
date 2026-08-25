"""
Non-AI Deterministic Rule Engine for Lisan al Dawat (Alkanz / Kanzmarjan / Unicode) Conversion.
Replaces legacy double-character keyboard codes with proper Unicode Lisan al Dawat characters.
100% pure, predictable, zero-distortion conversion.
"""

import re
from typing import Dict, Tuple, Optional

# Preset 1: Alkanz Normal Keyboard Layout
ALKANZ_NORMAL_RULES: Dict[str, str] = {
    # Double Arabic character codes -> Unicode LSD
    "كك": "گ",
    "سس": "ے",
    "ثث": "پ",
    "حح": "چ",
    "جج": "چ",
    "طط": "ٹ",
    "نن": "ں",
    "صص": "ژ",
    "ضض": "ڈ",
    "ظظ": "ڑ",
    "؛": "چهے",
    # Legacy Al Kanz / Bohra PUA & ligature glyphs
    "善": "هو",
    "善": "هو",
    "啣": "هو",
    "周": "الله",
    "呈": "رضي الله عنه",
    "吸": "رحمة الله عليه",
    "咞": "عليه السلام",
    "吆": "صلعم",
    "叱": "هو",
    # QWERTY keys -> Unicode LSD
    ";;": "گ",
    "ss": "ے",
    "ee": "پ",
    "pp": "چ",
    "qq": "ٹ",
    "ww": "ں",
    "T": "ے",
    "t": "ے",
    "//": "ء",
    "''": "،",
    "\"\"": "؛"
}

ALKANZ_URDU_RULES: Dict[str, str] = {
    "ثث": "پ", "حح": "چ", "كك": "گ", "طط": "ٹ", "نن": "ں",
    "صص": "ژ", "ضض": "ڈ", "ظظ": "ڑ", "سس": "ے", "T": "ے", "t": "ے", "善": "هو"
}

KANZMARJAN_RULES: Dict[str, str] = {
    "كك": "گ", "سس": "ے", "ثث": "پ", "حح": "چ", "طط": "ٹ", "نن": "ں",
    ";;": "گ", "ss": "ے", "ee": "پ", "pp": "چ", "qq": "ٹ", "ww": "ں", "T": "ے", "t": "ے", "善": "هو"
}

AMIRI_URDU_RULES: Dict[str, str] = {
    "گ": "گ", "پ": "پ", "چ": "چ", "ٹ": "ٹ", "ے": "ے", "ں": "ں", "ڈ": "ڈ", "ڑ": "ڑ", "ژ": "ژ", "T": "ے", "t": "ے", "善": "هو"
}

PRESETS = {
    "alkanz_normal": {"name": "Alkanz Normal", "rules": ALKANZ_NORMAL_RULES},
    "alkanz_urdu": {"name": "Alkanz Urdu", "rules": ALKANZ_URDU_RULES},
    "kanzmarjan": {"name": "Kanzmarjan Normal", "rules": KANZMARJAN_RULES},
    "amiri_urdu": {"name": "Amiri Urdu", "rules": AMIRI_URDU_RULES}
}

PUNCTUATION_CHARS = {'،', '؛', '.', ':', '!', '؟', '"', '(', ')', '[', ']', '•'}

def sanitize_text(text: str) -> str:
    """Strips invisible Unicode control characters and normalizes carriage returns."""
    if not text:
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return re.sub(r'[\u200e\u200f\ufeff\u202a-\u202e\xa0]', '', text)


def reverse_word_flow(line: str) -> str:
    """Reverses word sequence for LTR word-reversed PDF streams."""
    if not line or not line.strip():
        return ""

    tokens = line.strip().split()
    if len(tokens) <= 1:
        return line.strip()

    tokens.reverse()

    cleaned = []
    for tok in tokens:
        leading = ""
        core = tok
        while len(core) > 1 and core[0] in PUNCTUATION_CHARS:
            leading += core[0]
            core = core[1:]
        cleaned.append(core + leading)

    res = " ".join(cleaned)
    res = re.sub(r'\s+([،؛.:!?])', r'\1', res)
    return re.sub(r'\s+', ' ', res).strip()


def convert_text(
    text: str,
    rules: Optional[Dict[str, str]] = None,
    preset_key: str = "alkanz_normal"
) -> Tuple[str, int]:
    """Pure deterministic conversion replacing legacy keys with Unicode LSD."""
    if not text:
        return "", 0

    sanitized = sanitize_text(text)
    if rules is not None and isinstance(rules, dict) and len(rules) > 0:
        mapping_dict = rules
    elif preset_key in PRESETS:
        preset_val = PRESETS[preset_key]
        if isinstance(preset_val, dict) and "rules" in preset_val:
            mapping_dict = preset_val["rules"]
        else:
            mapping_dict = preset_val
    else:
        mapping_dict = ALKANZ_NORMAL_RULES
    sorted_patterns = sorted(mapping_dict.keys(), key=lambda k: len(k), reverse=True)

    converted_text = sanitized
    total_replacements = 0

    for source_pat in sorted_patterns:
        target_pat = mapping_dict[source_pat]
        if not source_pat:
            continue

        count = converted_text.count(source_pat)
        if count > 0:
            converted_text = converted_text.replace(source_pat, target_pat)
            total_replacements += count

    return converted_text, total_replacements
