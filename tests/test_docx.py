"""
Unit tests for Word (.docx) generator with RTL XML properties.
"""

import sys
import os
import io
from docx import Document

# Ensure root is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.docx_generator import generate_lsd_docx


def test_docx_generation():
    sample_pages = [
        {
            "page_num": 1,
            "text": "بسم الله الرحمن الرحيم\nاللسان الدعوة المباركة نى عظمت اور شان انى بقا نى ضمانت چھے۔\nتعليم وتدريس نى مجالس ما:"
        }
    ]
    
    docx_bytes = generate_lsd_docx(
        pages_data=sample_pages,
        document_title="اختبار مستند لسان الدعوة",
        include_images=False,
        font_name="Amiri"
    )
    
    assert docx_bytes is not None
    assert len(docx_bytes) > 1000  # Non-trivial binary docx file size
    
    # Read back generated document with python-docx
    doc = Document(io.BytesIO(docx_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    
    assert "اختبار مستند لسان الدعوة" in paragraphs[0]
    assert "بسم الله الرحمن الرحيم" in paragraphs[1]
    assert any("اللسان الدعوة المباركة" in p for p in paragraphs)
    print("Test passed: docx generation verified.")
