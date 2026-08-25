"""
Document Parser Module for Lisan al Dawat OCR App.
Extracts raw text from .docx, .txt, and .pdf documents cleanly.
"""

import io
from typing import Optional

def parse_docx(file_bytes: bytes) -> str:
    """Extracts text from DOCX file bytes."""
    import docx
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
            if row_text:
                paragraphs.append(row_text)
    return "\n".join(paragraphs)

def is_corrupted_pdf_text(text: str) -> bool:
    """Detects legacy Bohra custom font PUA corruption."""
    if not text:
        return True
    pua_count = sum(1 for c in text if '\uE000' <= c <= '\uF8FF' or c in {'善', '周', '呈', '吸'})
    return pua_count > 3

def parse_pdf_via_ocr(file_bytes: bytes) -> str:
    """Renders PDF pages to 150 DPI PNG images and runs local EasyOCR engine."""
    import fitz
    from backend.ocr_engine import extract_text_from_image
    
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages_text = []
    
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        res = extract_text_from_image(img_bytes)
        txt = res.get("text", "") if isinstance(res, dict) else str(res)
        if txt and txt.strip():
            pages_text.append(txt.strip())
            
    doc.close()
    return "\n\n".join(pages_text)

def parse_pdf(file_bytes: bytes) -> str:
    """Extracts text from PDF file bytes with PyMuPDF rendering fallback for corrupted font CMaps."""
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        lines = []
        for page in doc:
            t = page.get_text("text")
            if t and t.strip():
                lines.append(t.strip())
        doc.close()
        text = "\n".join(lines)
        
        if is_corrupted_pdf_text(text):
            return parse_pdf_via_ocr(file_bytes)
            
        return text
    except Exception as e:
        print(f"PyMuPDF text extraction failed: {e}. Trying OCR fallback...")
        return parse_pdf_via_ocr(file_bytes)

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Determines file type and extracts clean text."""
    fname = filename.lower()
    if fname.endswith('.docx'):
        return parse_docx(file_bytes)
    elif fname.endswith('.pdf'):
        return parse_pdf(file_bytes)
    elif fname.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')):
        from backend.ocr_engine import extract_text_from_image
        res = extract_text_from_image(file_bytes)
        return res.get("text", "") if isinstance(res, dict) else str(res)
    else:
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return file_bytes.decode('latin-1', errors='ignore')
