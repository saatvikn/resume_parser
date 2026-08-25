"""Helpers for safely handling uploaded resume files."""

from contextlib import contextmanager
import os
import tempfile

from src.exceptions import ResumeParserError, UnsupportedFileError


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


@contextmanager
def temporary_upload(uploaded_file):
    """Save an uploaded file temporarily and always remove it afterward."""
    extension = os.path.splitext(uploaded_file.name)[-1].lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileError("Only PDF and DOCX files are supported.")

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temporary_file:
            temporary_file.write(uploaded_file.getvalue())
            temporary_path = temporary_file.name

        yield temporary_path
    except ResumeParserError:
        raise
    except OSError as error:
        raise ResumeParserError(
            "The uploaded file could not be prepared for processing."
        ) from error
    finally:
        if temporary_path:
            try:
                os.remove(temporary_path)
            except FileNotFoundError:
                pass
