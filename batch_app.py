import streamlit as st
import json
import pandas as pd

from src.exceptions import ResumeParserError
from src.parser import parse_resume_file
from src.utils.uploads import temporary_upload

st.set_page_config(page_title="Batch Resume Parser", layout="wide")
st.title("📄 Batch Resume Parser")

st.markdown("""
Upload **multiple resumes (PDF or DOCX)** below.  
Each will be parsed using Gemini and results will be combined for download.
""")

uploaded_files = st.file_uploader(
    "Upload multiple resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if uploaded_files:
    results = []
    failures = []

    with st.spinner("Parsing resumes..."):
        for uploaded_file in uploaded_files:
            try:
                with temporary_upload(uploaded_file) as file_path:
                    data = parse_resume_file(file_path, use_gemini=True)
            except ResumeParserError as error:
                failures.append((uploaded_file.name, str(error)))
                continue

            data["file_name"] = uploaded_file.name
            results.append(data)

    if results:
        st.success(
            f"✅ Parsed {len(results)} of {len(uploaded_files)} resumes."
        )

    for file_name, error_message in failures:
        st.warning(f"Could not parse {file_name}: {error_message}")

    for result in results:
        with st.expander(f"📄 {result.get('file_name', 'Resume')}"):
            st.write("### Basic Info")
            st.write(f"**Name:** {result.get('name', 'N/A')}")
            st.write(f"**Email:** {result.get('email', 'N/A')}")
            st.write(f"**Phone:** {result.get('phone', 'N/A')}")
            st.write(f"**LinkedIn:** {result.get('linkedin', 'N/A')}")

            # Skills
            skills = result.get('skills', [])
            if skills:
                st.write("### Skills")
                st.table(pd.DataFrame(skills, columns=['Skill']))
            else:
                st.write("No skills found.")

            # Education
            education = result.get('education', [])
            if education:
                st.write("### Education")
                st.table(pd.DataFrame(education))
            else:
                st.write("No education details found.")
            
            # Work Experience
            experience = result.get('work_experience', [])
            if experience:
                st.write("### Work Experience")

                for exp in experience:
                    st.markdown(f"""
                    **Company:** {exp.get('company', 'N/A')}  
                    **Job Title:** {exp.get('job_title', 'N/A')}  
                    **Duration:** {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}  
                    **Location:** {exp.get('location', 'N/A')}
                    """)

                    responsibilities = exp.get('responsibilities', [])
                    if responsibilities:
                        st.write("**Responsibilities:**")
                        for resp in responsibilities:
                            st.markdown(f"- {resp}")
                    st.markdown("---")
            else:
                st.write("No experience details found.")

            # Projects
            projects = result.get('projects', [])
            if projects:
                st.write("### Projects")
                st.table(pd.DataFrame(projects))
            else:
                st.write("No project details found.")

    if results:
        combined_json = json.dumps(results, indent=4)
        st.download_button(
            label="📥 Download All Results as JSON",
            data=combined_json,
            file_name="batch_parsed_results.json",
            mime="application/json",
        )
