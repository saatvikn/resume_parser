from pdfminer.high_level import extract_text as extract_pdf_text
import docx2txt
import os
import re

import spacy

import json

nlp = spacy.load("en_core_web_sm")

def extract_text(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        return extract_pdf_text(file_path)
    elif ext == ".docx":
        return docx2txt.process(file_path)
    else:
        raise ValueError("Unsupported file format: Only PDF and DOCX are allowed")
    
def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r"(\+?\d[\d\s\-()]{8,15}\d)", text)
    return match.group(0) if match else None

def extract_linkedin(text):
    match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9\-_]+", text)
    return match.group(0) if match else None

def extract_name(text):
    lines = text.strip().split("\n")
    for line in lines:
        if line.strip():
            return line.strip()
    return None

# not working all the time so switch to llm
def extract_sections(text):
    sections = {
        "education": [],
        "experience": [],
        "skills": [],
        "certifications": [],
        "projects": []
    }

    current_section = None
    for line in text.split("\n"):
        line_lower = line.strip().lower()

        # Identify the section headers
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
        elif line.strip() == "":
            current_section = None
        elif current_section:
            sections[current_section].append(line.strip())

    return sections

def extract_skills(section_lines):
    text = " ".join(section_lines)
    return [skill.strip() for skill in re.split(r"[,•;]", text) if skill.strip()]

def save_to_json(data, output_path="output/parsed_resume.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
