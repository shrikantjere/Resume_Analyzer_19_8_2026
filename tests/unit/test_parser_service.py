"""Unit tests for the parser service."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from services.parser_service import ParserService
from core.exceptions import UnsupportedFileTypeError, FileTooLargeError, TextExtractionError


class TestParserService:
    """Test suite for the ParserService."""

    @pytest.fixture
    def parser(self) -> ParserService:
        return ParserService()

    def test_extract_text_from_raw(self, parser: ParserService) -> None:
        """Test extracting text from raw pasted input."""
        text = "  Hello  World  \n\n  "
        result = parser.extract_text_from_raw(text)
        assert result == "Hello  World"

    def test_extract_text_from_raw_empty(self, parser: ParserService) -> None:
        """Test that empty text raises error."""
        with pytest.raises(TextExtractionError):
            parser.extract_text_from_raw("   \n   ")

    def test_extract_text_from_txt(self, parser: ParserService, temp_resume_file: Path) -> None:
        """Test extracting text from a .txt file."""
        text = parser.extract_text(str(temp_resume_file), file_type="txt")
        assert "John Doe" in text
        assert "Python" in text

    def test_unsupported_file_type(self, parser: ParserService) -> None:
        """Test that unsupported file types raise an error."""
        with pytest.raises(UnsupportedFileTypeError):
            parser.extract_text("resume.png", file_type="png")

    def test_file_too_large(self, parser: ParserService, tmp_path: Path) -> None:
        """Test that oversized files raise an error."""
        large_file = tmp_path / "large.txt"
        # Create a file larger than the max (10 MB)
        large_file.write_text("x" * (11 * 1024 * 1024))

        with pytest.raises(FileTooLargeError):
            parser.extract_text(str(large_file), file_type="txt")