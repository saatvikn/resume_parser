def extract_sections(text):
    """Group resume lines under a small set of recognized section headings."""
    sections = {
        "education": [],
        "experience": [],
        "skills": [],
        "certifications": [],
        "projects": [],
    }

    current_section = None
    for line in text.split("\n"):
        line_lower = line.strip().lower()

        if "education" in line_lower:
            current_section = "education"
        elif "experience" in line_lower or "work history" in line_lower:
            current_section = "experience"
        elif "skill" in line_lower:
            current_section = "skills"
        elif "certification" in line_lower:
            current_section = "certifications"
        elif "project" in line_lower:
            current_section = "projects"
        elif not line.strip():
            current_section = None
        elif current_section:
            sections[current_section].append(line.strip())

    return sections
