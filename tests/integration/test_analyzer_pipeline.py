"""Integration tests for the full analysis pipeline."""

import pytest
from unittest.mock import MagicMock, patch
from services.analyzer_service import AnalyzerService
from services.parser_service import ParserService
from services.scoring_service import ScoringService
from core.db import DatabaseManager, AnalysisRepository


class TestAnalyzerPipeline:
    """Test suite for the full analysis pipeline."""

    @pytest.fixture
    def mock_ai_client(self) -> MagicMock:
        client = MagicMock()

        # Mock skill extraction
        client.chat_complete_json.side_effect = [
            # Skills extraction response
            {
                "technical_skills": [
                    {"name": "Python", "category": "Programming", "proficiency": "Advanced", "is_technical": True},
                    {"name": "SQL", "category": "Database", "proficiency": "Intermediate", "is_technical": True},
                ],
                "soft_skills": [
                    {"name": "Communication", "category": "Soft_Skill", "proficiency": "Advanced", "is_technical": False},
                ],
            },
            # Experience evaluation response
            {
                "work_experience": [
                    {"title": "Engineer", "company": "Tech Corp", "start_date": "2020-01", "end_date": "2023-06", "description": "Built software", "achievements": ["Improved performance"], "is_current": False},
                ],
                "total_years": 3.5,
                "quality_score": 70.0,
                "has_quantified_achievements": True,
                "experience_level": "Mid",
                "gaps": [],
                "top_achievements": ["Improved performance"],
                "industry_sectors": ["Technology"],
                "career_progression": "Steady growth",
            },
            # Summary generation response
            {"summary": "Experienced software engineer with 3+ years..."},
            # Job recommendations response
            {
                "recommendations": [
                    {"title": "Software Engineer", "industry": "Technology", "required_skills": ["Python", "SQL"], "match_percentage": 85, "experience_level": "Mid", "description": "Build software.", "missing_skills": []},
                ],
            },
            # Improvement suggestions response
            {
                "improvements": [
                    {"section": "Experience", "suggestion": "Add more achievements.", "priority": "High", "example": "Example text"},
                ],
            },
        ]

        client.generate_correlation_id.return_value = "test-pipeline-123"
        client.total_tokens_used = 500
        return client

    @pytest.fixture
    def analyzer(self, mock_ai_client: MagicMock, in_memory_db: DatabaseManager) -> AnalyzerService:
        return AnalyzerService(
            ai_client=mock_ai_client,
            parser=ParserService(),
            scorer=ScoringService(),
            db=in_memory_db,
        )

    def test_full_analysis_pipeline(
        self,
        analyzer: AnalyzerService,
        sample_resume_text: str,
    ) -> None:
        """Test the full analysis pipeline from text to result."""
        result = analyzer.analyze_text(
            resume_text=sample_resume_text,
            session_id="test-session",
        )

        # Verify all pipeline stages completed
        assert result.correlation_id == "test-pipeline-123"
        assert len(result.technical_skills) >= 2
        assert len(result.soft_skills) >= 1
        assert result.total_experience_years > 0
        assert result.overall_score > 0
        assert result.summary != ""
        assert result.improvements is not None

    def test_analysis_with_short_resume(
        self,
        analyzer: AnalyzerService,
        sample_short_resume_text: str,
    ) -> None:
        """Test analysis with a minimal resume."""
        result = analyzer.analyze_text(
            resume_text=sample_short_resume_text,
            session_id="test-session",
        )

        # Should still complete but with lower scores
        assert result.correlation_id is not None
        assert result.overall_score >= 0