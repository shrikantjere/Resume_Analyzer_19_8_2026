"""Unit tests for the improvement suggestion service."""

import pytest
from unittest.mock import MagicMock
from services.improvement_service import ImprovementService


class TestImprovementService:
    """Test suite for the ImprovementService."""

    def test_fallback_suggestions(self) -> None:
        """Test that fallback suggestions are provided when AI fails."""
        suggestions = ImprovementService._get_fallback_suggestions()
        assert len(suggestions) >= 5
        assert all("section" in s for s in suggestions)
        assert all("suggestion" in s for s in suggestions)
        assert all("priority" in s for s in suggestions)

    def test_fallback_has_high_priority(self) -> None:
        """Test that fallback includes high-priority suggestions."""
        suggestions = ImprovementService._get_fallback_suggestions()
        priorities = [s["priority"] for s in suggestions]
        assert "High" in priorities

    def test_generate_with_mock_ai(self) -> None:
        """Test improvement generation with mocked AI client."""
        mock_client = MagicMock()
        mock_client.chat_complete_json.return_value = {
            "improvements": [
                {
                    "section": "Experience",
                    "suggestion": "Add quantified achievements.",
                    "priority": "High",
                    "example": "Before: Did work. After: Improved by 40%.",
                },
                {
                    "section": "Skills",
                    "suggestion": "Add more relevant skills.",
                    "priority": "Medium",
                    "example": "Add cloud computing skills.",
                },
            ]
        }

        service = ImprovementService(ai_client=mock_client)
        improvements = service.generate(
            resume_text="Test resume with some content.",
            skills=["Python", "SQL"],
            correlation_id="test-123",
        )

        assert len(improvements) == 2
        assert improvements[0]["priority"] == "High"  # Sorted by priority
        assert improvements[0]["section"] == "Experience"

    def test_generate_empty_response(self) -> None:
        """Test fallback when AI returns empty response."""
        mock_client = MagicMock()
        mock_client.chat_complete_json.return_value = {"improvements": []}

        service = ImprovementService(ai_client=mock_client)
        improvements = service.generate(
            resume_text="Test resume.",
            correlation_id="test-123",
        )

        assert len(improvements) >= 5  # Should use fallback