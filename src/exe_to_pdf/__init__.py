"""Safe extraction of PDF documents embedded in EXE wrappers."""

from .core import ExtractionError, ExtractionResult, extract_pdf

__all__ = ["ExtractionError", "ExtractionResult", "extract_pdf"]
