"""Gemini integration for structured resume extraction."""

from functools import lru_cache
import json
import os
import textwrap

from dotenv import load_dotenv
from google import genai

from src.exceptions import GeminiExtractionError


MODEL_NAME = "gemini-3.6-flash"

NULLABLE_STRING = {"type": ["string", "null"]}

RESUME_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": NULLABLE_STRING,
        "email": NULLABLE_STRING,
        "phone": NULLABLE_STRING,
        "linkedin": NULLABLE_STRING,
        "skills": {
            "type": "array",
            "items": {"type": "string"},
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "institution": NULLABLE_STRING,
                    "degree": NULLABLE_STRING,
                    "grade": NULLABLE_STRING,
                    "graduation_date": NULLABLE_STRING,
                    "location": NULLABLE_STRING,
                },
                "required": [
                    "institution",
                    "degree",
                    "grade",
                    "graduation_date",
                    "location",
                ],
                "additionalProperties": False,
            },
        },
        "work_experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": NULLABLE_STRING,
                    "job_title": NULLABLE_STRING,
                    "start_date": NULLABLE_STRING,
                    "end_date": NULLABLE_STRING,
                    "location": NULLABLE_STRING,
                    "responsibilities": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": [
                    "company",
                    "job_title",
                    "start_date",
                    "end_date",
                    "location",
                    "responsibilities",
                ],
                "additionalProperties": False,
            },
        },
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": NULLABLE_STRING,
                    "description": NULLABLE_STRING,
                    "technologies": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "link": NULLABLE_STRING,
                },
                "required": [
                    "name",
                    "description",
                    "technologies",
                    "link",
                ],
                "additionalProperties": False,
            },
        },
        "certifications": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "name",
        "email",
        "phone",
        "linkedin",
        "skills",
        "education",
        "work_experience",
        "projects",
        "certifications",
    ],
    "additionalProperties": False,
}


load_dotenv()


@lru_cache(maxsize=1)
def get_client():
    """Create and reuse the configured Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise GeminiExtractionError(
            "GEMINI_API_KEY is not configured in the .env file."
        )

    return genai.Client(api_key=api_key)


def extract_advanced_fields_with_gemini(resume_text):
    """Use Gemini to extract a schema-constrained resume dictionary."""
    prompt = textwrap.dedent(f"""
        Extract structured information from the resume text below.

        Rules:
        1. Do not invent information that is not present in the resume.
        2. Use null for missing scalar values.
        3. Use an empty list for missing collection values.
        4. Preserve the meaning of the source text while normalizing whitespace.

        Resume:
        === START ===
        {resume_text}
        === END ===
    """)

    try:
        response = get_client().models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": RESUME_RESPONSE_SCHEMA,
                "automatic_function_calling": {"disable": True},
            },
        )

        if isinstance(response.parsed, dict):
            return response.parsed

        raw_output = (response.text or "").strip()
        if not raw_output:
            raise ValueError("Gemini returned an empty response.")

        return json.loads(raw_output)
    except GeminiExtractionError:
        raise
    except Exception as error:
        raise GeminiExtractionError(
            "Gemini could not return valid structured resume data."
        ) from error
