"""
Job-related domain models.

Defines data structures for job roles, recommendations,
matching results, missing skills, and filters.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from models.skills import Skill


class JobRole(BaseModel):
    """A job role with required skills and metadata."""

    title: str = Field(description="Job title")
    industry: str = Field(default="", description="Industry sector")
    required_skills: list[str] = Field(
        default_factory=list,
        description="Skills required for this role",
    )
    preferred_skills: list[str] = Field(
        default_factory=list,
        description="Preferred/nice-to-have skills",
    )
    experience_level: str = Field(
        default="Mid",
        description="Required experience level (Entry, Mid, Senior, Lead)",
    )
    description: str = Field(default="", description="Job description")
    avg_salary_range: Optional[str] = Field(default=None, description="Average salary range")
    growth_potential: Optional[str] = Field(
        default=None,
        description="Career growth potential description",
    )
    is_active: bool = Field(default=True, description="Whether this role is currently active")

    @property
    def all_required_skills(self) -> list[str]:
        """Return all required and preferred skills combined."""
        return self.required_skills + self.preferred_skills


class MatchResult(BaseModel):
    """Result of matching a resume to a job role."""

    job_role: JobRole = Field(description="The matched job role")
    match_percentage: float = Field(
        ge=0.0, le=100.0,
        description="Match percentage based on skill overlap",
    )
    matched_skills: list[str] = Field(
        default_factory=list,
        description="Skills that matched",
    )
    missing_skills: list[str] = Field(
        default_factory=list,
        description="Required skills missing from resume",
    )
    relevance_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Relevance score considering experience level",
    )


class JobRecommendation(BaseModel):
    """A job recommendation for the user."""

    title: str = Field(description="Recommended job title")
    match_percentage: float = Field(
        ge=0.0, le=100.0,
        description="Match percentage",
    )
    required_skills: list[str] = Field(
        default_factory=list,
        description="Skills required for this role",
    )
    matched_skills: list[str] = Field(
        default_factory=list,
        description="Skills from resume that match",
    )
    missing_skills: list[str] = Field(
        default_factory=list,
        description="Skills missing from resume",
    )
    experience_level: str = Field(default="Mid", description="Required experience level")
    industry: str = Field(default="", description="Industry sector")
    description: str = Field(default="", description="Brief job description")
    learning_resources: list[str] = Field(
        default_factory=list,
        description="Suggested learning resources for missing skills",
    )


class MissingSkill(BaseModel):
    """A skill that is missing from the resume but relevant for target roles."""

    skill_name: str = Field(description="Name of the missing skill")
    relevance_score: float = Field(
        ge=0.0, le=1.0,
        description="Relevance score (0-1)",
    )
    demand_level: str = Field(
        default="Medium",
        description="Market demand level (Low, Medium, High)",
    )
    related_roles: list[str] = Field(
        default_factory=list,
        description="Job roles that require this skill",
    )
    learning_resource: Optional[str] = Field(
        default=None,
        description="Suggested learning resource URL",
    )
    category: str = Field(default="Technical", description="Skill category")


class JobFilter(BaseModel):
    """Filters for job recommendations."""

    industries: list[str] = Field(default_factory=list, description="Industries to include")
    experience_levels: list[str] = Field(
        default_factory=list,
        description="Experience levels to include",
    )
    locations: list[str] = Field(default_factory=list, description="Locations to include")
    remote_only: bool = Field(default=False, description="Only show remote jobs")
    min_match_percentage: float = Field(
        default=10.0,
        ge=0.0, le=100.0,
        description="Minimum match percentage",
    )
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum results to return")