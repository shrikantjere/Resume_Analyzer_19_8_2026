# Architecture Document

## AI Resume Analyzer — Production-Grade System Architecture

**Version:** 1.0  
**Date:** August 19, 2026  
**Author:** Principal Software Architect  
**Status:** Approved

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PRESENTATION LAYER                               │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      Streamlit Frontend                               │  │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────┐  ┌────────────────┐   │  │
│  │  │ Upload   │  │ Dashboard │  │ Analysis     │  │ Report         │   │  │
│  │  │ Page     │  │ Page      │  │ Results Page  │  │ Download Page  │   │  │
│  │  └──────────┘  └───────────┘  └──────────────┘  └────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────────────────┘
                           │ HTTP / Session
                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            APPLICATION LAYER                                │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      Streamlit Backend (Python)                       │  │
│  │                                                                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐  │  │
│  │  │   Router /   │  │   Session    │  │   Service Orchestrator     │  │  │
│  │  │   Controller │──│   Manager    │──│   (Analysis Pipeline)      │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────┬───────────────┘  │  │
│  └────────────────────────────────────────────────────┼──────────────────┘  │
│                                                        │                     │
│  ┌─────────────────────────────────────────────────────┼──────────────────┐  │
│  │                    SERVICE LAYER                     │                  │  │
│  │                                                     ▼                  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐  │  │
│  │  │  Parser      │  │  Analyzer    │  │  Job Recommendation        │  │  │
│  │  │  Service     │  │  Service     │  │  Service                   │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────────────────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐  │  │
│  │  │  Report      │  │  Skills      │  │  Improvement               │  │  │
│  │  │  Generator   │  │  Service     │  │  Service                   │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────────────────┘
                           │
            ┌──────────────┼──────────────────┐
            ▼              ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────────────────────┐
