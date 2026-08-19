"""
Improvement suggestion service.

Generates actionable resume improvement suggestions using
OpenAI GPT-4o. Covers ATS optimization, phrasing, formatting,
and section-specific recommendations.
"""

from __future__ import annotations

from typing import Optional

from core.ai_client import AIClient
from core.exceptions import AIServiceError
from core.logging_config import get_logger, PerformanceLogger

logger = get_logger(__name__)

# System prompt for improvement suggestions
IMPROVEMENT_PROMPT = """You are a professional resume writer and ATS optimization expert.
Analyze this resume and provide actionable improvement suggestions.

For each suggestion, provide:
1. The section it applies to (Skills, Experience, Education, Projects, Summary, Formatting, ATS_Optimization)
2. A clear, actionable suggestion
3. Priority (High, Medium, Low)
4. An example of the improvement (before/after if applicable)

Focus on:
- ATS keyword optimization
- Weak phrasing and how to strengthen it
- Missing sections or content gaps
- Formatting improvements
- Quantified achievements
- Action verbs

Return a JSON object with this structure:
{
  "improvements": [
    {
      "section": "Experience",
      "suggestion": "Add quantified achievements to your work experience entries",
      "priority": "High",
      "example": "Before: 'Improved system performance'\nAfter: 'Improved system performance by 40%, reducing load time from 3s to 1.8s'"
    }
  ]
}

Provide 5-10 specific, actionable suggestions. Be constructive and practical."""


class ImprovementService:
    """Service for generating resume improvement suggestions.

    Uses OpenAI GPT-4o to analyze resumes and provide
    actionable, section-specific improvement recommendations.
    """

    def __init__(self, ai_client: Optional[AIClient] = None) -> None:
        """Initialize the improvement service.

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
    ) -> list[dict[str, str]]:
        """Generate improvement suggestions for the resume.

        Args:
            resume_text: The full resume text.
            skills: Optional list of extracted skills for context.
            experience_years: Optional years of experience.
            correlation_id: Optional trace ID.

        Returns:
            list[dict]: List of improvement suggestions, each with
                section, suggestion, priority, and example fields.

        Raises:
            AIServiceError: If the AI service call fails.
        """
        logger.info(
            "Generating improvement suggestions",
            extra={"correlation_id": correlation_id},
        )

        # Build context
        context_parts = [f"Resume:\n{resume_text}"]
        if skills:
            context_parts.append(f"\nDetected skills: {', '.join(skills[:15])}")
        if experience_years is not None:
            context_parts.append(f"\nExperience: {experience_years:.0f} years")

        user_prompt = "\n".join(context_parts)

        with PerformanceLogger(
            logger, "improvement_generation", correlation_id=correlation_id
        ) as perf:
            try:
                response = self.ai_client.chat_complete_json(
                    system_prompt=IMPROVEMENT_PROMPT,
                    user_prompt=user_prompt,
                    correlation_id=correlation_id,
                )
            except AIServiceError as e:
                logger.error(
                    "Failed to generate improvements: %s", e,
                    extra={"correlation_id": correlation_id},
                )
                return self._get_fallback_suggestions()

        improvements = response.get("improvements", [])

        if not improvements:
            logger.info(
                "No improvements generated, using fallback",
                extra={"correlation_id": correlation_id},
            )
            return self._get_fallback_suggestions()

        # Sort by priority
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        improvements.sort(
            key=lambda x: priority_order.get(x.get("priority", "Medium"), 1)
        )

        logger.info(
            "Generated %d improvement suggestions",
            len(improvements),
            extra={"correlation_id": correlation_id},
        )

        return improvements

    @staticmethod
    def _get_fallback_suggestions() -> list[dict[str, str]]:
        """Provide fallback suggestions when AI is unavailable.

        Returns:
            list[dict]: Basic improvement suggestions.
        """
        return [
            {
                "section": "Skills",
                "suggestion": "Add more technical skills relevant to your target roles.",
                "priority": "High",
                "example": "Review job descriptions in your field and add matching keywords.",
            },
            {
                "section": "Experience",
                "suggestion": "Quantify your achievements with specific metrics.",
                "priority": "High",
                "example": "Replace 'Improved efficiency' with 'Improved efficiency by 25%'",
            },
            {
                "section": "Experience",
                "suggestion": "Use strong action verbs to start each bullet point.",
                "priority": "Medium",
                "example": "Use verbs like: Led, Developed, Implemented, Optimized, Designed",
            },
            {
                "section": "ATS_Optimization",
                "suggestion": "Include industry-standard keywords from job descriptions.",
                "priority": "High",
                "example": "Add relevant certifications, tools, and methodologies.",
            },
            {
                "section": "Formatting",
                "suggestion": "Use a clean, consistent format with clear section headers.",
                "priority": "Medium",
                "example": "Ensure consistent font, spacing, and bullet point styles.",
            },
            {
                "section": "Summary",
                "suggestion": "Add a professional summary at the top of your resume.",
                "priority": "Medium",
                "example": "A 2-3 sentence summary highlighting your key qualifications.",
            },
            {
                "section": "Education",
                "suggestion": "Include relevant coursework, projects, and academic achievements.",
                "priority": "Low",
                "example": "List relevant courses, GPA (if > 3.5), and academic honors.",
            },
        ]