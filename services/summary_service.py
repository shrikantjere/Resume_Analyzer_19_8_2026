"""
Summary generation service.

Generates professional resume summaries using OpenAI GPT-4o.
Supports multiple tones and regeneration.
"""

from __future__ import annotations

from typing import Optional

from core.ai_client import AIClient
from core.exceptions import AIServiceError, SummaryGenerationError
from core.logging_config import get_logger, PerformanceLogger

logger = get_logger(__name__)

# System prompt for summary generation
SUMMARY_PROMPT = """You are a professional resume writer and career coach.
Generate a concise, impactful professional summary (3-5 sentences) based on the resume content.

The summary should:
1. Highlight the candidate's key skills and expertise
2. Mention years of experience and industry background
3. Showcase notable achievements
4. Indicate career level and career goals
5. Be written in a professional, confident tone
6. Be optimized for ATS systems (include relevant keywords)

Return a JSON object with this structure:
{
  "summary": "Experienced software engineer with 5+ years...",
  "tone": "professional",
  "key_highlights": ["5+ years experience", "Python expertise", "Team leadership"]
}

Do not use first-person ("I"). Use third-person implied or start with skills."""


class SummaryService:
    """Service for generating professional resume summaries.

    Uses OpenAI GPT-4o to create concise, impactful summaries
    tailored to the candidate's profile.
    """

    def __init__(self, ai_client: Optional[AIClient] = None) -> None:
        """Initialize the summary service.

        Args:
            ai_client: Optional AI client instance. Creates one if not provided.
        """
        self.ai_client = ai_client or AIClient()

    def generate(
        self,
        resume_text: str,
        skills: Optional[list[str]] = None,
        experience_years: Optional[float] = None,
        correlation_id: Optional[str] = None,
    ) -> str:
        """Generate a professional summary for the resume.

        Args:
            resume_text: The full resume text.
            skills: Optional list of extracted skills for context.
            experience_years: Optional years of experience for context.
            correlation_id: Optional trace ID for request correlation.

        Returns:
            str: Generated professional summary (3-5 sentences).

        Raises:
            SummaryGenerationError: If summary generation fails.
        """
        logger.info(
            "Generating professional summary",
            extra={"correlation_id": correlation_id},
        )

        # Build context-rich prompt
        context_parts = [f"Resume:\n{resume_text}"]
        if skills:
            context_parts.append(f"\nKey skills: {', '.join(skills[:10])}")
        if experience_years is not None:
            context_parts.append(f"\nTotal experience: {experience_years:.0f} years")

        user_prompt = "\n".join(context_parts)

        with PerformanceLogger(
            logger, "summary_generation", correlation_id=correlation_id
        ) as perf:
            try:
                response = self.ai_client.chat_complete_json(
                    system_prompt=SUMMARY_PROMPT,
                    user_prompt=user_prompt,
                    correlation_id=correlation_id,
                )
            except AIServiceError as e:
                raise SummaryGenerationError(
                    f"Failed to generate summary: {e}",
                    correlation_id=correlation_id,
                ) from e

        summary = response.get("summary", "")

        if not summary:
            raise SummaryGenerationError(
                "Generated summary was empty.",
                correlation_id=correlation_id,
            )

        logger.info(
            "Summary generated successfully (%d chars)",
            len(summary),
            extra={"correlation_id": correlation_id},
        )

        return summary

    def regenerate(
        self,
        resume_text: str,
        previous_summary: str,
        skills: Optional[list[str]] = None,
        correlation_id: Optional[str] = None,
    ) -> str:
        """Regenerate the summary with a different variation.

        Args:
            resume_text: The full resume text.
            previous_summary: The previously generated summary.
            skills: Optional list of extracted skills.
            correlation_id: Optional trace ID.

        Returns:
            str: New variation of the professional summary.
        """
        prompt = (
            f"Generate a DIFFERENT professional summary than this one:\n"
            f"Previous summary: {previous_summary}\n\n"
            f"Resume:\n{resume_text}"
        )
        if skills:
            prompt += f"\nKey skills: {', '.join(skills[:10])}"

        return self.generate(
            resume_text=prompt,
            skills=skills,
            correlation_id=correlation_id,
        )