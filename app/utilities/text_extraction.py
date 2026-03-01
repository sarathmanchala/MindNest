from PyPDF2 import PdfReader
import io
import pytesseract
from PIL import Image
from docx import Document

def extract_text(file, extension):
    file.seek(0)

    if extension == "txt":
        return read_text(file)

    elif extension == "pdf":
        return read_pdf(file)

    elif extension in {"png", "jpg", "jpeg"}:
        return read_image(file)

    elif extension == "docx":
        return read_docx(file)

    else:
        return ""

def read_text(file):
    return file.read().decode("utf-8")

def read_pdf(file):
    pdf = PdfReader(io.BytesIO(file.read()))
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""
    return text

def read_image(file):
    image = Image.open(io.BytesIO(file.read()))
    text = pytesseract.image_to_string(image)
    return text

def read_docx(file):
    doc = Document(io.BytesIO(file.read()))
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

