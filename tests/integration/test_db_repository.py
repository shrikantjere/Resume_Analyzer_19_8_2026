"""Integration tests for the database repository."""

import pytest
from core.db import DatabaseManager, AnalysisRepository, FeedbackRepository
from core.exceptions import IntegrityError


class TestDatabaseRepository:
    """Test suite for database repository operations."""

    @pytest.fixture
    def repo(self, in_memory_db: DatabaseManager) -> AnalysisRepository:
        return AnalysisRepository(in_memory_db)

    def test_save_and_retrieve_analysis(self, repo: AnalysisRepository) -> None:
        """Test saving and retrieving an analysis."""
        analysis_data = {
            "correlation_id": "test-123",
            "resume_text": "Sample resume text",
            "resume_score": 85.0,
            "skills": {"technical": ["Python"], "soft": ["Communication"]},
            "experience": {"total_years": 5},
            "summary": "Good summary",
            "job_recommendations": [],
            "missing_skills": [],
            "improvements": [],
        }

        # Save
        analysis_id = repo.save_analysis(analysis_data)
        assert analysis_id is not None
        assert analysis_id > 0

        # Retrieve
        retrieved = repo.get_analysis_by_id(analysis_id)
        assert retrieved is not None
        assert retrieved["resume_score"] == 85.0
        assert retrieved["correlation_id"] == "test-123"

    def test_get_nonexistent_analysis(self, repo: AnalysisRepository) -> None:
        """Test retrieving a non-existent analysis."""
        result = repo.get_analysis_by_id(99999)
        assert result is None

    def test_get_analyses_by_session(self, repo: AnalysisRepository) -> None:
        """Test retrieving analyses by session."""
        # Save two analyses
        for i in range(2):
            repo.save_analysis({
                "correlation_id": f"session-1-{i}",
                "resume_text": f"Resume {i}",
                "resume_score": 80.0 + i,
                "skills": {},
                "experience": {},
                "summary": "",
                "job_recommendations": [],
                "missing_skills": [],
                "improvements": [],
            })

        # Save a different session
        repo.save_analysis({
            "correlation_id": "session-2-0",
            "resume_text": "Other resume",
            "resume_score": 90.0,
            "skills": {},
            "experience": {},
            "summary": "",
            "job_recommendations": [],
            "missing_skills": [],
            "improvements": [],
        })

        # Query session 1
        results = repo.get_analyses_by_session("session-1")
        assert len(results) == 2


class TestFeedbackRepository:
    """Test suite for feedback repository."""

    @pytest.fixture
    def repo(self, in_memory_db: DatabaseManager) -> FeedbackRepository:
        return FeedbackRepository(in_memory_db)

    def test_save_feedback(self, in_memory_db: DatabaseManager) -> None:
        """Test saving user feedback."""
        # First save an analysis so the FK constraint is satisfied
        analysis_repo = AnalysisRepository(in_memory_db)
        analysis_id = analysis_repo.save_analysis({
            "correlation_id": "test-fb-1",
            "resume_text": "Test",
            "resume_score": 80.0,
            "skills": {},
            "experience": {},
            "summary": "",
            "job_recommendations": [],
            "missing_skills": [],
            "improvements": [],
        })

        feedback_repo = FeedbackRepository(in_memory_db)
        feedback_id = feedback_repo.save_feedback({
            "analysis_id": analysis_id,
            "rating": 5,
            "comment": "Great analysis!",
        })
        assert feedback_id is not None
        assert feedback_id > 0