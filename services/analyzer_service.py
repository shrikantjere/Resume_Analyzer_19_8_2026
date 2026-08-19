"""
Central analysis orchestrator service.

Coordinates the multi-stage analysis pipeline. Acts as a Facade
over all specialized services, exposing a single analyze() method.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from core.ai_client import AIClient
from core.config import get_settings
from core.db import AnalysisRepository, DatabaseManager
from core.exceptions import AnalysisError, ResumeAnalyzerError
from core.logging_config import get_logger, PerformanceLogger
from core.utils import sanitize_text
from models.analysis import AnalysisContext, AnalysisResult

from services.experience_service import ExperienceService
from services.improvement_service import ImprovementService
from services.job_recommendation_service import JobRecommendationService
from services.missing_skills_service import MissingSkillsService
from services.parser_service import ParserService
from services.scoring_service import ScoringService
from services.skill_extraction_service import SkillExtractionService
from services.summary_service import SummaryService

logger = get_logger(__name__)


class AnalyzerService:
    """Central orchestrator for resume analysis.

    Coordinates the multi-stage analysis pipeline:
    Parse → Extract Skills → Evaluate Experience → Score → Summarize → Recommend → Improve

    Acts as a Facade, hiding pipeline complexity from the UI layer.
    """

    def __init__(
        self,
        parser: Optional[ParserService] = None,
        skill_extractor: Optional[SkillExtractionService] = None,
        experience_service: Optional[ExperienceService] = None,
        scorer: Optional[ScoringService] = None,
        summarizer: Optional[SummaryService] = None,
        job_recommender: Optional[JobRecommendationService] = None,
        missing_skills: Optional[MissingSkillsService] = None,
        improver: Optional[ImprovementService] = None,
        ai_client: Optional[AIClient] = None,
        db: Optional[DatabaseManager] = None,
    ) -> None:
        """Initialize the analyzer service with all sub-services.

        All dependencies are injectable for testability.
        If not provided, defaults are created.
        """
        self.ai_client = ai_client or AIClient()
        self.parser = parser or ParserService()
        self.skill_extractor = skill_extractor or SkillExtractionService(self.ai_client)
        self.experience_service = experience_service or ExperienceService(self.ai_client)
        self.scorer = scorer or ScoringService()
        self.summarizer = summarizer or SummaryService(self.ai_client)
        self.job_recommender = job_recommender or JobRecommendationService(self.ai_client)
        self.missing_skills_service = missing_skills or MissingSkillsService()
        self.improver = improver or ImprovementService(self.ai_client)
        self.db = db or DatabaseManager()
        self.settings = get_settings()

    def analyze_text(
        self,
        resume_text: str,
        session_id: str = "default",
    ) -> AnalysisResult:
        """Analyze a resume from pasted text.

        This is the primary entry point for the UI layer.

        Args:
            resume_text: The resume text to analyze.
            session_id: The user's session ID.

        Returns:
            AnalysisResult: Complete analysis results.

        Raises:
            AnalysisError: If any stage of the analysis fails.
        """
        correlation_id = self.ai_client.generate_correlation_id()
        logger.info(
            "Starting text analysis (session=%s)",
            session_id,
            extra={"correlation_id": correlation_id},
        )

        context = AnalysisContext(
            correlation_id=correlation_id,
            session_id=session_id,
        )

        return self._run_pipeline(
            resume_text=sanitize_text(resume_text),
            context=context,
        )

    def analyze_file(
        self,
        file_path: str,
        file_type: Optional[str] = None,
        session_id: str = "default",
    ) -> AnalysisResult:
        """Analyze a resume from an uploaded file.

        Args:
            file_path: Path to the uploaded file.
            file_type: Optional file type override.
            session_id: The user's session ID.

        Returns:
            AnalysisResult: Complete analysis results.

        Raises:
            AnalysisError: If any stage of the analysis fails.
        """
        correlation_id = self.ai_client.generate_correlation_id()
        logger.info(
            "Starting file analysis (file=%s, session=%s)",
            file_path,
            session_id,
            extra={"correlation_id": correlation_id},
        )

        context = AnalysisContext(
            correlation_id=correlation_id,
            session_id=session_id,
        )

        # Extract text from file
        resume_text = self.parser.extract_text(
            file_path=file_path,
            file_type=file_type,
        )

        return self._run_pipeline(
            resume_text=resume_text,
            context=context,
        )

    # ── Pipeline ───────────────────────────────────────────────────────

    def _run_pipeline(
        self,
        resume_text: str,
        context: AnalysisContext,
    ) -> AnalysisResult:
        """Run the full analysis pipeline.

        Pipeline stages:
        1. Parse resume structure
        2. Extract skills
        3. Evaluate experience
        4. Calculate scores
        5. Generate summary
        6. Get job recommendations
        7. Identify missing skills
        8. Generate improvements

        Args:
            resume_text: Sanitized resume text.
            context: Analysis context with correlation ID.

        Returns:
            AnalysisResult: Complete analysis.

        Raises:
            AnalysisError: If pipeline execution fails.
        """
        pipeline_start = time.monotonic()
        correlation_id = context.correlation_id

        logger.info(
            "Pipeline started (correlation_id=%s)",
            correlation_id,
        )

        try:
            # Stage 1: Parse resume structure (basic)
            parsed = {"raw_text_length": len(resume_text)}

            # Stage 2: Extract skills
            with PerformanceLogger(
                logger, "pipeline.skills", correlation_id=correlation_id
            ):
                skill_inventory = self.skill_extractor.extract(
                    resume_text, correlation_id=correlation_id
                )

            # Stage 3: Evaluate experience
            with PerformanceLogger(
                logger, "pipeline.experience", correlation_id=correlation_id
            ):
                experience_summary = self.experience_service.evaluate(
                    resume_text, correlation_id=correlation_id
                )

            # Stage 4: Calculate scores
            with PerformanceLogger(
                logger, "pipeline.scoring", correlation_id=correlation_id
            ):
                resume_score = self.scorer.calculate(
                    skill_inventory=skill_inventory,
                    experience_evaluation=experience_summary.evaluation,
                    education_count=0,  # Would need AI parsing for this
                    project_count=0,    # Would need AI parsing for this
                    has_summary=False,
                    resume_text_length=len(resume_text),
                )

            # Stage 5: Generate summary
            with PerformanceLogger(
                logger, "pipeline.summary", correlation_id=correlation_id
            ):
                summary = self.summarizer.generate(
                    resume_text=resume_text,
                    skills=list(skill_inventory.skill_names),
                    experience_years=experience_summary.evaluation.total_years,
                    correlation_id=correlation_id,
                )

            # Stage 6: Get job recommendations
            with PerformanceLogger(
                logger, "pipeline.recommendations", correlation_id=correlation_id
            ):
                recommendations = self.job_recommender.get_recommendations(
                    skill_inventory=skill_inventory,
                    total_experience_years=experience_summary.evaluation.total_years,
                    experience_level=experience_summary.evaluation.experience_level,
                    correlation_id=correlation_id,
                )

            # Stage 7: Identify missing skills
            with PerformanceLogger(
                logger, "pipeline.missing_skills", correlation_id=correlation_id
            ):
                rec_dicts = [r.model_dump() for r in recommendations]
                missing = self.missing_skills_service.identify(
                    recommendations=recommendations,
                    skill_inventory=skill_inventory,
                )
                learning_suggestions = (
                    self.missing_skills_service.generate_learning_suggestions(missing)
                )

            # Stage 8: Generate improvements
            with PerformanceLogger(
                logger, "pipeline.improvements", correlation_id=correlation_id
            ):
                improvements = self.improver.generate(
                    resume_text=resume_text,
                    skills=list(skill_inventory.skill_names),
                    experience_years=experience_summary.evaluation.total_years,
                    correlation_id=correlation_id,
                )

            # Build result
            total_duration_ms = int((time.monotonic() - pipeline_start) * 1000)
            context.completed_at = None  # Will be set by model
            context.total_duration_ms = total_duration_ms
            context.token_usage = self.ai_client.total_tokens_used

            result = AnalysisResult(
                correlation_id=correlation_id,
                context=context,
                parsed_resume=parsed,
                skill_inventory=skill_inventory,
                experience_evaluation=experience_summary.evaluation,
                resume_score=resume_score,
                summary=summary,
                job_recommendations=[r.model_dump() for r in recommendations],
                missing_skills=[m.model_dump() for m in missing],
                improvements=improvements,
                learning_suggestions=learning_suggestions,
            )

            # Save to database
            try:
                repo = AnalysisRepository(self.db)
                result.id = repo.save_analysis(result.to_dict())
            except Exception as e:
                logger.warning(
                    "Failed to save analysis to database: %s", e,
                    extra={"correlation_id": correlation_id},
                )

            logger.info(
                "Pipeline completed in %dms",
                total_duration_ms,
                extra={"correlation_id": correlation_id},
            )

            return result

        except ResumeAnalyzerError:
            raise
        except Exception as e:
            elapsed = int((time.monotonic() - pipeline_start) * 1000)
            logger.critical(
                "Pipeline failed after %dms: %s",
                elapsed,
                str(e),
                extra={"correlation_id": correlation_id},
                exc_info=True,
            )
            raise AnalysisError(
                f"Analysis failed: {e}",
                correlation_id=correlation_id,
            ) from e