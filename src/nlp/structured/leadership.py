"""Extract positions of responsibility from leadership section records."""

import re

from src.nlp.patterns import DATE_RANGE_PATTERN, clean_bullet, find_date_range
from src.nlp.structured.common import (
    join_block,
    split_layout_columns,
    unique_strings,
)


NESTED_BULLET_PATTERN = re.compile(r"^\s*(?:◦|o\s{2,}|[-▪*])\s*")


def extract_positions_of_responsibility(blocks):
    """Build structured leadership records from top-level bullets."""
    positions = []

    for block in blocks:
        if not block:
            continue

        header_lines = []
        responsibilities = []
        for line in block:
            if NESTED_BULLET_PATTERN.match(line):
                responsibilities.append(clean_bullet(line))
            elif not responsibilities:
                header_lines.append(line)
            else:
                responsibilities.append(clean_bullet(line))

        first_columns = [
            clean_bullet(split_layout_columns(line)[0])
            for line in header_lines
        ]
        title = first_columns[0] if first_columns else None
        organization = first_columns[1] if len(first_columns) > 1 else None

        location = None
        for line in header_lines:
            for column in split_layout_columns(line)[1:]:
                if not DATE_RANGE_PATTERN.search(column):
                    location = column
                    break
            if location:
                break

        start_date, end_date = find_date_range(join_block(block))
        positions.append(
            {
                "title": title,
                "organization": organization,
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
                "responsibilities": unique_strings(responsibilities),
            }
        )

    return positions
