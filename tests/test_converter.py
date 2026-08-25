"""
Automated unit tests for Non-AI Alkanz / Unicode Lisan al Dawat converter engine.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.converter_engine import convert_text, ALKANZ_NORMAL_RULES


def test_alkanz_double_character_mappings():
    # Test كك -> گ
    res, count = convert_text("ككتاب", preset_key="alkanz_normal")
    assert res == "گتاب"
    assert count == 1

    # Test سس -> ے
    res, count = convert_text("سسند", preset_key="alkanz_normal")
    assert res == "ےند"
    assert count == 1

    # Test ثث -> پ
    res, count = convert_text("ثثول", preset_key="alkanz_normal")
    assert res == "پول"
    assert count == 1

    # Test حح -> چ
    res, count = convert_text("ححتطبيق", preset_key="alkanz_normal")
    assert res == "چتطبيق"
    assert count == 1

    # Test طط -> ٹ
    res, count = convert_text("ططقانون", preset_key="alkanz_normal")
    assert res == "ٹقانون"
    assert count == 1

    # Test نن -> ں
    res, count = convert_text("ننستقبل", preset_key="alkanz_normal")
    assert res == "ںستقبل"
    assert count == 1

    # Test ؛ -> چهے
    res, count = convert_text("كلمة؛اخيرة", preset_key="alkanz_normal")
    assert res == "كلمةچهےاخيرة"
    assert count == 1

    # Test جج -> چ
    res, count = convert_text("ججملة", preset_key="alkanz_normal")
    assert res == "چملة"
    assert count == 1


def test_qwerty_key_mappings():
    # Test ;; -> گ, ss -> ے, ee -> پ, pp -> چ, qq -> ٹ, ww -> ں
    raw = ";; ss ee pp qq ww"
    res, count = convert_text(raw, preset_key="alkanz_normal")
    assert res == "گ ے پ چ ٹ ں"
    assert count == 6


def test_custom_rules_override():
    custom = {"abc": "xyz", "foo": "bar"}
    res, count = convert_text("abc test foo", rules=custom)
    assert res == "xyz test bar"
    assert count == 2
