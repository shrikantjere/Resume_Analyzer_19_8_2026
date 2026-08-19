"""
Shared utility functions for the AI Resume Analyzer.

Provides file type detection, text sanitization, UUID generation,
similarity computation, and other common helpers.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Optional


def generate_id() -> str:
    """Generate a unique identifier using UUID v4.

    Returns:
        str: A UUID v4 string.
    """
    return str(uuid.uuid4())


def detect_file_type(file_path: str) -> str:
    """Detect file type by extension.

    Args:
        file_path: Path to the file.

    Returns:
        str: File extension in lowercase (e.g., 'pdf', 'docx', 'txt').
    """
    return Path(file_path).suffix.lower().lstrip(".")


def detect_file_type_by_magic(file_path: str) -> str:
    """Detect file type by magic bytes (MIME type).

    Uses python-magic to identify the actual file type regardless
    of extension. Falls back to extension-based detection.

    Args:
        file_path: Path to the file.

    Returns:
        str: Detected file type ('pdf', 'docx', 'txt', or 'unknown').
    """
    try:
        import magic

        mime = magic.from_file(file_path, mime=True)

        mime_map = {
            "application/pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "text/plain": "txt",
            "application/msword": "doc",  # Legacy .doc
        }

        return mime_map.get(mime, "unknown")
    except ImportError:
        # Fallback to extension detection
        return detect_file_type(file_path)


def is_supported_file_type(file_type: str) -> bool:
    """Check if the file type is supported.

    Args:
        file_type: File type string (e.g., 'pdf', 'docx').

    Returns:
        bool: True if the file type is supported.
    """
    return file_type.lower() in {"pdf", "docx", "txt", "doc"}


def sanitize_text(text: str) -> str:
    """Sanitize extracted text by removing control characters
    and normalizing whitespace.

    Args:
        text: Raw text to sanitize.

    Returns:
        str: Sanitized, normalized text.
    """
    if not text:
        return ""

    # Remove null bytes and control characters (except newlines and tabs)
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse multiple blank lines into at most one
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def truncate_text(text: str, max_chars: int = 10000) -> str:
    """Truncate text to a maximum number of characters.

    Args:
        text: Text to truncate.
        max_chars: Maximum number of characters.

    Returns:
        str: Truncated text, with a note if truncated.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... text truncated for analysis ...]"


def extract_emails(text: str) -> list[str]:
    """Extract email addresses from text.

    Args:
        text: Text to search.

    Returns:
        list[str]: List of found email addresses.
    """
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.findall(pattern, text)


def extract_phones(text: str) -> list[str]:
    """Extract phone numbers from text.

    Args:
        text: Text to search.

    Returns:
        list[str]: List of found phone numbers.
    """
    # Common phone number patterns
    patterns = [
        r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    ]
    results: list[str] = []
    for pattern in patterns:
        results.extend(re.findall(pattern, text))
    return results


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes.

    Returns:
        str: Formatted size string (e.g., '2.5 MB').
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Compute Jaccard similarity between two sets.

    J(A, B) = |A ∩ B| / |A ∪ B|

    Args:
        set_a: First set of items.
        set_b: Second set of items.

    Returns:
        float: Similarity score between 0.0 and 1.0.
    """
    if not set_a or not set_b:
        return 0.0

    intersection = set_a & set_b
    union = set_a | set_b

    if not union:
        return 0.0

    return len(intersection) / len(union)


def normalize_skill_name(skill: str) -> str:
    """Normalize a skill name for consistent comparison.

    Args:
        skill: Raw skill name.

    Returns:
        str: Normalized, lowercase, stripped skill name.
    """
    return skill.lower().strip().replace("-", " ").replace("/", " ")


def parse_experience_years(text: str) -> Optional[float]:
    """Extract years of experience from text.

    Attempts to parse various formats like "5 years", "3+ years",
    "2-4 years", etc.

    Args:
        text: Text containing experience information.

    Returns:
        Optional[float]: Extracted years, or None if not found.
    """
    patterns = [
        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience",
        r"experience\s*(?:of)?\s*(\d+)\+?\s*(?:years?|yrs?)",
        r"(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if match.lastindex == 2:  # Range like "2-4 years"
                return (float(match.group(1)) + float(match.group(2))) / 2
            return float(match.group(1))

    return None