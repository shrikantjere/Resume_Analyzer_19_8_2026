"""
Job recommendation service.

Matches extracted skills against job database to recommend
suitable roles. Uses Jaccard similarity for skill matching
with AI-based fallback.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from core.ai_client import AIClient
from core.config import get_settings
from core.exceptions import JobDatabaseError, MatchingError
from core.logging_config import get_logger, PerformanceLogger
from core.utils import jaccard_similarity, normalize_skill_name
from models.job import JobFilter, JobRecommendation, MatchResult
from models.skills import SkillInventory

logger = get_logger(__name__)

# System prompt for AI-based job matching (fallback)
JOB_MATCHING_PROMPT = """You are a career counselor and job market expert.
Based on the candidate's skills and experience, recommend suitable job roles.

For each recommendation, provide:
1. Job title
2. Industry
3. Required skills (list of 5-10 skills)
4. Match percentage (based on skill overlap)
5. Experience level required
6. Brief description
7. Missing skills that the candidate should acquire

Return a JSON object with this structure:
{
  "recommendations": [
    {
      "title": "Data Scientist",
      "industry": "Technology",
      "required_skills": ["Python", "SQL", "Machine Learning", "Statistics"],
      "match_percentage": 85,
      "experience_level": "Mid",
      "description": "Analyze large datasets to drive business decisions...",
      "missing_skills": ["Apache Spark", "TensorFlow"]
    }
  ]
}

Return at least 5 recommendations. Be realistic based on the candidate's profile."""


