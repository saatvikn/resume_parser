"""Shared local NLP and regex resume-parsing orchestration."""

from src.exceptions import EmptyDocumentError
from src.extractors.contact import (
    extract_email,
    extract_github,
    extract_linkedin,
    extract_name,
    extract_phone,
)
from src.extractors.sections import extract_section_blocks
from src.extractors.text import extract_text
from src.nlp import analyze_resume_text
from src.nlp.structured import (
    extract_certifications,
    extract_education,
    extract_positions_of_responsibility,
    extract_projects,
    extract_work_experience,
)


def _merge_unique_values(*value_groups):
    merged_values = []
    seen_values = set()

    for values in value_groups:
        for value in values or []:
            if not isinstance(value, str):
                continue

            cleaned_value = value.strip()
            normalized_value = cleaned_value.casefold()

            if not cleaned_value or normalized_value in seen_values:
                continue

            seen_values.add(normalized_value)
            merged_values.append(cleaned_value)

    return merged_values


def _first_person_candidate(nlp_analysis):
    people = nlp_analysis["entities"]["people"]
    header_people = [person for person in people if person["start"] < 500]
    candidates = header_people or people
    return candidates[0]["text"] if candidates else None


def _extract_candidate_name(text, nlp_analysis):
    return extract_name(text) or _first_person_candidate(nlp_analysis)


def parse_resume_text(text):
    """Parse extracted resume text entirely with local NLP and regex."""
    if not text or not text.strip():
        raise EmptyDocumentError(
            "No readable text was found in the uploaded document. "
            "Scanned PDFs are not supported yet."
        )

    nlp_analysis = analyze_resume_text(text)
    section_blocks = extract_section_blocks(text)
    nlp_skills = [
        skill_match["name"]
        for skill_match in nlp_analysis["skill_matches"]
        if skill_match.get("section") in {
            "skills",
            "projects",
            "work_experience",
            "positions_of_responsibility",
            "certifications",
        }
    ]

    return {
        "name": _extract_candidate_name(text, nlp_analysis),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "github": extract_github(text),
        "skills": _merge_unique_values(nlp_skills),
        "education": extract_education(
            section_blocks["education"], nlp_analysis
        ),
        "work_experience": extract_work_experience(
            section_blocks["experience"], nlp_analysis
        ),
        "projects": extract_projects(
            section_blocks["projects"], nlp_analysis
        ),
        "positions_of_responsibility": extract_positions_of_responsibility(
            section_blocks["leadership"]
        ),
        "certifications": extract_certifications(
            section_blocks["certifications"], nlp_analysis
        ),
        "nlp_analysis": nlp_analysis,
    }


def parse_resume_file(file_path):
    """Extract and parse one PDF or DOCX resume."""
    return parse_resume_text(extract_text(file_path))
