"""
Non-AI Deterministic Rule Engine for Lisan al Dawat (Alkanz / Kanzmarjan / Unicode) Conversion.
Replaces legacy double-character keyboard codes with proper Unicode Lisan al Dawat characters.
Preserves exact original document text, layout, and line structures with ZERO distortion.
"""

import re
from typing import Dict, List, Tuple, Optional

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

# Preset 2: Alkanz Urdu Keyboard Layout
ALKANZ_URDU_RULES: Dict[str, str] = {
    "ثث": "پ",
    "حح": "چ",
    "كك": "گ",
    "طط": "ٹ",
    "نن": "ں",
    "صص": "ژ",
    "ضض": "ڈ",
    "ظظ": "ڑ",
    "سس": "ے",
    "T": "ے",
    "t": "ے",
    "善": "هو",
}

# Preset 3: Kanzmarjan Normal Keyboard Layout
KANZMARJAN_RULES: Dict[str, str] = {
    "كك": "گ",
    "سس": "ے",
    "ثث": "پ",
    "حح": "چ",
    "طط": "ٹ",
    "نن": "ں",
    ";;": "گ",
    "ss": "ے",
    "ee": "پ",
    "pp": "چ",
    "qq": "ٹ",
    "ww": "ں",
    "T": "ے",
    "t": "ے",
    "善": "هو",
}

# Preset 4: Amiri Urdu Layout
AMIRI_URDU_RULES: Dict[str, str] = {
    "گ": "گ",
    "پ": "پ",
    "چ": "چ",
    "ٹ": "ٹ",
    "ے": "ے",
    "ں": "ں",
    "ڈ": "ڈ",
    "ڑ": "ڑ",
    "ژ": "ژ",
    "T": "ے",
    "t": "ے",
    "善": "هو",
}

PRESETS = {
    "alkanz_normal": {
        "name": "Alkanz Normal (كك➔گ, سس➔ے, ثث➔پ, T➔ے)",
        "rules": ALKANZ_NORMAL_RULES
    },
    "alkanz_urdu": {
        "name": "Alkanz Urdu Layout",
        "rules": ALKANZ_URDU_RULES
    },
    "kanzmarjan": {
        "name": "Kanzmarjan Normal Layout",
        "rules": KANZMARJAN_RULES
    },
    "amiri_urdu": {
        "name": "Amiri Urdu Standard",
        "rules": AMIRI_URDU_RULES
    }
}

PUNCTUATION_CHARS = {'،', '؛', '.', ':', '!', '؟', '"', '(', ')', '[', ']', '•'}

def sanitize_text(text: str) -> str:
    """Strips invisible Unicode control characters and normalizes carriage returns."""
    if not text:
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return re.sub(r'[\u200e\u200f\ufeff\u202a-\u202e\xa0]', '', text)


def fix_word_reversed_line(line: str) -> str:
    """Reverses word sequence for LTR word-reversed PDF streams (e.g., 'علي عبد ملا ... : بقلم' -> 'بقلم : ... ملا عبد علي')."""
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


def strip_punc(s: str) -> str:
    """Strips punctuation and symbols while retaining Arabic and alphanumeric characters."""
    if not s:
        return ""
    return re.sub(r'[^\w\u0600-\u06ff]', '', s)


def is_arabic_word_reversed(text: str) -> bool:
    """Detects explicit LTR word stream reversal in Bohra legacy PDF text extractions."""
    if not text:
        return False
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return False

    for line in lines[:20]:
        tokens = line.split()
        if not tokens or len(tokens) < 2:
            continue

        clean_last = strip_punc(tokens[-1])
        clean_first = strip_punc(tokens[0])

        if clean_last in ["بقلم", "الاستاذ", "الشيخ"] or clean_first in ["علي", "عبد", "ملا"] and "بقلم" in line:
            return True

    return False


def auto_fix_arabic_sentence_flow(text: str) -> str:
    """Normalizes PDF streams if word-sequence reversal is present."""
    if not text:
        return ""

    text = sanitize_text(text)
    if not is_arabic_word_reversed(text):
        return text

    lines = text.split('\n')
    fixed_lines = []
    for line in lines:
        if not line.strip():
            fixed_lines.append("")
        else:
            fixed_lines.append(fix_word_reversed_line(line))

    return "\n".join(fixed_lines)


def convert_text(
    text: str,
    rules: Optional[Dict[str, str]] = None,
    preset_key: str = "alkanz_normal"
) -> Tuple[str, int]:
    """Deterministically converts input text based on mapping rules without altering text structure."""
    if not text:
        return "", 0

    sanitized = sanitize_text(text)
    mapping_dict = rules if rules is not None else PRESETS.get(preset_key, {}).get("rules", ALKANZ_NORMAL_RULES)
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
