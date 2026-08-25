"""Command-line interface for the rule-based resume parser."""

import json
import sys

from src.exceptions import ResumeParserError
from src.parser import parse_resume_file
from src.utils.file_io import save_to_json


def main():
    """Parse one resume from the command line and save the result as JSON."""
    if len(sys.argv) != 2:
        print(
            "Usage: python resume_cli.py <resume.pdf|resume.docx>",
            file=sys.stderr,
        )
        return 1

    try:
        parsed_data = parse_resume_file(sys.argv[1], use_gemini=False)
        save_to_json(parsed_data, output_path="output/parsed_resume.json")
    except ResumeParserError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print("\n=== Parsed Data ===")
    print(json.dumps(parsed_data, indent=4))
    print("\n✅ Data saved to output/parsed_resume.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
