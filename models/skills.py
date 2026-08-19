"""
Skills domain models.

Defines skill-related data structures including skill
categorization, proficiency levels, and inventories.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SkillCategory(str, Enum):
    """Enumeration of skill categories/domains."""

    PROGRAMMING = "Programming"
    DATA_SCIENCE = "Data Science"
    WEB_DEVELOPMENT = "Web Development"
    DATABASE = "Database"
    DEVOPS = "DevOps"
    CLOUD = "Cloud Computing"
    AI_ML = "AI & Machine Learning"
    DESIGN = "Design"
    SOFT_SKILL = "Soft Skill"
    LANGUAGE = "Language"
    TOOL = "Tool & Platform"
    FRAMEWORK = "Framework"
    DOMAIN = "Domain Knowledge"
    OTHER = "Other"


class SkillProficiency(str, Enum):
    """Enumeration of skill proficiency levels."""

    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"
    UNKNOWN = "Unknown"


class Skill(BaseModel):
    """A single skill entity."""

    name: str = Field(description="Skill name")
    category: SkillCategory = Field(
        default=SkillCategory.OTHER,
        description="Skill category/domain",
    )
    proficiency: SkillProficiency = Field(
        default=SkillProficiency.UNKNOWN,
        description="Inferred proficiency level",
    )
    is_technical: bool = Field(default=True, description="Whether this is a technical skill")

    @property
    def normalized_name(self) -> str:
        """Return a normalized version of the skill name for comparison."""
        return self.name.lower().strip().replace("-", " ").replace("/", " ")


class SkillInventory(BaseModel):
    """Complete inventory of skills extracted from a resume."""

    technical_skills: list[Skill] = Field(
        default_factory=list,
        description="List of technical/hard skills",
    )
    soft_skills: list[Skill] = Field(
        default_factory=list,
        description="List of soft skills",
    )
    by_category: dict[str, list[Skill]] = Field(
        default_factory=dict,
        description="Skills grouped by category",
    )

    @property
    def all_skills(self) -> list[Skill]:
        """Return all skills combined."""
        return self.technical_skills + self.soft_skills

    @property
    def skill_names(self) -> set[str]:
        """Return set of all skill names."""
        return {s.normalized_name for s in self.all_skills}

    @property
    def total_count(self) -> int:
        """Return total number of skills."""
        return len(self.technical_skills) + len(self.soft_skills)

    def get_skills_by_category(self, category: SkillCategory) -> list[Skill]:
        """Get skills filtered by category.

        Args:
            category: The skill category to filter by.

        Returns:
            list[Skill]: Skills matching the given category.
        """
        return [s for s in self.all_skills if s.category == category]