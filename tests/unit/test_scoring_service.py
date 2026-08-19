"""Unit tests for the scoring service."""

import pytest
from services.scoring_service import ScoringService
from models.skills import SkillInventory, Skill, SkillCategory, SkillProficiency
from models.experience import ExperienceEvaluation


class TestScoringService:
    """Test suite for the ScoringService."""

    @pytest.fixture
    def scorer(self) -> ScoringService:
        return ScoringService()

    def test_perfect_resume_returns_high_score(
        self, scorer: ScoringService, sample_skill_inventory: SkillInventory,
        sample_experience_evaluation: ExperienceEvaluation,
    ) -> None:
        """Test that a well-rounded resume gets a high score."""
        score = scorer.calculate(
            skill_inventory=sample_skill_inventory,
            experience_evaluation=sample_experience_evaluation,
            education_count=1,
            project_count=3,
            has_summary=True,
            resume_text_length=2500,
        )

        assert score.overall >= 70.0
        assert score.overall <= 100.0

    def test_empty_resume_returns_low_score(self, scorer: ScoringService) -> None:
        """Test that an empty/minimal resume gets a low score."""
        empty_inventory = SkillInventory()
        empty_experience = ExperienceEvaluation()

        score = scorer.calculate(
            skill_inventory=empty_inventory,
            experience_evaluation=empty_experience,
            education_count=0,
            project_count=0,
            has_summary=False,
            resume_text_length=50,
        )

        assert score.overall < 30.0

    def test_score_always_between_0_and_100(
        self, scorer: ScoringService, sample_skill_inventory: SkillInventory,
    ) -> None:
        """Test that scores are always in valid range."""
        for exp_years in [0, 1, 5, 10, 20]:
            for skill_count in [0, 3, 10, 20]:
                inventory = SkillInventory(
                    technical_skills=[
                        Skill(name="Python", category=SkillCategory.PROGRAMMING)
                    ] * skill_count,
                )
                evaluation = ExperienceEvaluation(total_years=float(exp_years))

                score = scorer.calculate(
                    skill_inventory=inventory,
                    experience_evaluation=evaluation,
                    education_count=1,
                    project_count=1,
                    has_summary=True,
                    resume_text_length=1000,
                )

                assert 0 <= score.overall <= 100

    def test_section_scores_are_present(self, scorer: ScoringService) -> None:
        """Test that all expected section scores are present."""
        score = scorer.calculate(
            skill_inventory=SkillInventory(),
            experience_evaluation=ExperienceEvaluation(),
            education_count=0,
            project_count=0,
            has_summary=False,
            resume_text_length=100,
        )

        section_names = {s.section_name for s in score.section_scores}
        assert "Skills" in section_names
        assert "Experience" in section_names
        assert "Education" in section_names
        assert "Projects" in section_names

    def test_ats_optimization_bonus(self, scorer: ScoringService) -> None:
        """Test that ATS optimization contributes to the score."""
        # With good ATS signals
        good_inventory = SkillInventory(
            technical_skills=[Skill(name="Python", category=SkillCategory.PROGRAMMING)] * 10,
        )
        good_evaluation = ExperienceEvaluation(
            total_years=5.0, has_quantified_achievements=True, experience_level="Senior"
        )

        # With poor ATS signals
        poor_inventory = SkillInventory()
        poor_evaluation = ExperienceEvaluation()

        good_score = scorer.calculate(
            skill_inventory=good_inventory,
            experience_evaluation=good_evaluation,
            education_count=1,
            project_count=1,
            has_summary=True,
            resume_text_length=2000,
        )

        poor_score = scorer.calculate(
            skill_inventory=poor_inventory,
            experience_evaluation=poor_evaluation,
            education_count=0,
            project_count=0,
            has_summary=False,
            resume_text_length=50,
        )

        assert good_score.ats_optimization_score > poor_score.ats_optimization_score