│   AI / NLP LAYER │ │   DATA LAYER     │ │   EXTERNAL INTEGRATION LAYER     │
│                  │ │                  │ │                                  │
│  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌──────────────────────────┐   │
│  │  OpenAI    │  │ │  │  SQLite    │  │ │  │  Job API Aggregator      │   │
│  │  GPT-4o   │  │ │  │  Database  │  │ │  │  (Adzuna / Indeed API)    │   │
│  │  (Chat)   │  │ │  └────────────┘  │ │  └──────────────────────────┘   │
│  └────────────┘  │ │                  │ │                                  │
│  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌──────────────────────────┐   │
│  │  OpenAI    │  │ │  │  File      │  │ │  │  Learning Resource API   │   │
│  │  Embeddings│  │ │  │  Storage   │  │ │  │  (Coursera / Udemy)      │   │
│  └────────────┘  │ │  │  (Disk)    │  │ │  └──────────────────────────┘   │
│                  │ │  └────────────┘  │ │                                  │
└──────────────────┘ └──────────────────┘ └──────────────────────────────────┘
```

### Architecture Philosophy

The system follows a **Layered Architecture** with clear separation of concerns:

| Layer | Responsibility | Technology |
|---|---|---|
| **Presentation Layer** | UI rendering, user interaction, input validation | Streamlit |
| **Application Layer** | Session management, request routing, pipeline orchestration | Python + Streamlit callbacks |
| **Service Layer** | Business logic, resume parsing, scoring, recommendations | Pure Python modules |
| **AI / NLP Layer** | GPT-powered analysis, embeddings, content generation | OpenAI API (GPT-4o) |
| **Data Layer** | Persistence, file storage, caching | SQLite + Filesystem |
| **External Integration Layer** | Third-party APIs for job data, learning resources | HTTP clients |

---

## 2. Component Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        AI RESUME ANALYZER SYSTEM                             │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  STREAMLIT APP (app.py)                                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │   │
│  │  │ ui/          │  │ components/  │  │ pages/                   │   │   │
│  │  │  upload.py   │  │  sidebar.py  │  │  1_upload.py             │   │   │
│  │  │  dashboard.py│  │  charts.py   │  │  2_analysis.py           │   │   │
│  │  │  report.py   │  │  cards.py    │  │  3_recommendations.py    │   │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────────┘   │   │
│  │         └─────────────────┼─────────────────────┘                   │   │
│  │                           ▼                                         │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │              services/ (Service Orchestrator)                 │   │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │   │   │
│  │  │  │ parser   │  │ analyzer │  │ job_reco │  │ report_gen   │  │   │   │
│  │  │  │ service  │─▶│ service  │─▶│ service  │─▶│ service      │  │   │   │
│  │  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘  │   │   │
│  │  └───────┼─────────────┼─────────────┼───────────────┼──────────┘   │   │
│  └──────────┼─────────────┼─────────────┼───────────────┼──────────────┘   │
│             │             │             │               │                   │
│  ┌──────────▼─────────────▼─────────────▼───────────────▼──────────────┐   │
│  │                      models/ (Domain Models)                         │   │
│  │  Resume, ParsedResume, Skill, Experience, JobRecommendation,         │   │
│  │  AnalysisReport, UserSession, MissingSkill, ImprovementSuggestion    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│             │             │             │               │                   │
│  ┌──────────▼─────────────▼─────────────▼───────────────▼──────────────┐   │
│  │                      core/ (Core Infrastructure)                     │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │   │
│  │  │  ai_client   │  │  db          │  │  config                  │   │   │
│  │  │  (OpenAI)    │  │  (SQLite)    │  │  (settings + env)        │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │   │
│  │  │  logging     │  │  exceptions  │  │  utils (file, text,      │   │   │
│  │  │  config      │  │  (custom)    │  │  validation, pdf)        │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  tests/                                                              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ unit/    │  │  integ/  │  │  e2e/    │  │  fixtures│            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|---|---|
| **app.py** | Main entry point. Configures Streamlit page, initializes session state, mounts pages. |
| **ui/** | Pure UI rendering functions. Each file maps to a feature area. No business logic. |
| **components/** | Reusable Streamlit widgets (charts, cards, sidebar menus). |
| **services/parser_service.py** | Extracts text from PDF/DOCX/TXT. Delegates to AI for structured parsing. |
| **services/analyzer_service.py** | Orchestrates GPT calls for skill extraction, experience evaluation, scoring, and summary generation. |
| **services/job_recommendation_service.py** | Matches extracted skills against job database. Computes match percentage. Identifies missing skills. |
| **services/report_generator_service.py** | Assembles analysis data into a downloadable PDF report. |
| **models/** | Pydantic or dataclass domain models for type safety and data validation. |
| **core/ai_client.py** | Singleton wrapper around OpenAI API with retry, rate-limiting, and token management. |
| **core/db.py** | SQLite connection manager, repository pattern, migration runner. |
| **core/config.py** | Centralized configuration from environment variables + `.env` file. |
| **core/exceptions.py** | Custom exception hierarchy for the application. |
| **core/logging_config.py** | Structured logging setup (JSON format, log levels, rotation). |

---

## 3. Data Flow Diagram

### 3.1 Resume Upload & Analysis Flow

```
User                    Streamlit App              Service Layer            AI Layer             Data Layer
 │                          │                          │                      │                    │
 │  Upload Resume           │                          │                      │                    │
 │  (PDF/DOCX/TXT)          │                          │                      │                    │
 │─────────────────────────▶│                          │                      │                    │
 │                          │                          │                      │                    │
 │                          │  Validate file type      │                      │                    │
 │                          │  & size (≤10 MB)         │                      │                    │
 │                          │──────────────────────────│                      │                    │
 │                          │                          │                      │                    │
 │                          │  Save to temp storage    │                      │                    │
 │                          │──────────────────────────┼─────────────────────▶│                    │
 │                          │                          │                      │  Save raw file      │
 │                          │                          │                      │  to disk            │
 │                          │                          │                      │────────────────────▶│
 │                          │                          │                      │                    │
 │                          │  Extract text            │                      │                    │
 │                          │──────────────────────────▶ Parser Service       │                    │
 │                          │                          │  (pdfplumber/        │                    │
 │                          │                          │   python-docx)       │                    │
 │                          │                          │─────────────────────▶│                    │
 │                          │                          │                      │                    │
 │                          │      Plain Text          │                      │                    │
 │                          │◀─────────────────────────│                      │                    │
 │                          │                          │                      │                    │
 │                          │  Analyze Resume          │                      │                    │
 │                          │──────────────────────────▶ Analyzer Service     │                    │
 │                          │                          │                      │                    │
 │                          │                          │  Call GPT-4o         │                    │
 │                          │                          │  (structured output) │                    │
 │                          │                          │─────────────────────▶│                    │
 │                          │                          │                      │  OpenAI API         │
 │                          │                          │                      │  (Chat Completion)  │
 │                          │                          │                      │                    │
 │                          │                          │  Parsed + Scored     │                    │
 │                          │                          │◀─────────────────────│                    │
 │                          │                          │                      │                    │
 │                          │                          │  Save analysis       │                    │
 │                          │                          │  result to DB        │                    │
 │                          │                          │──────────────────────┼───────────────────▶│
 │                          │                          │                      │                    │
 │                          │      Analysis Result     │                      │                    │
 │                          │◀─────────────────────────│                      │                    │
 │                          │                          │                      │                    │
 │  Display Results         │                          │                      │                    │
 │◀─────────────────────────│                          │                      │                    │
 │                          │                          │                      │                    │
