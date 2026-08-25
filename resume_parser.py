from src.extractors.contact import (
    extract_email,
    extract_linkedin,
    extract_name,
    extract_phone,
)
from src.extractors.sections import extract_sections
from src.extractors.skills import extract_skills
from src.extractors.text import extract_text
from src.utils.file_io import save_to_json
import json
import sys

def parse_advanced_fields(file_path):
    text = extract_text(file_path)
    sections = extract_sections(text)

    # print("\n=== RAW TEXT ===")
    # print(text)

    data = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "education": sections.get("education", []),
        "experience": sections.get("experience", []),
        "skills": extract_skills(sections.get("skills", [])),
        "certifications": sections.get("certifications", []),
        "projects": sections.get("projects", [])
    }

    return data

if __name__ == "__main__":

    file_path = sys.argv[1]
    parsed_data = parse_advanced_fields(file_path)

    # Print in terminal
    print("\n=== Parsed Data ===")
    print(json.dumps(parsed_data, indent=4))

    # Save to JSON file
    save_to_json(parsed_data, output_path="output/parsed_resume.json")
    print("\n✅ Data saved to output/parsed_resume.json")
