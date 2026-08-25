import os

import docx2txt
from pdfminer.high_level import extract_text as extract_pdf_text


def extract_text(file_path):
    """Extract text from a supported resume file."""
    extension = os.path.splitext(file_path)[-1].lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)
    if extension == ".docx":
        return docx2txt.process(file_path)

    raise ValueError("Unsupported file format: Only PDF and DOCX are allowed")
