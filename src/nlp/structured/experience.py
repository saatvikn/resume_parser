"""Work-experience extraction using record structure and NLP evidence."""

import re

from src.nlp.patterns import (
    DATE_RANGE_PATTERN,
    JOB_TITLE_PHRASES,
    URL_PATTERN,
    clean_bullet,
    find_date_range,
)
from src.nlp.structured.common import (
    contains_phrase,
    entities_in_block,
    join_block,
    split_layout_columns,
    unique_strings,
)


NESTED_BULLET_PATTERN = re.compile(r"^\s*(?:◦|o\s{2,}|[-▪*])\s*")
EMPLOYMENT_TYPE_PATTERN = re.compile(
    r"\s*\((?:full[- ]time|part[- ]time|internship|contract)\)\s*$",
    re.IGNORECASE,
)


def _header_lines(block):
    """Return lines preceding the first nested responsibility bullet."""
    headers = []
    for line in block:
        if NESTED_BULLET_PATTERN.match(line):
            break
        headers.append(line)
    return headers


def _job_title_from_block(block, job_title_entities):
    """Prefer the first record header as the role title."""
    if block:
        candidate = clean_bullet(split_layout_columns(block[0])[0])
        if len(candidate.split()) <= 12:
            return candidate

    if job_title_entities:
        return job_title_entities[0]["text"]
    return contains_phrase(join_block(block), JOB_TITLE_PHRASES)


def _company_from_headers(headers, job_title, organization_entities):
    """Select a company only from record header lines."""
    for line in headers[1:]:
        candidate = clean_bullet(split_layout_columns(line)[0])
        if not candidate or DATE_RANGE_PATTERN.fullmatch(candidate):
            continue
        if job_title and candidate.casefold() == job_title.casefold():
            continue
        if candidate.casefold() in {"remote", "hybrid", "onsite", "on-site"}:
            continue
        candidate = DATE_RANGE_PATTERN.sub("", candidate).strip(" |-:")
        return EMPLOYMENT_TYPE_PATTERN.sub("", candidate).strip()

    return organization_entities[0]["text"] if organization_entities else None


def _location_from_headers(headers, location_entities):
    """Extract an explicit location from the record's right-hand column."""
    for line in headers:
        for column in split_layout_columns(line)[1:]:
            if DATE_RANGE_PATTERN.search(column):
                continue
            if len(column.split()) <= 5:
                return column

    for line in headers:
        cleaned_line = clean_bullet(line).strip()
        if cleaned_line.casefold() in {"remote", "hybrid", "onsite", "on-site"}:
            return cleaned_line
    return location_entities[0]["text"] if location_entities else None


def _responsibilities(block):
    """Keep nested bullets as responsibilities and exclude record headers."""
    nested_responsibilities = [
        clean_bullet(line)
        for line in block
        if NESTED_BULLET_PATTERN.match(line)
    ]
    if nested_responsibilities:
        return unique_strings(nested_responsibilities)

    responsibilities = []
    for line in block[2:]:
        cleaned_line = clean_bullet(line)
        if URL_PATTERN.fullmatch(cleaned_line):
            continue
        if DATE_RANGE_PATTERN.search(cleaned_line):
            continue
        if len(cleaned_line.split()) >= 5:
            responsibilities.append(cleaned_line)
    return unique_strings(responsibilities)


def extract_work_experience(blocks, nlp_analysis):
    """Build structured work-experience records from section blocks."""
    experience_records = []

    for block in blocks:
        block_text = join_block(block)
        if not block_text:
            continue

        organizations = entities_in_block(
            nlp_analysis, "organizations", block, "work_experience"
        )
        job_titles = entities_in_block(
            nlp_analysis, "job_titles", block, "work_experience"
        )
        locations = entities_in_block(
            nlp_analysis, "locations", block, "work_experience"
        )
        headers = _header_lines(block)

        job_title = _job_title_from_block(block, job_titles)
        company = _company_from_headers(headers, job_title, organizations)
        location = _location_from_headers(headers, locations)
        start_date, end_date = find_date_range(block_text)
        responsibilities = _responsibilities(block)

        if not any((company, job_title, start_date, responsibilities)):
            continue

        experience_records.append(
            {
                "company": company,
                "job_title": job_title,
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
                "responsibilities": responsibilities,
            }
        )

    return experience_records
