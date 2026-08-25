"""Certification extraction from sections and custom NLP entities."""

import re

from src.nlp.patterns import URL_PATTERN, clean_bullet
from src.nlp.structured.common import unique_strings


def extract_certifications(blocks, nlp_analysis):
    """Return deduplicated certification names and section evidence."""
    certification_values = []

    for block in blocks:
        for line in block:
            for value in re.split(r"\s*[;•]\s*", line):
                cleaned_value = URL_PATTERN.sub("", clean_bullet(value)).strip(" -|")
                if cleaned_value:
                    certification_values.append(cleaned_value)

    certification_values.extend(
        entity["text"]
        for entity in nlp_analysis["entities"].get("certifications", [])
    )
    return unique_strings(certification_values)
