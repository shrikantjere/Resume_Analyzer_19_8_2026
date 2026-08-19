"""
Pytest configuration and shared fixtures for the AI Resume Analyzer.

Provides test fixtures for configuration, database, AI client,
and sample data used across the test suite.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest

from core.config import Settings
from models.analysis import AnalysisResult, ResumeScore, SectionScore
from models.experience import ExperienceEvaluation
from models.skills import Skill, SkillCategory, SkillInventory, SkillProficiency


# ── Configuration Fixtures ───────────────────────────────────────────────

@pytest.fixture(autouse=True)
def test_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Override settings for all tests with mock values."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-12345")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "10")
    monkeypatch.setenv("JOB_DB_PATH", "data/job_database.json")


# ── Sample Data Fixtures ─────────────────────────────────────────────────

@pytest.fixture
def sample_resume_text() -> str:
    """Provide a sample resume text for testing."""
    return """John Doe
john.doe@email.com | (555) 123-4567 | San Francisco, CA

SUMMARY
Experienced software engineer with 5+ years building scalable web applications.

EXPERIENCE
Senior Software Engineer | Tech Corp | Jan 2020 - Present
- Led development of microservices architecture serving 1M+ users
- Improved API response time by 40% through caching optimization
- Mentored 3 junior developers
- Tech stack: Python, Django, PostgreSQL, AWS, Docker

Software Engineer | Startup Inc | Jun 2017 - Dec 2019
- Built RESTful APIs using Python and Flask
- Implemented CI/CD pipeline reducing deployment time by 60%
- Collaborated on database migration from MySQL to PostgreSQL

EDUCATION
B.S. Computer Science | University of California | 2013 - 2017
- GPA: 3.7/4.0
- Dean's List

SKILLS
Technical: Python, Django, Flask, PostgreSQL, MySQL, AWS, Docker, Git, REST APIs, JavaScript, React, TypeScript, Redis
Soft Skills: Team Leadership, Mentoring, Communication, Problem Solving, Agile

PROJECTS
E-commerce Platform: Built full-stack application using Django and React
Task Manager: Developed REST API with Flask and PostgreSQL

CERTIFICATIONS
AWS Certified Solutions Architect
"""


@pytest.fixture
def sample_short_resume_text() -> str:
    """Provide a short resume for edge case testing."""
    return """Jane Smith
jane@email.com

Skills: Python, Excel

