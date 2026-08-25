"""
Lisan al Dawat (LSD) Non-AI Image Handler Module.
100% Offline image reader.
"""

import io
from typing import Dict, Any
from PIL import Image


def extract_text_from_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Returns image metadata and status without any external AI or cloud API dependencies.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        w, h = image.size
        return {
            "success": True,
            "text": "",
            "dimensions": {"width": w, "height": h}
        }
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "error": str(e)
        }
