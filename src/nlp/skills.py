"""Skill extraction using spaCy's PhraseMatcher."""

from functools import lru_cache
import json
from pathlib import Path

from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
from spacy.util import filter_spans

from src.nlp.model import get_nlp


SKILLS_PATH = Path(__file__).resolve().parents[2] / "data" / "skills.json"


@lru_cache(maxsize=1)
def load_skill_taxonomy():
    """Load canonical skill names and their aliases."""
    with SKILLS_PATH.open(encoding="utf-8") as skills_file:
        return json.load(skills_file)


@lru_cache(maxsize=1)
def get_skill_aliases():
    """Map normalized aliases to their canonical skill names."""
    aliases = {}

    for canonical_name, skill_aliases in load_skill_taxonomy().items():
        aliases[canonical_name.casefold()] = canonical_name
        for alias in skill_aliases:
            aliases[alias.casefold()] = canonical_name

    return aliases


def canonicalize_skill_values(values):
    """Normalize known aliases while preserving unknown skill values."""
    aliases = get_skill_aliases()
    return [
        aliases.get(value.strip().casefold(), value.strip())
        for value in values or []
        if isinstance(value, str) and value.strip()
    ]


@lru_cache(maxsize=1)
def get_skill_matcher():
    """Build and reuse a case-insensitive skill phrase matcher."""
    nlp = get_nlp()
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    for canonical_name, aliases in load_skill_taxonomy().items():
        patterns = [nlp.make_doc(alias) for alias in aliases]
        matcher.add(canonical_name, patterns)

    return matcher


def extract_skill_matches(document):
    """Return normalized, non-overlapping skills with source evidence."""
    matcher = get_skill_matcher()
    spans = [
        Span(document, start, end, label=match_id)
        for match_id, start, end in matcher(document)
    ]
    filtered_spans = filter_spans(spans)

    matches = []

    for span in sorted(filtered_spans, key=lambda item: item.start_char):
        canonical_name = document.vocab.strings[span.label]
        matches.append(
            {
                "name": canonical_name,
                "text": span.text,
                "start": span.start_char,
                "end": span.end_char,
                "section": None,
            }
        )

    return matches
