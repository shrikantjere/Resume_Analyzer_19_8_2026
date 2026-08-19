"""Unit tests for utility functions."""

import pytest
from core.utils import (
    generate_id,
    detect_file_type,
    is_supported_file_type,
    sanitize_text,
    truncate_text,
    jaccard_similarity,
    normalize_skill_name,
    format_file_size,
    extract_emails,
    extract_phones,
)


class TestUtils:
    """Test suite for core utility functions."""

    def test_generate_id(self) -> None:
        id1 = generate_id()
        id2 = generate_id()
        assert len(id1) == 36  # UUID v4
        assert id1 != id2

    def test_detect_file_type(self) -> None:
        assert detect_file_type("resume.pdf") == "pdf"
        assert detect_file_type("resume.docx") == "docx"
        assert detect_file_type("resume.txt") == "txt"
        assert detect_file_type("resume.PDF") == "pdf"

    def test_is_supported_file_type(self) -> None:
        assert is_supported_file_type("pdf") is True
        assert is_supported_file_type("docx") is True
        assert is_supported_file_type("txt") is True
        assert is_supported_file_type("png") is False
        assert is_supported_file_type("jpg") is False

    def test_sanitize_text(self) -> None:
        assert sanitize_text("  Hello  ") == "Hello"
        assert sanitize_text("") == ""
        assert sanitize_text(None) == ""
        assert sanitize_text("Line1\n\n\nLine2") == "Line1\n\nLine2"

    def test_truncate_text(self) -> None:
        text = "A" * 100
        assert len(truncate_text(text, 50)) < 100
        assert len(truncate_text(text, 200)) == 100

    def test_jaccard_similarity(self) -> None:
        set_a = {"python", "sql", "docker"}
        set_b = {"python", "sql", "aws"}
        sim = jaccard_similarity(set_a, set_b)
        assert 0.0 < sim < 1.0
        assert sim == 2 / 4  # 2 common / 4 unique

    def test_jaccard_empty_sets(self) -> None:
        assert jaccard_similarity(set(), {"a"}) == 0.0
        assert jaccard_similarity(set(), set()) == 0.0

    def test_normalize_skill_name(self) -> None:
        assert normalize_skill_name("Python") == "python"
        assert normalize_skill_name("Machine Learning") == "machine learning"
        assert normalize_skill_name("C++") == "c++"

    def test_format_file_size(self) -> None:
        assert format_file_size(500) == "500 B"
        assert format_file_size(2048) == "2.0 KB"
        assert format_file_size(1048576) == "1.0 MB"
        assert format_file_size(1073741824) == "1.0 GB"

    def test_extract_emails(self) -> None:
        text = "Contact: john@email.com or support@test.co.uk"
        emails = extract_emails(text)
        assert len(emails) == 2
        assert "john@email.com" in emails

    def test_extract_emails_no_match(self) -> None:
        assert extract_emails("No email here") == []

    def test_extract_phones(self) -> None:
        text = "Phone: (555) 123-4567 or 555-123-4568"
        phones = extract_phones(text)
        assert len(phones) >= 1