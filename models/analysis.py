"""
Analysis domain models.

Defines the core analysis result data structures, including
resume scores, section scores, and analysis context.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from models.experience import ExperienceEvaluation, WorkExperience
from models.resume import Education, Project
from models.skills import Skill, SkillInventory


class SectionScore(BaseModel):
    """Score for a specific resume section."""

    section_name: str = Field(description="Section name (e.g., 'Education', 'Skills')")
    score: float = Field(default=0.0, ge=0.0, le=100.0, description="Section score 0-100")
    max_score: float = Field(default=100.0, description="Maximum possible score")
    weight: float = Field(default=0.0, ge=0.0, le=1.0, description="Weight in overall score")
    feedback: str = Field(default="", description="Feedback for this section")

    @property
    def percentage(self) -> float:
        """Return score as a percentage of max_score."""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100.0


class ResumeScore(BaseModel):
    """Overall resume score with section breakdown."""

    overall: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall resume score")
    section_scores: list[SectionScore] = Field(
        default_factory=list,
        description="Scores for individual sections",
    )
    ats_optimization_score: float = Field(
        default=0.0, ge=0.0, le=100.0,
        description="ATS keyword optimization score",
    )
    completeness_score: float = Field(
        default=0.0, ge=0.0, le=100.0,
        description="Section completeness score",
    )
    formatting_score: float = Field(
        default=0.0, ge=0.0, le=100.0,
        description="Formatting and structure score",
    )

    @property
    def section_map(self) -> dict[str, float]:
        """Return a mapping of section name to score."""
        return {s.section_name: s.score for s in self.section_scores}


class AnalysisContext(BaseModel):
    """Context for a single analysis run."""

    correlation_id: str = Field(description="Unique trace ID for this analysis")
    session_id: str = Field(default="", description="User session ID")
    started_at: datetime = Field(default_factory=datetime.now, description="Analysis start time")
    completed_at: Optional[datetime] = Field(default=None, description="Analysis completion time")
    total_duration_ms: Optional[int] = Field(default=None, description="Total duration in ms")
    token_usage: int = Field(default=0, description="Total tokens used in this analysis")
    analysis_version: str = Field(default="1.0.0", description="Analysis pipeline version")


class AnalysisResult(BaseModel):
    """Complete analysis result for a resume."""

    id: Optional[int] = Field(default=None, description="Database ID")
    correlation_id: str = Field(default="", description="Trace ID for this analysis")
    context: AnalysisContext = Field(
        default_factory=lambda: AnalysisContext(correlation_id="pending"),
        description="Analysis context metadata",
    )

    # Parsed data
    parsed_resume: Optional[dict[str, Any]] = Field(
        default=None,
        description="Structured parsed resume data",
    )
    education: list[Education] = Field(default_factory=list, description="Education entries")
    work_experience: list[WorkExperience] = Field(
        default_factory=list, description="Work experience entries"
    )
    projects: list[Project] = Field(default_factory=list, description="Project entries")

    # Skills
    skill_inventory: SkillInventory = Field(
        default_factory=SkillInventory,
        description="Extracted skills inventory",
    )

    # Experience
    experience_evaluation: ExperienceEvaluation = Field(
        default_factory=ExperienceEvaluation,
        description="Experience evaluation results",
    )

    # Scores
    resume_score: ResumeScore = Field(
        default_factory=ResumeScore,
        description="Resume scoring results",
    )

    # Summary
    summary: str = Field(default="", description="Generated professional summary")

    # Recommendations
    job_recommendations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Job recommendations",
    )
    missing_skills: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Missing skills identified",
    )
    improvements: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Improvement suggestions",
    )
    learning_suggestions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Learning resource suggestions",
    )

    @property
    def technical_skills(self) -> list[Skill]:
        """Return extracted technical skills."""
        return self.skill_inventory.technical_skills

    @property
    def technical_skill_names(self) -> list[str]:
        """Return names of technical skills."""
        return [s.name for s in self.skill_inventory.technical_skills]

    @property
    def soft_skills(self) -> list[Skill]:
        """Return extracted soft skills."""
        return self.skill_inventory.soft_skills

    @property
    def soft_skill_names(self) -> list[str]:
        """Return names of soft skills."""
        return [s.name for s in self.skill_inventory.soft_skills]

    @property
    def all_skill_names(self) -> list[str]:
        """Return all skill names."""
        return self.technical_skill_names + self.soft_skill_names

    @property
    def total_experience_years(self) -> float:
        """Return total years of experience."""
        return self.experience_evaluation.total_years

    @property
    def experience_level(self) -> str:
        """Return inferred experience level."""
        return self.experience_evaluation.experience_level

    @property
    def overall_score(self) -> float:
        """Return the overall resume score."""
        return self.resume_score.overall

    def to_dict(self) -> dict[str, Any]:
        """Convert the analysis result to a dictionary for serialization.

        Returns:
            dict: Serializable dictionary representation.
        """
        return {
            "id": self.id,
            "correlation_id": self.correlation_id,
            "overall_score": self.overall_score,
            "section_scores": [
                s.model_dump() for s in self.resume_score.section_scores
            ],
            "technical_skills": self.technical_skill_names,
            "soft_skills": self.soft_skill_names,
            "total_experience_years": self.total_experience_years,
            "experience_level": self.experience_level,
            "summary": self.summary,
            "job_recommendations": self.job_recommendations,
            "missing_skills": self.missing_skills,
            "improvements": self.improvements,
            "learning_suggestions": self.learning_suggestions,
        }