```

### 3.2 Job Recommendation Flow

```
User                    Streamlit App              Job Reco Service          AI Layer             Data Layer
 │                          │                          │                      │                    │
 │  View Recommendations    │                          │                      │                    │
 │─────────────────────────▶│                          │                      │                    │
 │                          │  Request recommendations │                      │                    │
 │                          │──────────────────────────▶ Job Reco Service      │                    │
 │                          │                          │                      │                    │
 │                          │                          │  Load extracted      │                    │
 │                          │                          │  skills from DB      │                    │
 │                          │                          │──────────────────────┼───────────────────▶│
 │                          │                          │                      │                    │
 │                          │                          │  Skills data         │                    │
 │                          │                          │◀─────────────────────┼────────────────────│
 │                          │                          │                      │                    │
 │                          │                          │  Load job roles      │                    │
 │                          │                          │  from DB             │                    │
 │                          │                          │──────────────────────┼───────────────────▶│
 │                          │                          │                      │                    │
 │                          │                          │  Job roles           │                    │
 │                          │                          │◀─────────────────────┼────────────────────│
 │                          │                          │                      │                    │
 │                          │                          │  Compute skill-match │                    │
 │                          │                          │  percentage          │                    │
 │                          │                          │  (Jaccard similarity)│                    │
 │                          │                          │                      │                    │
 │                          │                          │  Identify missing    │                    │
 │                          │                          │  skills per role     │                    │
 │                          │                          │                      │                    │
 │                          │                          │  Call GPT for        │                    │
 │                          │                          │  improvement tips    │                    │
 │                          │                          │─────────────────────▶│                    │
 │                          │                          │                      │  OpenAI API         │
 │                          │                          │◀─────────────────────│                    │
 │                          │                          │                      │                    │
 │                          │  Recommendations +       │                      │                    │
 │                          │  Missing Skills          │                      │                    │
 │                          │◀─────────────────────────│                      │                    │
 │                          │                          │                      │                    │
 │  View Recommendations    │                          │                      │                    │
 │◀─────────────────────────│                          │                      │                    │
 │                          │                          │                      │                    │
```

### 3.3 Report Download Flow

```
User                    Streamlit App              Report Generator           Data Layer
 │                          │                          │                      │
 │  Click "Download Report" │                          │                      │
 │─────────────────────────▶│                          │                      │
 │                          │                          │                      │
 │                          │  Fetch full analysis     │                      │
 │                          │──────────────────────────▶ Report Generator      │
 │                          │                          │                      │
 │                          │                          │  Load analysis data  │
 │                          │                          │──────────────────────▶│
 │                          │                          │                      │
 │                          │                          │  Analysis data       │
 │                          │                          │◀─────────────────────│
 │                          │                          │                      │
 │                          │                          │  Generate PDF        │
 │                          │                          │  (ReportLab /        │
 │                          │                          │   WeasyPrint)        │
 │                          │                          │                      │
 │                          │                          │  Save to temp        │
 │                          │                          │──────────────────────▶│
 │                          │                          │                      │
 │                          │     PDF File Path        │                      │
 │                          │◀─────────────────────────│                      │
 │                          │                          │                      │
 │  Download PDF            │                          │                      │
 │◀─────────────────────────│                          │                      │
 │                          │                          │                      │
