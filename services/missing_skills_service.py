"""
Missing skills identification service.

Identifies skills that are required for target job roles
but missing from the resume. Ranks by relevance and demand.
"""

from __future__ import annotations

from typing import Optional

from core.logging_config import get_logger
from core.utils import normalize_skill_name
from models.job import JobRecommendation, MissingSkill
from models.skills import SkillInventory

logger = get_logger(__name__)


class MissingSkillsService:
    """Service for identifying missing skills.

    Analyzes job recommendations against the candidate's
    existing skills to identify gaps and rank them by relevance.
    """

    def identify(
        self,
        recommendations: list[JobRecommendation],
        skill_inventory: SkillInventory,
    ) -> list[MissingSkill]:
        """Identify missing skills from job recommendations.

        Args:
            recommendations: List of job recommendations.
            skill_inventory: Candidate's extracted skills.

        Returns:
            list[MissingSkill]: Ranked list of missing skills.
        """
        logger.info(
            "Identifying missing skills from %d recommendations",
            len(recommendations),
        )

        if not recommendations:
            return []

        existing_skills = skill_inventory.skill_names

        # Collect all missing skills across recommendations
        missing_skill_map: dict[str, dict] = {}

        for rec in recommendations:
            for skill in rec.missing_skills:
                normalized = normalize_skill_name(skill)

                # Skip if the candidate already has this skill
                if normalized in existing_skills:
                    continue

                if normalized not in missing_skill_map:
                    missing_skill_map[normalized] = {
                        "skill_name": skill,
                        "count": 0,
                        "related_roles": [],
                        "total_match_weight": 0.0,
                    }

                missing_skill_map[normalized]["count"] += 1
                missing_skill_map[normalized]["related_roles"].append(rec.title)
                missing_skill_map[normalized]["total_match_weight"] += rec.match_percentage

        # Convert to MissingSkill objects and rank
        missing_skills: list[MissingSkill] = []
        for normalized, data in missing_skill_map.items():
            # Relevance score: combination of frequency and match weight
            freq_score = min(1.0, data["count"] / max(len(recommendations), 1))
            weight_score = min(1.0, data["total_match_weight"] / (100.0 * data["count"]))
            relevance = (freq_score * 0.6 + weight_score * 0.4)

            # Demand level based on frequency
            if data["count"] >= len(recommendations) * 0.5:
                demand = "High"
            elif data["count"] >= len(recommendations) * 0.25:
                demand = "Medium"
            else:
                demand = "Low"

            # Determine category
            category = self._infer_category(data["skill_name"])

            missing_skills.append(
                MissingSkill(
                    skill_name=data["skill_name"],
                    relevance_score=round(relevance, 2),
                    demand_level=demand,
                    related_roles=list(set(data["related_roles"])),
                    category=category,
                )
            )

        # Sort by relevance (highest first)
        missing_skills.sort(key=lambda ms: ms.relevance_score, reverse=True)

        logger.info(
            "Identified %d missing skills",
            len(missing_skills),
        )

        return missing_skills

    def generate_learning_suggestions(
        self,
        missing_skills: list[MissingSkill],
    ) -> list[dict[str, str]]:
        """Generate learning resource suggestions for missing skills.

        Args:
            missing_skills: List of identified missing skills.

        Returns:
            list[dict]: Learning suggestions with skill name and resource.
        """
        suggestions: list[dict[str, str]] = []

        for skill in missing_skills:
            resource = self._get_resource_for_skill(skill.skill_name, skill.category)
            suggestions.append({
                "skill": skill.skill_name,
                "category": skill.category,
                "suggestion": f"Learn {skill.skill_name}",
                "resource": resource,
            })

        return suggestions

    @staticmethod
    def _infer_category(skill_name: str) -> str:
        """Infer the category of a skill based on its name.

        Args:
            skill_name: Name of the skill.

        Returns:
            str: Inferred category.
        """
        technical_keywords = [
            "python", "java", "javascript", "sql", "aws", "docker",
            "kubernetes", "react", "angular", "node", "machine learning",
            "data", "api", "git", "linux", "cloud", "devops", "ci/cd",
        ]
        name_lower = skill_name.lower()

        for keyword in technical_keywords:
            if keyword in name_lower:
                return "Technical"

        return "Professional Development"

    @staticmethod
    def _get_resource_for_skill(skill_name: str, category: str) -> str:
        """Get a suggested learning resource for a skill.

        Args:
            skill_name: Name of the skill.
            category: Skill category.

        Returns:
            str: Suggested learning resource URL or description.
        """
        # Common skill resources
        resource_map = {
            "python": "https://www.python.org/about/gettingstarted/",
            "sql": "https://www.w3schools.com/sql/",
            "machine learning": "https://www.coursera.org/learn/machine-learning",
            "data science": "https://www.datacamp.com/",
            "aws": "https://aws.amazon.com/training/",
            "docker": "https://docs.docker.com/get-started/",
            "kubernetes": "https://kubernetes.io/docs/tutorials/",
            "react": "https://react.dev/learn",
            "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
            "git": "https://git-scm.com/doc",
        }

        name_lower = skill_name.lower()
        for key, url in resource_map.items():
            if key in name_lower:
                return url

        # Generic resource
        return f"https://www.coursera.org/search?query={skill_name.replace(' ', '+')}"