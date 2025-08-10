import fitz
import re
import docx2txt
from pdf2image import convert_from_path
import pytesseract

class ResumeParserTool:
    def _run(self, file_path: str):
        text = ""

        if file_path.lower().endswith(".pdf"):
            text = self.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(".docx"):
            text = self.extract_text_from_docx(file_path)

        # Fallback to OCR if nothing extracted
        if not text.strip():
            text = self.ocr_extract_text(file_path)

        email = self.extract_email(text)
        return {"text": text.strip(), "email": email}

    def extract_text_from_pdf(self, file_path):
        text = ""
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
        return text

    def extract_text_from_docx(self, file_path):
        return docx2txt.process(file_path)

    def ocr_extract_text(self, file_path):
        try:
            images = convert_from_path(file_path)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img)
            return text
        except Exception as e:
            print(f"OCR failed: {e}")
            return ""

    def extract_email(self, text):
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else ""
