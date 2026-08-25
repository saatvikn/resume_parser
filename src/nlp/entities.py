"""Named-entity extraction with skill-aware filtering."""

import re

from src.extractors.sections import identify_section_heading, section_for_offset


ENTITY_GROUPS = {
    "PERSON": "people",
    "ORG": "organizations",
    "GPE": "locations",
    "LOC": "locations",
    "DATE": "dates",
    "DEGREE": "degrees",
    "JOB_TITLE": "job_titles",
    "CERTIFICATION": "certifications",
}


def _overlaps_skill(entity, skill_matches):
    return any(
        entity.start_char < skill["end"] and entity.end_char > skill["start"]
        for skill in skill_matches
    )


def extract_named_entities(document, source_text, skill_matches):
    """Group useful entities while excluding spans already known as skills."""
    entities = {
        "people": [],
        "organizations": [],
        "locations": [],
        "dates": [],
        "degrees": [],
        "job_titles": [],
        "certifications": [],
    }
    seen_entities = set()

    for entity in document.ents:
        group_name = ENTITY_GROUPS.get(entity.label_)
        raw_entity_text = entity.text

        if entity.label_ == "DATE" and "\n" in raw_entity_text:
            raw_entity_text = raw_entity_text.splitlines()[0]

        entity_text = re.sub(r"\s+", " ", raw_entity_text).strip()
        entity_end = entity.start_char + len(raw_entity_text.rstrip())

        if not group_name or not entity_text:
            continue
        if identify_section_heading(entity_text):
            continue
        if (
            entity.label_ in {"PERSON", "ORG", "GPE", "LOC", "DATE"}
            and _overlaps_skill(entity, skill_matches)
        ):
            continue
        if (
            entity.label_ == "DATE"
            and len(re.sub(r"\D", "", entity_text)) >= 7
        ):
            continue

        identity = (group_name, entity_text.casefold())
        if identity in seen_entities:
            continue

        seen_entities.add(identity)
        entities[group_name].append(
            {
                "text": entity_text,
                "label": entity.label_,
                "start": entity.start_char,
                "end": entity_end,
                "section": section_for_offset(source_text, entity.start_char),
            }
        )

    return entities
