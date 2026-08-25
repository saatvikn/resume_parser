import re


def extract_skills(section_lines):
    """Split the contents of a skills section into individual values."""
    text = " ".join(section_lines)
    return [
        skill.strip()
        for skill in re.split(r"[,•;]", text)
        if skill.strip()
    ]
