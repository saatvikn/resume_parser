"""Application-specific exceptions for resume processing."""


class ResumeParserError(Exception):
    """Base exception for expected resume parser failures."""


class UnsupportedFileError(ResumeParserError):
    """Raised when a file is not a supported resume format."""


class EmptyDocumentError(ResumeParserError):
    """Raised when no readable text can be extracted from a resume."""


class TextExtractionError(ResumeParserError):
    """Raised when a supported document cannot be read."""


class NLPProcessingError(ResumeParserError):
    """Raised when the local spaCy pipeline cannot process resume text."""
