"""Unit tests for the missing skills identification service."""

import pytest
from services.missing_skills_service import MissingSkillsService
from models.job import JobRecommendation, MissingSkill
from models.skills import SkillInventory, Skill, SkillCategory, SkillProficiency


class TestMissingSkillsService:
    """Test suite for the MissingSkillsService."""

    @pytest.fixture
    def service(self) -> MissingSkillsService:
        return MissingSkillsService()

    @pytest.fixture
    def sample_recommendations(self) -> list[JobRecommendation]:
        return [
            JobRecommendation(
                title="Software Engineer",
                match_percentage=85.0,
                required_skills=["Python", "Java", "SQL", "Docker"],
                matched_skills=["Python", "SQL"],
                missing_skills=["Java", "Docker"],
                experience_level="Mid",
                industry="Technology",
                description="Build software.",
            ),
            JobRecommendation(
                title="Data Scientist",
                match_percentage=60.0,
                required_skills=["Python", "SQL", "Machine Learning", "Statistics"],
                matched_skills=["Python", "SQL"],
                missing_skills=["Machine Learning", "Statistics"],
                experience_level="Mid",
                industry="Technology",
                description="Analyze data.",
            ),
        ]

    @pytest.fixture
    def sample_inventory(self) -> SkillInventory:
        return SkillInventory(
            technical_skills=[
                Skill(name="Python", category=SkillCategory.PROGRAMMING),
                Skill(name="SQL", category=SkillCategory.DATABASE),
            ],
        )

    def test_identify_missing_skills(
        self,
        service: MissingSkillsService,
        sample_recommendations: list[JobRecommendation],
        sample_inventory: SkillInventory,
    ) -> None:
        """Test that missing skills are correctly identified."""
        missing = service.identify(sample_recommendations, sample_inventory)

        # Java and Docker should be missing
        missing_names = [m.skill_name for m in missing]
        assert "Java" in missing_names
        assert "Docker" in missing_names
        assert "Machine Learning" in missing_names
        assert "Statistics" in missing_names

        # Python and SQL should NOT be in missing (they're in inventory)
        assert "Python" not in missing_names
        assert "SQL" not in missing_names

    def test_missing_skills_ranked_by_relevance(
        self,
        service: MissingSkillsService,
        sample_recommendations: list[JobRecommendation],
        sample_inventory: SkillInventory,
    ) -> None:
        """Test that missing skills are ranked by relevance."""
        missing = service.identify(sample_recommendations, sample_inventory)

        # Should be sorted by relevance descending
        for i in range(len(missing) - 1):
            assert missing[i].relevance_score >= missing[i + 1].relevance_score

    def test_no_missing_skills_when_all_match(
        self,
        service: MissingSkillsService,
        sample_inventory: SkillInventory,
    ) -> None:
        """Test that no missing skills are returned when all match."""
        # Create a recommendation that only requires Python (which is in inventory)
        recs = [
            JobRecommendation(
                title="Python Developer",
                match_percentage=100.0,
                required_skills=["Python"],
                matched_skills=["Python"],
                missing_skills=[],
                experience_level="Mid",
                industry="Technology",
                description="Python dev.",
            )
        ]

        missing = service.identify(recs, sample_inventory)
        assert len(missing) == 0

    def test_empty_recommendations(
        self,
        service: MissingSkillsService,
        sample_inventory: SkillInventory,
    ) -> None:
        """Test handling of empty recommendations."""
        missing = service.identify([], sample_inventory)
        assert missing == []

    def test_generate_learning_suggestions(
        self,
        service: MissingSkillsService,
    ) -> None:
        """Test that learning suggestions are generated."""
        missing = [
            MissingSkill(
                skill_name="Python",
                relevance_score=0.9,
                demand_level="High",
                related_roles=["Software Engineer"],
                category="Technical",
            ),
        ]

        suggestions = service.generate_learning_suggestions(missing)
        assert len(suggestions) == 1
        assert suggestions[0]["skill"] == "Python"
        assert "suggestion" in suggestions[0]
        assert "resource" in suggestions[0]