"""Unified Streamlit interface for one or more local resume parses."""

import hashlib
import html
import json
from pathlib import Path
import re

import streamlit as st

from src.exceptions import ResumeParserError
from src.parser import parse_resume_file
from src.utils.uploads import temporary_upload


PARSER_CACHE_VERSION = "phrase-matcher-only-v3"


st.set_page_config(
    page_title="NLP Resume Parser",
    page_icon="📄",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }
        .local-badge {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border: 1px solid #34d399;
            border-radius: 999px;
            color: #047857;
            background: rgba(52, 211, 153, 0.12);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            margin-bottom: 0.7rem;
        }
        .hero-copy {
            color: #64748b;
            font-size: 1.05rem;
            max-width: 760px;
            margin-bottom: 1.2rem;
        }
        .skill-chip {
            display: inline-block;
            padding: 0.3rem 0.65rem;
            margin: 0.2rem 0.25rem 0.2rem 0;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.12);
            color: #2563eb;
            font-size: 0.88rem;
            font-weight: 600;
        }
        [data-testid="stFileUploaderDropzone"] {
            border: 1.5px dashed #94a3b8;
            border-radius: 0.9rem;
        }
        [data-testid="stMetric"] {
            border: 1px solid rgba(148, 163, 184, 0.35);
            border-radius: 0.8rem;
            padding: 0.8rem 1rem;
            background: rgba(148, 163, 184, 0.06);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def _display(value):
    return value if value else "Not detected"


def _render_skill_chips(skills):
    if not skills:
        st.caption("No skills detected.")
        return

    chips = "".join(
        f'<span class="skill-chip">{html.escape(skill)}</span>'
        for skill in skills
    )
    st.markdown(chips, unsafe_allow_html=True)


def _render_overview(result):
    st.subheader(_display(result.get("name")))
    st.caption(result.get("file_name", "Resume"))

    email_column, phone_column, linkedin_column, github_column = st.columns(4)
    with email_column:
        st.markdown("**Email**")
        st.write(_display(result.get("email")))
    with phone_column:
        st.markdown("**Phone**")
        st.write(_display(result.get("phone")))
    with linkedin_column:
        st.markdown("**LinkedIn**")
        st.write(_display(result.get("linkedin")))
    with github_column:
        st.markdown("**GitHub**")
        st.write(_display(result.get("github")))

    st.divider()
    st.markdown("#### Detected skills")
    _render_skill_chips(result.get("skills", []))

    st.markdown("#### Certifications")
    certifications = result.get("certifications", [])
    if certifications:
        st.dataframe(
            [
                {"Certification": certification}
                for certification in certifications
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.caption("No certifications detected.")


def _render_experience(result):
    experience_records = result.get("work_experience", [])
    if not experience_records:
        st.info("No structured work experience was detected.")
        return

    for experience in experience_records:
        with st.container(border=True):
            st.markdown(
                f"#### {html.escape(_display(experience.get('job_title')))}"
            )
            company_column, dates_column, location_column = st.columns(3)
            with company_column:
                st.markdown("**Company**")
                st.write(_display(experience.get("company")))
            with dates_column:
                st.markdown("**Duration**")
                st.write(
                    f"{_display(experience.get('start_date'))} — "
                    f"{_display(experience.get('end_date'))}"
                )
            with location_column:
                st.markdown("**Location**")
                st.write(_display(experience.get("location")))

            responsibilities = experience.get("responsibilities", [])
            if responsibilities:
                st.markdown("**Responsibilities**")
                for responsibility in responsibilities:
                    st.write(f"• {responsibility}")
            else:
                st.caption("No responsibilities detected for this role.")


def _render_education_and_projects(result):
    education_column, projects_column = st.columns(2, gap="large")

    with education_column:
        st.markdown("### Education")
        education_records = result.get("education", [])
        if not education_records:
            st.info("No structured education was detected.")

        for education in education_records:
            with st.container(border=True):
                st.markdown(
                    f"#### {html.escape(_display(education.get('degree')))}"
                )
                st.write(_display(education.get("institution")))
                st.caption(
                    " · ".join(
                        value
                        for value in (
                            education.get("location"),
                            education.get("graduation_date"),
                            education.get("grade"),
                        )
                        if value
                    )
                    or "Additional details were not detected."
                )

    with projects_column:
        st.markdown("### Projects")
        projects = result.get("projects", [])
        if not projects:
            st.info("No structured projects were detected.")

        for project in projects:
            with st.container(border=True):
                st.markdown(
                    f"#### {html.escape(_display(project.get('name')))}"
                )
                if project.get("description"):
                    st.write(project["description"])
                if project.get("link"):
                    st.write(project["link"])
                project_dates = " — ".join(
                    value
                    for value in (
                        project.get("start_date"),
                        project.get("end_date"),
                    )
                    if value
                )
                if project_dates:
                    st.caption(project_dates)
                if project.get("technologies"):
                    _render_skill_chips(project["technologies"])


def _render_positions_of_responsibility(result):
    positions = result.get("positions_of_responsibility", [])
    if not positions:
        st.info("No positions of responsibility were detected.")
        return

    for position in positions:
        with st.container(border=True):
            st.markdown(f"#### {html.escape(_display(position.get('title')))}")
            organization_column, dates_column, location_column = st.columns(3)
            with organization_column:
                st.markdown("**Organization**")
                st.write(_display(position.get("organization")))
            with dates_column:
                st.markdown("**Duration**")
                st.write(
                    f"{_display(position.get('start_date'))} — "
                    f"{_display(position.get('end_date'))}"
                )
            with location_column:
                st.markdown("**Location**")
                st.write(_display(position.get("location")))

            responsibilities = position.get("responsibilities", [])
            if responsibilities:
                st.markdown("**Responsibilities**")
                for responsibility in responsibilities:
                    st.write(f"• {responsibility}")


def _entity_rows(result):
    rows = []
    entities = result.get("nlp_analysis", {}).get("entities", {})

    for group_name, group_entities in entities.items():
        for entity in group_entities:
            rows.append(
                {
                    "type": group_name,
                    "text": entity.get("text"),
                    "section": entity.get("section"),
                    "start": entity.get("start"),
                    "end": entity.get("end"),
                }
            )

    return rows


def _render_nlp_evidence(result):
    st.info(
        "This view shows why values were detected. Character offsets refer "
        "to positions in the extracted resume text."
    )

    nlp_analysis = result.get("nlp_analysis", {})
    skill_matches = nlp_analysis.get("skill_matches", [])
    entity_rows = _entity_rows(result)

    st.markdown("### Skill evidence")
    if skill_matches:
        st.dataframe(
            skill_matches,
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.caption("No skill evidence is available.")

    st.markdown("### Named entities")
    if entity_rows:
        st.dataframe(
            entity_rows,
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.caption("No named-entity evidence is available.")

    with st.expander("View complete JSON"):
        st.json(result)


def _download_file_name(source_name):
    source_stem = Path(source_name).stem
    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", source_stem).strip("_.")
    return f"{safe_stem or 'resume'}_parsed.json"


def _upload_signature(uploaded_files):
    digest = hashlib.sha256()
    digest.update(PARSER_CACHE_VERSION.encode("utf-8"))

    for uploaded_file in uploaded_files:
        digest.update(uploaded_file.name.encode("utf-8"))
        digest.update(uploaded_file.getvalue())

    return digest.hexdigest()


with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
        1. Extract text from PDF or DOCX.
        2. Detect sections and contact fields.
        3. Run spaCy NER and resume-specific rules.
        4. Normalize skills with PhraseMatcher.
        5. Build structured, downloadable JSON.
        """
    )
    st.divider()
    st.success("Local processing")
    st.caption(
        "Uploaded resume text is processed on this machine and is not sent "
        "to an external AI API."
    )

st.markdown('<span class="local-badge">LOCAL NLP · PRIVATE</span>', unsafe_allow_html=True)
st.title("NLP Resume Parser")
st.markdown(
    '<p class="hero-copy">Turn one or many PDF/DOCX resumes into '
    "structured, explainable data using spaCy, PhraseMatcher, and regex.</p>",
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "Upload one or more resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    help="You can select several files in the file picker.",
)

if not uploaded_files:
    for state_key in (
        "resume_upload_signature",
        "resume_results",
        "resume_failures",
    ):
        st.session_state.pop(state_key, None)

    st.info(
        "Upload at least one PDF or DOCX resume to extract structured data "
        "and download it as JSON."
    )
    st.stop()

upload_signature = _upload_signature(uploaded_files)

if st.session_state.get("resume_upload_signature") != upload_signature:
    results = []
    failures = []
    progress = st.progress(0, text="Preparing local NLP pipeline...")

    for index, uploaded_file in enumerate(uploaded_files, start=1):
        progress.progress(
            (index - 1) / len(uploaded_files),
            text=f"Analyzing {uploaded_file.name}...",
        )

        try:
            with temporary_upload(uploaded_file) as file_path:
                parsed_data = parse_resume_file(file_path)
        except ResumeParserError as error:
            failures.append((uploaded_file.name, str(error)))
        else:
            parsed_data["file_name"] = uploaded_file.name
            results.append(parsed_data)

    progress.progress(1.0, text="Analysis complete.")
    progress.empty()
    st.session_state["resume_upload_signature"] = upload_signature
    st.session_state["resume_results"] = results
    st.session_state["resume_failures"] = failures
else:
    results = st.session_state.get("resume_results", [])
    failures = st.session_state.get("resume_failures", [])

unique_skills = {
    skill.casefold(): skill
    for result in results
    for skill in result.get("skills", [])
}
metric_columns = st.columns(4)
metric_columns[0].metric("Uploaded", len(uploaded_files))
metric_columns[1].metric("Parsed", len(results))
metric_columns[2].metric("Failed", len(failures))
metric_columns[3].metric("Unique skills", len(unique_skills))

if failures:
    with st.expander(f"Review {len(failures)} parsing failure(s)", expanded=True):
        for file_name, error_message in failures:
            st.error(f"{file_name}: {error_message}")

if not results:
    st.error("None of the uploaded resumes could be parsed.")
    st.stop()

st.divider()
selected_index = st.selectbox(
    "Choose a parsed resume",
    options=range(len(results)),
    format_func=lambda result_index: (
        f"{_display(results[result_index].get('name'))} — "
        f"{results[result_index]['file_name']}"
    ),
)
selected_result = results[selected_index]

download_column, download_all_column = st.columns([1, 1])
with download_column:
    st.download_button(
        "Download selected JSON",
        data=json.dumps(selected_result, indent=2),
        file_name=_download_file_name(selected_result["file_name"]),
        mime="application/json",
        use_container_width=True,
    )
with download_all_column:
    st.download_button(
        "Download all JSON",
        data=json.dumps(results, indent=2),
        file_name="parsed_resumes.json",
        mime="application/json",
        use_container_width=True,
        disabled=len(results) == 1,
        help="Upload multiple resumes to enable the combined download.",
    )

summary_tab, resume_tab, nlp_tab = st.tabs(
    ["Summary", "Resume details", "NLP details"]
)

with summary_tab:
    _render_overview(selected_result)

with resume_tab:
    st.subheader("Work experience")
    _render_experience(selected_result)
    st.divider()
    _render_education_and_projects(selected_result)
    st.divider()
    st.subheader("Positions of responsibility")
    _render_positions_of_responsibility(selected_result)

with nlp_tab:
    _render_nlp_evidence(selected_result)
