"""
FastAPI Application Backend for Lisan al Dawat (Alkanz / Kanzmarjan / Unicode) Non-AI Document Converter.
"""

import os
import json
import base64
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.converter_engine import convert_text, PRESETS, ALKANZ_NORMAL_RULES
from backend.docx_generator import generate_lsd_docx
from backend.doc_parser import extract_text_from_file

app = FastAPI(
    title="Lisan al Dawat Alkanz Unicode Document Converter",
    description="Non-AI Deterministic Converter for Alkanz, Kanzmarjan, and Unicode Lisan al Dawat documents.",
    version="2.0.0"
)

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConvertTextRequest(BaseModel):
    text: str
    preset: Optional[str] = "alkanz_normal"
    custom_rules: Optional[Dict[str, str]] = None


class ExportDocxRequest(BaseModel):
    title: Optional[str] = "Lisan al Dawat Document"
    text: str
    font_name: str = "Amiri"
    font_size: int = 14


@app.get("/api/presets")
async def get_presets():
    """Returns available keyboard conversion presets and default mapping rules."""
    return JSONResponse(content={
        "success": True,
        "presets": PRESETS,
        "default_preset": "alkanz_normal"
    })


@app.post("/api/convert")
async def convert_document(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    preset: str = Form("alkanz_normal"),
    custom_rules_json: Optional[str] = Form(None)
):
    """
    Deterministically converts uploaded document or text string using specified mapping rules.
    """
    try:
        raw_text = ""
        filename = "pasted_text.txt"
        image_base64 = None
        
        if file is not None:
            filename = file.filename
            content = await file.read()
            if content:
                ext = filename.lower().split('.')[-1] if '.' in filename else ''
                if ext in ['png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff']:
                    b64_str = base64.b64encode(content).decode('utf-8')
                    image_base64 = f"data:image/{ext if ext != 'jpg' else 'jpeg'};base64,{b64_str}"
                
                raw_text = await asyncio.to_thread(extract_text_from_file, content, filename)
        elif text:
            raw_text = text
            
        if not raw_text and not image_base64:
            raw_text = ""
            
        # Parse custom rules if provided
        rules_dict = None
        if custom_rules_json:
            try:
                rules_dict = json.loads(custom_rules_json)
            except Exception:
                rules_dict = None
                
        converted_text, replacements_count = convert_text(
            raw_text,
            rules=rules_dict,
            preset_key=preset
        )
        
        return JSONResponse(content={
            "success": True,
            "filename": filename,
            "original_text": raw_text,
            "converted_text": converted_text,
            "replacements_count": replacements_count,
            "preset_used": preset,
            "image_base64": image_base64
        })
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from urllib.parse import quote

@app.post("/api/export-docx")
async def export_docx(req: ExportDocxRequest):
    """
    Generates downloadable Microsoft Word (.docx) document with native RTL formatting.
    """
    try:
        pages_payload = [{
            "page_num": 1,
            "text": req.text,
            "image_bytes": None
        }]
        
        docx_bytes = generate_lsd_docx(
            pages_data=pages_payload,
            document_title=req.title or "Lisan al Dawat Document",
            include_images=False,
            font_name=req.font_name,
            font_size=req.font_size
        )
        
        ascii_filename = "LSD_Converted_Document.docx"
        encoded_filename = quote(f"{req.title or 'LSD_Converted_Document'}.docx")
        
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=\"{ascii_filename}\"; filename*=UTF-8''{encoded_filename}"
            }
        )
    except Exception as e:
        print(f"Error in /api/export-docx: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate docx: {str(e)}")


@app.get("/api/fonts")
async def get_fonts():
    """Returns list of uploaded custom preset font files."""
    fonts_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "fonts")
    fonts_list = []
    if os.path.exists(fonts_dir):
        for fname in os.listdir(fonts_dir):
            if fname.lower().endswith(('.ttf', '.otf', '.woff', '.woff2')):
                name = os.path.splitext(fname)[0].replace('-', ' ').replace('_', ' ')
                fonts_list.append({
                    "font_name": name,
                    "filename": fname,
                    "url": f"/static/fonts/{fname}"
                })
    return JSONResponse(content={"success": True, "fonts": fonts_list})


@app.post("/api/upload-font")
async def upload_font(file: UploadFile = File(...)):
    """Uploads custom font file (.ttf, .otf, .woff) to preset fonts directory."""
    try:
        fonts_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "fonts")
        os.makedirs(fonts_dir, exist_ok=True)
        
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded font file is empty.")
            
        save_path = os.path.join(fonts_dir, file.filename)
        with open(save_path, "wb") as f:
            f.write(content)
            
        font_name = os.path.splitext(file.filename)[0].replace('-', ' ').replace('_', ' ')
        
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "font_name": font_name,
            "url": f"/static/fonts/{file.filename}"
        })
    except Exception as e:
        print(f"Error uploading font: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sample")
async def get_sample():
    """
    Returns sample document text encoded with Alkanz keyboard layout.
    """
    sample_path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "sample_alkanz.txt")
    raw_sample = ""
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            raw_sample = f.read()
            
    converted_sample, count = convert_text(raw_sample, preset_key="alkanz_normal")
    
    return JSONResponse(content={
        "success": True,
        "filename": "sample_alkanz.txt",
        "original_text": raw_sample,
        "converted_text": converted_sample,
        "replacements_count": count
    })


# Serve static frontend files
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def read_root():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Lisan al Dawat Non-AI Converter Backend API is running."}
