"""Mock OpenAI responses for testing."""

from typing import Any


def get_mock_skill_extraction_response() -> dict[str, Any]:
    """Return a mock OpenAI response for skill extraction."""
    return {
        "technical_skills": [
            {"name": "Python", "category": "Programming", "proficiency": "Advanced", "is_technical": True},
            {"name": "SQL", "category": "Database", "proficiency": "Intermediate", "is_technical": True},
            {"name": "Django", "category": "Framework", "proficiency": "Advanced", "is_technical": True},
            {"name": "AWS", "category": "Cloud_Computing", "proficiency": "Intermediate", "is_technical": True},
        ],
        "soft_skills": [
            {"name": "Communication", "category": "Soft_Skill", "proficiency": "Advanced", "is_technical": False},
            {"name": "Team Leadership", "category": "Soft_Skill", "proficiency": "Intermediate", "is_technical": False},
        ],
    }


def get_mock_experience_response() -> dict[str, Any]:
    """Return a mock OpenAI response for experience evaluation."""
    return {
        "work_experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "start_date": "2020-01",
                "end_date": "2023-06",
                "description": "Led development of microservices architecture.",
                "achievements": ["Improved performance by 40%", "Managed team of 5"],
                "is_current": False,
            },
        ],
        "total_years": 5.5,
        "quality_score": 75.0,
        "has_quantified_achievements": True,
        "experience_level": "Senior",
        "gaps": [],
        "top_achievements": ["Improved performance by 40%"],
        "industry_sectors": ["Technology"],
        "career_progression": "Steady growth from junior to senior roles",
    }


def get_mock_summary_response() -> dict[str, str]:
    """Return a mock OpenAI response for summary generation."""
    return {
        "summary": "Experienced software engineer with 5+ years of experience building scalable applications. Proficient in Python, Django, and cloud technologies. Strong track record of improving system performance and leading development teams.",
        "tone": "professional",
        "key_highlights": ["5+ years experience", "Python expertise", "Team leadership"],
    }


def get_mock_job_recommendations_response() -> dict[str, Any]:
    """Return a mock OpenAI response for job recommendations."""
    return {
        "recommendations": [
            {
                "title": "Senior Software Engineer",
                "industry": "Technology",
                "required_skills": ["Python", "Java", "SQL", "Docker", "AWS", "Microservices"],
                "match_percentage": 85,
                "experience_level": "Senior",
                "description": "Lead development of software systems and mentor junior engineers.",
                "missing_skills": ["Java", "Docker"],
            },
            {
                "title": "Data Engineer",
                "industry": "Technology",
                "required_skills": ["Python", "SQL", "ETL", "Apache Spark", "AWS"],
                "match_percentage": 70,
                "experience_level": "Mid",
                "description": "Build and maintain data pipelines.",
                "missing_skills": ["Apache Spark", "ETL"],
            },
        ],
    }


def get_mock_improvements_response() -> dict[str, Any]:
    """Return a mock OpenAI response for improvement suggestions."""
    return {
        "improvements": [
            {
                "section": "Experience",
                "suggestion": "Add more quantified achievements to your work experience.",
                "priority": "High",
                "example": "Before: 'Improved performance'\nAfter: 'Improved performance by 40%, reducing load time from 3s to 1.8s'",
            },
            {
                "section": "Skills",
                "suggestion": "Add cloud computing skills to your skills section.",
                "priority": "Medium",
                "example": "Add AWS, Azure, or GCP to your technical skills.",
            },
        ],
    }