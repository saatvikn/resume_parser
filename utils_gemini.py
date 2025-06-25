import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import textwrap

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Load API key from env variable
genai.configure(api_key=api_key)

# Create gemini model 
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

def extract_advanced_fields_with_gemini(resume_text):

    # for m in genai.list_models():
    #     print(m.name)

    # prompt = textwrap.dedent(f"""
    #     You are an expert resume parser. Your task is to extract the following fields in JSON format:
    #     "Skills", "Education", "Work Experience", and "Projects".

    #     Resume:
    #     === START ===
    #     {resume_text}
    #     === END ===
    # """)

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

        # Check if empty
        raw_output = response.text.strip()
        
        if not raw_output:
            raise ValueError("Gemini returned an empty response.")

        # Remove ```json wrapper if present
        if raw_output.startswith("```json"):
            raw_output = raw_output.replace("```json", "").replace("```", "").strip()

        return json.loads(raw_output)

    except Exception as e:
        print(f"⚠️ Failed to parse Gemini response: {e}")
        return {
            "error": "Gemini returned no content or invalid JSON.",
            "raw_response": raw_output if 'raw_output' in locals() else ""
        }