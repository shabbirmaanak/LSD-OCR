"""
Non-AI Deterministic Rule Engine for Lisan al Dawat (Alkanz / Kanzmarjan / Unicode) Conversion.
Replaces legacy double-character keyboard codes with proper Unicode Lisan al Dawat characters.
Preserves exact original document text, layout, and line structures.
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
    """Strips invisible Unicode control characters, carriage returns, and zero-width spaces."""
    if not text:
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return re.sub(r'[\u200e\u200f\ufeff\u202a-\u202e\xa0]', '', text)

def fix_reversed_arabic_line(line: str) -> str:
    """Reverses LTR Arabic character streams while preserving English text & numbers intact."""
    clean_line = line.replace('ـ', '').replace('\u200c', '').replace('\u200d', '')
    if not clean_line.strip():
        return ""
    
    if re.match(r'^\s*Page\s+\d+\s+of\s+\d+\s*$', clean_line, re.IGNORECASE):
        return clean_line.strip()

    has_arabic = any('\u0600' <= c <= '\u06ff' for c in clean_line)
    if not has_arabic:
        return clean_line.strip()

    placeholders = {}
    def replacer(match):
        key = f"__ENG{len(placeholders)}__"
        placeholders[key] = match.group(0)
        return key

    protected = re.sub(r'[a-zA-Z]+', replacer, clean_line)
    rev = protected[::-1]
    
    for key, val in placeholders.items():
        rev_key = key[::-1]
        rev = rev.replace(rev_key, val)
        
    return rev.strip()


def rejoin_spaced_arabic_letters(line: str) -> str:
    """Rejoins isolated Arabic letters separated by inter-letter spaces inside words."""
    clean_line = line.replace('ـ', '').replace('\u200c', '').replace('\u200d', '')
    if not clean_line.strip():
        return ""
    
    tokens = clean_line.strip().split()
    merged = []
    buffer = ""

    for tok in tokens:
        clean_t = re.sub(r'[^\w]', '', tok)
        has_arabic = any('\u0600' <= c <= '\u06ff' for c in clean_t)
        is_letter_piece = has_arabic and len(clean_t) <= 2 and not any(c in PUNCTUATION_CHARS for c in tok)

        if is_letter_piece:
            buffer += tok
        else:
            if buffer:
                merged.append(buffer)
                buffer = ""
            merged.append(tok)

    if buffer:
        merged.append(buffer)

    return " ".join(merged)


def fix_word_reversed_line(line: str) -> str:
    """Reverses word sequence for LTR word-reversed PDF streams (e.g., 'علي عبد ملا ... : بقلم' -> 'بقلم : ... ملا عبد علي')."""
    clean_line = line.replace('ـ', '').replace('\u200c', '').replace('\u200d', '').replace('`', '')
    if not clean_line.strip():
        return ""

    tokens = clean_line.strip().split()
    if len(tokens) <= 1:
        return clean_line.strip()

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
    res = re.sub(r'\s+', ' ', res).strip()

    if res and res[0] in ['،', '؛'] and len(res.split()) > 2:
        res = res[1:].strip() + ' ' + res[0]

    return res


def strip_punc(s: str) -> str:
    """Strips punctuation and symbols while retaining Arabic and alphanumeric characters."""
    if not s:
        return ""
    return re.sub(r'[^\w\u0600-\u06ff]', '', s)


def is_arabic_word_reversed(text: str) -> bool:
    """Detects multi-signal LTR word stream reversal in Arabic/LSD documents."""
    if not text:
        return False
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return False
    
    score = 0
    keywords_end = {"بقلم", "الاستاذ", "الشيخ", "شهر", "عالم", "اسلام", "ربيع", "مؤمنين", "علي", "عبد", "ملا", "چاول", "شكر", "دلكشي", "انار", "صلوات", "تناول", "رسول", "تلاوت", "تعليم"}
    
    for line in lines[:30]:
        tokens = line.split()
        if not tokens:
            continue
        
        last_tok = strip_punc(tokens[-1])
        first_tok = strip_punc(tokens[0])
        
        if last_tok in keywords_end or any(k in last_tok for k in ["بقلم", "شهر", "عالم", "ربيع", "اسلام", "مؤمنين"]):
            score += 2
        if first_tok in {"ائي", "ال", "تو", "ان", "ن", "واسط", "چ", "علي", "عبد", "ملا"}:
            score += 1

    return score >= 1


def auto_fix_arabic_sentence_flow(text: str) -> str:
    """
    Automatic Punctuation-Aware Arabic Sentence Flow & Word/Character Order Normalizer.
    Supports Type A (LTR Reversed Character Streams), Type B (Disconnected Inter-Letter Spaces),
    and Type C (Word-Sequence LTR Reversed Streams e.g. 'علي عبد ملا ... : بقلم').
    """
    if not text:
        return ""

    text = sanitize_text(text)
    lines = text.split('\n')

    doc_is_word_reversed = is_arabic_word_reversed(text)

    fixed_lines = []
    for line in lines:
        clean_line = line.replace('ـ', '').replace('\u200c', '').replace('\u200d', '').replace('`', '')
        if not clean_line.strip():
            fixed_lines.append("")
            continue

        tokens = clean_line.strip().split()
        if not tokens:
            fixed_lines.append("")
            continue

        first_word = strip_punc(tokens[0])
        last_word = strip_punc(tokens[-1])

        # 1. Check for Type A (Character Reversed Stream e.g. 'لمضم' or 'يـعالدلا')
        is_truly_char_reversed = (
            'لمضم' in clean_line or 'يـعالدلا' in clean_line or
            first_word in ['لمضم', 'يـعالدلا'] or
            (last_word.endswith('دلا') and not first_word.startswith('ال'))
        )

        if is_truly_char_reversed:
            fixed_lines.append(fix_reversed_arabic_line(line))
            continue

        # 2. Check for Type C (Word Sequence Reversed Stream)
        if doc_is_word_reversed or last_word in ['بقلم', 'الاستاذ', 'الشيخ'] or last_word.endswith('بقلم'):
            fixed_lines.append(fix_word_reversed_line(line))
            continue

        # 3. Check for Type B (Disconnected Inter-Letter Spaces: e.g., 'ت س ل س ل' -> 'تسلسل')
        single_letter_count = sum(1 for t in tokens if len(re.sub(r'[^\w]', '', t)) == 1 and any('\u0600' <= c <= '\u06ff' for c in t))
        if single_letter_count >= 3:
            fixed_lines.append(rejoin_spaced_arabic_letters(line))
        else:
            fixed_lines.append(clean_line.strip())

    return "\n".join(fixed_lines)


def clean_legacy_artifacts(text: str) -> str:
    """Cleans unwanted character artifacts and normalizes sentence flow."""
    if not text:
        return ""

    text = auto_fix_arabic_sentence_flow(text)
    cleaned = text.replace("ـ", "").replace("\u200c", "").replace("\u200d", "").replace("`", "")
    return cleaned


def convert_text(
    text: str,
    rules: Optional[Dict[str, str]] = None,
    preset_key: str = "alkanz_normal"
) -> Tuple[str, int]:
    """Deterministically converts input text based on mapping rules."""
    if not text:
        return "", 0

    mapping_dict = rules if rules is not None else PRESETS.get(preset_key, {}).get("rules", ALKANZ_NORMAL_RULES)
    sorted_patterns = sorted(mapping_dict.keys(), key=lambda k: len(k), reverse=True)
    
    converted_text = clean_legacy_artifacts(text)
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
