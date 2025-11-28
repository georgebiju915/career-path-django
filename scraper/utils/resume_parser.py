"""
Resume parsing helpers.

Provides:
- parse_resume_from_upload(file_obj, ...)  -> robust multi-backend extraction + skill extraction
- parse_resume_text(text)                  -> lightweight parser for pasted text (compat)
- extract_text_from_pdf(file_obj)          -> convenience wrapper for file-only extraction (compat)
"""

import logging
from .pdf_utils import extract_text_auto, extract_text_with_pymupdf, ocr_pdf_with_pymupdf
from .skill_extractor import extract_skills_from_text

logger = logging.getLogger(__name__)


def parse_resume_from_upload(file_obj, skills_list=None, ocr_if_empty=True):
    """
    Robust pipeline for uploaded files (PDF or text files).
    Tries PyMuPDF, pdfminer, Tika, then OCR. Returns dict with:
      - extracted_text
      - skills (dict of skill -> count)
      - skill_matches (contexts)
      - metadata
    """
    try:
        text = extract_text_auto(file_obj, ocr_if_empty=ocr_if_empty)
    except Exception as e:
        logger.exception("extract_text_auto failed: %s", e)
        # last-resort: try PyMuPDF directly, then simple decode
        try:
            file_obj.seek(0)
            text = extract_text_with_pymupdf(file_obj)
        except Exception:
            try:
                file_obj.seek(0)
                raw = file_obj.read()
                text = raw.decode("utf-8", errors="ignore")
            except Exception:
                text = ""

    skills_data = extract_skills_from_text(text or "", skills_list=skills_list)
    return {
        "extracted_text": text or "",
        "skills": skills_data.get("skills", {}),
        "skill_matches": skills_data.get("matches", {}),
        "metadata": {"tokens": skills_data.get("total_tokens", 0)}
    }


# Backwards-compatible wrapper used by older code
def parse_resume_text(text):
    """
    Compatibility wrapper expected by older views:
    - Accepts plain text (string) and returns a dict roughly matching parse_resume_from_upload output.
    """
    if not isinstance(text, str):
        # attempt to coerce
        try:
            text = str(text)
        except Exception:
            text = ""

    skills_data = extract_skills_from_text(text or "")
    return {
        "extracted_text": text or "",
        "skills": skills_data.get("skills", {}),
        "skill_matches": skills_data.get("matches", {}),
        "metadata": {"tokens": skills_data.get("total_tokens", 0)}
    }


def extract_text_from_pdf(file_obj, ocr_if_empty=True):
    """
    Compatibility wrapper to return text extracted from a PDF/file-like object.
    Uses the same auto pipeline as parse_resume_from_upload.
    """
    try:
        return extract_text_auto(file_obj, ocr_if_empty=ocr_if_empty)
    except Exception as e:
        logger.exception("extract_text_from_pdf failed: %s", e)
        # fallback: try PyMuPDF direct or OCR as last resort
        try:
            file_obj.seek(0)
            return extract_text_with_pymupdf(file_obj)
        except Exception:
            try:
                file_obj.seek(0)
                return ocr_pdf_with_pymupdf(file_obj)
            except Exception:
                return ""