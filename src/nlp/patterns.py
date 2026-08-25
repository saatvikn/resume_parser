"""Resume-specific NLP phrases and regular-expression patterns."""

import re


DEGREE_PHRASES = [
    "associate degree",
    "bachelor of arts",
    "bachelor of business administration",
    "bachelor of commerce",
    "bachelor of computer applications",
    "bachelor of engineering",
    "bachelor of science",
    "bachelor of technology",
    "b.a.",
    "b.b.a.",
    "b.com",
    "b.c.a.",
    "b.e.",
    "b.sc",
    "b.tech",
    "doctor of philosophy",
    "master of arts",
    "master of business administration",
    "master of computer applications",
    "master of engineering",
    "master of science",
    "master of technology",
    "m.a.",
    "m.b.a.",
    "m.c.a.",
    "m.e.",
    "m.s.",
    "m.sc",
    "m.tech",
    "ph.d.",
]

JOB_TITLE_PHRASES = [
    "ai engineer",
    "backend developer",
    "backend engineer",
    "business analyst",
    "data analyst",
    "data engineer",
    "data scientist",
    "devops engineer",
    "frontend developer",
    "frontend engineer",
    "full stack developer",
    "full stack engineer",
    "graduate engineer trainee",
    "machine learning engineer",
    "mobile application developer",
    "product manager",
    "project manager",
    "research assistant",
    "research intern",
    "software developer",
    "software development engineer",
    "software engineer",
    "software engineering intern",
    "software intern",
    "systems engineer",
    "technical lead",
    "teaching assistant",
    "web developer",
]

CERTIFICATION_PHRASES = [
    "aws certified cloud practitioner",
    "aws certified developer",
    "aws certified solutions architect",
    "azure fundamentals",
    "certified kubernetes administrator",
    "google associate cloud engineer",
    "google data analytics professional certificate",
    "microsoft certified azure fundamentals",
    "oracle certified professional",
    "professional scrum master",
]


def entity_ruler_patterns():
    """Return case-insensitive phrase patterns for spaCy EntityRuler."""
    patterns = []

    for label, phrases in (
        ("DEGREE", DEGREE_PHRASES),
        ("JOB_TITLE", JOB_TITLE_PHRASES),
        ("CERTIFICATION", CERTIFICATION_PHRASES),
    ):
        for phrase in phrases:
            patterns.append(
                {
                    "label": label,
                    "pattern": [
                        {"LOWER": token}
                        for token in phrase.lower().split()
                    ],
                }
            )

    return patterns


MONTH = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
    r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
    r"nov(?:ember)?|dec(?:ember)?)"
)
DATE_VALUE = rf"(?:{MONTH}\s+\d{{4}}|\d{{1,2}}[/-]\d{{4}}|\d{{4}})"
DATE_RANGE_PATTERN = re.compile(
    rf"(?P<start>{DATE_VALUE})\s*(?:-|–|—|to)\s*"
    rf"(?P<end>{DATE_VALUE}|present|current|now)",
    re.IGNORECASE,
)
SINGLE_DATE_PATTERN = re.compile(DATE_VALUE, re.IGNORECASE)
GRADE_PATTERN = re.compile(
    r"\b(?:(?:cgpa|gpa|grade)\s*[:\-]?\s*\d+(?:\.\d+)?"
    r"(?:\s*/\s*\d+(?:\.\d+)?)?(?:\s*%)?"
    r"|\d+(?:\.\d+)?\s*(?:%|percent))(?!\w)",
    re.IGNORECASE,
)
URL_PATTERN = re.compile(
    r"(?:(?:https?://|www\.)[^\s)\]}>,]+|"
    r"(?:github|gitlab)\.com/[a-zA-Z0-9._/-]+)",
    re.IGNORECASE,
)
BULLET_PREFIX_PATTERN = re.compile(r"^\s*(?:[-•▪◦*]|\d+[.)])\s*")


def find_date_range(text):
    """Return normalized start/end dates from the first date range."""
    match = DATE_RANGE_PATTERN.search(text)
    if not match:
        return None, None
    return match.group("start").strip(), match.group("end").strip()


def find_single_date(text):
    """Return the first standalone month/year or year value."""
    match = SINGLE_DATE_PATTERN.search(text)
    return match.group(0).strip() if match else None


def find_grade(text):
    """Return the first GPA, CGPA, or percentage value."""
    match = GRADE_PATTERN.search(text)
    return match.group(0).strip() if match else None


def clean_bullet(text):
    """Remove a common list prefix and surrounding whitespace."""
    return BULLET_PREFIX_PATTERN.sub("", text).strip()
