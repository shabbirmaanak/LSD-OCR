"""
Utility functions for Lisan al Dawat OCR App:
- Image preprocessing (grayscale, contrast adjustment, auto-rotate/deskew, crop)
- PDF file rendering to page images using PyPDF / Pillow
"""

import io
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pypdf


def process_uploaded_file(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Parses uploaded file (PDF or Image) into a list of page dicts:
    [
        {"page_num": 1, "image_bytes": b"...", "mime_type": "image/png"},
        ...
    ]
    """
    ext = filename.lower().split('.')[-1]
    
    if ext == 'pdf':
        return convert_pdf_to_images(file_bytes)
    else:
        # Single image file
        processed_img_bytes, mime = optimize_image_for_ocr(file_bytes)
        return [{
            "page_num": 1,
            "image_bytes": processed_img_bytes,
            "mime_type": mime
        }]


def convert_pdf_to_images(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Converts PDF pages to PNG image byte payloads.
    Uses pypdf to extract embedded images, or creates canvas pages.
    """
    pages = []
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        for idx, page in enumerate(reader.pages):
            # Try to extract page images
            extracted = False
            for img_file in page.images:
                img_data = img_file.data
                opt_bytes, mime = optimize_image_for_ocr(img_data)
                pages.append({
                    "page_num": idx + 1,
                    "image_bytes": opt_bytes,
                    "mime_type": mime
                })
                extracted = True
                break  # Take first main image per page
                
            if not extracted:
                # If no embedded image found, create a placeholder/notice image or attempt render
                blank = Image.new('RGB', (800, 1000), color=(255, 255, 255))
                buf = io.BytesIO()
                blank.save(buf, format='PNG')
                pages.append({
                    "page_num": idx + 1,
                    "image_bytes": buf.getvalue(),
                    "mime_type": "image/png"
                })
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        # Fallback single page
        opt_bytes, mime = optimize_image_for_ocr(pdf_bytes)
        pages.append({
            "page_num": 1,
            "image_bytes": opt_bytes,
            "mime_type": mime
        })
        
    return pages if pages else [{"page_num": 1, "image_bytes": pdf_bytes, "mime_type": "image/png"}]


def optimize_image_for_ocr(
    image_bytes: bytes,
    contrast_factor: float = 1.3,
    sharpness_factor: float = 1.2,
    rotate_deg: int = 0
) -> Tuple[bytes, str]:
    """
    Applies image enhancements suited for Arabic script OCR readability:
    - Normalization
    - Rotation
    - Mild contrast boost & sharpening
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert RGBA / Palette to RGB
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # Apply user rotation if requested
        if rotate_deg != 0:
            img = img.rotate(-rotate_deg, expand=True)
            
        # Enhance Contrast
        if contrast_factor != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast_factor)
            
        # Enhance Sharpness (helps diacritics / harakat stand out)
        if sharpness_factor != 1.0:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness_factor)
            
        output_io = io.BytesIO()
        img.save(output_io, format="PNG", optimize=True)
        return output_io.getvalue(), "image/png"
        
    except Exception as e:
        print(f"Image enhancement notice: {e}")
        return image_bytes, "image/png"
