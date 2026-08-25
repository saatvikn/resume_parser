"""Detect resume sections and group their records by structural markers."""

import re


SECTION_ALIASES = {
    "education": {
        "education",
        "academic background",
        "academic qualifications",
        "qualifications",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
    },
    "skills": {
        "skills",
        "technical skills",
        "core competencies",
        "technologies",
    },
    "certifications": {
        "certifications",
        "certificates",
        "licenses and certifications",
    },
    "projects": {
        "projects",
        "personal projects",
        "academic projects",
    },
    "leadership": {
        "positions of responsibility",
        "position of responsibility",
        "leadership",
        "leadership experience",
    },
    "other": {
        "achievements",
        "achievements and awards",
        "awards",
        "awards and honors",
        "awards & honors",
        "co-curricular activities",
        "courses",
        "coursework",
        "extra curricular activities",
        "extracurricular activities",
        "interests",
        "key courses taken",
        "languages",
        "professional summary",
        "publications",
        "summary",
        "volunteering",
    },
}

EXTRACTED_SECTIONS = {
    "education",
    "experience",
    "skills",
    "certifications",
    "projects",
    "leadership",
}

PUBLIC_SECTION_NAMES = {
    "experience": "work_experience",
    "leadership": "positions_of_responsibility",
}

TOP_LEVEL_BULLET_PATTERN = re.compile(r"^\s*[•▪]\s+")
INSTITUTION_PATTERN = re.compile(
    r"\b(?:academy|college|institute|school|university)\b",
    re.IGNORECASE,
)


def _normalized_heading(line):
    """Return comparable heading text without accepting bullet entries."""
    stripped_line = line.strip()
    if not stripped_line or TOP_LEVEL_BULLET_PATTERN.match(stripped_line):
        return ""
    return re.sub(r"\s+", " ", stripped_line).rstrip(":").strip().casefold()


def _looks_like_generic_heading(line):
    """Recognize short all-uppercase headings as section boundaries."""
    stripped_line = line.strip().rstrip(":").strip()
    words = stripped_line.split()
    return (
        1 <= len(words) <= 7
        and len(stripped_line) <= 60
        and any(character.isalpha() for character in stripped_line)
        and stripped_line.isupper()
    )


def identify_section_heading(line):
    """Return the canonical section name for a heading-like line."""
    normalized_line = _normalized_heading(line)

    for section_name, aliases in SECTION_ALIASES.items():
        if normalized_line in aliases:
            return section_name

    if normalized_line and _looks_like_generic_heading(line):
        return "other"

    return None


def public_section_name(section_name):
    """Translate an internal section name to its public output name."""
    if not section_name or section_name == "other":
        return None
    return PUBLIC_SECTION_NAMES.get(section_name, section_name)


def section_for_offset(text, character_offset):
    """Return the most recent resume section heading before an offset."""
    current_section = None
    consumed_characters = 0

    for line in text.splitlines(keepends=True):
        if consumed_characters > character_offset:
            break

        detected_section = identify_section_heading(line)
        if detected_section:
            current_section = detected_section

        consumed_characters += len(line)

    return public_section_name(current_section)


def _starts_new_record(section_name, line, current_block):
    """Decide whether a line begins a new record in the current section."""
    if not current_block:
        return False
    if TOP_LEVEL_BULLET_PATTERN.match(line):
        return section_name not in {"skills"}
    if (
        section_name == "education"
        and not line.lstrip().startswith("(")
        and INSTITUTION_PATTERN.search(line)
    ):
        return any(INSTITUTION_PATTERN.search(value) for value in current_block)
    return False


def extract_section_blocks(text):
    """Group section content by bullets and semantic starts, not whitespace."""
    section_blocks = {
        section_name: []
        for section_name in EXTRACTED_SECTIONS
    }
    current_section = None
    current_block = []

    def save_current_block():
        nonlocal current_block
        if current_section in EXTRACTED_SECTIONS and current_block:
            section_blocks[current_section].append(current_block)
        current_block = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        detected_section = identify_section_heading(line)

        if detected_section:
            save_current_block()
            current_section = detected_section
            continue
        if not line or current_section not in EXTRACTED_SECTIONS:
            continue
        if _starts_new_record(current_section, line, current_block):
            save_current_block()

        current_block.append(line)

    save_current_block()
    return section_blocks


def extract_sections(text):
    """Group resume lines under recognized section headings."""
    section_blocks = extract_section_blocks(text)

    return {
        section_name: [
            line
            for block in blocks
            for line in block
        ]
        for section_name, blocks in section_blocks.items()
    }
