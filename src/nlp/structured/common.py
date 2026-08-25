"""Shared helpers for structured local resume extraction."""

import re

from src.nlp.patterns import clean_bullet


def join_block(block):
    """Join a section block into searchable text."""
    return "\n".join(line.strip() for line in block if line.strip())


def split_layout_columns(line):
    """Split columns marked by the layout-aware text extractor."""
    return [
        value.strip()
        for value in re.split(r"\s*\|\s*", line)
        if value.strip()
    ]


def entities_in_block(nlp_analysis, group_name, block, section_name):
    """Return entity records whose text appears in a section block."""
    block_text = join_block(block).casefold()
    return [
        entity
        for entity in nlp_analysis["entities"].get(group_name, [])
        if entity.get("section") == section_name
        and entity["text"].casefold() in block_text
    ]


def unique_strings(values):
    """Deduplicate non-empty strings without changing their order."""
    unique_values = []
    seen_values = set()

    for value in values:
        if not isinstance(value, str):
            continue

        cleaned_value = clean_bullet(value)
        normalized_value = cleaned_value.casefold()
        if not cleaned_value or normalized_value in seen_values:
            continue

        seen_values.add(normalized_value)
        unique_values.append(cleaned_value)

    return unique_values


def contains_phrase(text, phrases):
    """Return the first configured phrase found in text."""
    normalized_text = text.casefold()

    for phrase in sorted(phrases, key=len, reverse=True):
        if re.search(
            rf"(?<!\w){re.escape(phrase.casefold())}(?!\w)",
            normalized_text,
        ):
            return phrase

    return None
