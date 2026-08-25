"""Education extraction using section structure, NLP evidence, and regex."""

import re

from src.nlp.patterns import (
    DATE_RANGE_PATTERN,
    DATE_VALUE,
    DEGREE_PHRASES,
    clean_bullet,
    find_date_range,
    find_grade,
    find_single_date,
)
from src.nlp.structured.common import (
    contains_phrase,
    entities_in_block,
    join_block,
    split_layout_columns,
)


INSTITUTION_PATTERN = re.compile(
    r"\b(?:academy|college|institute|school|university)\b",
    re.IGNORECASE,
)
GRADUATION_LABEL_PATTERN = re.compile(
    rf"(?:expected\s+)?graduation(?:\s+year)?\s*:\s*(?P<date>{DATE_VALUE})",
    re.IGNORECASE,
)


def _institution_from_block(block, institutions):
    """Prefer a header institution line over generic ORG entities."""
    for line in block:
        first_column = clean_bullet(split_layout_columns(line)[0])
        if INSTITUTION_PATTERN.search(first_column):
            return first_column

    return institutions[0]["text"] if institutions else None


def _degree_from_block(block, degree_entities):
    """Keep the complete degree/major line instead of only a matched phrase."""
    for line in block:
        first_column = clean_bullet(split_layout_columns(line)[0])
        if contains_phrase(first_column, DEGREE_PHRASES):
            return re.split(
                r"\s*;\s*(?:gpa|cgpa|grade)\b",
                first_column,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip()
        if re.search(r"\bclass\s+(?:x|xii|10|12)\b", first_column, re.IGNORECASE):
            return first_column

    return degree_entities[0]["text"] if degree_entities else None


def _graduation_date_from_block(block_text, date_entities):
    """Prefer labeled graduation dates or the end of an education range."""
    labeled_date = GRADUATION_LABEL_PATTERN.search(block_text)
    if labeled_date:
        return labeled_date.group("date").strip()

    start_date, end_date = find_date_range(block_text)
    if start_date and end_date:
        return end_date
    if date_entities:
        return date_entities[-1]["text"]
    return find_single_date(block_text)


def _location_from_block(block, locations):
    """Use an explicit right-column location before a generic GPE entity."""
    for line in block:
        columns = split_layout_columns(line)
        for column in columns[1:]:
            if DATE_RANGE_PATTERN.search(column):
                continue
            if GRADUATION_LABEL_PATTERN.search(column):
                continue
            if find_grade(column) or len(column.split()) > 5:
                continue
            return column

    if locations:
        return locations[0]["text"]

    for line in block:
        first_column = clean_bullet(split_layout_columns(line)[0])
        if INSTITUTION_PATTERN.search(first_column) and "," in first_column:
            location_candidate = first_column.rsplit(",", maxsplit=1)[-1].strip()
            if len(location_candidate.split()) <= 3:
                return location_candidate
    return None


def extract_education(blocks, nlp_analysis):
    """Build normalized education objects from education section blocks."""
    education_records = []

    for block in blocks:
        block_text = join_block(block)
        if not block_text:
            continue

        institutions = entities_in_block(
            nlp_analysis, "organizations", block, "education"
        )
        degrees = entities_in_block(
            nlp_analysis, "degrees", block, "education"
        )
        dates = entities_in_block(nlp_analysis, "dates", block, "education")
        locations = entities_in_block(
            nlp_analysis, "locations", block, "education"
        )

        institution = _institution_from_block(block, institutions)
        degree = _degree_from_block(block, degrees)
        grade = find_grade(block_text)
        graduation_date = _graduation_date_from_block(block_text, dates)
        location = _location_from_block(block, locations)

        if not any((institution, degree, graduation_date, grade)):
            continue

        education_records.append(
            {
                "institution": institution,
                "degree": degree,
                "grade": grade,
                "graduation_date": graduation_date,
                "location": location,
            }
        )

    return education_records
