"""Clean explicitly listed values from a resume skills section."""

import re

from src.nlp.patterns import clean_bullet


CATEGORY_PREFIX_PATTERN = re.compile(
    r"^(?:languages?|frameworks?|databases?|tools?|technologies|"
    r"operating systems?|oss?)\s*:?\s*",
    re.IGNORECASE,
)
PROFICIENCY_PATTERN = re.compile(
    r"\s*\((?:beginner|basic|intermediate|advanced|expert|proficient)\)\s*$",
    re.IGNORECASE,
)
CATEGORY_NAMES = {
    "database",
    "databases",
    "framework",
    "frameworks",
    "language",
    "languages",
    "operating systems",
    "os",
    "oss",
    "technologies",
    "tools",
}


def extract_skills(section_lines):
    """Return cleaned skill values without category or proficiency labels."""
    extracted_skills = []

    for line in section_lines:
        cleaned_line = clean_bullet(line)
        cleaned_line = CATEGORY_PREFIX_PATTERN.sub("", cleaned_line)

        for value in re.split(r"[,;|]", cleaned_line):
            cleaned_value = PROFICIENCY_PATTERN.sub("", value).strip(" :-")
            if not cleaned_value:
                continue
            if cleaned_value.casefold() in CATEGORY_NAMES:
                continue
            if len(cleaned_value.split()) > 6:
                continue
            extracted_skills.append(cleaned_value)

    return extracted_skills
