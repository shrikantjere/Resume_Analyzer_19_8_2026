"""
Resume scoring service.

Computes resume scores based on completeness, keyword density,
formatting, and skill relevance. Pure computation, no AI calls.
"""

from __future__ import annotations

from typing import Optional

from core.logging_config import get_logger
from models.analysis import ResumeScore, SectionScore
from models.experience import ExperienceEvaluation
from models.skills import SkillInventory

logger = get_logger(__name__)

# Scoring weights
WEIGHTS = {
    "skills": 0.30,
    "experience": 0.30,
    "education": 0.20,
    "projects": 0.20,
}


class ScoringService:
    """Service for computing resume scores.

    Uses a weighted algorithm to evaluate resume completeness,
    skill relevance, experience quality, and formatting.
    Pure computation with no external dependencies.
    """

    def __init__(self) -> None:
        """Initialize the scoring service."""
        self.skill_minimum = 3  # Minimum skills for full score
        self.experience_minimum = 1.0  # Minimum years for full experience score

    def calculate(
        self,
        skill_inventory: SkillInventory,
        experience_evaluation: ExperienceEvaluation,
        education_count: int = 0,
        project_count: int = 0,
        has_summary: bool = False,
        resume_text_length: int = 0,
    ) -> ResumeScore:
        """Calculate the overall resume score.

        Args:
            skill_inventory: Extracted skills inventory.
            experience_evaluation: Evaluated work experience.
            education_count: Number of education entries.
            project_count: Number of project entries.
            has_summary: Whether a professional summary exists.
            resume_text_length: Length of resume text in characters.

        Returns:
            ResumeScore: Overall and section scores.
        """
        logger.info("Calculating resume score")

        # Calculate section scores
        skills_score = self._score_skills(skill_inventory)
        experience_score = self._score_experience(experience_evaluation)
        education_score = self._score_education(education_count)
        projects_score = self._score_projects(project_count)
        ats_score = self._score_ats_optimization(
            skill_inventory, experience_evaluation, resume_text_length
        )
        completeness_score = self._score_completeness(
            skill_inventory,
            experience_evaluation,
            education_count,
            project_count,
            has_summary,
        )
        formatting_score = self._score_formatting(resume_text_length)

        # Build section scores
        section_scores = [
            SectionScore(
                section_name="Skills",
                score=skills_score,
                weight=WEIGHTS["skills"],
                feedback=self._get_skills_feedback(skills_score, skill_inventory),
            ),
            SectionScore(
                section_name="Experience",
                score=experience_score,
                weight=WEIGHTS["experience"],
                feedback=self._get_experience_feedback(
                    experience_score, experience_evaluation
                ),
            ),
            SectionScore(
                section_name="Education",
                score=education_score,
                weight=WEIGHTS["education"],
                feedback=self._get_education_feedback(education_count),
            ),
            SectionScore(
                section_name="Projects",
                score=projects_score,
                weight=WEIGHTS["projects"],
                feedback=self._get_projects_feedback(project_count),
            ),
        ]

        # Calculate weighted overall score
        overall = (
            skills_score * WEIGHTS["skills"]
            + experience_score * WEIGHTS["experience"]
            + education_score * WEIGHTS["education"]
            + projects_score * WEIGHTS["projects"]
        )

        # Apply ATS bonus (max +5 points)
        ats_bonus = (ats_score / 100.0) * 5
        overall = min(100.0, overall + ats_bonus)

        logger.info(
            "Score calculated: overall=%.1f, skills=%.1f, exp=%.1f, edu=%.1f, proj=%.1f",
            overall,
            skills_score,
            experience_score,
            education_score,
            projects_score,
        )

        return ResumeScore(
            overall=round(overall, 1),
            section_scores=section_scores,
            ats_optimization_score=round(ats_score, 1),
            completeness_score=round(completeness_score, 1),
            formatting_score=round(formatting_score, 1),
        )

    # ── Section Scoring ────────────────────────────────────────────────

    def _score_skills(self, inventory: SkillInventory) -> float:
        """Score the skills section.

        Args:
            inventory: Skill inventory.

        Returns:
            float: Score 0-100.
        """
        count = inventory.total_count
        if count == 0:
            return 0.0
        score = min(100.0, (count / self.skill_minimum) * 100.0)

        # Bonus for having both technical and soft skills
        if inventory.technical_skills and inventory.soft_skills:
            score = min(100.0, score + 10)

        # Bonus for skill diversity (multiple categories)
        category_count = len(inventory.by_category)
        if category_count >= 4:
            score = min(100.0, score + 5)

        return score

    def _score_experience(self, evaluation: ExperienceEvaluation) -> float:
        """Score the experience section.

        Args:
            evaluation: Experience evaluation.

        Returns:
            float: Score 0-100.
        """
        if evaluation.total_years <= 0:
            return 0.0

        # Base score from years
        years_score = min(100.0, (evaluation.total_years / self.experience_minimum) * 100.0)

        # Quality bonus
        quality_bonus = evaluation.quality_score * 0.2

        # Quantified achievements bonus
        quantified_bonus = 10.0 if evaluation.has_quantified_achievements else 0.0

        score = years_score + quality_bonus + quantified_bonus
        return min(100.0, score)

    def _score_education(self, count: int) -> float:
        """Score the education section.

        Args:
            count: Number of education entries.

        Returns:
            float: Score 0-100.
        """
        if count == 0:
            return 0.0
        if count >= 1:
            return 80.0
        if count >= 2:
            return 100.0
        return 50.0

    def _score_projects(self, count: int) -> float:
        """Score the projects section.

        Args:
            count: Number of project entries.

        Returns:
            float: Score 0-100.
        """
        if count == 0:
            return 0.0
        if count >= 3:
            return 100.0
        if count >= 2:
            return 80.0
        return 50.0

    def _score_ats_optimization(
        self,
        inventory: SkillInventory,
        evaluation: ExperienceEvaluation,
        text_length: int,
    ) -> float:
        """Score ATS keyword optimization.

        Args:
            inventory: Skill inventory.
            evaluation: Experience evaluation.
            text_length: Resume text length.

        Returns:
            float: Score 0-100.
        """
        score = 50.0  # Base score

        # Skills presence
        if inventory.total_count >= 10:
            score += 15
        elif inventory.total_count >= 5:
            score += 10

        # Quantified achievements
        if evaluation.has_quantified_achievements:
            score += 15

        # Experience level mentioned
        if evaluation.experience_level != "Entry":
            score += 10

        # Adequate text length
        if 500 <= text_length <= 5000:
            score += 10

        return min(100.0, score)

    def _score_completeness(
        self,
        inventory: SkillInventory,
        evaluation: ExperienceEvaluation,
        education_count: int,
        project_count: int,
        has_summary: bool,
    ) -> float:
        """Score resume completeness.

        Args:
            inventory: Skill inventory.
            evaluation: Experience evaluation.
            education_count: Number of education entries.
            project_count: Number of project entries.
            has_summary: Whether a summary exists.

        Returns:
            float: Score 0-100.
        """
        checks = 0
        total = 5  # Number of completeness checks

        if inventory.total_count > 0:
            checks += 1
        if evaluation.total_years > 0 or evaluation.total_roles > 0:
            checks += 1
        if education_count > 0:
            checks += 1
        if project_count > 0:
            checks += 1
        if has_summary:
            checks += 1

        return (checks / total) * 100.0

    def _score_formatting(self, text_length: int) -> float:
        """Score resume formatting.

        Args:
            text_length: Resume text length.

        Returns:
            float: Score 0-100.
        """
        if text_length < 200:
            return 20.0  # Too short
        if text_length < 500:
            return 50.0  # Short
        if text_length > 8000:
            return 60.0  # Too long
        if 2000 <= text_length <= 5000:
            return 100.0  # Ideal length
        return 80.0  # Good length

    # ── Feedback Generation ────────────────────────────────────────────

    def _get_skills_feedback(self, score: float, inventory: SkillInventory) -> str:
        """Generate feedback for the skills section.

        Args:
            score: Skills section score.
            inventory: Skill inventory.

        Returns:
            str: Feedback message.
        """
        if score >= 90:
            return "Excellent skill coverage! Strong mix of technical and soft skills."
        if score >= 70:
            return "Good skill coverage. Consider adding more domain-specific skills."
        if inventory.soft_skills and not inventory.technical_skills:
            return "Good soft skills. Add more technical skills to strengthen your resume."
        if inventory.technical_skills and not inventory.soft_skills:
            return "Good technical skills. Adding soft skills would strengthen your profile."
        return "Consider adding more skills, especially those relevant to your target roles."

    def _get_experience_feedback(
        self, score: float, evaluation: ExperienceEvaluation
    ) -> str:
        """Generate feedback for the experience section.

        Args:
            score: Experience section score.
            evaluation: Experience evaluation.

        Returns:
            str: Feedback message.
        """
        if score >= 90:
            return "Strong experience section with quantified achievements."
        if score >= 70:
            return "Good experience. Try to quantify achievements with metrics."
        if not evaluation.has_quantified_achievements:
            return "Add measurable achievements (e.g., 'Increased sales by 30%')."
        return "Consider adding more detail to your work experience entries."

    def _get_education_feedback(self, count: int) -> str:
        """Generate feedback for the education section.

        Args:
            count: Number of education entries.

        Returns:
            str: Feedback message.
        """
        if count >= 2:
            return "Good education section with multiple qualifications."
        if count == 1:
            return "Education section present. Consider adding relevant coursework."
        return "Education section is missing. Add your educational background."

    def _get_projects_feedback(self, count: int) -> str:
        """Generate feedback for the projects section.

        Args:
            count: Number of project entries.

        Returns:
            str: Feedback message.
        """
        if count >= 3:
            return "Strong project portfolio demonstrating practical skills."
        if count >= 1:
            return "Projects present. Consider adding more with tech stack details."
        return "Projects section is missing. Add personal or academic projects."