```

---

## 4. Folder Structure

```
resume_analyzer/
│
├── app.py                          # Streamlit entry point
├── .env                            # Environment variables (not committed)
├── .env.example                    # Template for environment variables
├── .gitignore
├── requirements.txt                # Python dependencies
├── README.md
│
├── pages/                          # Streamlit multi-page app
│   ├── __init__.py
│   ├── 1_upload_resume.py          # Upload & initial analysis page
│   ├── 2_analysis_results.py       # Detailed analysis view
│   ├── 3_job_recommendations.py    # Job recommendations & missing skills
│   └── 4_report_download.py        # Report export & download
│
├── ui/                             # Presentation / UI layer
│   ├── __init__.py
│   ├── upload_widgets.py           # Upload form, file drag-drop, paste area
│   ├── analysis_display.py         # Score cards, section breakdowns, charts
│   ├── recommendation_display.py   # Job cards, match bars, skill tags
│   ├── report_ui.py                # Download buttons, preview
│   └── styles.py                   # Custom CSS, theme overrides
│
├── components/                     # Reusable Streamlit components
│   ├── __init__.py
│   ├── sidebar.py                  # Navigation sidebar
│   ├── score_gauge.py              # Circular / linear score gauge
│   ├── skill_chart.py              # Skill category radar/bar chart
│   ├── job_card.py                 # Reusable job recommendation card
│   └── feedback_form.py            # User feedback widget
│
├── services/                       # Business logic layer
│   ├── __init__.py
│   ├── parser_service.py           # Resume text extraction (PDF/DOCX/TXT)
│   ├── analyzer_service.py         # GPT-based analysis orchestration
│   ├── scoring_service.py          # Resume scoring algorithm
│   ├── skill_extraction_service.py # Skill detection & categorization
│   ├── experience_service.py       # Experience evaluation & timeline analysis
│   ├── summary_service.py          # AI summary generation
│   ├── job_recommendation_service.py # Job matching & recommendation engine
│   ├── missing_skills_service.py   # Missing skill identification
│   ├── improvement_service.py      # Improvement suggestion generation
│   └── report_generator_service.py # PDF/JSON report generation
│
├── core/                           # Core infrastructure
│   ├── __init__.py
│   ├── config.py                   # Configuration management (pydantic-settings)
│   ├── ai_client.py                # OpenAI API client (singleton, retry, rate-limit)
│   ├── db.py                       # SQLite connection, session factory, migrations
│   ├── logging_config.py           # Structured logging setup
│   ├── exceptions.py               # Custom exception hierarchy
│   └── utils.py                    # Shared utilities (file helpers, text processing)
│
├── models/                         # Domain models (Pydantic / dataclasses)
│   ├── __init__.py
│   ├── resume.py                   # Resume, ParsedResume, Section
│   ├── skills.py                   # Skill, SkillCategory, SkillProficiency
│   ├── experience.py               # WorkExperience, ExperienceEvaluation
│   ├── analysis.py                 # AnalysisResult, SectionScore, ResumeScore
│   ├── job.py                      # JobRole, JobRecommendation, MatchResult
│   ├── report.py                   # AnalysisReport, ReportSection
│   └── user.py                     # UserSession, UserFeedback
│
├── data/                           # Runtime data (gitignored)
│   ├── uploads/                    # Uploaded resume files (temp)
│   ├── reports/                    # Generated PDF reports
│   └── job_database.json           # Curated job roles dataset
│
├── db/                             # Database artifacts
│   ├── schema.sql                  # Full DDL for SQLite
│   ├── migrations/                 # Sequential migration files
│   │   ├── 001_initial_schema.sql
│   │   └── 002_add_job_feedback.sql
│   └── seed.sql                    # Seed data (job roles, skill categories)
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures, mock OpenAI client
│   │
│   ├── unit/                       # Unit tests (fast, no external deps)
│   │   ├── __init__.py
│   │   ├── test_parser_service.py
│   │   ├── test_scoring_service.py
│   │   ├── test_skill_extraction.py
│   │   ├── test_experience_service.py
│   │   ├── test_job_matching.py
│   │   ├── test_missing_skills.py
│   │   ├── test_improvement_service.py
│   │   ├── test_report_generator.py
│   │   ├── test_models.py
│   │   └── test_utils.py
│   │
│   ├── integration/                # Integration tests (real DB, mocked AI)
│   │   ├── __init__.py
│   │   ├── test_analyzer_pipeline.py
│   │   ├── test_job_recommendation_flow.py
│   │   ├── test_report_generation.py
│   │   └── test_db_repository.py
│   │
│   ├── e2e/                        # End-to-end tests (Streamlit test runner)
│   │   ├── __init__.py
│   │   ├── test_upload_flow.py
│   │   ├── test_analysis_flow.py
│   │   └── test_download_flow.py
│   │
│   └── fixtures/                   # Test data
│       ├── sample_resume.pdf
│       ├── sample_resume.docx
│       ├── sample_resume.txt
│       ├── parsed_resume_fixture.json
│       └── mock_openai_responses.py
│
└── docs/                           # Documentation
    ├── architecture.md
    ├── api.md
    └── setup.md
```

---

## 5. Design Patterns

### 5.1 Pattern Catalog

| Pattern | Where Used | Rationale |
|---|---|---|
| **Layered Architecture** | Entire system | Separates concerns (UI → Service → Core → Data), enabling independent testing and evolution of each layer. |
| **Singleton** | `core/ai_client.py` | Single OpenAI client instance with connection pooling, rate-limit tracking, and token budgeting. Prevents exhausting API rate limits across multiple analysis threads. |
| **Repository Pattern** | `core/db.py` | Abstracts SQLite behind a repository interface. Makes data access testable with in-memory SQLite and allows future migration to PostgreSQL without changing business logic. |
| **Strategy Pattern** | `services/parser_service.py` | Multiple parsing strategies (pdfplumber, python-docx, plain text) selected via a strategy resolver. New file formats can be added without modifying the orchestration code. |
| **Factory Pattern** | `models/` | Factory methods for creating domain models from raw GPT responses (e.g., `AnalysisResult.from_gpt_response(response)`). Centralizes parsing/validation logic. |
| **Pipeline Pattern** | `services/analyzer_service.py` | Analysis pipeline as a chain of composable stages: Extract → Parse → Score → Summarize. Each stage is a callable class, enabling easy reordering, addition, or skipping of stages. |
| **Dependency Injection** | `services/` via constructor | Services receive their dependencies (AI client, DB session, config) via constructor injection, making unit testing trivial (swap real OpenAI for a mock). |
| **DTO / Data Transfer Objects** | `models/` | Pydantic models serve as DTOs between layers, ensuring type safety, validation, and serialization. |
| **Facade** | `services/analyzer_service.py` | Single `analyze()` method on the Analyzer Service hides the complexity of the multi-stage pipeline from the Streamlit UI layer. |
| **Template Method** | `services/report_generator_service.py` | Report generation defines a skeleton (Header → Sections → Footer) while subclasses override specific section rendering (PDF vs JSON). |
| **Observer (via Streamlit Session State)** | `app.py` / `pages/` | Session state acts as an observable store. UI components react to state changes (e.g., analysis complete → show results). |

### 5.2 Key Pattern: Analysis Pipeline

```python
# Pseudocode illustrating the Pipeline Pattern

