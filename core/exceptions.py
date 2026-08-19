"""
Custom exception hierarchy for the AI Resume Analyzer.

All exceptions inherit from ResumeAnalyzerError, providing a
consistent error handling interface across the application.
"""

from __future__ import annotations

from typing import Optional


class ResumeAnalyzerError(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        correlation_id: Optional[str] = None,
    ) -> None:
        """Initialize the base exception.

        Args:
            message: Human-readable error description.
            correlation_id: Optional trace ID for request correlation.
        """
        self.correlation_id = correlation_id
        super().__init__(message)


# ── File Processing Errors ────────────────────────────────────────────────


class FileProcessingError(ResumeAnalyzerError):
    """Base error for file processing failures."""


class UnsupportedFileTypeError(FileProcessingError):
    """Raised when the uploaded file type is not supported."""

    def __init__(
        self,
        file_type: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        self.file_type = file_type
        super().__init__(
            f"Unsupported file type: '{file_type}'. "
            f"Please upload a PDF, DOCX, or TXT file.",
            correlation_id=correlation_id,
        )


class FileTooLargeError(FileProcessingError):
    """Raised when the uploaded file exceeds the size limit."""

    def __init__(
        self,
        file_size_mb: float,
        max_size_mb: int,
        correlation_id: Optional[str] = None,
    ) -> None:
        self.file_size_mb = file_size_mb
        self.max_size_mb = max_size_mb
        super().__init__(
            f"File size ({file_size_mb:.1f} MB) exceeds the "
            f"maximum allowed size of {max_size_mb} MB.",
            correlation_id=correlation_id,
        )


class FileCorruptedError(FileProcessingError):
    """Raised when a file cannot be read (corrupted or invalid)."""

    def __init__(
        self,
        filename: str,
        detail: str = "",
        correlation_id: Optional[str] = None,
    ) -> None:
        self.filename = filename
        detail_msg = f" {detail}" if detail else ""
        super().__init__(
            f"Unable to read file '{filename}'. It may be corrupted or "
            f"in an invalid format.{detail_msg}",
            correlation_id=correlation_id,
        )


class TextExtractionError(FileProcessingError):
    """Raised when text cannot be extracted from the file."""

    def __init__(
        self,
        filename: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        self.filename = filename
        super().__init__(
            f"Could not extract text from '{filename}'. "
            f"The file may be empty or image-based.",
            correlation_id=correlation_id,
        )


# ── Analysis Errors ────────────────────────────────────────────────────────


class AnalysisError(ResumeAnalyzerError):
    """Base error for resume analysis failures."""


class AIServiceError(AnalysisError):
    """Base error for AI service call failures."""


class OpenAITimeoutError(AIServiceError):
    """Raised when an OpenAI API call times out."""

    def __init__(
        self,
        duration_ms: int,
        correlation_id: Optional[str] = None,
    ) -> None:
        self.duration_ms = duration_ms
        super().__init__(
            f"OpenAI API call timed out after {duration_ms}ms. "
            f"Please try again.",
            correlation_id=correlation_id,
        )


class OpenAIRateLimitError(AIServiceError):
    """Raised when OpenAI rate limit is exceeded."""

    def __init__(
        self,
        retry_after: int = 30,
        correlation_id: Optional[str] = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(
            f"OpenAI API rate limit exceeded. "
            f"Please wait {retry_after} seconds before retrying.",
            correlation_id=correlation_id,
        )


class OpenAITokenLimitError(AIServiceError):
    """Raised when the resume text exceeds the token limit."""

    def __init__(
        self,
        token_count: int,
        max_tokens: int,
        correlation_id: Optional[str] = None,
    ) -> None:
        self.token_count = token_count
        self.max_tokens = max_tokens
        super().__init__(
            f"Resume text is too long ({token_count} tokens, "
            f"max {max_tokens}). Please shorten the resume.",
            correlation_id=correlation_id,
        )


class OpenAISchemaError(AIServiceError):
    """Raised when GPT response does not match the expected schema."""

    def __init__(
        self,
        detail: str = "Unexpected response format from AI service.",
        correlation_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            f"{detail} Please try again.",
            correlation_id=correlation_id,
        )


class ScoringError(AnalysisError):
    """Raised when resume scoring fails."""


class SummaryGenerationError(AnalysisError):
    """Raised when summary generation fails."""


# ── Recommendation Errors ──────────────────────────────────────────────────


class RecommendationError(ResumeAnalyzerError):
    """Base error for job recommendation failures."""


class JobDatabaseError(RecommendationError):
    """Raised when the job database cannot be loaded."""

    def __init__(
        self,
        detail: str = "Job database is unavailable.",
        correlation_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            detail,
            correlation_id=correlation_id,
        )


class MatchingError(RecommendationError):
    """Raised when job matching computation fails."""


# ── Report Errors ──────────────────────────────────────────────────────────


class ReportError(ResumeAnalyzerError):
    """Base error for report generation failures."""


class PDFGenerationError(ReportError):
    """Raised when PDF report generation fails."""


class ReportNotFoundError(ReportError):
    """Raised when a requested report is not found."""

    def __init__(
        self,
        report_id: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        self.report_id = report_id
        super().__init__(
            f"Report '{report_id}' not found.",
            correlation_id=correlation_id,
        )


# ── Database Errors ────────────────────────────────────────────────────────


class DatabaseError(ResumeAnalyzerError):
    """Base error for database operations."""


class ConnectionError(DatabaseError):
    """Raised when database connection fails."""


class MigrationError(DatabaseError):
    """Raised when database migration fails."""


class IntegrityError(DatabaseError):
    """Raised on database integrity constraint violations."""


# ── Configuration Errors ──────────────────────────────────────────────────


class ConfigurationError(ResumeAnalyzerError):
    """Base error for configuration issues."""


class MissingAPIKeyError(ConfigurationError):
    """Raised when a required API key is missing."""

    def __init__(self, key_name: str = "OPENAI_API_KEY") -> None:
        self.key_name = key_name
        super().__init__(
            f"Missing required configuration: {key_name}. "
            f"Please set it in your .env file or environment variables."
        )


class InvalidConfigError(ConfigurationError):
    """Raised when a configuration value is invalid."""