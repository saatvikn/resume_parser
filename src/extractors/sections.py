"""Detect resume sections and group their records by structural markers."""

import re


SECTION_ALIASES = {
    "education": {
        "education",
        "academic background",
        # Used by the tabular BITS resume in the local sample set.
        "academic details",
        "academic qualifications",
        "qualifications",
    },
    "experience": {
        "experience",
        "internship experience",
        "summer internship",
        # This combined heading was previously discarded as an unknown section.
        "summer internship / work experience",
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

TOP_LEVEL_BULLET_PATTERN = re.compile(r"^\s*[•▪](?:\s+|$)")
INSTITUTION_PATTERN = re.compile(
    r"\b(?:academy|college|institute|school|university)\b",
    re.IGNORECASE,
)


def _normalized_heading(line):
    stripped_line = line.strip()
    if not stripped_line or TOP_LEVEL_BULLET_PATTERN.match(stripped_line):
        return ""
    return re.sub(r"\s+", " ", stripped_line).rstrip(":").strip().casefold()


def _looks_like_table_header(line):
    stripped_line = line.strip()
    # Column labels such as "COURSE | INSTITUTE | SCORE" sit inside a section.
    # Treating them as generic headings caused the rows below them to disappear.
    return "|" in stripped_line and stripped_line.isupper()


def _looks_like_generic_heading(line):
    stripped_line = line.strip().rstrip(":").strip()
    words = stripped_line.split()
    return (
        1 <= len(words) <= 7
        and len(stripped_line) <= 60
        and "|" not in stripped_line
        and not any(character.isdigit() for character in stripped_line)
        and any(character.isalpha() for character in stripped_line)
        and stripped_line.isupper()
    )


def identify_section_heading(line):
    normalized_line = _normalized_heading(line)

    for section_name, aliases in SECTION_ALIASES.items():
        if normalized_line in aliases:
            return section_name

    if normalized_line and _looks_like_generic_heading(line):
        return "other"

    return None


def public_section_name(section_name):
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


def _starts_with_job_title(line):
    from src.nlp.patterns import JOB_TITLE_PHRASES, clean_bullet

    cleaned_line = clean_bullet(line).casefold()
    if len(cleaned_line.split()) > 18:
        return False

    return any(
        re.match(rf"^{re.escape(job_title)}(?:\b|\s*[|,–—-])", cleaned_line)
        for job_title in JOB_TITLE_PHRASES
    )


def _looks_like_dated_header(line):
    from src.nlp.patterns import DATE_RANGE_PATTERN, clean_bullet

    return (
        len(clean_bullet(line).split()) <= 24
        and DATE_RANGE_PATTERN.search(line) is not None
    )


def _looks_like_project_header(line):
    if _looks_like_dated_header(line):
        return True
    if not TOP_LEVEL_BULLET_PATTERN.match(line):
        return False

    from src.nlp.patterns import clean_bullet

    header, separator, _ = clean_bullet(line).partition(":")
    return bool(separator) and 1 <= len(header.split()) <= 12


def _starts_new_record(section_name, line, current_block):
    if not current_block:
        return False

    # Real resumes in the sample set use the same `•` marker for record
    # headers and descriptions. Section-specific signals avoid turning every
    # responsibility into a separate job, project, or leadership position.
    if section_name == "experience":
        return _starts_with_job_title(line)
    if section_name == "projects":
        return _looks_like_project_header(line)
    if section_name == "leadership":
        return _looks_like_dated_header(line)
    if section_name == "certifications":
        return TOP_LEVEL_BULLET_PATTERN.match(line) is not None
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
        if _looks_like_table_header(line):
            continue

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
    section_blocks = extract_section_blocks(text)

    return {
        section_name: [
            line
            for block in blocks
            for line in block
        ]
        for section_name, blocks in section_blocks.items()
    }
