"""
Experience evaluation service.

Extracts work experience, evaluates quality, detects timeline
gaps, and infers experience level using OpenAI GPT-4o.
"""

from __future__ import annotations

from typing import Optional

from core.ai_client import AIClient
from core.exceptions import AIServiceError, OpenAISchemaError
from core.logging_config import get_logger, PerformanceLogger
from models.experience import (
    ExperienceEvaluation,
    ExperienceSummary,
    TimelineGap,
    WorkExperience,
)

logger = get_logger(__name__)

# System prompt for experience evaluation
EXPERIENCE_PROMPT = """You are a career assessment expert. Analyze the work experience section of this resume.

Extract and evaluate the following:
1. Each work experience entry (title, company, dates, description, achievements)
2. Total years of professional experience
3. Quality of descriptions (look for quantified achievements, action verbs, impact)
4. Employment timeline gaps
5. Career progression
6. Industry sectors

Return a JSON object with this structure:
{
  "work_experience": [
    {
      "title": "Software Engineer",
      "company": "Tech Corp",
      "start_date": "2019-01",
      "end_date": "2023-06",
      "description": "Led development of...",
      "achievements": ["Increased performance by 40%", "Managed team of 5"],
      "is_current": false
    }
  ],
  "total_years": 4.5,
  "quality_score": 75.0,
  "has_quantified_achievements": true,
  "experience_level": "Mid",
  "gaps": [
    {"start_date": "2023-01", "end_date": "2023-06", "duration_months": 5, "description": "Career transition"}
  ],
  "top_achievements": ["Increased performance by 40%", "Managed team of 5"],
  "industry_sectors": ["Technology", "Finance"],
  "career_progression": "Steady growth from junior to senior roles"
}

Be thorough. If a section is missing, return empty arrays or nulls."""


class ExperienceService:
    """Service for extracting and evaluating work experience.

    Uses OpenAI GPT-4o to parse experience entries, evaluate
    quality, and identify timeline gaps.
    """

    def __init__(self, ai_client: Optional[AIClient] = None) -> None:
        """Initialize the experience service.

        Args:
            ai_client: Optional AI client instance. Creates one if not provided.
        """
        self.ai_client = ai_client or AIClient()

    def evaluate(
        self,
        resume_text: str,
        correlation_id: Optional[str] = None,
    ) -> ExperienceSummary:
        """Evaluate work experience from resume text.

        Args:
            resume_text: The full resume text to analyze.
            correlation_id: Optional trace ID for request correlation.

        Returns:
            ExperienceSummary: Extracted experience with evaluation.

        Raises:
            AIServiceError: If the AI service call fails.
        """
        logger.info(
            "Starting experience evaluation",
            extra={"correlation_id": correlation_id},
        )

        with PerformanceLogger(
            logger, "experience_evaluation", correlation_id=correlation_id
        ) as perf:
            response = self.ai_client.chat_complete_json(
                system_prompt=EXPERIENCE_PROMPT,
                user_prompt=f"Evaluate the work experience in this resume:\n\n{resume_text}",
                correlation_id=correlation_id,
            )

        summary = self._parse_response(response)

        logger.info(
            "Experience evaluation complete: %d years, %d roles, level=%s",
            summary.evaluation.total_years,
            summary.evaluation.total_roles,
            summary.evaluation.experience_level,
            extra={"correlation_id": correlation_id},
        )

        return summary

    def _parse_response(self, response: dict) -> ExperienceSummary:
        """Parse the AI response into an ExperienceSummary.

        Args:
            response: JSON response from the AI service.

        Returns:
            ExperienceSummary: Parsed experience summary.
        """
        # Parse work experience entries
        work_entries: list[WorkExperience] = []
        for item in response.get("work_experience", []):
            try:
                entry = WorkExperience(
                    title=item.get("title", ""),
                    company=item.get("company", ""),
                    start_date=item.get("start_date"),
                    end_date=item.get("end_date"),
                    description=item.get("description", ""),
                    achievements=item.get("achievements", []),
                    is_current=item.get("is_current", False),
                )
                work_entries.append(entry)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning("Failed to parse work entry: %s - %s", item, e)

        # Parse gaps
        gaps: list[TimelineGap] = []
        for item in response.get("gaps", []):
            try:
                gap = TimelineGap(
                    start_date=item.get("start_date", ""),
                    end_date=item.get("end_date", ""),
                    duration_months=item.get("duration_months", 0),
                    description=item.get("description"),
                )
                gaps.append(gap)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning("Failed to parse gap: %s - %s", item, e)

        # Build evaluation
        evaluation = ExperienceEvaluation(
            total_years=float(response.get("total_years", 0)),
            total_roles=len(work_entries),
            gaps=gaps,
            quality_score=float(response.get("quality_score", 0)),
            relevance_score=float(response.get("relevance_score", 50)),
            has_quantified_achievements=response.get("has_quantified_achievements", False),
            experience_level=response.get("experience_level", "Entry"),
        )

        # Build summary
        summary = ExperienceSummary(
            evaluation=evaluation,
            top_achievements=response.get("top_achievements", []),
            industry_sectors=response.get("industry_sectors", []),
            career_progression=response.get("career_progression", ""),
        )

        return summary