class AnalysisPipeline:
    def __init__(self, stages: list[AnalysisStage]):
        self.stages = stages

    def execute(self, resume_text: str, context: AnalysisContext) -> AnalysisResult:
        result = AnalysisResult()
        for stage in self.stages:
            stage.process(resume_text, result, context)
        return result

# Usage in analyzer_service.py
pipeline = AnalysisPipeline(stages=[
    SkillExtractionStage(ai_client),
    ExperienceEvaluationStage(ai_client),
    ScoringStage(),
    SummaryGenerationStage(ai_client),
    ImprovementSuggestionStage(ai_client),
])
```

### 5.3 Key Pattern: Repository

```python
# Pseudocode illustrating the Repository Pattern

class AnalysisRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def save_analysis(self, analysis: AnalysisResult) -> int:
        with self.db.session() as session:
            cursor = session.execute(
                "INSERT INTO analyses (...) VALUES (...) RETURNING id",
                analysis.to_db_row()
            )
            session.commit()
            return cursor.fetchone()[0]

    def get_analysis_by_id(self, analysis_id: int) -> AnalysisResult | None:
        row = self.db.fetch_one("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
        return AnalysisResult.from_db_row(row) if row else None
```

---

## 6. Security Considerations

### 6.1 Threat Model & Mitigations

| Threat | Risk Level | Mitigation |
|---|---|---|
| **PII Leakage** — Resumes contain names, emails, phone numbers, addresses | **Critical** | — Encrypt uploaded files at rest (AES-256-GCM via `cryptography` library)<br>— Delete raw resume files immediately after text extraction<br>— Never log raw resume content<br>— Anonymize analysis data before storing in SQLite<br>— Provide a data deletion endpoint for GDPR/CCPA compliance |
| **OpenAI API Key Exposure** | **Critical** | — Load API key from environment variable (`OPENAI_API_KEY`)<br>— Never commit `.env` to version control<br>— Use `.env.example` with placeholder values<br>— Implement key rotation warning in logs |
| **Prompt Injection** — Malicious resume text attempts to manipulate GPT output | **High** | — Isolate user input in the system prompt using delimiters<br>— Use structured output (JSON mode) to constrain responses<br>— Validate GPT output schema before processing<br>— Rate-limit API calls per session |
| **Insecure Direct Object Reference (IDOR)** — User accesses another user's analysis | **High** | — Generate unique, non-guessable analysis IDs (UUID v4)<br>— Associate analyses with session IDs<br>— Enforce session-based access control |
| **File Upload Vulnerabilities** — Malicious file uploads (malware, zip bombs) | **High** | — Validate file type by magic bytes (not just extension)<br>— Enforce 10 MB file size limit<br>— Scan with `python-magic` for MIME type verification<br>— Store uploaded files outside the web root |
| **Dependency Vulnerabilities** | **Medium** | — Pin dependency versions in `requirements.txt`<br>— Run `pip-audit` or `safety` in CI pipeline<br>— Regular `pip-review` for security updates |
| **SQLite Injection** | **Medium** | — Use parameterized queries exclusively (no f-string interpolation in SQL)<br>— Leverage Pydantic validation before DB writes |
| **Session Hijacking** | **Medium** | — Use Streamlit's built-in secure session cookies<br>— Set `SameSite=Strict` on session cookies<br>— Regenerate session ID on each analysis |

### 6.2 Security Checklist

- [x] API key loaded from environment, never hardcoded
- [x] File uploads validated by magic bytes + extension
- [x] Uploaded files deleted after text extraction
- [x] SQLite queries use parameterized statements
- [x] GPT responses validated against expected schema
- [x] Analysis IDs use UUID v4 (non-sequential)
- [x] `.env` in `.gitignore`
- [x] Logging excludes PII and API keys
- [x] Rate limiting on analysis endpoint (per IP / session)
- [x] Input text sanitized before GPT API calls (strip control characters, limit length)

---

## 7. Logging Strategy

### 7.1 Logging Principles

| Principle | Implementation |
|---|---|
| **Structured** | JSON-formatted logs for machine readability and correlation |
| **Level-appropriate** | Use DEBUG / INFO / WARNING / ERROR consistently |
| **Correlation ID** | Unique request ID per analysis session for tracing across layers |
| **PII-safe** | Never log resume content, PII, or API keys |
| **Rotating** | Log rotation to prevent disk exhaustion |
| **Environment-aware** | Console logging in development; file + console in production |

### 7.2 Log Configuration (`core/logging_config.py`)

```python
import logging
import json
import uuid
from datetime import datetime, timezone

class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "tokens_used": getattr(record, "tokens_used", None),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)
```

### 7.3 Log Events Catalog

| Event | Level | Fields | When |
|---|---|---|---|
| Analysis started | INFO | `correlation_id`, `file_type`, `file_size` | Resume upload received |
| File parsed | INFO | `correlation_id`, `text_length`, `extraction_time_ms` | Text extracted from file |
| GPT API call started | DEBUG | `correlation_id`, `model`, `prompt_tokens` | Before OpenAI API call |
| GPT API call completed | INFO | `correlation_id`, `model`, `tokens_used`, `duration_ms` | OpenAI API response received |
| GPT API call failed | ERROR | `correlation_id`, `model`, `error_type`, `retry_count` | After retries exhausted |
| Analysis completed | INFO | `correlation_id`, `resume_score`, `total_duration_ms` | Full pipeline done |
| Job recommendation generated | INFO | `correlation_id`, `top_roles`, `match_scores` | Job matching completed |
| Report downloaded | INFO | `correlation_id`, `report_type`, `file_size` | PDF/JSON served |
| Rate limit hit | WARNING | `correlation_id`, `retry_after` | OpenAI rate-limit response |
| Session error | ERROR | `correlation_id`, `error_type`, `stack_trace` | Unhandled exception |
| Security event | CRITICAL | `correlation_id`, `event_type`, `ip_address` | Suspicious activity detected |

### 7.4 Log Consumption

```
Console (dev):     stderr with colored level
Production file:   logs/analyzer.log (rotating, 10 MB per file, 5 backups)
Error file:        logs/errors.log (ERROR+ only, for alerting)
```

---

## 8. Error Handling Strategy

### 8.1 Exception Hierarchy

```
ResumeAnalyzerError (Base)
├── FileProcessingError
│   ├── UnsupportedFileTypeError
│   ├── FileTooLargeError
│   ├── FileCorruptedError
│   └── TextExtractionError
├── AnalysisError
│   ├── AIServiceError
│   │   ├── OpenAITimeoutError
│   │   ├── OpenAIRateLimitError
│   │   ├── OpenAITokenLimitError
│   │   └── OpenAISchemaError
│   ├── ScoringError
│   └── SummaryGenerationError
├── RecommendationError
│   ├── JobDatabaseError
│   └── MatchingError
├── ReportError
│   ├── PDFGenerationError
│   └── ReportNotFoundError
├── DatabaseError
│   ├── ConnectionError
│   ├── MigrationError
│   └── IntegrityError
└── ConfigurationError
    ├── MissingAPIKeyError
    └── InvalidConfigError
