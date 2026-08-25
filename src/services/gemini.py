import json
import os
import textwrap

import google.generativeai as genai
from dotenv import load_dotenv

from src.exceptions import GeminiExtractionError


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(model_name="gemini-3.6-flash")


def extract_advanced_fields_with_gemini(resume_text):
    """Use Gemini to extract structured fields from resume text."""
    if not api_key:
        raise GeminiExtractionError(
            "GEMINI_API_KEY is not configured in the .env file."
        )

    prompt = textwrap.dedent(f"""
        You are an expert resume parser. Your task is to extract structured data from the resume text.

        Return the following fields in a single, valid JSON object:
        - name
        - email
        - phone
        - linkedin
        - skills (as a list)
        - education (list of objects)
        - work_experience (list of objects)
        - projects (list of objects)
        - certifications (list of strings)

        JSON Schema:
        {{
          "name": "Full Name",
          "email": "email@example.com",
          "phone": "+91-1234567890",
          "linkedin": "https://linkedin.com/in/username",
          "skills": ["Python", "SQL", "Machine Learning"],
          "education": [
            {{
              "institution": "University Name",
              "degree": "Degree Title",
              "Grade": null,
              "graduation_date": "Month Year",
              "location": "City, State"
            }}
          ],
          "work_experience": [
            {{
              "company": "Company Name",
              "job_title": "Your Title",
              "start_date": "Month Year",
              "end_date": "Month Year or 'Present'",
              "location": "City, State",
              "responsibilities": [
                "Responsibility 1",
                "Responsibility 2"
              ]
            }}
          ],
          "projects": [
            {{
              "name": "Project Name",
              "description": "What the project does",
              "technologies": ["Tech 1", "Tech 2"],
              "link": "URL or null"
            }}
          ],
          "certifications": ["Certificate 1", "Certificate 2"]
        }}

        Rules:
        1. If any field is not found, return `null` (for strings) or `[]` (for lists).
        2. The output must be valid JSON only — no markdown, no explanation.
        3. Wrap up everything inside a single JSON object only.

        Resume:
        === START ===
        {resume_text}
        === END ===
    """)

    print("Prompt length:", len(prompt))

    try:
        response = model.generate_content(prompt)
        raw_output = response.text.strip()

        if not raw_output:
            raise ValueError("Gemini returned an empty response.")

        if raw_output.startswith("```json"):
            raw_output = raw_output.replace("```json", "").replace("```", "").strip()

        return json.loads(raw_output)

    except Exception as error:
        raise GeminiExtractionError(
            "Gemini could not return valid structured resume data."
        ) from error
