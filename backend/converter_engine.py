"""
Non-AI Deterministic Rule Engine for Lisan al Dawat (Alkanz / Kanzmarjan / Unicode) Conversion.
Replaces legacy double-character keyboard codes and Bohra extended codepoints with proper Unicode Lisan al Dawat characters.
"""

import re
from typing import Dict, Tuple, Optional

# Preset 1: Alkanz Normal Keyboard Layout + Bohra Font Mappings
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
    
    # Bohra / Alkanz extended Latin codepoint mappings
    "Ţ": "ے",
    "ţ": "ے",
    "Ṣ": "گ",
    "ṣ": "گ",
    
    # QWERTY double-key codes -> Unicode LSD
    ";;": "گ",
    "ss": "ے",
    "ee": "پ",
    "pp": "چ",
    "qq": "ٹ",
    "ww": "ں",
    "//": "ء",
    "''": "،",
    "\"\"": "؛"
}

ALKANZ_URDU_RULES: Dict[str, str] = {
    "ثث": "پ", "حح": "چ", "كك": "گ", "طط": "ٹ", "نن": "ں",
    "صص": "ژ", "ضض": "ڈ", "ظظ": "ڑ", "سس": "ے",
    "Ţ": "ے", "ţ": "ے", "Ṣ": "گ", "ṣ": "گ"
}

KANZMARJAN_RULES: Dict[str, str] = {
    "كك": "گ", "سس": "ے", "ثث": "پ", "حح": "چ", "طط": "ٹ", "نن": "ں",
    "Ţ": "ے", "ţ": "ے", "Ṣ": "گ", "ṣ": "گ",
    ";;": "گ", "ss": "ے", "ee": "پ", "pp": "چ", "qq": "ٹ", "ww": "ں"
}

AMIRI_URDU_RULES: Dict[str, str] = {
    "گ": "گ", "پ": "پ", "چ": "چ", "ٹ": "ٹ", "ے": "ے", "ں": "ں", "ڈ": "ڈ", "ڑ": "ڑ", "ژ": "ژ",
    "Ţ": "ے", "ţ": "ے", "Ṣ": "گ", "ṣ": "گ"
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


def rejoin_spaced_arabic_letters(text: str) -> str:
    """Rejoins isolated Arabic single letters separated by spaces (e.g. 'ت س ل س ل' -> 'تسلسل')."""
    if not text:
        return ""
    lines = text.split('\n')
    fixed = []
    for line in lines:
        if not line.strip():
            fixed.append("")
            continue
        tokens = line.strip().split()
        merged = []
        buffer = ""
        for tok in tokens:
            clean_t = re.sub(r'[^\w]', '', tok)
            has_arabic = any('\u0600' <= c <= '\u06ff' for c in clean_t)
            is_single_letter = has_arabic and len(clean_t) <= 1
            if is_single_letter:
                buffer += tok
            else:
                if buffer:
                    merged.append(buffer)
                    buffer = ""
                merged.append(tok)
        if buffer:
            merged.append(buffer)
        fixed.append(" ".join(merged))
    return "\n".join(fixed)


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
