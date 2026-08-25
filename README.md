# Resume Parser with Gemini and Streamlit

A Python application that extracts structured information from PDF and DOCX resumes. It provides Streamlit interfaces for parsing one resume or processing multiple resumes in a batch, and it can export the results as JSON.

The web applications currently use Google's Gemini API for structured extraction. The repository also contains a rule-based parser that uses regular expressions and resume-section detection.

## Features

- Upload PDF and DOCX resumes.
- Parse one resume through a Streamlit interface.
- Parse multiple resumes through a batch interface.
- Extract:
  - Name
  - Email address
  - Phone number
  - LinkedIn profile
  - Skills
  - Education
  - Work experience
  - Projects
  - Certifications
- Review extracted information in the browser.
- Download individual or combined results as JSON.
- Run the rule-based parser from the command line.

## Technology Stack

- Python 3.12
- Streamlit
- Google Gemini (`gemini-3.6-flash`)
- PDFMiner
- docx2txt
- pandas
- spaCy (installed for the planned NLP pipeline; it is not yet used for production extraction)

## Project Structure

```text
.
|-- app.py              # Single-resume Streamlit application
|-- batch_app.py        # Multiple-resume Streamlit application
|-- resume_parser.py    # Rule-based command-line parser
|-- src/
|   |-- extractors/     # Text, contact, section, and skill extraction
|   |-- services/       # External service integrations
|   `-- utils/          # Shared file utilities
|-- requirements.txt    # Python dependencies
|-- .env.example        # Example API-key configuration
`-- README.md
```

## Prerequisites

Before installing the project, make sure you have:

- Python 3.12 installed.
- A Gemini API key.
- PowerShell or another command-line shell.

Create a Gemini API key through [Google AI Studio](https://aistudio.google.com/app/apikey).

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/saatvikn/resume_parser.git
cd resume_parser
```

### 2. Create a virtual environment

```powershell
py -3.12 -m venv venv
```

### 3. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

The terminal prompt should now start with `(venv)`.

Activation is optional if you call the virtual environment's Python executable directly.

### 4. Upgrade the package-installation tools

```powershell
python -m pip install --upgrade pip setuptools wheel
```

### 5. Install the project dependencies

```powershell
python -m pip install -r requirements.txt
```

### 6. Configure the Gemini API key

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your key:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Do not commit `.env`. It is excluded by `.gitignore`.

### 7. Verify the installation

```powershell
python -m pip check
```

The expected result is:

```text
No broken requirements found.
```

## Usage

### Parse one resume

Start the main application:

```powershell
streamlit run app.py
```

Then:

1. Open the local URL shown by Streamlit.
2. Upload a PDF or DOCX resume.
3. Wait for Gemini to process the extracted text.
4. Review the JSON result.
5. Select **Download JSON** to save the result.

### Parse multiple resumes

Stop the current Streamlit server with `Ctrl+C`, then run:

```powershell
streamlit run batch_app.py
```

Upload multiple PDF or DOCX files. The application displays each candidate separately and provides a combined JSON download.

### Run the rule-based command-line parser

```powershell
python resume_parser.py path\to\resume.pdf
```

This command does not use Gemini. It uses the regular expressions and section extractors in `src/extractors`, prints the extracted data, and saves it to:

```text
output/parsed_resume.json
```

## Example Output

```json
{
  "name": "Candidate Name",
  "email": "candidate@example.com",
  "phone": "+91-1234567890",
  "linkedin": "https://linkedin.com/in/candidate",
  "skills": ["Python", "SQL", "Machine Learning"],
  "education": [],
  "work_experience": [],
  "projects": [],
  "certifications": []
}
```

Actual nested fields depend on the information found in the resume.

## Privacy

The Streamlit applications extract resume text and send it to the configured Gemini API. Resumes normally contain personal information, so:

- Use synthetic or redacted resumes while developing and demonstrating the application.
- Obtain permission before processing another person's resume.
- Do not commit resumes, extracted output, or API keys.
- Review Google's Gemini API data-handling terms before using real candidate information.

The `resumes/`, `output/`, `.env`, `venv/`, and `plan.md` paths are ignored by Git.

## Current Limitations

- spaCy is installed, but the current extraction path does not perform spaCy NER yet.
- Gemini is currently the main extraction engine for both Streamlit applications.
- The batch parser processes files sequentially.
- Scanned or image-only PDFs are not supported because OCR is not implemented.
- Resume layouts and model responses can affect extraction accuracy.
- The project does not currently include automated tests or an evaluation dataset.
- Temporary upload-file cleanup and stronger UI error handling are planned improvements.

## Troubleshooting

### PowerShell blocks virtual-environment activation

You can run the application without activating the environment:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

### `GEMINI_API_KEY` is missing

Confirm that `.env` exists in the project root and contains:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Restart Streamlit after changing `.env`.

### A virtual-environment file is locked

Stop Streamlit and close editors that are using the environment before deleting or recreating `venv/`. Python editor extensions may keep `venv\Scripts\python.exe` open.

### PDF parsing returns empty text

The PDF may contain scanned images instead of embedded text. OCR support has not yet been added.

## Planned Development

The next development stages are:

1. Refactor parsing logic out of the Streamlit files and add automated tests.
2. Migrate to the current Google GenAI SDK with Pydantic structured output.
3. Implement a genuine spaCy NLP pipeline with NER, PhraseMatcher, section context, evidence, and evaluation metrics.
4. Add explainable resume-to-job matching with skill normalization and TF-IDF similarity.

## Responsible Use

This project is intended for document parsing, experimentation, and decision support. It should not make automatic hiring decisions. Candidate matching must exclude protected personal attributes and should always be reviewed by a person.
