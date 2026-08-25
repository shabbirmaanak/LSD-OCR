# Lisan al Dawat (LSD) OCR System & Word Document Generator

An AI-powered OCR application for digitizing Lisan al Dawat (LSD) documents, manuscripts, and PDFs, and exporting native Microsoft Word (`.docx`) files formatted with Right-To-Left (RTL) Arabic typography.

## Features

- **Gemini 3.7 Flash Vision OCR**: Fine-tuned system prompts for Lisan al Dawat Arabic script, diacritical marks (harakat), ligatures, and Bohra terminology.
- **Interactive Split-Pane UI**: Side-by-side visual document viewer (zoom, pan, rotation) and live RTL text editor.
- **Native `.docx` Exporter**: Generates Microsoft Word documents configured with OpenXML `w:bidi` and `w:rtl` parameters, proper Arabic fonts (Amiri, Scheherazade New), and optional page image attachments.
- **Multi-Format Ingestion**: Supports single/multi-page images (PNG, JPG, WEBP) and PDF files.
- **Demo Mode**: Built-in sample Lisan al Dawat document for quick testing without requiring an API key.

## Project Structure

```
lsd_ocr_app/
├── backend/
│   ├── app.py                 # FastAPI web application
│   ├── ocr_engine.py          # Gemini 3.7 Flash LSD Vision OCR Engine
│   ├── docx_generator.py      # Native Word (.docx) generator with RTL XML styling
│   ├── utils.py               # Image processing & PDF page extractor
│   └── requirements.txt       # Dependencies
├── frontend/
│   ├── index.html             # Web UI HTML layout
│   ├── css/style.css          # Custom styling and font loaders
│   └── js/
│       ├── app.js             # Main application logic
│       ├── docViewer.js       # Document viewer canvas
│       └── editor.js          # RTL text editor & counter
├── sample_data/
│   └── sample_lsd.png         # Pre-bundled Lisan al Dawat sample image
├── tests/
│   ├── test_api.py            # API endpoint integration tests
│   └── test_docx.py           # Docx generator unit tests
└── run.sh                     # Server startup script
```

## Quickstart

1. **Activate Virtual Environment**:
   ```bash
   cd /Users/shabbirmaanak/.gemini/antigravity/scratch/lsd_ocr_app
   source .venv/bin/activate
   ```

2. **Start the Web Application**:
   ```bash
   ./run.sh
   ```
   Or run manually:
   ```bash
   python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access in Browser**:
   Open [http://localhost:8000](http://localhost:8000)

4. **API Key Setup**:
   Set `export GEMINI_API_KEY="your-key-here"` or enter your key in the web interface settings modal.
