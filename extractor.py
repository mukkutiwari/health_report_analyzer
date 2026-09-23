import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import io

# If Tesseract is installed somewhere else, update the path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from PDF using PyMuPDF.
    If no text found, fallback to OCR extraction.
    """

    # ------------------------------
    # 1. Try extracting text directly
    # ------------------------------
    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()

    text_output = ""
    try:
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in pdf:
            text_output += page.get_text("text")
    except Exception as e:
        print("PyMuPDF extraction error:", e)

    # If text is found → return
    if text_output.strip():
        return text_output

    # ------------------------------
    # 2. Fallback → OCR for scanned PDFs
    # ------------------------------
    uploaded_file.seek(0)
    images = convert_from_bytes(pdf_bytes)

    ocr_text = ""
    for img in images:
        gray = img.convert("L")  # better OCR accuracy
        ocr_text += pytesseract.image_to_string(gray)

    return ocr_text
