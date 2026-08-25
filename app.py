import json
import streamlit as st

from src.exceptions import ResumeParserError
from src.parser import parse_resume_file
from src.utils.uploads import temporary_upload

# Streamlit app UI
st.set_page_config(page_title="Resume Parser", layout="wide")
st.title("📄 Resume Parser by Saatvik 🏢")

uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    try:
        with st.spinner("Parsing resume..."):
            with temporary_upload(uploaded_file) as file_path:
                parsed_data = parse_resume_file(file_path, use_gemini=True)
    except ResumeParserError as error:
        st.error(str(error))
    else:
        st.subheader("📅 Extracted Data")
        st.json(parsed_data)

        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(parsed_data, indent=4),
            file_name="parsed_resume.json",
            mime="application/json",
        )
