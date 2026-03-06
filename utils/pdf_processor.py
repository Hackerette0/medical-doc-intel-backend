import pdfplumber
import PyPDF2
from PIL import Image
import io
import logging
import pytesseract
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TESSERACT_AVAILABLE = False
try:
    pytesseract.get_tesseract_version()
    TESSERACT_AVAILABLE = True
    logger.info("Tesseract OCR available")
except Exception:
    logger.warning("Tesseract not found – OCR disabled. Install for scanned PDFs.")

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text = ""
    
    try:
        # 1. pdfplumber (best for tables)
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(layout=True) or ""
                text += page_text + "\n"
                
                # General table extraction (works on any blood report)
                tables = page.extract_tables()
                for table in tables or []:
                    if table and len(table) > 1:
                        text += "\n--- BLOOD REPORT TABLE ---\n"
                        for row in table:
                            row_str = " | ".join(str(cell).strip() if cell else "" for cell in row)
                            text += row_str + "\n"
                        text += "--- END TABLE ---\n"
        
        # 2. PyPDF2 fallback (for text-heavy pages)
        if len(text) < 300:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            for page in pdf_reader.pages:
                text += page.extract_text() or "" + "\n"
        
        text = re.sub(r'\s+', ' ', text)
        logger.info(f"Total extracted: {len(text)} chars")
        
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        text = ""
    
    # OCR only if very low AND available
    if len(text) < 400 and TESSERACT_AVAILABLE:
        text += ocr_pdf(pdf_bytes)
    
    return text.strip() or "PDF processed with limited text - analysis may be partial."

def ocr_pdf(pdf_bytes: bytes) -> str:
    if not TESSERACT_AVAILABLE:
        return ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            ocr_text = ""
            for page in pdf.pages:
                img = page.to_image(resolution=300)
                pil_img = Image.open(io.BytesIO(img.original))
                page_ocr = pytesseract.image_to_string(pil_img, config='--psm 6')
                ocr_text += page_ocr + "\n"
            return ocr_text
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""