import io
from typing import Optional
import logging

logger = logging.getLogger("greenlight.tools.script")


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text content from a PDF screenplay file using pypdf."""
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages_text = []
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            pages_text.append(f"--- [PAGE {idx + 1}] ---\n{page_text}")
            
        full_text = "\n\n".join(pages_text)
        logger.info(f"Extracted {len(reader.pages)} pages from PDF ({len(full_text)} characters).")
        return full_text
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        return ""


def clean_screenplay_text(raw_text: str) -> str:
    """Cleans up formatting, strips excess whitespace, and normalizes line breaks."""
    if not raw_text:
        return ""
    lines = raw_text.splitlines()
    cleaned_lines = [line.rstrip() for line in lines]
    return "\n".join(cleaned_lines)
