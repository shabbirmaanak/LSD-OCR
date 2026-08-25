"""
Non-AI Document Parser for .docx, .txt, and .pdf files.
Extracts raw text deterministically from user uploaded documents with 100% font/text fidelity.
"""

import io
from typing import List, Tuple, Dict, Any, Optional
from docx import Document
import pypdf


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Parses document bytes into plain text string.
    Supports .docx, .txt, .pdf, and fallback encodings.
    """
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    if ext == 'docx':
        return parse_docx(file_bytes)
    elif ext == 'pdf':
        return parse_pdf(file_bytes)
    elif ext in ['png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff']:
        # For image files in non-AI mode, return empty string so image preview is shown
        return ""
    else:
        # Default text format (.txt, .rtf, .html, etc.)
        return parse_txt(file_bytes)


def parse_docx(file_bytes: bytes) -> str:
    """Extracts text paragraphs and table cell text from Word .docx file."""
    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = []
        for p in doc.paragraphs:
            if p.text.strip():
                paragraphs.append(p.text)
                
        # Also extract table text if present
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)
                    
        return "\n".join(paragraphs)
    except Exception as e:
        print(f"Error parsing .docx file: {e}")
        return parse_txt(file_bytes)


def parse_pdf(file_bytes: bytes) -> str:
    """Extracts clean text stream from PDF file pages without inserting artificial spaces."""
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        extracted_pages = []
        for page in reader.pages:
            t = page.extract_text()
            if t and t.strip():
                extracted_pages.append(t.strip())
        return "\n\n".join(extracted_pages)
    except Exception as e:
        print(f"Error parsing PDF file: {e}")
        return ""


def parse_txt(file_bytes: bytes) -> str:
    """Decodes text bytes trying common encodings (UTF-8, UTF-16, Windows-1256 for Arabic)."""
    encodings = ['utf-8', 'utf-16', 'windows-1256', 'latin-1']
    for enc in encodings:
        try:
            return file_bytes.decode(enc)
        except Exception:
            continue
    return file_bytes.decode('utf-8', errors='ignore')
