# NLP Resume Parser

A local PDF/DOCX resume parser built with Python, spaCy, regex, and Streamlit. It extracts contact details, skills, education, work experience, projects, certifications, and positions of responsibility into structured JSON.

The project does not call Gemini or another generative-AI API. The Streamlit app and command-line interface both use the same parser in `src/parser.py`.

## Features

- Parse one or several PDF/DOCX resumes.
- Preserve multi-column PDF text with layout-aware extraction.
- Extract contact fields with regex and header rules.
- Detect general entities with spaCy NER.
- Detect degrees, job titles, and certifications with EntityRuler.
- Normalize skill aliases with PhraseMatcher and `data/skills.json`.
- Show source text, character offsets, and section evidence.
- Download individual or batch results as JSON.

## Processing Workflow

```text
PDF / DOCX
    |
    v
Text extraction and normalization
    |
    v
Section detection and record grouping
    |
    +--> Regex: contacts, URLs, grades, date ranges
    +--> spaCy NER: people, organizations, locations, dates
    +--> EntityRuler: degrees, job titles, certifications
    +--> PhraseMatcher: normalized skills
    |
    v
Section-aware structured extractors
    |
    v
Streamlit / CLI / JSON
```

1. `pdfplumber` extracts PDF text in visual reading order; `docx2txt` handles DOCX files.
2. Heading aliases identify education, experience, skills, projects, leadership, and certification sections.
3. Section content is grouped into records using job-title, date, institution, and bullet-layout signals.
4. The resume text is processed once by the cached spaCy pipeline.
5. Regex and NLP evidence are combined to build structured records.
6. Streamlit or the CLI presents the same parser output.

## How spaCy Is Used

spaCy is the NLP library; `en_core_web_sm` is the pretrained English model. Calling `nlp(text)` returns a `Doc` containing tokens, named entities, and character offsets.

### Pretrained NER

The English model supplies general entities:

| Label | Used for |
|---|---|
| `PERSON` | Candidate-name fallback |
| `ORG` | Companies and institutions |
| `GPE`, `LOC` | Cities and locations |
| `DATE` | Employment and education dates |

### EntityRuler

The general model has no resume-specific labels for degrees or job titles. `src/nlp/model.py` adds an EntityRuler after NER with patterns from `src/nlp/patterns.py`:

```text
Bachelor of Technology       -> DEGREE
Software Engineering Intern  -> JOB_TITLE
AWS Certified Developer      -> CERTIFICATION
```

### PhraseMatcher

`src/nlp/skills.py` builds a case-insensitive PhraseMatcher from `data/skills.json`. Aliases are returned as one canonical value:

```json
{
  "Python": ["python", "python3"],
  "Natural Language Processing": ["natural language processing", "nlp"]
}
```

A match keeps both the normalized name and its evidence:

```json
{
  "name": "Python",
  "text": "python3",
  "start": 412,
  "end": 419,
  "section": "skills"
}
```

The spaCy model and matchers are cached, so batch parsing does not reload them for every resume.

## Rules Added From Real Failures

The section parser was adjusted after reviewing four resume layouts:

- `ACADEMIC DETAILS` is treated as education.
- `SUMMER INTERNSHIP / WORK EXPERIENCE` is treated as experience.
- Uppercase table headers such as `COURSE | INSTITUTE | SCORE` do not end the active section.
- A `•` bullet is not automatically a new record because some resumes use the same bullet for project headers and responsibility lines.
- Experience records use known job-title headers; project and leadership records use date or compact header signals.

These are deterministic layout heuristics, not claims that every resume format is supported.

## Project Structure

```text
app.py                     Streamlit batch/single-resume interface
resume_cli.py              Command-line interface
data/skills.json           Canonical skill names and aliases
src/parser.py              Shared parser orchestration
src/extractors/            Text, contact, and section extraction
src/nlp/model.py           Cached spaCy model and EntityRuler
src/nlp/entities.py        Entity filtering and section evidence
src/nlp/skills.py          PhraseMatcher skill extraction
src/nlp/patterns.py        Resume phrases and regex patterns
src/nlp/structured/        Structured record builders
```

## Installation

Python 3.12 is recommended.

```powershell
git clone https://github.com/saatvikn/resume_parser.git
cd resume_parser

py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
python -m pip check
```

No API key or `.env` file is required.

## Usage

Run the Streamlit app:

```powershell
python -m streamlit run app.py
```

The interface has three views: summary, structured resume details, and NLP evidence.

Run the CLI:

```powershell
python resume_cli.py path\to\resume.pdf
```

The CLI prints the parsed result and saves `output/parsed_resume.json`.

## Output

```json
{
  "name": "Candidate Name",
  "email": "candidate@example.com",
  "phone": "+91 12345 67890",
  "linkedin": "https://linkedin.com/in/candidate",
  "github": "https://github.com/candidate",
  "skills": ["Python", "spaCy", "SQL"],
  "education": [],
  "work_experience": [],
  "projects": [],
  "positions_of_responsibility": [],
  "certifications": [],
  "nlp_analysis": {
    "entities": {},
    "skill_matches": []
  }
}
```

`nlp_analysis` exposes the evidence used by the parser instead of hiding the extraction process.

## Current Status

The parser runs locally on the four development resumes and the main structural counts have been manually reviewed. This is a smoke check, not an accuracy benchmark.

The next step is to annotate a privacy-safe evaluation set and measure precision, recall, F1, and parsing latency by field. Accuracy numbers should not be added to a resume until that evaluation exists.

## Limitations

- `en_core_web_sm` is a general English model and can misclassify resume-specific text.
- Rule coverage depends on the headings, phrases, and skill aliases currently configured.
- Unusual PDF layouts can still produce incorrect reading order or record grouping.
- Scanned/image-only PDFs require OCR, which is not implemented.
- Batch files are processed sequentially.
- Automatic hiring decisions and protected-attribute scoring are outside the project scope.

## Privacy

Resume text is processed locally and is not sent to an external API. Use synthetic or redacted resumes for demonstrations, obtain permission before processing someone else's resume, and do not commit resume files or generated output.

## Troubleshooting

If PowerShell blocks environment activation, call the environment's interpreter directly:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

If a PDF produces no text, it is probably scanned and must be converted with OCR before upload.
