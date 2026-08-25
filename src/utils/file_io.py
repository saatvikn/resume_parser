import json
import os


def save_to_json(data, output_path="output/parsed_resume.json"):
    """Save parsed resume data as formatted JSON."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as output_file:
        json.dump(data, output_file, indent=4)
