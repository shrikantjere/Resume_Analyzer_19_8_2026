"""
Report generation service.

Generates downloadable analysis reports in PDF and JSON formats.
Uses WeasyPrint for HTML-to-PDF conversion and Jinja2 for templating.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from core.config import get_settings
from core.exceptions import PDFGenerationError, ReportError, ReportNotFoundError
from core.logging_config import get_logger, PerformanceLogger
from core.utils import generate_id
from models.analysis import AnalysisResult
from models.report import AnalysisReport, ReportFormat, ReportMetadata, ReportSection

logger = get_logger(__name__)


class ReportGeneratorService:
    """Service for generating downloadable analysis reports.

    Supports PDF and JSON formats. Uses WeasyPrint for PDF
    conversion and Jinja2 for HTML templating.
    """

    def __init__(self) -> None:
        """Initialize the report generator service."""
        self.settings = get_settings()

    def generate_pdf(
        self,
        analysis: AnalysisResult,
        correlation_id: Optional[str] = None,
    ) -> str:
        """Generate a PDF report from analysis results.

        Args:
            analysis: The completed analysis result.
            correlation_id: Optional trace ID.

        Returns:
            str: File path to the generated PDF.

        Raises:
            PDFGenerationError: If PDF generation fails.
        """
        logger.info(
            "Generating PDF report for analysis %s",
            analysis.correlation_id,
            extra={"correlation_id": correlation_id},
        )

        with PerformanceLogger(
            logger, "pdf_report_generation", correlation_id=correlation_id
        ) as perf:
            report = self._build_report(analysis, ReportFormat.PDF)
            html = report.to_html()

            try:
                from weasyprint import HTML
            except ImportError:
                raise PDFGenerationError(
                    "PDF generation support not installed (weasyprint required)."
                )

            # Ensure output directory exists
            output_dir = Path(self.settings.report_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            filename = f"resume_analysis_{report.metadata.report_id}.pdf"
            output_path = output_dir / filename

            try:
                HTML(string=html).write_pdf(str(output_path))
            except Exception as e:
                raise PDFGenerationError(
                    f"Failed to generate PDF: {e}",
                    correlation_id=correlation_id,
                ) from e

            report.metadata.file_path = str(output_path)
            report.metadata.file_size_bytes = output_path.stat().st_size

            logger.info(
                "PDF report generated: %s (%d bytes)",
                filename,
                report.metadata.file_size_bytes,
                extra={"correlation_id": correlation_id},
            )

        return str(output_path)

    def generate_json(
        self,
        analysis: AnalysisResult,
        correlation_id: Optional[str] = None,
    ) -> str:
        """Generate a JSON report from analysis results.

        Args:
            analysis: The completed analysis result.
            correlation_id: Optional trace ID.

        Returns:
            str: File path to the generated JSON file.

        Raises:
            ReportError: If JSON generation fails.
        """
        logger.info(
            "Generating JSON report for analysis %s",
            analysis.correlation_id,
            extra={"correlation_id": correlation_id},
        )

        report = self._build_report(analysis, ReportFormat.JSON)

        # Ensure output directory exists
        output_dir = Path(self.settings.report_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        filename = f"resume_analysis_{report.metadata.report_id}.json"
        output_path = output_dir / filename

        try:
            report_data = analysis.to_dict()
            report_data["report_id"] = report.metadata.report_id
            report_data["generated_at"] = report.metadata.created_at.isoformat()

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, default=str)

            report.metadata.file_path = str(output_path)
            report.metadata.file_size_bytes = output_path.stat().st_size

            logger.info(
                "JSON report generated: %s (%d bytes)",
                filename,
                report.metadata.file_size_bytes,
                extra={"correlation_id": correlation_id},
            )

        except (OSError, json.JSONEncodeError) as e:
            raise ReportError(
                f"Failed to generate JSON report: {e}",
                correlation_id=correlation_id,
            ) from e

        return str(output_path)

    def get_report_path(self, report_id: str) -> str:
        """Get the file path for a previously generated report.

        Args:
            report_id: The report identifier.

        Returns:
            str: File path to the report.

        Raises:
            ReportNotFoundError: If the report file is not found.
        """
        report_dir = Path(self.settings.report_path)

        # Check PDF
        pdf_path = report_dir / f"resume_analysis_{report_id}.pdf"
        if pdf_path.exists():
            return str(pdf_path)

        # Check JSON
        json_path = report_dir / f"resume_analysis_{report_id}.json"
        if json_path.exists():
            return str(json_path)

        raise ReportNotFoundError(report_id=report_id)

    def cleanup_old_reports(self, max_age_hours: int = 24) -> int:
        """Clean up report files older than the specified age.

        Args:
            max_age_hours: Maximum age in hours before deletion.

        Returns:
            int: Number of files deleted.
        """
        import time

        report_dir = Path(self.settings.report_path)
        if not report_dir.exists():
            return 0

        cutoff = time.time() - (max_age_hours * 3600)
        deleted = 0

        for file_path in report_dir.glob("resume_analysis_*"):
            if file_path.stat().st_mtime < cutoff:
                file_path.unlink()
                deleted += 1

        if deleted:
            logger.info("Cleaned up %d old report files", deleted)

        return deleted

    # ── Internal Builders ──────────────────────────────────────────────

    def _build_report(
        self,
        analysis: AnalysisResult,
        fmt: ReportFormat,
    ) -> AnalysisReport:
        """Build an AnalysisReport from analysis results.

        Args:
            analysis: The completed analysis result.
            fmt: Target report format.

        Returns:
            AnalysisReport: Populated report ready for export.
        """
        report_id = generate_id()

        report = AnalysisReport(
            metadata=ReportMetadata(
                report_id=report_id,
                analysis_id=analysis.id or 0,
                created_at=datetime.now(),
                format=fmt,
            ),
            candidate_name=analysis.parsed_resume.get("name", "Candidate")
            if analysis.parsed_resume else "Candidate",
            overall_score=analysis.overall_score,
            summary=analysis.summary,
        )

        # Add sections
        self._add_score_section(report, analysis)
        self._add_skills_section(report, analysis)
        self._add_experience_section(report, analysis)
        self._add_recommendations_section(report, analysis)
        self._add_missing_skills_section(report, analysis)
        self._add_improvements_section(report, analysis)

        return report

    def _add_score_section(self, report: AnalysisReport, analysis: AnalysisResult) -> None:
        """Add score section to the report.

        Args:
            report: The report being built.
            analysis: The analysis result.
        """
        score = analysis.resume_score
        sections_html = "<ul>"
        for s in score.section_scores:
            sections_html += f"<li><strong>{s.section_name}:</strong> {s.score:.0f}/100</li>"
        sections_html += "</ul>"

        content = (
            f"<p><strong>Overall Score:</strong> {score.overall:.0f}/100</p>"
            f"<p><strong>ATS Optimization:</strong> {score.ats_optimization_score:.0f}/100</p>"
            f"<p><strong>Completeness:</strong> {score.completeness_score:.0f}/100</p>"
            f"<p><strong>Formatting:</strong> {score.formatting_score:.0f}/100</p>"
            f"{sections_html}"
        )

        report.add_section("Resume Score", content, icon="📊")

    def _add_skills_section(self, report: AnalysisReport, analysis: AnalysisResult) -> None:
        """Add skills section to the report.

        Args:
            report: The report being built.
            analysis: The analysis result.
        """
        tech_skills = ", ".join(analysis.technical_skill_names) or "None detected"
        soft_skills = ", ".join(analysis.soft_skill_names) or "None detected"

        content = (
            f"<p><strong>Technical Skills:</strong> {tech_skills}</p>"
            f"<p><strong>Soft Skills:</strong> {soft_skills}</p>"
            f"<p><strong>Total Skills:</strong> {analysis.skill_inventory.total_count}</p>"
        )

        report.add_section("Skills Inventory", content, icon="🎯")

    def _add_experience_section(
        self, report: AnalysisReport, analysis: AnalysisResult
    ) -> None:
        """Add experience section to the report.

        Args:
            report: The report being built.
            analysis: The analysis result.
        """
        exp = analysis.experience_evaluation
        content = (
            f"<p><strong>Total Experience:</strong> {exp.total_years:.1f} years</p>"
            f"<p><strong>Experience Level:</strong> {exp.experience_level}</p>"
            f"<p><strong>Quality Score:</strong> {exp.quality_score:.0f}/100</p>"
            f"<p><strong>Quantified Achievements:</strong> "
            f"{'Yes' if exp.has_quantified_achievements else 'No'}</p>"
        )

        if exp.gaps:
            content += "<p><strong>Timeline Gaps:</strong></p><ul>"
            for gap in exp.gaps:
                content += (
                    f"<li>{gap.start_date} to {gap.end_date} "
                    f"({gap.duration_months} months)</li>"
                )
            content += "</ul>"

        report.add_section("Experience Assessment", content, icon="💼")

    def _add_recommendations_section(
        self, report: AnalysisReport, analysis: AnalysisResult
    ) -> None:
        """Add job recommendations section to the report.

        Args:
            report: The report being built.
            analysis: The analysis result.
        """
        if not analysis.job_recommendations:
            report.add_section(
                "Job Recommendations",
                "<p>No job recommendations available.</p>",
                icon="💡",
            )
            return

        content = "<ol>"
        for rec in analysis.job_recommendations[:5]:
            content += (
                f"<li><strong>{rec.get('title', 'Role')}</strong> - "
                f"Match: {rec.get('match_percentage', 0):.0f}%<br>"
                f"<em>{rec.get('description', '')[:100]}...</em></li>"
            )
        content += "</ol>"

        report.add_section("Job Recommendations", content, icon="💡")

    def _add_missing_skills_section(
        self, report: AnalysisReport, analysis: AnalysisResult
    ) -> None:
        """Add missing skills section to the report.

        Args:
            report: The report being built.
            analysis: The analysis result.
        """
        if not analysis.missing_skills:
            report.add_section(
                "Missing Skills",
                "<p>No critical missing skills identified.</p>",
                icon="📚",
            )
            return

        content = "<ul>"
        for skill in analysis.missing_skills[:5]:
            content += (
                f"<li><strong>{skill.get('skill_name', '')}</strong> - "
                f"Relevance: {skill.get('relevance_score', 0):.0%} - "
                f"Demand: {skill.get('demand_level', 'Medium')}</li>"
            )
        content += "</ul>"

        report.add_section("Missing Skills", content, icon="📚")

    def _add_improvements_section(
        self, report: AnalysisReport, analysis: AnalysisResult
    ) -> None:
        """Add improvement suggestions section to the report.

        Args:
            report: The report being built.
            analysis: The analysis result.
        """
        if not analysis.improvements:
            report.add_section(
                "Improvement Suggestions",
                "<p>No improvement suggestions available.</p>",
                icon="✨",
            )
            return

        content = "<ul>"
        for imp in analysis.improvements[:5]:
            priority = imp.get("priority", "Medium")
            badge = f"<strong>[{priority}]</strong>"
            content += (
                f"<li>{badge} <strong>{imp.get('section', 'General')}:</strong> "
                f"{imp.get('suggestion', '')}</li>"
            )
        content += "</ul>"

        report.add_section("Improvement Suggestions", content, icon="✨")