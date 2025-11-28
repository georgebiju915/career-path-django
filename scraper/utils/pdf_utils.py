import io
import logging

# External libs (install in requirements)
# pip install pymupdf pdfminer.six tika pillow pytesseract
try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

from pdfminer.high_level import extract_text as pdfminer_extract_text

# Tika (optional) — requires Java. If not available, leave as None.
try:
    from tika import parser as tika_parser
    tika_available = True
except Exception:
    tika_parser = None
    tika_available = False

# OCR
try:
    from PIL import Image
    import pytesseract
    ocr_available = True
except Exception:
    Image = None
    pytesseract = None
    ocr_available = False

logger = logging.getLogger(__name__)


def extract_text_with_pymupdf(file_obj):
    if fitz is None:
        raise RuntimeError("PyMuPDF (fitz) not installed")
    file_obj.seek(0)
    data = file_obj.read()
    # open from bytes
    doc = fitz.open(stream=data, filetype="pdf")
    out = []
    for page in doc:
        try:
            txt = page.get_text("text")
        except Exception:
            txt = page.get_text()
        out.append(txt)
    return "\n\n".join(out)


def extract_text_with_pdfminer(file_obj):
    file_obj.seek(0)
    data = file_obj.read()
    # pdfminer accepts file path or bytesIO
    try:
        return pdfminer_extract_text(io.BytesIO(data))
    except Exception as e:
        logger.exception("pdfminer extraction failed: %s", e)
        return ""


def extract_text_with_tika(file_obj):
    if not tika_available:
        raise RuntimeError("tika is not available (install tika-python and Java)")
    file_obj.seek(0)
    data = file_obj.read()
    # tika.parser.from_buffer returns dict with 'content'
    parsed = tika_parser.from_buffer(data)
    return parsed.get("content") or ""


def ocr_pdf_with_pymupdf(file_obj, dpi=150, lang="eng"):
    """
    Render pages to images (via fitz) and run pytesseract.
    Returns combined text.
    """
    if not (ocr_available and fitz):
        raise RuntimeError("OCR path requires pillow, pytesseract and PyMuPDF")
    file_obj.seek(0)
    data = file_obj.read()
    doc = fitz.open(stream=data, filetype="pdf")
    texts = []
    for page in doc:
        # render page to pixmap
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes("png")
        im = Image.open(io.BytesIO(img_bytes))
        txt = pytesseract.image_to_string(im, lang=lang)
        texts.append(txt)
    return "\n\n".join(texts)


def extract_text_auto(file_obj, ocr_if_empty=True, min_chars=50):
    """
    Try multiple extractors. Return extracted text (string).
    Strategy:
      1) PyMuPDF
      2) pdfminer.six
      3) Tika (if installed)
      4) OCR (if enabled)
    """
    # try PyMuPDF
    try:
        if fitz:
            txt = extract_text_with_pymupdf(file_obj)
            if txt and len(txt.strip()) >= min_chars:
                return txt
    except Exception:
        logger.exception("PyMuPDF extractor failed")

    # try pdfminer
    try:
        txt = extract_text_with_pdfminer(file_obj)
        if txt and len(txt.strip()) >= min_chars:
            return txt
    except Exception:
        logger.exception("pdfminer extractor failed")

    # try tika
    if tika_available:
        try:
            txt = extract_text_with_tika(file_obj)
            if txt and len(txt.strip()) >= min_chars:
                return txt
        except Exception:
            logger.exception("tika extractor failed")

    # fallback to OCR
    if ocr_if_empty:
        try:
            txt = ocr_pdf_with_pymupdf(file_obj)
            return txt
        except Exception:
            logger.exception("OCR extractor failed")

    # last resort: return whatever pdfminer returned (might be empty)
    try:
        file_obj.seek(0)
        return pdfminer_extract_text(io.BytesIO(file_obj.read()))
    except Exception:
        return ""