"""Project extraction using record structure, URLs, and skill evidence."""

import re

from src.nlp.patterns import (
    DATE_RANGE_PATTERN,
    SINGLE_DATE_PATTERN,
    URL_PATTERN,
    clean_bullet,
    find_date_range,
    find_single_date,
)
from src.nlp.structured.common import (
    join_block,
    split_layout_columns,
    unique_strings,
)


def _project_technologies(block_text, nlp_analysis):
    normalized_block = block_text.casefold()
    return unique_strings(
        match["name"]
        for match in nlp_analysis["skill_matches"]
        if match.get("section") == "projects"
        and re.search(
            rf"(?<!\w){re.escape(match['text'].casefold())}(?!\w)",
            normalized_block,
        )
    )


def _normalized_link(link):
    if link and not link.casefold().startswith(("http://", "https://")):
        return f"https://{link}"
    return link


def extract_projects(blocks, nlp_analysis):
    """Build one project object per top-level project record."""
    projects = []

    for block in blocks:
        if not block:
            continue

        block_text = join_block(block)
        header_columns = split_layout_columns(block[0])
        header = clean_bullet(header_columns[0])
        link_match = URL_PATTERN.search(block_text)
        link = _normalized_link(link_match.group(0)) if link_match else None
        header = URL_PATTERN.sub("", header).strip(" |-:")
        header = DATE_RANGE_PATTERN.sub("", header).strip(" |-:")
        header = SINGLE_DATE_PATTERN.sub("", header).strip(" |-:")

        header_parts = re.split(r"\s+-\s+", header, maxsplit=1)
        name = header_parts[0].strip() if header_parts else None
        description_parts = []
        if len(header_parts) > 1:
            description_parts.append(header_parts[1].strip())

        for line in block[1:]:
            cleaned_line = clean_bullet(URL_PATTERN.sub("", line)).strip(" |-:")
            if not cleaned_line:
                continue
            if SINGLE_DATE_PATTERN.fullmatch(cleaned_line):
                continue
            if re.fullmatch(
                rf"{SINGLE_DATE_PATTERN.pattern}\s*(?:-|–|—|to)\s*"
                rf"(?:{SINGLE_DATE_PATTERN.pattern}|present|current|now)",
                cleaned_line,
                re.IGNORECASE,
            ):
                continue
            description_parts.append(cleaned_line)

        start_date, end_date = find_date_range(block_text)
        if not start_date:
            start_date = find_single_date(" ".join(header_columns[1:]))
            if not start_date:
                start_date = find_single_date(block_text)

        description = " ".join(unique_strings(description_parts)) or None
        technologies = _project_technologies(block_text, nlp_analysis)

        if not any((name, description, technologies, link)):
            continue

        projects.append(
            {
                "name": name,
                "description": description,
                "technologies": technologies,
                "link": link,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

    return projects
