import streamlit as st
import json
from src.extractors.contact import (
    extract_email,
    extract_linkedin,
    extract_name,
    extract_phone,
)
from src.extractors.sections import extract_sections
from src.extractors.skills import extract_skills
from src.extractors.text import extract_text
from src.services.gemini import extract_advanced_fields_with_gemini

import tempfile
import os

# Using NLP
def parse_resume(uploaded_file):
    # Having gthe correct file extension when saving as a tempfile
    # Get correct extension
    extension = os.path.splitext(uploaded_file.name)[-1].lower()
    if extension not in [".pdf", ".docx"]:
        raise ValueError("Only PDF and DOCX files are supported")

    # Save with correct suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    # Pass path to parser by calling the functions in util
    text = extract_text(temp_file_path)
    sections = extract_sections(text)

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

# Using gemini AI
def parse_resume_with_gemini(uploaded_file):
    # Having gthe correct file extension when saving as a tempfile
    # Get correct extension
    extension = os.path.splitext(uploaded_file.name)[-1].lower()
    if extension not in [".pdf", ".docx"]:
        raise ValueError("Only PDF and DOCX files are supported")

    # Save with correct suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    # Pass path to parser by calling the functions in utils_gemini
    text = extract_text(temp_file_path)

    return extract_advanced_fields_with_gemini(text)

# Streamlit app UI
st.set_page_config(page_title="Resume Parser", layout="wide")
st.title("📄 Resume Parser by Saatvik 🏢")

uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    with st.spinner("Parsing resume..."):
        ####
        #parsed_data = parse_resume(uploaded_file)
        parsed_data = parse_resume_with_gemini(uploaded_file)
        ####

    st.subheader("📅 Extracted Data")
    st.json(parsed_data)

    # Offer download as JSON button
    st.download_button(
        label="📥 Download JSON",
        data=json.dumps(parsed_data, indent=4),
        file_name="parsed_resume.json",
        mime="application/json"
    )