class JobRecommendationService:
    """Service for matching resumes to job recommendations.

    Uses a hybrid approach: Jaccard similarity against a curated
    job database, with AI-based fallback for broader matching.
    """

    def __init__(
        self,
        ai_client: Optional[AIClient] = None,
    ) -> None:
        """Initialize the job recommendation service.

        Args:
            ai_client: Optional AI client for fallback matching.
        """
        self.ai_client = ai_client or AIClient()
        self.settings = get_settings()
        self._job_roles: Optional[list[dict[str, Any]]] = None

    def get_recommendations(
        self,
        skill_inventory: SkillInventory,
        total_experience_years: float = 0.0,
        experience_level: str = "Entry",
        filters: Optional[JobFilter] = None,
        correlation_id: Optional[str] = None,
    ) -> list[JobRecommendation]:
        """Get job recommendations based on skills and experience.

        Args:
            skill_inventory: Extracted skills inventory.
            total_experience_years: Total years of experience.
            experience_level: Inferred experience level.
            filters: Optional filters for recommendations.
            correlation_id: Optional trace ID.

        Returns:
            list[JobRecommendation]: Ranked job recommendations.

        Raises:
            JobDatabaseError: If the job database cannot be loaded.
            MatchingError: If matching computation fails.
        """
        effective_filter = filters or JobFilter()
        skill_names = skill_inventory.skill_names

        logger.info(
            "Getting job recommendations: %d skills, %s level",
            len(skill_names),
            experience_level,
            extra={"correlation_id": correlation_id},
        )

        with PerformanceLogger(
            logger, "job_recommendation", correlation_id=correlation_id
        ) as perf:
            try:
                # Try database-based matching first
                recommendations = self._match_from_database(
                    skill_names=skill_names,
                    total_experience_years=total_experience_years,
                    experience_level=experience_level,
                    filters=effective_filter,
                )
            except (JobDatabaseError, OSError, json.JSONDecodeError):
                # Fall back to AI-based matching
                logger.info(
                    "Falling back to AI-based job matching",
                    extra={"correlation_id": correlation_id},
                )
                recommendations = self._match_from_ai(
                    skill_inventory=skill_inventory,
                    total_experience_years=total_experience_years,
                    correlation_id=correlation_id,
                )

        # Apply filters
        recommendations = self._apply_filters(recommendations, effective_filter)

        # Sort by match percentage descending
        recommendations.sort(key=lambda r: r.match_percentage, reverse=True)

        # Limit results
        recommendations = recommendations[: effective_filter.max_results]

        logger.info(
            "Found %d job recommendations",
            len(recommendations),
            extra={"correlation_id": correlation_id},
        )

        return recommendations

    # ── Database Matching ──────────────────────────────────────────────

    def _match_from_database(
        self,
        skill_names: set[str],
        total_experience_years: float,
        experience_level: str,
        filters: JobFilter,
    ) -> list[JobRecommendation]:
        """Match skills against the curated job database.

        Args:
            skill_names: Set of normalized skill names from resume.
            total_experience_years: Total years of experience.
            experience_level: Inferred experience level.
            filters: Job filters.

        Returns:
            list[JobRecommendation]: Matched recommendations.

        Raises:
            JobDatabaseError: If the database cannot be loaded.
        """
        job_roles = self._load_job_roles()
        recommendations: list[JobRecommendation] = []

        for role in job_roles:
            # Parse required skills
            required_skills_raw = role.get("required_skills", [])
            if isinstance(required_skills_raw, str):
                required_skills = json.loads(required_skills_raw)
            else:
                required_skills = required_skills_raw

            required_normalized = {normalize_skill_name(s) for s in required_skills}
            preferred_skills = role.get("preferred_skills", [])

            # Compute Jaccard similarity
            match_percentage = jaccard_similarity(skill_names, required_normalized) * 100.0

            # Apply experience level penalty
            level_penalty = self._experience_level_penalty(
                role.get("experience_level", "Mid"),
                experience_level,
            )
            match_percentage = max(0.0, match_percentage - level_penalty)

            # Skip if below minimum
            if match_percentage < filters.min_match_percentage:
                continue

            # Find matched and missing skills
            matched = [s for s in required_skills if normalize_skill_name(s) in skill_names]
            missing = [s for s in required_skills if normalize_skill_name(s) not in skill_names]

            recommendations.append(
                JobRecommendation(
                    title=role.get("title", "Unknown Role"),
                    match_percentage=round(match_percentage, 1),
                    required_skills=required_skills,
                    matched_skills=matched,
                    missing_skills=missing,
                    experience_level=role.get("experience_level", "Mid"),
                    industry=role.get("industry", ""),
                    description=role.get("description", ""),
                    learning_resources=[],
                )
            )

        return recommendations

    def _load_job_roles(self) -> list[dict[str, Any]]:
        """Load job roles from the database file.

        Returns:
            list[dict]: List of job role definitions.

        Raises:
            JobDatabaseError: If the file cannot be loaded.
        """
        if self._job_roles is not None:
            return self._job_roles

        path = Path(self.settings.job_db_path)
        if not path.exists():
            raise JobDatabaseError(f"Job database not found at {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._job_roles = data if isinstance(data, list) else data.get("roles", [])
            logger.info("Loaded %d job roles from database", len(self._job_roles))
            return self._job_roles
        except (OSError, json.JSONDecodeError) as e:
            raise JobDatabaseError(f"Failed to load job database: {e}") from e

    # ── AI-Based Matching (Fallback) ───────────────────────────────────

    def _match_from_ai(
        self,
        skill_inventory: SkillInventory,
        total_experience_years: float,
        correlation_id: Optional[str] = None,
    ) -> list[JobRecommendation]:
        """Use AI to generate job recommendations.

        Args:
            skill_inventory: Skills inventory.
            total_experience_years: Total experience years.
            correlation_id: Optional trace ID.

        Returns:
            list[JobRecommendation]: AI-generated recommendations.
        """
        skills_text = ", ".join(
            [s.name for s in skill_inventory.technical_skills[:15]]
            + [s.name for s in skill_inventory.soft_skills[:5]]
        )

        user_prompt = (
            f"Skills: {skills_text}\n"
            f"Total experience: {total_experience_years:.0f} years\n"
            f"Please recommend suitable job roles."
        )

        response = self.ai_client.chat_complete_json(
            system_prompt=JOB_MATCHING_PROMPT,
            user_prompt=user_prompt,
            correlation_id=correlation_id,
        )

        recommendations: list[JobRecommendation] = []
        for item in response.get("recommendations", []):
            recommendations.append(
                JobRecommendation(
                    title=item.get("title", "Unknown Role"),
                    match_percentage=float(item.get("match_percentage", 50)),
                    required_skills=item.get("required_skills", []),
                    matched_skills=[s for s in item.get("required_skills", [])
                                    if s in skills_text],
                    missing_skills=item.get("missing_skills", []),
                    experience_level=item.get("experience_level", "Mid"),
                    industry=item.get("industry", ""),
                    description=item.get("description", ""),
                )
            )

        return recommendations

    # ── Helpers ────────────────────────────────────────────────────────

    def _apply_filters(
        self,
        recommendations: list[JobRecommendation],
        filters: JobFilter,
    ) -> list[JobRecommendation]:
        """Apply filters to recommendations.

        Args:
            recommendations: List of recommendations to filter.
            filters: Filter criteria.

        Returns:
            list[JobRecommendation]: Filtered recommendations.
        """
        if not filters.industries and not filters.experience_levels:
            return recommendations

        filtered = []
        for rec in recommendations:
            if filters.industries and rec.industry not in filters.industries:
                continue
            if filters.experience_levels and rec.experience_level not in filters.experience_levels:
                continue
            filtered.append(rec)

        return filtered or recommendations  # Return all if filters eliminate everything

    @staticmethod
    def _experience_level_penalty(
        role_level: str,
        candidate_level: str,
    ) -> float:
        """Calculate penalty for experience level mismatch.

        Args:
            role_level: Required experience level for the role.
            candidate_level: Candidate's inferred experience level.

        Returns:
            float: Penalty percentage (0-40).
        """
        levels = ["Entry", "Mid", "Senior", "Lead"]
        if role_level not in levels or candidate_level not in levels:
            return 0.0

        role_idx = levels.index(role_level)
        candidate_idx = levels.index(candidate_level)
        diff = abs(role_idx - candidate_idx)

        penalties = {0: 0.0, 1: 10.0, 2: 25.0, 3: 40.0}
        return penalties.get(diff, 0.0)