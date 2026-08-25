# NLP Resume Parser with spaCy and Streamlit

A local Python application that extracts structured information from PDF and DOCX resumes. It provides one unified Streamlit interface for parsing one or many resumes, a command-line interface, and downloadable JSON output.

The parser uses a deterministic NLP pipeline: regular expressions for contact details and dates, spaCy named-entity recognition, an EntityRuler for resume-specific entities, a PhraseMatcher with a normalized skills taxonomy, and section-aware rules for education, experience, projects, and certifications. Resume contents are not sent to an external AI service.

## Features

- Upload PDF and DOCX resumes.
- Parse one resume or multiple resumes from the same interface.
- Extract email, phone, LinkedIn, and GitHub information with regular expressions.
- Preserve multi-column PDF reading order with layout-aware extraction.
- Detect people, organizations, locations, and dates with spaCy NER.
- Detect resume-specific degrees, job titles, and certifications with spaCy EntityRuler patterns.
- Normalize skills and aliases with spaCy PhraseMatcher and `data/skills.json`.
- Build structured education, work-experience, project, leadership, and certification records.
- Attach character offsets and resume-section context to NLP evidence.
- Review results in Streamlit and download them as JSON.
- Run the same parsing pipeline from the command line.

## Technology Stack

- Python 3.12
- spaCy with `en_core_web_sm`
- Streamlit
- pdfplumber with PDFMiner
- docx2txt
- pandas
- Python regular expressions

## Project Structure

```text
.
|-- app.py                 # Unified one-or-many resume Streamlit application
|-- resume_cli.py          # Command-line application
|-- data/
|   `-- skills.json        # Canonical skills and aliases
|-- src/
|   |-- extractors/        # Text, contact, section, and skill extraction
|   |-- nlp/
|   |   |-- structured/    # Education, experience, project, certification extraction
|   |   |-- entities.py    # Named-entity normalization
|   |   |-- model.py       # Cached spaCy model and EntityRuler
|   |   |-- patterns.py    # Resume phrases and regular expressions
|   |   |-- pipeline.py    # NLP orchestration
|   |   `-- skills.py      # PhraseMatcher skill extraction
|   |-- utils/             # File and upload utilities
|   |-- exceptions.py      # Application-specific exceptions
|   `-- parser.py          # Shared local parsing workflow
|-- requirements.txt       # Direct Python dependencies
`-- README.md
```

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/saatvikn/resume_parser.git
cd resume_parser
```

### 2. Create and activate a virtual environment

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

The terminal prompt should now start with `(venv)`. If PowerShell blocks activation, you can use `.\venv\Scripts\python.exe` in place of `python` in the commands below.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip check
```

No API key or `.env` file is required.

## Usage

### Run the Streamlit application

```powershell
streamlit run app.py
```

Open the local URL shown by Streamlit and upload one or more PDF/DOCX resumes. The application provides processing progress, summary metrics, structured result tabs, NLP evidence, individual JSON downloads, and a combined download when several resumes are uploaded.

### Use the command line

```powershell
python resume_cli.py path\to\resume.pdf
```

The result is printed and saved to `output/parsed_resume.json`.

## Output Shape

```json
{
  "name": "Candidate Name",
  "email": "candidate@example.com",
  "phone": "+91 12345 67890",
  "linkedin": "https://linkedin.com/in/candidate",
  "github": "https://github.com/candidate",
  "skills": ["Python", "spaCy", "SQL"],
  "education": [
    {
      "institution": "Example University",
      "degree": "Bachelor of Technology",
      "grade": "CGPA: 8.5/10",
      "graduation_date": "2025",
      "location": "Bengaluru"
    }
  ],
  "work_experience": [
    {
      "company": "Example Company",
      "job_title": "Software Engineering Intern",
      "start_date": "Jan 2024",
      "end_date": "Jun 2024",
      "location": "Bengaluru",
      "responsibilities": ["Built a Python data-processing pipeline."]
    }
  ],
  "projects": [],
  "positions_of_responsibility": [],
  "certifications": [],
  "nlp_analysis": {
    "entities": {},
    "skill_matches": []
  }
}
```

`nlp_analysis` preserves the evidence used by the parser, including the original matched text, normalized skill names, character offsets, and section labels.

## How the Pipeline Works

1. pdfplumber preserves PDF line and column order; docx2txt handles DOCX files.
2. Section detection recognizes both extracted and boundary-only headings.
3. Top-level bullets start records and nested bullets remain attached as evidence.
4. Regular expressions extract contact fields, URLs, dates, ranges, and grades.
5. spaCy NER, EntityRuler, and PhraseMatcher produce contextual entities and normalized skills.
6. Section-aware extractors build consistent education, experience, project, leadership, and certification objects.

## Privacy and Responsible Use

Processing is local and no resume text is sent to an external AI API. Resumes still contain personal information, so use synthetic or redacted documents for demonstrations, obtain permission before processing someone else's resume, and do not commit resumes or generated output.

This project is intended for document parsing and decision support. It should not make automatic hiring decisions or rank candidates using protected personal attributes. Results should be reviewed by a person.

## Current Limitations

- `en_core_web_sm` is a general English model, so it can miss or misclassify resume-specific entities.
- Entity coverage depends on the phrases in `src/nlp/patterns.py` and aliases in `data/skills.json`.
- Section extraction depends on recognizable headings and reasonably ordered text.
- Highly graphical or unusually positioned PDF elements may still need layout-specific handling.
- Scanned or image-only PDFs are unsupported because OCR is not implemented.
- Multiple uploaded files are processed sequentially.
- The project does not yet include an annotated evaluation dataset or automated tests.

## Troubleshooting

### PowerShell blocks virtual-environment activation

Run Streamlit through the environment's Python executable:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

### The spaCy model is missing

Install all project dependencies again:

```powershell
python -m pip install -r requirements.txt
```

### A virtual-environment file is locked

Stop Streamlit with `Ctrl+C` and close editors or terminals using the environment before deleting or recreating `venv`.

### PDF parsing returns no text

The PDF may contain scanned images instead of embedded text. Convert it with OCR before uploading it.

## Suggested Next Steps

1. Create a small annotated evaluation set and report precision, recall, and F1 for each extracted field.
2. Expand job-title, degree, certification, and skill patterns from evaluation errors.
3. Add explainable resume-to-job matching with normalized skill overlap and TF-IDF similarity.
