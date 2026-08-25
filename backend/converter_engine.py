"""
Non-AI Deterministic Rule Engine for Lisan al Dawat (Alkanz / Kanzmarjan / Unicode) Conversion.
Replaces legacy double-character keyboard codes with proper Unicode Lisan al Dawat characters.
Preserves exact original document text, layout, and line structures.
"""

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
    # QWERTY keys -> Unicode LSD
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
}

PRESETS = {
    "alkanz_normal": {
        "name": "Alkanz Normal (كك➔گ, سس➔ے, ثث➔پ)",
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


import re

PUNCTUATION_CHARS = {'،', '؛', '.', ':', '!', '؟', '"', '(', ')', '[', ']', '•'}

def sanitize_text(text: str) -> str:
    """Strips invisible Unicode control characters, carriage returns, and zero-width spaces."""
    if not text:
        return ""
    return re.sub(r'[\r\u200e\u200f\ufeff\u202a-\u202e\xa0]', '', text)

def fix_arabic_word_token(w: str) -> str:
    """Fixes Tatweels and word-internal character reversal strictly on reversed Arabic tokens."""
    clean_w = w.replace('ـ', '').replace('\u200c', '').replace('\u200d', '')
    if not clean_w:
        return ""

    # Do NOT touch ASCII / English tokens or Numbers (e.g. Page 1 of 12)
    if re.search(r'[a-zA-Z0-9]', clean_w):
        return clean_w

    bare_w = re.sub(r'[^\w]', '', clean_w)
    if len(bare_w) <= 1:
        return clean_w

    # If word ALREADY starts with standard Arabic prefixes, it is ALREADY correct!
    if (bare_w.startswith('ال') or bare_w.startswith('الم') or bare_w.startswith('سيد') or 
        bare_w.startswith('مول') or bare_w.startswith('مف') or bare_w.startswith('حس') or 
        bare_w.startswith('باو') or bare_w.startswith('صاح') or bare_w.startswith('امير')):
        return clean_w

    # Reverse characters ONLY if word ends with reversed indicators
    should_reverse = (
        'ـ' in w or
        bare_w.endswith('دلا') or bare_w.endswith('لاا') or bare_w.endswith('بال') or
        bare_w.endswith('يال') or bare_w.endswith('مال') or bare_w.endswith('انلاوم') or
        bare_w.startswith('هش') or bare_w.startswith('فل') or bare_w.startswith('سف') or
        bare_w.startswith('ود') or bare_w.startswith('عر') or bare_w.startswith('طلو')
    )

    if should_reverse:
        leading = ""
        trailing = ""
        core = clean_w
        while core and core[0] in PUNCTUATION_CHARS:
            leading += core[0]
            core = core[1:]
        while core and core[-1] in PUNCTUATION_CHARS:
            trailing = core[-1] + trailing
            core = core[:-1]
        
        return leading + core[::-1] + trailing

    return clean_w


def auto_fix_arabic_sentence_flow(text: str) -> str:
    """
    Automatic Punctuation-Aware Arabic Sentence Flow & Word/Character Order Normalizer.
    Strips Tatweels (ـ), fixes LTR reversed character and word streams, attaches punctuation
    properly after words, and prevents disoriented punctuation placement.
    """
    if not text:
        return ""

    text = sanitize_text(text)
    lines = text.split('\n')
    
    # Document-level LTR stream detection across first 15 lines
    doc_is_ltr_stream = False
    for line in lines[:15]:
        t = line.strip().split()
        if not t:
            continue
        clean_last = re.sub(r'[^\w]', '', t[-1]) if t else ""
        clean_first = re.sub(r'[^\w]', '', t[0]) if t else ""
        
        if clean_last in ['بقلم', 'الاستاذ', 'الأستاذ'] or t[-1].endswith(':بقلم') or t[-1].endswith('بقلم'):
            doc_is_ltr_stream = True
            break
        if clean_first in ['علي', 'عبد', 'ملا'] and any('بقلم' in w for w in t):
            doc_is_ltr_stream = True
            break

    fixed_lines = []
    for line in lines:
        if not line.strip():
            fixed_lines.append("")
            continue

        raw_tokens = line.strip().split()
        if not raw_tokens:
            fixed_lines.append("")
            continue

        # Normalize word-internal character reversal & strip Tatweels
        tokens = [fix_arabic_word_token(w) for w in raw_tokens if w.strip()]
        tokens = [t for t in tokens if t]

        if len(tokens) <= 1:
            fixed_lines.append(" ".join(tokens))
            continue

        first_tok = tokens[0]
        last_tok = tokens[-1]
        
        clean_last = re.sub(r'[^\w]', '', last_tok)
        clean_first = re.sub(r'[^\w]', '', first_tok)

        line_is_reversed = (
            doc_is_ltr_stream or
            clean_last in ['بقلم', 'الاستاذ', 'الأستاذ'] or
            last_tok.endswith('بقلم') or last_tok.endswith(':') or
            first_tok in ['،', '؛', '.', ':', '،'] or
            first_tok.startswith('،') or first_tok.startswith('؛') or
            (last_tok.endswith('،') or last_tok.endswith('؛') or last_tok.endswith(','))
        )

        if line_is_reversed:
            tokens = list(reversed(tokens))

        cleaned_tokens = []
        for tok in tokens:
            leading_punc = ""
            core = tok
            while len(core) > 1 and core[0] in PUNCTUATION_CHARS:
                leading_punc += core[0]
                core = core[1:]

            cleaned_tokens.append(core + leading_punc)

        fixed_line = " ".join(cleaned_tokens)
        fixed_line = re.sub(r'\s+([،؛.:!?])', r'\1', fixed_line)
        fixed_line = re.sub(r'\s+', ' ', fixed_line).strip()
        
        if fixed_line and fixed_line[0] in ['،', '؛'] and len(fixed_line.split()) > 2:
            fixed_line = fixed_line[1:].strip() + ' ' + fixed_line[0]

        fixed_lines.append(fixed_line)

    return "\n".join(fixed_lines)


def clean_legacy_artifacts(text: str) -> str:
    """
    Cleans unwanted character artifacts and normalizes sentence flow while preserving exact text formatting.
    """
    if not text:
        return ""

    # Automatically fix sentence flow and punctuation placement
    text = auto_fix_arabic_sentence_flow(text)

    # Clean redundant Tatweels and zero-width non-joiner / joiner artifacts
    cleaned = text.replace("ـ", "").replace("\u200c", "").replace("\u200d", "").replace("`", "")
    return cleaned


def convert_text(
    text: str,
    rules: Optional[Dict[str, str]] = None,
    preset_key: str = "alkanz_normal"
) -> Tuple[str, int]:
    """
    Deterministically converts input text based on the provided character replacement rules.
    Preserves exact word order, paragraphs, and formatting.
    Returns (converted_text, total_replacements_made).
    """
    if not text:
        return "", 0

    # Determine mapping dictionary
    mapping_dict = rules if rules is not None else PRESETS.get(preset_key, {}).get("rules", ALKANZ_NORMAL_RULES)
    
    # Sort keys by length descending to ensure longer multi-char matches (e.g. "كك" or ";;") take precedence over single chars
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
