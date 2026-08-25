"""Shared resume parsing orchestration."""

from src.exceptions import EmptyDocumentError
from src.extractors.contact import (
    extract_email,
    extract_linkedin,
    extract_name,
    extract_phone,
)
from src.extractors.sections import extract_sections
from src.extractors.skills import extract_skills
from src.extractors.text import extract_text


def parse_resume_file(file_path, use_gemini=True):
    """Parse a resume using Gemini or the rule-based extraction pipeline."""
    text = extract_text(file_path)

    if not text or not text.strip():
        raise EmptyDocumentError(
            "No readable text was found in the uploaded document. "
            "Scanned PDFs are not supported yet."
        )

    if use_gemini:
        from src.services.gemini import extract_advanced_fields_with_gemini

        return extract_advanced_fields_with_gemini(text)

    sections = extract_sections(text)
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "education": sections.get("education", []),
        "experience": sections.get("experience", []),
        "skills": extract_skills(sections.get("skills", [])),
        "certifications": sections.get("certifications", []),
        "projects": sections.get("projects", []),
    }