```

### 8.2 Error Handling Strategy

```python
# Pattern: Centralized error boundary in service layer

from core.exceptions import (
    ResumeAnalyzerError, FileProcessingError, AIServiceError,
    OpenAITimeoutError, OpenAIRateLimitError
)
from core.logging_config import get_logger

logger = get_logger(__name__)

class AnalyzerService:
    def analyze(self, resume_text: str, correlation_id: str) -> AnalysisResult:
        try:
            # Stage 1: Extract skills
            skills = self._extract_skills(resume_text, correlation_id)

            # Stage 2: Evaluate experience
            experience = self._evaluate_experience(resume_text, correlation_id)

            # Stage 3: Score resume
            score = self._calculate_score(skills, experience)

            # Stage 4: Generate summary
            summary = self._generate_summary(resume_text, skills, experience, correlation_id)

            return AnalysisResult(skills=skills, experience=experience, score=score, summary=summary)

        except OpenAIRateLimitError as e:
            logger.warning("Rate limit hit", extra={"correlation_id": correlation_id, "retry_after": e.retry_after})
            raise AIServiceError("Analysis temporarily unavailable. Please try again in a few seconds.") from e

        except OpenAITimeoutError as e:
            logger.error("OpenAI timeout", extra={"correlation_id": correlation_id, "duration_ms": e.duration_ms})
            raise AIServiceError("Analysis timed out. Please try again.") from e

        except OpenAISchemaError as e:
            logger.error("GPT response schema validation failed", extra={"correlation_id": correlation_id})
            raise AIServiceError("Unexpected response format. Please try again.") from e

        except FileProcessingError:
            raise  # Re-raise file errors directly to UI

        except ResumeAnalyzerError as e:
            logger.error("Analysis failed", extra={"correlation_id": correlation_id, "error": str(e)})
            raise

        except Exception as e:
            logger.critical("Unexpected error in analysis pipeline", extra={"correlation_id": correlation_id}, exc_info=True)
            raise ResumeAnalyzerError("An unexpected error occurred. Please try again.") from e
