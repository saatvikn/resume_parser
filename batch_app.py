import streamlit as st
import json
import tempfile
import os
from utils import extract_text
from utils_gemini import extract_advanced_fields_with_gemini
import pandas as pd

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
    with st.spinner("Parsing resumes..."):
        for uploaded_file in uploaded_files:
            suffix = os.path.splitext(uploaded_file.name)[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_path = temp_file.name

            text = extract_text(temp_path)
            data = extract_advanced_fields_with_gemini(text)
            data['file_name'] = uploaded_file.name
            results.append(data)

    st.success("✅ Batch parsing complete!")

    # Show results per file
    for result in results:
        # with st.expander(f"📄 {result.get('file_name', 'Resume')}"):
        #     st.json(result)

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

            # # Work Experience
            # experience = result.get('work_experience', [])
            # if experience:
            #     st.write("### Work Experience")

            #     # Clean responsibilities for display
            #     for exp in experience:
            #         if isinstance(exp.get('responsibilities'), list):
            #              exp['responsibilities'] = "\n".join(exp['responsibilities'])

            #     st.table(pd.DataFrame(experience))
            # else:
            #     st.write("No experience details found.")

            # Projects
            projects = result.get('projects', [])
            if projects:
                st.write("### Projects")
                st.table(pd.DataFrame(projects))
            else:
                st.write("No project details found.")

    # Download all results as combined JSON
    combined_json = json.dumps(results, indent=4)
    st.download_button(
        label="📥 Download All Results as JSON",
        data=combined_json,
        file_name="batch_parsed_results.json",
        mime="application/json"
    )
