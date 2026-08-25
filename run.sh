#!/bin/bash

# Lisan al Dawat (LSD) OCR System Launch Script

echo "========================================================"
echo " Starting Lisan al Dawat OCR & Word Exporter Server..."
echo "========================================================"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "Serving web app at: http://localhost:8000"
python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
