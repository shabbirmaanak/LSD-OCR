"""
Lisan al Dawat (LSD) Offline Image OCR Engine Module.
Supports local image preprocessing, fast binarization, and offline neural OCR.
100% Offline - Zero Cloud AI / API dependencies.
"""

import io
import re
from typing import Dict, Any, Optional
from PIL import Image, ImageEnhance, ImageFilter

_EASYOCR_READER = None


def get_easyocr_reader():
    """Lazy initializer for offline EasyOCR Arabic/Urdu model."""
    global _EASYOCR_READER
    if _EASYOCR_READER is None:
        try:
            import easyocr
            _EASYOCR_READER = easyocr.Reader(['ar', 'ur'], gpu=False)
        except Exception as e:
            print(f"Warning: EasyOCR offline model not loaded: {e}")
            _EASYOCR_READER = False
    return _EASYOCR_READER


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Applies image enhancement pipeline for document scans:
    - Grayscale conversion
    - Contrast boost for yellowed paper
    - Sharpness enhancement
    """
    img_gray = image.convert('L')
    enhancer = ImageEnhance.Contrast(img_gray)
    img_contrast = enhancer.enhance(1.8)
    sharpener = ImageEnhance.Sharpness(img_contrast)
    img_sharp = sharpener.enhance(2.0)
    return img_sharp


def extract_text_from_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Extracts text from scanned image bytes using 100% offline local OCR.
    """
    try:
        raw_img = Image.open(io.BytesIO(image_bytes))
        w, h = raw_img.size
        processed_img = preprocess_image(raw_img)

        # 1. Try pytesseract first (instant C++ binary if available)
        try:
            import pytesseract
            text = pytesseract.image_to_string(processed_img, lang='ara+urd').strip()
            if text:
                return {
                    "success": True,
                    "text": text,
                    "engine": "pytesseract",
                    "dimensions": {"width": w, "height": h}
                }
        except Exception:
            pass

        # 2. Try EasyOCR offline reader
        reader = get_easyocr_reader()
        if reader:
            buf = io.BytesIO()
            processed_img.save(buf, format='PNG')
            buf.seek(0)
            
            results = reader.readtext(buf.getvalue(), detail=0, paragraph=True)
            extracted_text = "\n".join(results).strip()

            return {
                "success": True,
                "text": extracted_text,
                "engine": "easyocr",
                "dimensions": {"width": w, "height": h}
            }

        return {
            "success": False,
            "text": "",
            "error": "No offline OCR engine active"
        }
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "error": str(e)
        }