```

### 8.3 Error Display Strategy (Streamlit)

| Error Type | User-Facing Message | UI Action |
|---|---|---|
| `UnsupportedFileTypeError` | "Please upload a PDF, DOCX, or TXT file." | Show inline error on upload widget |
| `FileTooLargeError` | "File size exceeds the 10 MB limit." | Show inline error with file size shown |
| `FileCorruptedError` | "Unable to read this file. It may be corrupted." | Show error + retry button |
| `OpenAIRateLimitError` | "High demand! Please wait a moment and try again." | Show spinner + auto-retry after delay |
| `OpenAITimeoutError` | "Analysis is taking longer than expected." | Show retry button |
| `OpenAITokenLimitError` | "Resume is too long. Please shorten it." | Show character count + suggestion |
| `DatabaseError` | "System error. Please try again." | Show generic error + contact support |
| `ConfigurationError` | "System not configured properly. Contact administrator." | Show during startup only |

### 8.4 Graceful Degradation

| Scenario | Fallback Behavior |
|---|---|
| OpenAI API is down | Show cached scoring rules; inform user of limited analysis |
| Job database is empty | Show "No recommendations available" section; skip missing skills |
| PDF extraction fails | Fall back to plain text mode; ask user to paste resume text |
| Report generation fails | Allow JSON download as fallback |

---

## 9. Testing Strategy

### 9.1 Test Pyramid

```
         ╱╲
        ╱  ╲          E2E Tests (3-5)
       ╱    ╲         Streamlit app flow tests
      ╱      ╲
     ╱────────╲
    ╱          ╲      Integration Tests (10-15)
   ╱            ╲     DB + Service layer with mocked AI
  ╱──────────────╲
 ╱                  ╲  Unit Tests (40-60)
╱                    ╲ Pure logic, mocked boundaries, fast (< 100ms each)
────────────────────────
```

### 9.2 Unit Testing (`tests/unit/`)

| Test File | What It Tests | Strategy |
|---|---|---|
| `test_parser_service.py` | Text extraction from each file type; error handling for corrupted files | Mock file I/O, test with fixture files |
| `test_scoring_service.py` | Resume score calculation algorithm; edge cases (empty resume, perfect resume) | Pure function testing, no mocks |
| `test_skill_extraction.py` | Skill extraction from GPT response; skill categorization; deduplication | Mock OpenAI client, test parsing logic |
| `test_experience_service.py` | Year extraction; timeline gap detection; quality scoring | Pure functions with pre-built inputs |
| `test_job_matching.py` | Jaccard similarity computation; match percentage threshold filtering | Pure function testing |
| `test_missing_skills.py` | Diff logic between required and existing skills; relevance ranking | Pure function, test with fixture data |
| `test_improvement_service.py` | Suggestion generation from GPT; formatting of suggestions | Mock OpenAI, test suggestion structure |
| `test_report_generator.py` | PDF/JSON generation; report structure; error handling | Mock file I/O, verify content structure |
| `test_models.py` | Pydantic validation; serialization; factory methods | Pure data model tests |
| `test_utils.py` | File type detection; text sanitization; UUID generation | Pure function tests |

**Unit Test Example:**

```python
# tests/unit/test_scoring_service.py
import pytest
from services.scoring_service import ResumeScorer
from models.analysis import SectionScore

class TestResumeScorer:
    def setup_method(self):
        self.scorer = ResumeScorer()

    def test_perfect_resume_returns_100(self):
        skills = ["Python", "SQL", "Machine Learning", "Project Management"]
        experience_years = 10
        sections_complete = {"education": True, "experience": True, "skills": True, "projects": True}
        score = self.scorer.calculate(skills, experience_years, sections_complete)
        assert score.overall == 100

    def test_empty_skills_penalizes_score(self):
        skills = []
        experience_years = 0
        sections_complete = {"education": True, "experience": False, "skills": False, "projects": False}
        score = self.scorer.calculate(skills, experience_years, sections_complete)
        assert score.overall < 50
        assert score.section_scores["skills"] < 30

    def test_score_always_between_0_and_100(self):
        for _ in range(100):
            score = self.scorer.calculate(
                skills=["Python"] * 5,
                experience_years=5,
                sections_complete={"education": True, "experience": True, "skills": True, "projects": True}
            )
            assert 0 <= score.overall <= 100
```

### 9.3 Integration Testing (`tests/integration/`)

| Test File | What It Tests | Strategy |
|---|---|---|
| `test_analyzer_pipeline.py` | Full pipeline from text → AnalysisResult | In-memory SQLite, mocked OpenAI responses |
| `test_job_recommendation_flow.py` | Skills → Recommendations → Missing skills chain | Seeded job database, real matching logic |
| `test_report_generation.py` | AnalysisResult → PDF/JSON output | Generate reports, validate file structure |
| `test_db_repository.py` | CRUD operations, migrations, constraints | In-memory SQLite, run migrations |

**Integration Test Example:**

```python
# tests/integration/test_analyzer_pipeline.py
import pytest
from services.analyzer_service import AnalyzerService
from services.parser_service import ParserService
from core.db import DatabaseManager
from core.ai_client import AIClient

