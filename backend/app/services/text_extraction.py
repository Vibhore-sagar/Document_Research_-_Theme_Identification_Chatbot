# backend/app/services/text_extraction.py

import fitz  # PyMuPDF
import pytesseract
# from pdf2image import convert_from_path
import os
from PIL import Image
import tempfile

# backend/app/services/text_extraction.py

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text using PyMuPDF for normal PDFs; falls back to Tesseract OCR if empty."""
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        page_text = page.get_text()
        if page_text.strip():
            text += page_text
        else:
            text += ocr_page(page)

    return text

def ocr_page(page) -> str:
    """Converts page to image and runs OCR using Tesseract."""
    pix = page.get_pixmap(dpi=300)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return pytesseract.image_to_string(img)

