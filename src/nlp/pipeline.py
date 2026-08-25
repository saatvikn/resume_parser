"""Orchestrate the local spaCy analysis for one resume."""

from src.extractors.sections import section_for_offset
from src.exceptions import NLPProcessingError
from src.nlp.entities import extract_named_entities
from src.nlp.model import get_nlp
from src.nlp.skills import extract_skill_matches


def analyze_resume_text(text):
    """Run spaCy once and return NER plus normalized skill evidence."""
    try:
        document = get_nlp()(text)
        skill_matches = extract_skill_matches(document)

        for skill in skill_matches:
            skill["section"] = section_for_offset(text, skill["start"])

        return {
            "entities": extract_named_entities(document, text, skill_matches),
            "skill_matches": skill_matches,
        }
    except NLPProcessingError:
        raise
    except Exception as error:
        raise NLPProcessingError(
            "The local NLP pipeline could not analyze this resume."
        ) from error
