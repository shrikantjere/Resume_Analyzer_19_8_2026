"""
Resume parsing service.

Extracts text from uploaded resume files (PDF, DOCX, TXT).
Uses a strategy pattern to select the appropriate parser
based on file type.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.config import get_settings
from core.exceptions import (
    FileCorruptedError,
    FileTooLargeError,
    TextExtractionError,
    UnsupportedFileTypeError,
)
from core.logging_config import get_logger
from core.utils import (
    detect_file_type_by_magic,
    is_supported_file_type,
    sanitize_text,
)

logger = get_logger(__name__)


class ParserService:
    """Service for extracting text from resume files.

    Supports PDF, DOCX, and plain text formats. Uses
    strategy-based resolution to select the appropriate parser.
    """

    def __init__(self) -> None:
        """Initialize the parser service with configuration."""
        self.settings = get_settings()

    def extract_text(
        self,
        file_path: str,
        file_type: Optional[str] = None,
    ) -> str:
        """Extract text from a resume file.

        Args:
            file_path: Path to the resume file.
            file_type: Optional file type override. Auto-detected if None.

        Returns:
            str: Extracted and sanitized text from the file.

        Raises:
            UnsupportedFileTypeError: If the file type is not supported.
            FileTooLargeError: If the file exceeds the size limit.
            FileCorruptedError: If the file cannot be read.
            TextExtractionError: If text cannot be extracted.
        """
        path = Path(file_path)

        # Detect file type
        if file_type is None:
            file_type = detect_file_type_by_magic(file_path)

        if not is_supported_file_type(file_type):
            raise UnsupportedFileTypeError(
                file_type=file_type,
            )

        # Check file size
        file_size = path.stat().st_size
        max_size = self.settings.max_file_size_bytes
        if file_size > max_size:
            file_size_mb = file_size / (1024 * 1024)
            raise FileTooLargeError(
                file_size_mb=file_size_mb,
                max_size_mb=self.settings.max_file_size_mb,
            )

        # Dispatch to appropriate parser
        parser_map = {
            "pdf": self._extract_pdf,
            "docx": self._extract_docx,
            "doc": self._extract_docx,
            "txt": self._extract_text,
        }

        parser = parser_map.get(file_type)
        if parser is None:
            raise UnsupportedFileTypeError(file_type=file_type)

        logger.info(
            "Extracting text from %s file: %s",
            file_type,
            path.name,
        )

        try:
            text = parser(file_path)
            sanitized = sanitize_text(text)

            if not sanitized:
                raise TextExtractionError(filename=path.name)

            logger.info(
                "Text extracted successfully: %d characters",
                len(sanitized),
            )
            return sanitized

        except FileCorruptedError:
            raise
        except TextExtractionError:
            raise
        except Exception as e:
            raise FileCorruptedError(
                filename=path.name,
                detail=str(e),
            ) from e

    def extract_text_from_raw(self, text: str) -> str:
        """Sanitize and validate raw pasted text.

        Args:
            text: Raw text input from the user.

        Returns:
            str: Sanitized text.

        Raises:
            TextExtractionError: If the text is empty after sanitization.
        """
        sanitized = sanitize_text(text)
        if not sanitized:
            raise TextExtractionError(filename="pasted_text")
        return sanitized

    # ── Parser Strategies ──────────────────────────────────────────────

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file using pdfplumber.

        Args:
            file_path: Path to the PDF file.

        Returns:
            str: Extracted text.

        Raises:
            FileCorruptedError: If the PDF cannot be parsed.
        """
        try:
            import pdfplumber
        except ImportError:
            raise FileCorruptedError(
                filename=Path(file_path).name,
                detail="PDF support not installed (pdfplumber required).",
            )

        try:
            text_parts: list[str] = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return "\n\n".join(text_parts)
        except Exception as e:
            raise FileCorruptedError(
                filename=Path(file_path).name,
                detail=f"PDF parsing error: {e}",
            ) from e

    def _extract_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file using python-docx.

        Args:
            file_path: Path to the DOCX file.

        Returns:
            str: Extracted text.

        Raises:
            FileCorruptedError: If the DOCX cannot be parsed.
        """
        try:
            import docx
        except ImportError:
            raise FileCorruptedError(
                filename=Path(file_path).name,
                detail="DOCX support not installed (python-docx required).",
            )

        try:
            doc = docx.Document(file_path)
            text_parts: list[str] = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            return "\n".join(text_parts)
        except Exception as e:
            raise FileCorruptedError(
                filename=Path(file_path).name,
                detail=f"DOCX parsing error: {e}",
            ) from e

    def _extract_text(self, file_path: str) -> str:
        """Read text from a plain text file.

        Args:
            file_path: Path to the TXT file.

        Returns:
            str: File contents.

        Raises:
            FileCorruptedError: If the file cannot be read.
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            raise FileCorruptedError(
                filename=Path(file_path).name,
                detail=f"Text file read error: {e}",
            ) from e