Education: B.A. Business
"""


@pytest.fixture
def sample_skill_inventory() -> SkillInventory:
    """Provide a sample skill inventory."""
    return SkillInventory(
        technical_skills=[
            Skill(name="Python", category=SkillCategory.PROGRAMMING, proficiency=SkillProficiency.ADVANCED),
            Skill(name="SQL", category=SkillCategory.DATABASE, proficiency=SkillProficiency.INTERMEDIATE),
            Skill(name="Django", category=SkillCategory.FRAMEWORK, proficiency=SkillProficiency.ADVANCED),
            Skill(name="AWS", category=SkillCategory.CLOUD, proficiency=SkillProficiency.INTERMEDIATE),
            Skill(name="Docker", category=SkillCategory.DEVOPS, proficiency=SkillProficiency.INTERMEDIATE),
            Skill(name="JavaScript", category=SkillCategory.PROGRAMMING, proficiency=SkillProficiency.INTERMEDIATE),
            Skill(name="React", category=SkillCategory.WEB_DEVELOPMENT, proficiency=SkillProficiency.INTERMEDIATE),
            Skill(name="PostgreSQL", category=SkillCategory.DATABASE, proficiency=SkillProficiency.INTERMEDIATE),
        ],
        soft_skills=[
            Skill(name="Team Leadership", category=SkillCategory.SOFT_SKILL, proficiency=SkillProficiency.ADVANCED, is_technical=False),
            Skill(name="Communication", category=SkillCategory.SOFT_SKILL, proficiency=SkillProficiency.ADVANCED, is_technical=False),
            Skill(name="Problem Solving", category=SkillCategory.SOFT_SKILL, proficiency=SkillProficiency.ADVANCED, is_technical=False),
        ],
    )


@pytest.fixture
def sample_experience_evaluation() -> ExperienceEvaluation:
    """Provide a sample experience evaluation."""
    return ExperienceEvaluation(
        total_years=5.5,
        total_roles=2,
        quality_score=75.0,
        relevance_score=80.0,
        has_quantified_achievements=True,
        experience_level="Senior",
    )


@pytest.fixture
def sample_analysis_result(
    sample_skill_inventory: SkillInventory,
    sample_experience_evaluation: ExperienceEvaluation,
) -> AnalysisResult:
    """Provide a sample analysis result."""
    score = ResumeScore(
        overall=82.5,
        section_scores=[
            SectionScore(section_name="Skills", score=85.0, weight=0.3, feedback="Good skills."),
            SectionScore(section_name="Experience", score=80.0, weight=0.3, feedback="Good experience."),
            SectionScore(section_name="Education", score=70.0, weight=0.2, feedback="Education present."),
            SectionScore(section_name="Projects", score=90.0, weight=0.2, feedback="Strong projects."),
        ],
    )

    return AnalysisResult(
        correlation_id="test-correlation-123",
        skill_inventory=sample_skill_inventory,
        experience_evaluation=sample_experience_evaluation,
        resume_score=score,
        summary="Experienced software engineer with 5+ years of experience...",
        job_recommendations=[
            {"title": "Software Engineer", "match_percentage": 85.0, "required_skills": ["Python", "Java"], "matched_skills": ["Python"], "missing_skills": ["Java"], "experience_level": "Mid", "industry": "Technology", "description": "Build software."},
            {"title": "Data Scientist", "match_percentage": 45.0, "required_skills": ["Python", "ML"], "matched_skills": ["Python"], "missing_skills": ["ML"], "experience_level": "Mid", "industry": "Technology", "description": "Analyze data."},
        ],
        missing_skills=[
            {"skill_name": "Java", "relevance_score": 0.85, "demand_level": "High", "related_roles": ["Software Engineer"]},
            {"skill_name": "Machine Learning", "relevance_score": 0.45, "demand_level": "Medium", "related_roles": ["Data Scientist"]},
        ],
        improvements=[
            {"section": "Experience", "suggestion": "Add more quantified achievements.", "priority": "High", "example": "Before: Improved performance. After: Improved performance by 40%."},
        ],
    )


# ── Mock AI Client Fixture ───────────────────────────────────────────────

@pytest.fixture
def mock_ai_client() -> MagicMock:
    """Provide a mocked AI client for testing."""
    client = MagicMock()

    # Mock chat_complete_json responses
    client.chat_complete_json.return_value = {
        "technical_skills": [
            {"name": "Python", "category": "Programming", "proficiency": "Advanced", "is_technical": True},
            {"name": "SQL", "category": "Database", "proficiency": "Intermediate", "is_technical": True},
        ],
        "soft_skills": [
            {"name": "Communication", "category": "Soft_Skill", "proficiency": "Advanced", "is_technical": False},
        ],
    }

    client.chat_complete.return_value = "Test response text."

    # Mock correlation ID generation
    client.generate_correlation_id.return_value = "test-correlation-456"

    return client


# ── Database Fixture ─────────────────────────────────────────────────────

@pytest.fixture
def in_memory_db(tmp_path: Path) -> Generator[Any, None, None]:
    """Provide a temporary SQLite database for testing."""
    from core.db import DatabaseManager

    db_path = tmp_path / "test.db"
    db = DatabaseManager(db_url=str(db_path))
    db.run_migrations()

    yield db


# ── Temporary File Fixtures ──────────────────────────────────────────────

@pytest.fixture
def temp_resume_file(tmp_path: Path) -> Path:
    """Create a temporary resume text file."""
    file_path = tmp_path / "resume.txt"
    file_path.write_text(
        "John Doe\njohn@email.com\n\n"
        "Skills: Python, SQL, Django\n\n"
        "Experience: 5 years at Tech Corp\n"
    )
    return file_path