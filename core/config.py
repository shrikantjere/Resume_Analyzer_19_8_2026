"""
Configuration management for the AI Resume Analyzer.

Uses pydantic-settings to load and validate configuration from
environment variables and .env file. Provides a singleton Settings
object that is accessible throughout the application.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file.

    All configuration is validated at startup. Required values
    (like OPENAI_API_KEY) will raise an error if missing.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        frozen=True,
    )

    # ── OpenAI ──────────────────────────────────────────────────────────
    openai_api_key: SecretStr = Field(
        default=...,
        description="OpenAI API key for GPT model access",
    )
    openai_model: str = Field(
        default="gpt-4o",
        description="OpenAI model identifier to use for analysis",
    )
    openai_max_tokens: int = Field(
        default=4096,
        ge=512,
        le=16384,
        description="Maximum tokens per OpenAI API call",
    )
    openai_temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Temperature for GPT response randomness",
    )
    openai_retry_count: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of retry attempts for failed API calls",
    )
    openai_timeout: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout in seconds for OpenAI API calls",
    )

    # ── Database ────────────────────────────────────────────────────────
    database_url: str = Field(
        default="sqlite:///data/analyzer.db",
        description="SQLite database connection URL",
    )

    # ── Application ─────────────────────────────────────────────────────
    max_file_size_mb: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum allowed resume file size in MB",
    )
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Application log level",
    )
    log_format: str = Field(
        default="json",
        pattern="^(json|text)$",
        description="Log output format: json or text",
    )
    upload_dir: str = Field(
        default="data/uploads",
        description="Directory for temporary upload storage",
    )
    report_dir: str = Field(
        default="data/reports",
        description="Directory for generated report files",
    )
    job_db_path: str = Field(
        default="data/job_database.json",
        description="Path to the curated job roles dataset",
    )
    job_cache_ttl_hours: int = Field(
        default=24,
        ge=1,
        le=168,
        description="TTL in hours for cached job data",
    )
    max_analysis_per_session: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum analyses per user session",
    )

    @property
    def max_file_size_bytes(self) -> int:
        """Return max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def upload_path(self) -> Path:
        """Return upload directory as a Path object."""
        return Path(self.upload_dir)

    @property
    def report_path(self) -> Path:
        """Return report directory as a Path object."""
        return Path(self.report_dir)

    @property
    def job_db_full_path(self) -> Path:
        """Return full path to job database JSON file."""
        return Path(self.job_db_path)


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton Settings instance.

    Uses lru_cache so Settings is loaded only once per process
    and reused thereafter.

    Returns:
        Settings: The application settings instance.
    """
    return Settings()