class TestAnalyzerPipeline:
    @pytest.fixture
    def db(self, tmp_path):
        db = DatabaseManager(f"sqlite:///{tmp_path}/test.db")
        db.run_migrations()
        return db

    @pytest.fixture
    def ai_client(self, mocker):
        client = mocker.Mock(spec=AIClient)
        # Mock GPT response for skill extraction
        client.extract_skills.return_value = ["Python", "SQL", "Django"]
        # Mock GPT response for summary
        client.generate_summary.return_value = "Experienced developer..."
        return client

    def test_full_analysis_pipeline(self, db, ai_client):
        parser = ParserService()
        analyzer = AnalyzerService(ai_client=ai_client, db=db)

        resume_text = parser.extract_text("tests/fixtures/sample_resume.pdf")
        result = analyzer.analyze(resume_text, correlation_id="test-123")

        assert result.skills == ["Python", "SQL", "Django"]
        assert 0 <= result.score.overall <= 100
        assert result.summary is not None

        # Verify data persisted to DB
        saved = db.analyses.get_by_id(result.id)
        assert saved is not None
        assert saved.resume_score == result.score.overall
```

### 9.4 End-to-End Testing (`tests/e2e/`)

| Test File | What It Tests | Tool |
|---|---|---|
| `test_upload_flow.py` | Upload PDF → See progress → Analysis results displayed | `streamlit.testing` (or Playwright) |
| `test_analysis_flow.py` | Navigate pages → View skills → View recommendations → View improvements | `streamlit.testing` |
| `test_download_flow.py` | Click download → PDF generated → File saved successfully | `streamlit.testing` + file system |

**E2E Test Example (using Streamlit's test runner):**

```python
# tests/e2e/test_upload_flow.py
import pytest
from streamlit.testing import StreamlitTestRunner

def test_upload_and_analysis_flow():
    runner = StreamlitTestRunner("app.py")
    runner.start()

    # Step 1: Verify upload page is shown
    assert "Upload Resume" in runner.title

    # Step 2: Upload a file
    upload = runner.find("file_uploader")
    upload.upload("tests/fixtures/sample_resume.pdf")

    # Step 3: Wait for analysis to complete
    runner.wait_for_text("Resume Score", timeout=30)

    # Step 4: Verify score is displayed
    score = runner.find("[data-testid='resume-score']")
    assert score.value is not None
    assert 0 <= int(score.value) <= 100
```

### 9.5 Test Configuration (`tests/conftest.py`)

```python
import pytest
from core.config import Settings

@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    """Override settings for all tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

@pytest.fixture
def sample_resume_text():
    """Load sample resume text from fixture."""
    with open("tests/fixtures/sample_resume.txt") as f:
        return f.read()

@pytest.fixture
def mock_openai_response():
    """Return a standardized mock OpenAI response."""
    return {
        "skills": ["Python", "SQL", "AWS"],
        "experience_years": 5,
        "education": "Bachelor's in Computer Science",
        "summary": "Experienced software engineer...",
    }
```

### 9.6 Test Coverage Targets

| Layer | Coverage Target | Notes |
|---|---|---|
| `models/` | 100% | Pure data models, easy to cover |
| `services/` (non-AI) | ≥ 95% | Scoring, matching, missing skills, utils |
| `services/` (AI-dependent) | ≥ 85% | Mock AI client, test orchestration logic |
| `core/` | ≥ 90% | Config, DB, exceptions, utils |
| `ui/` | ≥ 70% | Streamlit rendering logic |
| `pages/` | ≥ 60% | Page orchestration (E2E tests cover this) |

### 9.7 CI Integration

```yaml
# .github/workflows/test.yml (conceptual)
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/unit --cov=services --cov=models --cov=core --cov-report=term-missing
      - run: pytest tests/integration --cov=services --cov-append
      - run: pytest tests/e2e
      - run: pip-audit  # Check for vulnerable dependencies
```

---

## Appendix: Key Technology Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Frontend** | Streamlit | Fastest time-to-MVP for data-centric Python apps; single language (Python) across stack; built-in session state |
| **AI Model** | OpenAI GPT-4o | Best-in-class structured output (JSON mode); high accuracy on skill extraction; reliable summarization |
| **Database** | SQLite | Zero-config; sufficient for single-server deployment; easy to migrate to PostgreSQL later via repository pattern |
| **PDF Parsing** | pdfplumber | Better text extraction accuracy than PyPDF2; handles complex layouts |
| **DOCX Parsing** | python-docx | De facto standard for Word document processing |
| **PDF Generation** | WeasyPrint | HTML/CSS → PDF conversion; easy to style professional reports |
| **Testing** | pytest + pytest-cov | Industry standard; rich plugin ecosystem; Streamlit test runner |
| **Config** | pydantic-settings | Type-safe configuration from env vars; `.env` file support |
| **Encryption** | cryptography (Fernet) | Simple AES-256-GCM symmetric encryption for file storage |