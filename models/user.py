"""
User session and feedback domain models.

Defines data structures for user sessions, feedback,
and session state management.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionState(BaseModel):
    """Current session state for the Streamlit app."""

    analysis_id: Optional[int] = Field(default=None, description="Current analysis ID")
    correlation_id: Optional[str] = Field(default=None, description="Current correlation ID")
    resume_text: str = Field(default="", description="Current resume text")
    analysis_complete: bool = Field(default=False, description="Whether analysis is done")
    analysis_error: Optional[str] = Field(default=None, description="Analysis error message")
    current_page: str = Field(default="upload", description="Current page name")
    analysis_count: int = Field(default=0, description="Analyses performed in this session")


class UserSession(BaseModel):
    """A user session record."""

    session_id: str = Field(description="Unique session identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation time")
    last_active_at: datetime = Field(
        default_factory=datetime.now,
        description="Last activity timestamp",
    )
    analysis_count: int = Field(default=0, description="Number of analyses performed")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")


class UserFeedback(BaseModel):
    """User feedback on an analysis."""

    analysis_id: int = Field(description="ID of the analysis being rated")
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5")
    comment: str = Field(default="", description="Optional feedback comment")
    created_at: datetime = Field(default_factory=datetime.now, description="Feedback timestamp")