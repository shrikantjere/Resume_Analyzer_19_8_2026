"""
Skill extraction service.

Extracts and categorizes skills from resume text using
OpenAI GPT-4o. Identifies technical and soft skills,
infers proficiency levels, and categorizes by domain.
"""

from __future__ import annotations

import json
from typing import Optional

from core.ai_client import AIClient
from core.exceptions import AIServiceError, OpenAISchemaError
from core.logging_config import get_logger, PerformanceLogger
from models.skills import Skill, SkillCategory, SkillInventory, SkillProficiency

logger = get_logger(__name__)

# System prompt for skill extraction
SKILL_EXTRACTION_PROMPT = """You are a skilled resume parser specializing in skill identification.
Analyze the resume text and extract all skills mentioned.

For each skill, determine:
1. The skill name (exact as written, normalized)
2. Category: Programming, Data_Science, Web_Development, Database, DevOps, Cloud_Computing, AI_ML, Design, Soft_Skill, Language, Tool_Platform, Framework, Domain_Knowledge, or Other
3. Proficiency level: Beginner, Intermediate, Advanced, Expert, or Unknown (infer from context)
4. Whether it's a technical skill (true/false)

Return a JSON object with this structure:
{
  "technical_skills": [
    {"name": "Python", "category": "Programming", "proficiency": "Advanced", "is_technical": true},
    {"name": "SQL", "category": "Database", "proficiency": "Intermediate", "is_technical": true}
  ],
  "soft_skills": [
    {"name": "Communication", "category": "Soft_Skill", "proficiency": "Advanced", "is_technical": false}
  ]
}

Be thorough. Extract ALL skills mentioned, even implicit ones.
If no skills are found, return empty arrays."""


