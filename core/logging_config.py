"""
Structured logging configuration for the AI Resume Analyzer.

Provides JSON-formatted logging with correlation ID support,
PII-safe message formatting, and rotating file handlers.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from pythonjsonlogger import jsonlogger

from core.config import get_settings


def get_logger(
    name: str = "resume_analyzer",
    correlation_id: Optional[str] = None,
) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name (typically __name__ from the calling module).
        correlation_id: Optional correlation ID for request tracing.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers if called multiple times per module
    if logger.handlers:
        return logger

    settings = get_settings()
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # ── Console Handler ──────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if settings.log_format == "json":
        formatter = JsonFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── File Handler (rotating) ──────────────────────────────────────
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=log_dir / "analyzer.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # ── Error File Handler (ERROR+ only) ─────────────────────────────
    error_handler = RotatingFileHandler(
        filename=log_dir / "errors.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # Store correlation_id as a filter for contextual logging
    if correlation_id:
        logger = logging.LoggerAdapter(logger, {"correlation_id": correlation_id})

    return logger


class JsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that adds standard fields to every log entry."""

    def add_fields(
        self,
        log_record: dict,
        record: logging.LogRecord,
        message_dict: dict,
    ) -> None:
        """Add standard fields to the log record.

        Args:
            log_record: The log record dict to add fields to.
            record: The original log record.
            message_dict: Additional message dict from the log call.
        """
        super().add_fields(log_record, record, message_dict)

        # Ensure timestamp exists
        if "timestamp" not in log_record:
            log_record["timestamp"] = self.formatTime(record, self.datefmt)

        # Map standard logging levelname to 'level'
        log_record["level"] = record.levelname

        # Add correlation_id if present in the record
        correlation_id = getattr(record, "correlation_id", None)
        if correlation_id:
            log_record["correlation_id"] = correlation_id

        # Add duration_ms if present
        duration_ms = getattr(record, "duration_ms", None)
        if duration_ms is not None:
            log_record["duration_ms"] = duration_ms

        # Add tokens_used if present
        tokens_used = getattr(record, "tokens_used", None)
        if tokens_used is not None:
            log_record["tokens_used"] = tokens_used


class PerformanceLogger:
    """Context manager for performance logging.

    Usage:
        with PerformanceLogger(logger, "analyze_resume") as perf:
            result = analyzer.analyze(text)
            perf.tokens_used = 1500
    """

    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Initialize the performance logger.

        Args:
            logger: Logger instance to log to.
            operation: Name of the operation being measured.
            correlation_id: Optional correlation ID for tracing.
        """
        self.logger = logger
        self.operation = operation
        self.correlation_id = correlation_id
        self.tokens_used: Optional[int] = None

    def __enter__(self) -> "PerformanceLogger":
        """Start the performance timer."""
        import time

        self.start_time = time.monotonic()
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Log the performance metrics on exit."""
        import time

        duration_ms = int((time.monotonic() - self.start_time) * 1000)

        extra: dict = {
            "duration_ms": duration_ms,
            "operation": self.operation,
        }
        if self.correlation_id:
            extra["correlation_id"] = self.correlation_id
        if self.tokens_used is not None:
            extra["tokens_used"] = self.tokens_used

        if exc_type is not None:
            self.logger.error(
                f"{self.operation} failed after {duration_ms}ms",
                extra=extra,
                exc_info=(exc_type, exc_val, exc_tb),
            )
        else:
            self.logger.info(
                f"{self.operation} completed in {duration_ms}ms",
                extra=extra,
            )