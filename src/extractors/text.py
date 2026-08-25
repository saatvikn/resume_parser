import os
import re

import docx2txt
import pdfplumber

from src.exceptions import TextExtractionError, UnsupportedFileError


COLUMN_GAP_PATTERN = re.compile(r"\s{5,}")
REPEATED_SPACE_PATTERN = re.compile(r"[ \t]{2,}")


def _normalize_line(raw_line):
    """Normalize PDF artifacts while preserving columns and bullet levels."""
    line = raw_line.strip().replace("\uf0b7", "•")
    line = COLUMN_GAP_PATTERN.sub(" | ", line)
    return REPEATED_SPACE_PATTERN.sub(" ", line).strip()


def _normalize_document_text(text):
    """Normalize each line without flattening the document structure."""
    normalized_lines = [_normalize_line(line) for line in text.splitlines()]
    return "\n".join(normalized_lines).strip()


def _extract_pdf_text(file_path):
    """Extract PDF text in visual reading order with column separation."""
    pages = []

    with pdfplumber.open(file_path) as document:
        for page in document.pages:
            page_text = page.extract_text(
                layout=True,
                x_tolerance=1,
                y_tolerance=3,
            )
            if page_text:
                pages.append(_normalize_document_text(page_text))

    return "\n\n".join(pages)


def extract_text(file_path):
    """Extract text from a supported resume file."""
    extension = os.path.splitext(file_path)[-1].lower()

    if extension not in {".pdf", ".docx"}:
        raise UnsupportedFileError(
            "Unsupported file format: Only PDF and DOCX are allowed."
        )

    try:
        if extension == ".pdf":
            return _extract_pdf_text(file_path)
        return _normalize_document_text(docx2txt.process(file_path))
    except Exception as error:
        raise TextExtractionError(
            "The resume text could not be extracted from this file."
        ) from error
