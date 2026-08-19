"""Unit tests for the report generator service."""

import pytest
from unittest.mock import patch, MagicMock
from services.report_generator_service import ReportGeneratorService
from models.analysis import AnalysisResult


class TestReportGeneratorService:
    """Test suite for the ReportGeneratorService."""

    @pytest.fixture
    def generator(self) -> ReportGeneratorService:
        return ReportGeneratorService()

    def test_build_report_has_sections(
        self,
        generator: ReportGeneratorService,
        sample_analysis_result: AnalysisResult,
    ) -> None:
        """Test that the report is built with all expected sections."""
        report = generator._build_report(sample_analysis_result, "pdf")

        assert report.metadata.report_id is not None
        assert report.overall_score == 82.5
        assert len(report.sections) >= 4

    def test_report_sections_in_order(
        self,
        generator: ReportGeneratorService,
        sample_analysis_result: AnalysisResult,
    ) -> None:
        """Test that report sections are in correct order."""
        report = generator._build_report(sample_analysis_result, "pdf")

        orders = [s.order for s in report.sections]
        assert orders == sorted(orders)

    def test_report_html_generation(
        self,
        generator: ReportGeneratorService,
        sample_analysis_result: AnalysisResult,
    ) -> None:
        """Test that HTML generation produces valid output."""
        report = generator._build_report(sample_analysis_result, "pdf")
        html = report.to_html()

        assert "<!DOCTYPE html>" in html
        assert "Resume Analysis Report" in html
        assert "82" in html  # Score should be present

    def test_build_json_report(
        self,
        generator: ReportGeneratorService,
        sample_analysis_result: AnalysisResult,
    ) -> None:
        """Test JSON report structure."""
        report = generator._build_report(sample_analysis_result, "json")

        assert report.metadata.format.value == "json"
        # JSON reports should also have sections
        assert len(report.sections) > 0