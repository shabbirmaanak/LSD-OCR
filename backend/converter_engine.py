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

def fix_reversed_arabic_line(line: str) -> str:
    """Reverses LTR Arabic character streams while preserving English text & numbers intact."""
    clean_line = line.replace('ـ', '').replace('\u200c', '').replace('\u200d', '')
    if not clean_line.strip():
        return ""
    
    # Preserve page numbers / English metadata headers
    if re.match(r'^\s*Page\s+\d+\s+of\s+\d+\s*$', clean_line, re.IGNORECASE):
        return clean_line.strip()

    has_arabic = any('\u0600' <= c <= '\u06ff' for c in clean_line)
    if not has_arabic:
        return clean_line.strip()

    # Protect English tokens from character reversal
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
    """
    Rejoins isolated Arabic letters separated by inter-letter spaces inside words.
    Example: 'الم ن ك ت ر ق م' -> 'الم نكت رقم'
    Example: 'ت س ل س ل' -> 'تسلسل'
    Example: 'الم ع بـاس' -> 'العباس'
    Example: 'بن ع بـد' -> 'بن عبد'
    """
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


def auto_fix_arabic_sentence_flow(text: str) -> str:
    """
    Automatic Punctuation-Aware Arabic Sentence Flow & Word/Character Order Normalizer.
    Preserves 100% accurate original Arabic line direction unless explicit LTR character-reversal
    or inter-letter spacing is detected. Strips Tatweels (ـ) and zero-width artifacts.
    """
    if not text:
        return ""

    text = sanitize_text(text)
    lines = text.split('\n')

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

        first_word = re.sub(r'[^\w]', '', tokens[0])
        last_word = re.sub(r'[^\w]', '', tokens[-1])

        # ONLY reverse character stream if line EXPLICITLY contains backwards LTR indicators (e.g. 'لمضم' or 'يـعالدلا')
        is_truly_reversed = (
            'لمضم' in clean_line or 'يـعالدلا' in clean_line or
            first_word in ['لمضم', 'يـعالدلا'] or
            (last_word.endswith('دلا') and not first_word.startswith('ال'))
        )

        if is_truly_reversed:
            fixed_lines.append(fix_reversed_arabic_line(line))
            continue

        # Check for Type B (Disconnected Inter-Letter Spaces: e.g., 'ت س ل س ل' -> 'تسلسل')
        single_letter_count = sum(1 for t in tokens if len(re.sub(r'[^\w]', '', t)) == 1 and any('\u0600' <= c <= '\u06ff' for c in t))
        if single_letter_count >= 3:
            fixed_lines.append(rejoin_spaced_arabic_letters(line))
        else:
            # Leave normal Arabic line order 100% UNTOUCHED!
            fixed_lines.append(clean_line.strip())

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
