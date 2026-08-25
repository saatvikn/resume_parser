"""Load and reuse the spaCy English language model."""

from functools import lru_cache

import spacy

from src.exceptions import NLPProcessingError
from src.nlp.patterns import entity_ruler_patterns


@lru_cache(maxsize=1)
def get_nlp():
    """Load spaCy once for reuse across one or many resume parses."""
    try:
        nlp = spacy.load("en_core_web_sm")
        ruler = nlp.add_pipe(
            "entity_ruler",
            after="ner",
            config={"overwrite_ents": True},
        )
        ruler.add_patterns(entity_ruler_patterns())
        return nlp
    except OSError as error:
        raise NLPProcessingError(
            "The spaCy English model is not installed. "
            "Install the dependencies from requirements.txt."
        ) from error
