"""Unit tests for domain models."""

import pytest
from pydantic import ValidationError
from models.skills import Skill, SkillCategory, SkillProficiency, SkillInventory
from models.experience import ExperienceEvaluation, TimelineGap, WorkExperience
from models.analysis import AnalysisResult, ResumeScore, SectionScore
from models.job import JobRole, JobRecommendation, MissingSkill, JobFilter
from models.resume import Resume, ParsedResume, Education, Project


class TestSkillModels:
    """Test suite for skill domain models."""

    def test_skill_creation(self) -> None:
        skill = Skill(name="Python", category=SkillCategory.PROGRAMMING)
        assert skill.name == "Python"
        assert skill.category == SkillCategory.PROGRAMMING
        assert skill.proficiency == SkillProficiency.UNKNOWN
        assert skill.is_technical is True

    def test_skill_normalized_name(self) -> None:
        skill = Skill(name="Machine Learning")
        assert skill.normalized_name == "machine learning"

    def test_skill_inventory_empty(self) -> None:
        inv = SkillInventory()
        assert inv.total_count == 0
        assert inv.all_skills == []
        assert inv.skill_names == set()

    def test_skill_inventory_with_skills(self) -> None:
        inv = SkillInventory(
            technical_skills=[Skill(name="Python")],
            soft_skills=[Skill(name="Communication", is_technical=False)],
        )
        assert inv.total_count == 2
        assert len(inv.technical_skills) == 1
        assert len(inv.soft_skills) == 1


class TestExperienceModels:
    """Test suite for experience domain models."""

    def test_experience_evaluation_defaults(self) -> None:
        eval = ExperienceEvaluation()
        assert eval.total_years == 0.0
        assert eval.total_roles == 0
        assert eval.quality_score == 0.0
        assert eval.experience_level == "Entry"

    def test_timeline_gap_creation(self) -> None:
        gap = TimelineGap(
            start_date="2023-01",
            end_date="2023-06",
            duration_months=5,
            description="Career transition",
        )
        assert gap.duration_months == 5
        assert gap.description == "Career transition"

    def test_work_experience_quantified_check(self) -> None:
        exp = WorkExperience(
            title="Engineer",
            company="Tech Corp",
            achievements=["Increased sales by 30%"],
        )
        assert exp.has_quantified_achievements is True

        exp2 = WorkExperience(
            title="Engineer",
            company="Tech Corp",
            description="Did some work",
        )
        assert exp2.has_quantified_achievements is False


class TestAnalysisModels:
    """Test suite for analysis domain models."""

    def test_analysis_result_defaults(self) -> None:
        result = AnalysisResult(correlation_id="test-123")
        assert result.correlation_id == "test-123"
        assert result.overall_score == 0.0
        assert result.technical_skills == []
        assert result.soft_skills == []

    def test_analysis_result_with_data(self, sample_analysis_result: AnalysisResult) -> None:
        assert sample_analysis_result.overall_score == 82.5
        assert len(sample_analysis_result.technical_skills) == 8
        assert len(sample_analysis_result.soft_skills) == 3
        assert sample_analysis_result.total_experience_years == 5.5
        assert sample_analysis_result.experience_level == "Senior"

    def test_section_score_percentage(self) -> None:
        score = SectionScore(section_name="Test", score=75.0, weight=0.5)
        assert score.percentage == 75.0
        assert score.score == 75.0

    def test_resume_score_section_map(self) -> None:
        score = ResumeScore(
            overall=85.0,
            section_scores=[
                SectionScore(section_name="Skills", score=90.0, weight=0.3),
                SectionScore(section_name="Experience", score=80.0, weight=0.3),
            ],
        )
        assert score.section_map["Skills"] == 90.0
        assert score.section_map["Experience"] == 80.0


class TestJobModels:
    """Test suite for job domain models."""

    def test_job_role_creation(self) -> None:
        role = JobRole(
            title="Software Engineer",
            required_skills=["Python", "Java"],
        )
        assert role.title == "Software Engineer"
        assert len(role.required_skills) == 2

    def test_job_recommendation_creation(self) -> None:
        rec = JobRecommendation(
            title="Data Scientist",
            match_percentage=85.0,
            required_skills=["Python", "ML"],
            matched_skills=["Python"],
            missing_skills=["ML"],
        )
        assert rec.match_percentage == 85.0
        assert "ML" in rec.missing_skills

    def test_job_filter_defaults(self) -> None:
        filter = JobFilter()
        assert filter.min_match_percentage == 30.0
        assert filter.max_results == 10
        assert filter.remote_only is False


class TestResumeModels:
    """Test suite for resume domain models."""

    def test_resume_validation(self) -> None:
        with pytest.raises(ValidationError):
            Resume(raw_text="")

    def test_resume_valid(self) -> None:
        resume = Resume(raw_text="This is a resume")
        assert resume.raw_text == "This is a resume"
        assert resume.file_type == "text"

    def test_education_is_complete(self) -> None:
        edu = Education(degree="B.S.", institution="MIT")
        assert edu.is_complete is True

        edu2 = Education(degree="", institution="")
        assert edu2.is_complete is False

    def test_project_has_technologies(self) -> None:
        proj = Project(name="Test", technologies=["Python", "Django"])
        assert proj.has_technologies is True

        proj2 = Project(name="Test")
        assert proj2.has_technologies is False