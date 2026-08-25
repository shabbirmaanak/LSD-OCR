"""
Document Parser Module for LSD Converter.
Extracts raw text from .docx, .pdf, .txt, and image files.
"""

import io
from typing import Dict, Any


def parse_docx(file_bytes: bytes) -> str:
    """Extracts raw text from .docx file bytes using python-docx."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        
        # Also extract table text if present
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                if row_text:
                    paragraphs.append(row_text)
                    
        return "\n".join(paragraphs)
    except Exception as e:
        print(f"Error parsing .docx: {e}")
        return ""


def parse_pdf_via_ocr(file_bytes: bytes) -> str:
    """Fallback OCR for scanned image PDFs."""
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages_text = []
        for page in doc:
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            try:
                from backend.ocr_engine import extract_text_from_image
                res = extract_text_from_image(img_bytes)
                txt = res.get("text", "") if isinstance(res, dict) else str(res)
                if txt and txt.strip():
                    pages_text.append(txt.strip())
            except Exception:
                pass
        doc.close()
        return "\n\n".join(pages_text)
    except Exception as e:
        print(f"Error in OCR PDF parse: {e}")
        return ""


def parse_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from PDF file bytes using PyMuPDF (fitz).
    Always returns extracted text for text-based PDFs.
    Falls back to OCR only if 0 text characters are extracted (scanned image PDF).
    """
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        lines = []
        for page in doc:
            t = page.get_text("text")
            if t and t.strip():
                lines.append(t.strip())
        doc.close()
        extracted_text = "\n".join(lines).strip()
        
        if extracted_text:
            return extracted_text
            
        # If 0 text extracted, try OCR fallback
        return parse_pdf_via_ocr(file_bytes)
    except Exception as e:
        print(f"PyMuPDF text extraction error: {e}")
        return parse_pdf_via_ocr(file_bytes)


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Determines file type and extracts clean text."""
    fname = filename.lower()
    if fname.endswith('.docx'):
        return parse_docx(file_bytes)
    elif fname.endswith('.pdf'):
        return parse_pdf(file_bytes)
    elif fname.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')):
        try:
            from backend.ocr_engine import extract_text_from_image
            res = extract_text_from_image(file_bytes)
            return res.get("text", "") if isinstance(res, dict) else str(res)
        except Exception as e:
            print(f"Image OCR error: {e}")
            return ""
    else:
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_bytes.decode('latin-1')
            except Exception:
                return ""
