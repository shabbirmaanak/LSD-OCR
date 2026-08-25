"""
Integration tests for LSD Non-AI Alkanz Converter FastAPI endpoints.
"""

import sys
import os
import io
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import app

client = TestClient(app)


def test_get_presets_endpoint():
    response = client.get("/api/presets")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "alkanz_normal" in data["presets"]


def test_get_sample_endpoint():
    response = client.get("/api/sample")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "گتاب" in data["converted_text"]


def test_convert_endpoint():
    payload = {"text": "ككتاب سسند ثثول", "preset": "alkanz_normal"}
    response = client.post("/api/convert", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["converted_text"] == "گتاب ےند پول"
    assert data["replacements_count"] == 3


def test_image_convert_endpoint():
    # Read sample image bytes
    sample_img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_data", "sample_lsd.png"))
    if os.path.exists(sample_img_path):
        with open(sample_img_path, "rb") as f:
            img_bytes = f.read()
        response = client.post(
            "/api/convert",
            files={"file": ("sample_lsd.png", io.BytesIO(img_bytes), "image/png")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "converted_text" in data


def test_export_docx_endpoint():
    payload = {
        "title": "Test LSD Document",
        "text": "بسم الله الرحمن الرحيم\nگتاب ےند",
        "font_name": "Amiri",
        "font_size": 14
    }
    response = client.post("/api/export-docx", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert len(response.content) > 1000


def test_fonts_endpoints():
    # Test GET /api/fonts
    res_get = client.get("/api/fonts")
    assert res_get.status_code == 200
    assert res_get.json()["success"] is True

    # Test POST /api/upload-font
    test_filename = "TempTestFont.ttf"
    target_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "fonts", test_filename))
    
    try:
        fake_font = io.BytesIO(b"Fake Font Binary Data")
        res_post = client.post(
            "/api/upload-font",
            files={"file": (test_filename, fake_font, "font/ttf")}
        )
        assert res_post.status_code == 200
        assert res_post.json()["success"] is True
        assert res_post.json()["font_name"] == "TempTestFont"
    finally:
        if os.path.exists(target_path):
            os.remove(target_path)
