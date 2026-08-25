import os

import docx2txt
from pdfminer.high_level import extract_text as extract_pdf_text

from src.exceptions import TextExtractionError, UnsupportedFileError


def extract_text(file_path):
    """Extract text from a supported resume file."""
    extension = os.path.splitext(file_path)[-1].lower()

    if extension not in {".pdf", ".docx"}:
        raise UnsupportedFileError(
            "Unsupported file format: Only PDF and DOCX are allowed."
        )

    try:
        if extension == ".pdf":
            return extract_pdf_text(file_path)
        return docx2txt.process(file_path)
    except Exception as error:
        raise TextExtractionError(
            "The resume text could not be extracted from this file."
        ) from error
