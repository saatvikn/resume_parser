import re


def extract_email(text):
    """Return the first email address found in the supplied text."""
    match = re.search(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        text,
        )
    return match.group(0) if match else None


def extract_phone(text):
    """Return the first phone-number-like value found in the supplied text."""
    match = re.search(r"(\+?\d[\d\s\-()]{8,15}\d)", text)
    return match.group(0) if match else None


def extract_linkedin(text):
    """Return the first LinkedIn profile URL found in the supplied text."""
    match = re.search(
        r"(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9\-_]+",
        text,
    )
    return match.group(0) if match else None


def extract_name(text):
    """Use the first non-empty line as the candidate name."""
    for line in text.strip().split("\n"):
        if line.strip():
            return line.strip()
    return None
