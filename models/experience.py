"""
Experience domain models.

Defines data structures for work experience evaluation,
timeline analysis, and experience summaries.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    """A single work experience entry."""

    title: str = Field(default="", description="Job title")
    company: str = Field(default="", description="Company or organization name")
    location: Optional[str] = Field(default=None, description="Work location")
    start_date: Optional[str] = Field(default=None, description="Start date")
    end_date: Optional[str] = Field(default=None, description="End date (or 'Present')")
    description: str = Field(default="", description="Job description / responsibilities")
    achievements: list[str] = Field(default_factory=list, description="Key achievements")
    is_current: bool = Field(default=False, description="Whether this is a current position")

    @property
    def duration_years(self) -> Optional[float]:
        """Estimate duration in years based on dates."""
        if not self.start_date:
            return None
        return _estimate_years(self.start_date, self.end_date)

    @property
    def has_quantified_achievements(self) -> bool:
        """Check if the description contains quantified achievements."""
        import re
        text = " ".join(self.achievements) if self.achievements else self.description
        return bool(re.search(r"\d+%|\d+x|\d+,\d+|\$\d+", text))


class ExperienceEvaluation(BaseModel):
    """Evaluation of a candidate's work experience."""

    total_years: float = Field(default=0.0, description="Total years of professional experience")
    total_roles: int = Field(default=0, description="Total number of roles held")
    gaps: list[TimelineGap] = Field(default_factory=list, description="Employment timeline gaps")
    quality_score: float = Field(
        default=0.0, ge=0.0, le=100.0,
        description="Quality score based on description quality",
    )
    relevance_score: float = Field(
        default=0.0, ge=0.0, le=100.0,
        description="Relevance score for target roles",
    )
    has_quantified_achievements: bool = Field(
        default=False,
        description="Whether experience includes quantified results",
    )
    experience_level: str = Field(
        default="Entry",
        description="Inferred experience level (Entry, Mid, Senior, Lead)",
    )


class TimelineGap(BaseModel):
    """A gap in the employment timeline."""

    start_date: str = Field(description="Start of the gap period")
    end_date: str = Field(description="End of the gap period")
    duration_months: int = Field(description="Duration of the gap in months")
    description: Optional[str] = Field(default=None, description="Context about the gap")


class ExperienceSummary(BaseModel):
    """Summary of work experience evaluation."""

    evaluation: ExperienceEvaluation = Field(
        default_factory=ExperienceEvaluation,
        description="Full experience evaluation",
    )
    top_achievements: list[str] = Field(
        default_factory=list,
        description="Top 3 achievements extracted",
    )
    industry_sectors: list[str] = Field(
        default_factory=list,
        description="Industry sectors worked in",
    )
    career_progression: str = Field(
        default="",
        description="Career progression narrative",
    )


def _estimate_years(start_date: str, end_date: Optional[str] = None) -> Optional[float]:
    """Estimate years between two date strings.

    Args:
        start_date: Start date string.
        end_date: End date string (or None/"Present" for current).

    Returns:
        Optional[float]: Estimated years, or None if parsing fails.
    """
    import re
    from datetime import datetime

    current_year = datetime.now().year

    # Try to extract years
    start_match = re.search(r"(\d{4})", start_date)
    if not start_match:
        return None

    start_year = int(start_match.group(1))

    if not end_date or end_date.lower() == "present":
        end_year = current_year
    else:
        end_match = re.search(r"(\d{4})", end_date)
        if not end_match:
            end_year = current_year
        else:
            end_year = int(end_match.group(1))

    return max(0.0, float(end_year - start_year))