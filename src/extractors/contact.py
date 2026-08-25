"""Deterministic extraction of resume header and contact fields."""

import re


PROFILE_PATH_PATTERN = r"[a-zA-Z0-9][a-zA-Z0-9._-]*"


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
    return match.group(0).strip() if match else None


def _normalized_profile_url(profile_url):
    """Add HTTPS when a detected profile URL has no scheme."""
    cleaned_url = profile_url.strip().rstrip(".,;)")
    if not cleaned_url.casefold().startswith(("http://", "https://")):
        return f"https://{cleaned_url}"
    return cleaned_url


def extract_linkedin(text):
    """Return a normalized LinkedIn URL or build one from a labeled handle."""
    url_match = re.search(
        rf"(?:https?://)?(?:www\.)?linkedin\.com/in/{PROFILE_PATH_PATTERN}",
        text,
        re.IGNORECASE,
    )
    if url_match:
        return _normalized_profile_url(url_match.group(0))

    handle_match = re.search(
        rf"\blinkedin\s*:\s*@?(?P<handle>{PROFILE_PATH_PATTERN})\b",
        text,
        re.IGNORECASE,
    )
    if handle_match:
        return f"https://linkedin.com/in/{handle_match.group('handle')}"
    return None


def extract_github(text):
    """Return the first normalized GitHub profile URL."""
    match = re.search(
        rf"(?:https?://)?(?:www\.)?github\.com/{PROFILE_PATH_PATTERN}",
        text,
        re.IGNORECASE,
    )
    return _normalized_profile_url(match.group(0)) if match else None


def _looks_like_name(line):
    """Return whether a header line resembles a person's name."""
    if any(marker in line.casefold() for marker in ("@", "http", "linkedin", "github")):
        return False
    if any(character.isdigit() for character in line) or "|" in line:
        return False

    words = line.split()
    if not 2 <= len(words) <= 5:
        return False
    return all(re.fullmatch(r"[A-Za-z][A-Za-z.'-]*", word) for word in words)


def extract_name(text):
    """Return the first plausible name from the resume header."""
    non_empty_lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in non_empty_lines[:8]:
        if _looks_like_name(line):
            return line.title() if line.isupper() else line
    return None