class SkillExtractionService:
    """Service for extracting and categorizing skills from resume text.

    Uses OpenAI GPT-4o to identify technical and soft skills,
    infer proficiency levels, and categorize by domain.
    """

    def __init__(self, ai_client: Optional[AIClient] = None) -> None:
        """Initialize the skill extraction service.

        Args:
            ai_client: Optional AI client instance. Creates one if not provided.
        """
        self.ai_client = ai_client or AIClient()

    def extract(self, resume_text: str, correlation_id: Optional[str] = None) -> SkillInventory:
        """Extract and categorize skills from resume text.

        Args:
            resume_text: The full resume text to analyze.
            correlation_id: Optional trace ID for request correlation.

        Returns:
            SkillInventory: Categorized skills with proficiency levels.

        Raises:
            AIServiceError: If the AI service call fails.
            OpenAISchemaError: If the response cannot be parsed.
        """
        logger.info(
            "Starting skill extraction",
            extra={"correlation_id": correlation_id, "text_length": len(resume_text)},
        )

        with PerformanceLogger(
            logger, "skill_extraction", correlation_id=correlation_id
        ) as perf:
            response = self.ai_client.chat_complete_json(
                system_prompt=SKILL_EXTRACTION_PROMPT,
                user_prompt=f"Extract all skills from this resume:\n\n{resume_text}",
                correlation_id=correlation_id,
            )

        skills = self._parse_response(response)
        categorized = self._categorize(skills)

        logger.info(
            "Skill extraction complete: %d technical, %d soft skills",
            len(categorized.technical_skills),
            len(categorized.soft_skills),
            extra={"correlation_id": correlation_id},
        )

        return categorized

    def extract_from_text(
        self,
        text: str,
        correlation_id: Optional[str] = None,
    ) -> SkillInventory:
        """Alias for extract() for API consistency.

        Args:
            text: The resume text to analyze.
            correlation_id: Optional trace ID.

        Returns:
            SkillInventory: Extracted skills.
        """
        return self.extract(text, correlation_id=correlation_id)

    def _parse_response(self, response: dict) -> list[Skill]:
        """Parse the AI response into Skill objects.

        Args:
            response: JSON response from the AI service.

        Returns:
            list[Skill]: Parsed skill objects.

        Raises:
            OpenAISchemaError: If the response structure is invalid.
        """
        skills: list[Skill] = []

        # Parse technical skills
        for item in response.get("technical_skills", []):
            try:
                skill = Skill(
                    name=item.get("name", "Unknown"),
                    category=self._parse_category(item.get("category", "Other")),
                    proficiency=self._parse_proficiency(item.get("proficiency", "Unknown")),
                    is_technical=True,
                )
                skills.append(skill)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning("Failed to parse technical skill: %s - %s", item, e)

        # Parse soft skills
        for item in response.get("soft_skills", []):
            try:
                skill = Skill(
                    name=item.get("name", "Unknown"),
                    category=self._parse_category(item.get("category", "Soft_Skill")),
                    proficiency=self._parse_proficiency(item.get("proficiency", "Unknown")),
                    is_technical=False,
                )
                skills.append(skill)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning("Failed to parse soft skill: %s - %s", item, e)

        return skills

    def _categorize(self, skills: list[Skill]) -> SkillInventory:
        """Categorize skills into technical vs soft and by domain.

        Args:
            skills: List of extracted skills.

        Returns:
            SkillInventory: Categorized skill inventory.
        """
        technical: list[Skill] = []
        soft: list[Skill] = []
        by_category: dict[str, list[Skill]] = {}

        for skill in skills:
            if skill.is_technical:
                technical.append(skill)
            else:
                soft.append(skill)

            category = skill.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(skill)

        # Deduplicate by normalized name (keep highest proficiency)
        technical = self._deduplicate(technical)
        soft = self._deduplicate(soft)

        return SkillInventory(
            technical_skills=technical,
            soft_skills=soft,
            by_category=by_category,
        )

    def _deduplicate(self, skills: list[Skill]) -> list[Skill]:
        """Remove duplicate skills keeping the highest proficiency.

        Args:
            skills: List of skills to deduplicate.

        Returns:
            list[Skill]: Deduplicated skills.
        """
        seen: dict[str, Skill] = {}
        proficiency_order = {
            SkillProficiency.UNKNOWN: 0,
            SkillProficiency.BEGINNER: 1,
            SkillProficiency.INTERMEDIATE: 2,
            SkillProficiency.ADVANCED: 3,
            SkillProficiency.EXPERT: 4,
        }

        for skill in skills:
            normalized = skill.normalized_name
            if normalized in seen:
                existing = seen[normalized]
                if proficiency_order.get(skill.proficiency, 0) > proficiency_order.get(
                    existing.proficiency, 0
                ):
                    seen[normalized] = skill
            else:
                seen[normalized] = skill

        return list(seen.values())

    @staticmethod
    def _parse_category(category: str) -> SkillCategory:
        """Parse a category string into a SkillCategory enum.

        Args:
            category: Category string from AI response.

        Returns:
            SkillCategory: Parsed category enum.
        """
        category_map = {
            "programming": SkillCategory.PROGRAMMING,
            "data_science": SkillCategory.DATA_SCIENCE,
            "data science": SkillCategory.DATA_SCIENCE,
            "web_development": SkillCategory.WEB_DEVELOPMENT,
            "web development": SkillCategory.WEB_DEVELOPMENT,
            "database": SkillCategory.DATABASE,
            "devops": SkillCategory.DEVOPS,
            "cloud_computing": SkillCategory.CLOUD,
            "cloud computing": SkillCategory.CLOUD,
            "ai_ml": SkillCategory.AI_ML,
            "ai & machine learning": SkillCategory.AI_ML,
            "design": SkillCategory.DESIGN,
            "soft_skill": SkillCategory.SOFT_SKILL,
            "soft skill": SkillCategory.SOFT_SKILL,
            "language": SkillCategory.LANGUAGE,
            "tool_platform": SkillCategory.TOOL,
            "tool & platform": SkillCategory.TOOL,
            "framework": SkillCategory.FRAMEWORK,
            "domain_knowledge": SkillCategory.DOMAIN,
            "domain knowledge": SkillCategory.DOMAIN,
        }
        return category_map.get(category.lower().strip(), SkillCategory.OTHER)

    @staticmethod
    def _parse_proficiency(proficiency: str) -> SkillProficiency:
        """Parse a proficiency string into a SkillProficiency enum.

        Args:
            proficiency: Proficiency string from AI response.

        Returns:
            SkillProficiency: Parsed proficiency enum.
        """
        prof_map = {
            "beginner": SkillProficiency.BEGINNER,
            "intermediate": SkillProficiency.INTERMEDIATE,
            "advanced": SkillProficiency.ADVANCED,
            "expert": SkillProficiency.EXPERT,
        }
        return prof_map.get(proficiency.lower().strip(), SkillProficiency.UNKNOWN)