"""
Resume domain models.

Defines the data structures for resumes, parsed content,
education, projects, and certifications.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class ResumeSection(str, Enum):
    """Enumeration of standard resume sections."""

    CONTACT = "contact"
    SUMMARY = "summary"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    ACHIEVEMENTS = "achievements"
    LANGUAGES = "languages"
    OTHER = "other"


class Education(BaseModel):
    """Educational qualification entry."""

    degree: str = Field(default="", description="Degree or qualification name")
    institution: str = Field(default="", description="Institution or university name")
    field_of_study: str = Field(default="", description="Field or major of study")
    start_date: Optional[str] = Field(default=None, description="Start date (year or full date)")
    end_date: Optional[str] = Field(default=None, description="End date or expected graduation")
    gpa: Optional[str] = Field(default=None, description="GPA or grade if available")
    achievements: list[str] = Field(default_factory=list, description="Academic achievements")

    @property
    def is_complete(self) -> bool:
        """Check if the education entry has essential fields."""
        return bool(self.degree and self.institution)


class Project(BaseModel):
    """Project entry from a resume."""

    name: str = Field(default="", description="Project name")
    description: str = Field(default="", description="Project description")
    technologies: list[str] = Field(default_factory=list, description="Technologies used")
    url: Optional[str] = Field(default=None, description="Project URL or link")
    duration: Optional[str] = Field(default=None, description="Project duration")

    @property
    def has_technologies(self) -> bool:
        """Check if the project lists technologies used."""
        return len(self.technologies) > 0


class Certification(BaseModel):
    """Professional certification entry."""

    name: str = Field(default="", description="Certification name")
    issuer: str = Field(default="", description="Issuing organization")
    date_obtained: Optional[str] = Field(default=None, description="Date obtained")
    url: Optional[str] = Field(default=None, description="Verification URL")
    does_not_expire: bool = Field(default=False, description="Whether certification is lifetime")


class Resume(BaseModel):
    """Raw resume data as submitted by the user."""

    raw_text: str = Field(default="", description="Raw text extracted from resume")
    file_type: str = Field(default="text", description="Original file type (pdf, docx, txt)")
    file_name: str = Field(default="pasted_text.txt", description="Original file name")
    file_size_bytes: int = Field(default=0, description="File size in bytes")
    submitted_at: datetime = Field(default_factory=datetime.now, description="Submission timestamp")

    @field_validator("raw_text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        """Validate that the resume text is not empty."""
        if not v.strip():
            raise ValueError("Resume text cannot be empty")
        return v


class ParsedResume(BaseModel):
    """Structured, parsed representation of a resume."""

    name: Optional[str] = Field(default=None, description="Candidate's full name")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    location: Optional[str] = Field(default=None, description="City/region")
    linkedin: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    portfolio: Optional[str] = Field(default=None, description="Portfolio or personal website")
    professional_summary: Optional[str] = Field(
        default=None, description="Professional summary statement"
    )
    education: list[Education] = Field(default_factory=list, description="Education entries")
    work_experience: list[dict[str, Any]] = Field(
        default_factory=list, description="Work experience entries"
    )
    projects: list[Project] = Field(default_factory=list, description="Project entries")
    certifications: list[Certification] = Field(
        default_factory=list, description="Certification entries"
    )
    languages: list[str] = Field(default_factory=list, description="Languages known")
    raw_sections: dict[str, str] = Field(
        default_factory=dict, description="Raw text by section"
    )

    @property
    def total_sections(self) -> int:
        """Count the number of non-empty sections."""
        count = 0
        if self.education:
            count += 1
        if self.work_experience:
            count += 1
        if self.projects:
            count += 1
        if self.certifications:
            count += 1
        if self.professional_summary:
            count += 1
        if self.languages:
            count += 1
        return count