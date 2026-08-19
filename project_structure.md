# Project Structure — AI Resume Analyzer

**Version:** 1.0  
**Author:** Senior Python Architect  
**Date:** August 19, 2026

---

## 1. Folder Structure (Complete Tree)

```
resume_analyzer/
│
├── app.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── Makefile
├── pyproject.toml
├── README.md
│
├── pages/
│   ├── __init__.py
│   ├── 1_upload_resume.py
│   ├── 2_analysis_results.py
│   ├── 3_job_recommendations.py
│   └── 4_report_download.py
│
├── ui/
│   ├── __init__.py
│   ├── upload_widgets.py
│   ├── analysis_display.py
│   ├── recommendation_display.py
│   ├── report_ui.py
│   └── styles.py
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py
│   ├── score_gauge.py
│   ├── skill_chart.py
│   ├── job_card.py
│   └── feedback_form.py
│
├── services/
│   ├── __init__.py
│   ├── parser_service.py
│   ├── analyzer_service.py
│   ├── scoring_service.py
│   ├── skill_extraction_service.py
│   ├── experience_service.py
│   ├── summary_service.py
│   ├── job_recommendation_service.py
│   ├── missing_skills_service.py
│   ├── improvement_service.py
│   └── report_generator_service.py
│
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── ai_client.py
│   ├── db.py
│   ├── logging_config.py
│   ├── exceptions.py
│   └── utils.py
│
├── models/
│   ├── __init__.py
│   ├── resume.py
│   ├── skills.py
│   ├── experience.py
│   ├── analysis.py
│   ├── job.py
│   ├── report.py
│   └── user.py
│
├── data/
│   ├── uploads/
│   ├── reports/
│   └── job_database.json
│
├── db/
│   ├── schema.sql
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   └── 002_add_job_feedback.sql
│   └── seed.sql
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   │
│   ├── unit/
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
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_analyzer_pipeline.py
│   │   ├── test_job_recommendation_flow.py
│   │   ├── test_report_generation.py
│   │   └── test_db_repository.py
│   │
│   ├── e2e/
│   │   ├── __init__.py
│   │   ├── test_upload_flow.py
│   │   ├── test_analysis_flow.py
│   │   └── test_download_flow.py
│   │
│   └── fixtures/
│       ├── sample_resume.pdf
│       ├── sample_resume.docx
│       ├── sample_resume.txt
│       ├── parsed_resume_fixture.json
│       └── mock_openai_responses.py
│
└── docs/
    ├── architecture.md
    ├── api.md
    └── setup.md
```

---

## 2. Root Files — Purpose & Responsibilities

### `app.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Application entry point. Bootstraps the Streamlit app, configures global page settings, initializes session state, and registers all page routes. |
| **Responsibilities** | — Set Streamlit page config (title, layout, icon)<br>— Initialize global session state variables<br>— Mount page modules from `pages/`<br>— Configure logging at startup<br>— Register shutdown hooks for cleanup |
| **Dependencies** | `pages/.*`, `core/logging_config.py`, `core/config.py`, `core/exceptions.py`, Streamlit |
| **Imports From** | `core.config → Settings`, `core.logging_config → setup_logging`, `streamlit` |

### `.env`

| Attribute | Detail |
|---|---|
| **Purpose** | Local environment variables file. Never committed to version control. Contains secrets and environment-specific configuration. |
| **Responsibilities** | Hold `OPENAI_API_KEY`, `DATABASE_URL`, `LOG_LEVEL`, `MAX_FILE_SIZE`, `JOB_API_KEY` etc. |
| **Dependencies** | Loaded by `core/config.py` via `pydantic-settings` |

### `.env.example`

| Attribute | Detail |
|---|---|
| **Purpose** | Template file showing all required environment variables with placeholder values. Committed to version control as developer documentation. |
| **Responsibilities** | Document all env vars, their types, and default values for onboarding new developers |

### `.gitignore`

| Attribute | Detail |
|---|---|
| **Purpose** | Prevent accidental commits of sensitive or generated files |
| **Responsibilities** | Ignore `.env`, `data/uploads/`, `data/reports/`, `__pycache__/`, `*.pyc`, `.venv/`, `.pytest_cache/`, `*.db`, `logs/` |

### `requirements.txt`

| Attribute | Detail |
|---|---|
| **Purpose** | Production dependency manifest. Pinned versions for reproducible builds. |
| **Responsibilities** | List all runtime packages with exact versions |

### `requirements-dev.txt`

| Attribute | Detail |
|---|---|
| **Purpose** | Development-only dependencies for testing, linting, and tooling |
| **Responsibilities** | List `pytest`, `pytest-cov`, `pytest-mock`, `black`, `ruff`, `mypy`, `pre-commit`, `pip-audit` |

### `Makefile`

| Attribute | Detail |
|---|---|
| **Purpose** | Developer convenience commands for common workflows |
| **Responsibilities** | `make install`, `make test`, `make lint`, `make format`, `make run`, `make clean`, `make migrate` |

### `pyproject.toml`

| Attribute | Detail |
|---|---|
| **Purpose** | Modern Python project configuration. Consolidates tool configs (black, ruff, mypy, pytest). |
| **Responsibilities** | Project metadata, build system, tool configuration in one canonical file |

### `README.md`

| Attribute | Detail |
|---|---|
| **Purpose** | Project overview for developers and users |
| **Responsibilities** | Description, setup instructions, usage guide, architecture overview, contributing guidelines |

---

## 3. `pages/` — Streamlit Page Modules

### `pages/__init__.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Package marker. May export page registration helper. |
| **Responsibilities** | Make `pages` a proper Python package; optionally expose `register_pages()` function |

### `pages/1_upload_resume.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Page 1 — Resume upload and submission. First screen the user sees. |
| **Responsibilities** | — Render upload form (file uploader + text paste area)<br>— Validate file type and size client-side<br>— Call `parser_service` to extract text<br>— Call `analyzer_service` to start analysis<br>— Show progress indicator during analysis<br>— Store `AnalysisResult` in session state<br>— Navigate to page 2 on completion |
| **Dependencies** | `ui/upload_widgets.py`, `services/parser_service.py`, `services/analyzer_service.py`, `models/analysis.py`, `core/exceptions.py`, `core/logging_config.py` |
| **Imports From** | `ui.upload_widgets → render_upload_form`, `services.parser_service → ParserService`, `services.analyzer_service → AnalyzerService`, `models.analysis → AnalysisResult`, `core.exceptions → FileProcessingError` |

### `pages/2_analysis_results.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Page 2 — Detailed analysis report. Shows resume score, skills, experience, and summary. |
| **Responsibilities** | — Display Resume Score (gauge chart)<br>— Show section-wise scores (Education, Experience, Skills, Projects)<br>— Render extracted skills categorized by domain<br>— Display experience evaluation with timeline<br>— Show generated professional summary (with regenerate button)<br>— Display improvement suggestions |
| **Dependencies** | `ui/analysis_display.py`, `models/analysis.py`, `models/skills.py`, `models/experience.py`, `services/summary_service.py`, `services/improvement_service.py` |
| **Imports From** | `ui.analysis_display → render_score_gauge, render_skills_section, render_experience_section, render_summary_section, render_improvements`, `services.summary_service → SummaryService`, `services.improvement_service → ImprovementService` |

### `pages/3_job_recommendations.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Page 3 — Job recommendations and missing skills. |
| **Responsibilities** | — Display top 5–10 job recommendations with match percentages<br>— Show missing skills per recommended role<br>— Provide filters (industry, experience level, location)<br>— Render skill gap visualization<br>— Show learning resources for missing skills |
| **Dependencies** | `ui/recommendation_display.py`, `services/job_recommendation_service.py`, `services/missing_skills_service.py`, `models/job.py`, `models/skills.py` |
| **Imports From** | `ui.recommendation_display → render_job_recommendations, render_missing_skills, render_filters`, `services.job_recommendation_service → JobRecommendationService`, `services.missing_skills_service → MissingSkillsService` |

### `pages/4_report_download.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Page 4 — Report download and export. |
| **Responsibilities** | — Show report preview<br>— Provide PDF download button<br>— Provide JSON export option<br>— Allow user to edit summary before export<br>— Track download analytics |
| **Dependencies** | `ui/report_ui.py`, `services/report_generator_service.py`, `models/report.py` |
| **Imports From** | `ui.report_ui → render_report_preview, render_download_buttons`, `services.report_generator_service → ReportGeneratorService` |

---

## 4. `ui/` — Presentation Layer

### `ui/__init__.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Package marker. May export UI utility constants. |
| **Responsibilities** | Make `ui` a proper Python package |

### `ui/upload_widgets.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Upload form UI components. Pure rendering, no business logic. |
| **Responsibilities** | — Render file uploader with drag-and-drop zone<br>— Render text paste text area<br>— Show file validation errors inline<br>— Display upload progress bar<br>— Render format hints (acceptable formats, size limit) |
| **Dependencies** | `streamlit`, `components/sidebar.py` |
| **Imports From** | `streamlit` (st.file_uploader, st.text_area, st.progress, st.error) |

### `ui/analysis_display.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Analysis results UI components. |
| **Responsibilities** | — Render score gauge chart<br>— Render section-wise score breakdown<br>— Render skills inventory with category badges<br>— Render experience evaluation card<br>— Render professional summary with regenerate button<br>— Render improvement suggestions as accordion items |
| **Dependencies** | `components/score_gauge.py`, `components/skill_chart.py`, `streamlit` |
| **Imports From** | `components.score_gauge → render_gauge`, `components.skill_chart → render_radar_chart`, `streamlit` |

### `ui/recommendation_display.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Job recommendation UI components. |
| **Responsibilities** | — Render job recommendation cards with match bars<br>— Render missing skills list with relevance ranking<br>— Render filter controls (dropdowns, sliders)<br>— Render skill gap visualization (before/after tags) |
| **Dependencies** | `components/job_card.py`, `streamlit` |
| **Imports From** | `components.job_card → render_job_card`, `streamlit` |

### `ui/report_ui.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Report download UI components. |
| **Responsibilities** | — Render report preview (miniaturized view)<br>— Render download buttons (PDF, JSON)<br>— Render editable summary field<br>— Show download success/error toasts |
| **Dependencies** | `streamlit` |
| **Imports From** | `streamlit` |

### `ui/styles.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Custom CSS and theme overrides for the Streamlit app. |
| **Responsibilities** | — Define CSS for custom components (gauges, cards, badges)<br>— Override Streamlit default theme colors<br>— Define responsive breakpoints<br>— Inject print styles for report rendering |
| **Dependencies** | `streamlit` (st.markdown for CSS injection) |
| **Imports From** | `streamlit` |

---

## 5. `components/` — Reusable Streamlit Widgets

### `components/__init__.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Package marker. Exports all component render functions. |
| **Responsibilities** | Make `components` a proper package; re-export public API |

### `components/sidebar.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Navigation sidebar. Shown on all pages. |
| **Responsibilities** | — Render navigation links (Upload, Analysis, Recommendations, Download)<br>— Show current page indicator<br>— Render session info (analysis ID, timestamp)<br>— Provide dark mode toggle |
| **Dependencies** | `streamlit` |
| **Imports From** | `streamlit` |

### `components/score_gauge.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Circular/linear score gauge visualization. |
| **Responsibilities** | — Render a circular gauge SVG for overall score<br>— Render linear gauges for section scores<br>— Color-code by score range (red < 40, yellow 40–70, green > 70)<br>— Animate gauge fill on load |
| **Dependencies** | `streamlit` (st.markdown for SVG injection) |
| **Imports From** | `streamlit` |

### `components/skill_chart.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Skill category visualization (radar/bar chart). |
| **Responsibilities** | — Render radar chart for skill domain distribution<br>— Render horizontal bar chart for skill counts<br>— Color-code by category (Technical, Design, Soft Skills) |
| **Dependencies** | `streamlit`, `plotly` (or `matplotlib`) |
| **Imports From** | `plotly.express` or `matplotlib.pyplot` |

### `components/job_card.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Reusable job recommendation card. |
| **Responsibilities** | — Render job title, company, location<br>— Render match percentage bar<br>— Render required skills as tags<br>— Render missing skills highlighted in red<br>— Provide expandable detail section |
| **Dependencies** | `streamlit` |
| **Imports From** | `streamlit` |

### `components/feedback_form.py`

| Attribute | Detail |
|---|---|
| **Purpose** | User feedback collection widget. |
| **Responsibilities** | — Render star rating (1–5)<br>— Render optional text feedback area<br>— Submit feedback to `core/db.py`<br>— Show thank-you message on submit |
| **Dependencies** | `core/db.py`, `models/user.py`, `streamlit` |
| **Imports From** | `core.db → FeedbackRepository`, `models.user → UserFeedback` |

---

## 6. `services/` — Business Logic Layer

### `services/__init__.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Package marker. Exports all service classes for convenient importing. |
| **Responsibilities** | Make `services` a proper package; re-export service classes |

### `services/parser_service.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Resume file parsing and text extraction. First stage of the analysis pipeline. |
| **Responsibilities** | — Detect file type by magic bytes (not extension)<br>— Extract text from PDF using `pdfplumber`<br>— Extract text from DOCX using `python-docx`<br>— Handle plain text files directly<br>— Validate file size (≤ 10 MB)<br>— Sanitize extracted text (remove control characters, normalize whitespace)<br>— Raise `UnsupportedFileTypeError`, `FileTooLargeError`, `FileCorruptedError` |
| **Dependencies** | `core/exceptions.py`, `core/utils.py`, `core/config.py` |
| **Imports From** | `core.exceptions → UnsupportedFileTypeError, FileTooLargeError, FileCorruptedError`, `core.utils → detect_file_type, sanitize_text`, `core.config → settings` |
| **External Libraries** | `pdfplumber`, `python-docx`, `python-magic` |
| **Design Pattern** | Strategy Pattern — selects parser strategy based on file type |

### `services/analyzer_service.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Central analysis orchestrator. Coordinates the multi-stage analysis pipeline. |
| **Responsibilities** | — Orchestrate the full analysis pipeline<br>— Call `skill_extraction_service` for skill detection<br>— Call `experience_service` for experience evaluation<br>— Call `scoring_service` for resume scoring<br>— Call `summary_service` for summary generation<br>— Call `improvement_service` for improvement suggestions<br>— Save `AnalysisResult` to database via `core/db.py`<br>— Manage correlation ID for tracing<br>— Implement retry logic for OpenAI calls<br>— Handle partial failures gracefully |
| **Dependencies** | `services/skill_extraction_service.py`, `services/experience_service.py`, `services/scoring_service.py`, `services/summary_service.py`, `services/improvement_service.py`, `core/db.py`, `core/ai_client.py`, `core/exceptions.py`, `core/logging_config.py`, `models/analysis.py` |
| **Imports From** | `services.skill_extraction_service → SkillExtractionService`, `services.experience_service → ExperienceService`, `services.scoring_service → ScoringService`, `services.summary_service → SummaryService`, `services.improvement_service → ImprovementService`, `core.db → AnalysisRepository`, `core.ai_client → AIClient`, `core.exceptions → AnalysisError, AIServiceError`, `models.analysis → AnalysisResult` |
| **Design Pattern** | Facade Pattern — exposes a single `analyze()` method hiding pipeline complexity |

### `services/scoring_service.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Resume scoring algorithm. Pure computation, no AI calls. |
| **Responsibilities** | — Calculate overall Resume Score (0–100)<br>— Calculate section scores (Education, Experience, Skills, Projects)<br>— Weight: Skills 30%, Experience 30%, Education 20%, Projects 20%<br>— Penalize missing sections<br>— Reward keyword density (ATS optimization)<br>— Reward quantified achievements<br>— Normalize scores to 0–100 range |
| **Dependencies** | `models/analysis.py` (SectionScore, ResumeScore) |
| **Imports From** | `models.analysis → SectionScore, ResumeScore`, `models.skills → Skill`, `models.experience → WorkExperience` |
| **Design Pattern** | Pure function — no side effects, no external dependencies, trivially testable |

### `services/skill_extraction_service.py`

| Attribute | Detail |
|---|---|
| **Purpose** | AI-powered skill detection and categorization from resume text. |
| **Responsibilities** | — Call OpenAI GPT-4o with structured extraction prompt<br>— Parse JSON response into `Skill` objects<br>— Categorize skills by domain (Programming, Data Science, Design, Soft Skills, etc.)<br>— Infer proficiency level (Beginner, Intermediate, Advanced) from context<br>— Deduplicate skills (case-insensitive, synonyms)<br>— Validate extracted skills against known skill taxonomy |
| **Dependencies** | `core/ai_client.py`, `models/skills.py`, `core/exceptions.py`, `core/logging_config.py` |
| **Imports From** | `core.ai_client → AIClient`, `models.skills → Skill, SkillCategory, SkillProficiency`, `core.exceptions → AIServiceError, OpenAISchemaError` |
| **Design Pattern** | Strategy Pattern — different extraction strategies (AI-based vs regex-based fallback) |

### `services/experience_service.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Work experience extraction and evaluation. |
| **Responsibilities** | — Extract work history entries (title, company, dates, description)<br>— Calculate total years of experience<br>— Detect employment timeline gaps<br>— Evaluate quality of experience descriptions (quantified vs vague)<br>— Score experience relevance to target roles<br>— Flag inconsistencies (overlapping dates, missing months) |
| **Dependencies** | `core/ai_client.py`, `models/experience.py`, `core/exceptions.py` |
| **Imports From** | `core.ai_client → AIClient`, `models.experience → WorkExperience, ExperienceEvaluation, TimelineGap`, `core.exceptions → AIServiceError` |

### `services/summary_service.py`

| Attribute | Detail |
|---|---|
| **Purpose** | AI-powered professional summary generation. |
| **Responsibilities** | — Call GPT-4o to generate 3–5 sentence professional summary<br>— Incorporate extracted skills, experience, and education<br>— Support multiple tones (professional, concise, detailed)<br>— Allow regeneration (pass `regenerate=True` flag)<br>— Validate summary length and quality |
| **Dependencies** | `core/ai_client.py`, `core/exceptions.py` |
| **Imports From** | `core.ai_client → AIClient`, `core.exceptions → AIServiceError, SummaryGenerationError` |

### `services/job_recommendation_service.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Job matching and recommendation engine. |
| **Responsibilities** | — Load job roles from database or JSON file<br>— Compute Jaccard similarity between resume skills and job required skills<br>— Rank jobs by match percentage (descending)<br>— Return top 5–10 recommendations<br>— Support filtering (industry, experience level, location, remote)<br>— Cache job data with TTL for freshness<br>— Fall back to AI-based matching if skill-based matching yields < 3 results |
| **Dependencies** | `core/db.py`, `models/job.py`, `models/skills.py`, `core/config.py`, `core/exceptions.py`, `data/job_database.json` |
| **Imports From** | `core.db → JobRepository`, `models.job → JobRole, JobRecommendation, MatchResult`, `models.skills → Skill`, `core.config → settings`, `core.exceptions → JobDatabaseError, MatchingError` |
| **Design Pattern** | Strategy Pattern — multiple matching algorithms (Jaccard, TF-IDF, AI-based) |

### `services/missing_skills_service.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Identify skills missing from the resume that are required for recommended jobs. |
| **Responsibilities** | — Diff required skills (from job DB) against extracted skills (from resume)<br>— Rank missing skills by relevance and demand<br>— Generate learning resource suggestions for each missing skill<br>— Provide skill gap percentage per job role |
| **Dependencies** | `models/skills.py`, `models/job.py`, `core/exceptions.py` |
| **Imports From** | `models.skills → Skill`, `models.job → JobRole, MissingSkill` |

### `services/improvement_service.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Generate actionable resume improvement suggestions. |
| **Responsibilities** | — Analyze each resume section for weaknesses<br>— Generate ATS keyword optimization suggestions<br>— Suggest phrasing improvements (weak verbs → strong verbs)<br>— Provide formatting tips<br>— Show before/after examples for common weak patterns<br>— Prioritize suggestions by impact |
| **Dependencies** | `core/ai_client.py`, `core/exceptions.py` |
| **Imports From** | `core.ai_client → AIClient`, `core.exceptions → AIServiceError` |

### `services/report_generator_service.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Generate downloadable analysis reports (PDF and JSON). |
| **Responsibilities** | — Assemble all analysis data into report structure<br>— Generate PDF using WeasyPrint (HTML → PDF)<br>— Generate JSON export<br>— Apply professional report template (CSS styling)<br>— Include all sections: Score, Skills, Experience, Recommendations, Improvements<br>— Handle file naming (UUID-based, non-guessable)<br>— Clean up old reports (TTL-based cleanup) |
| **Dependencies** | `core/db.py`, `models/report.py`, `models/analysis.py`, `core/exceptions.py`, `core/config.py`, `core/logging_config.py` |
| **Imports From** | `core.db → AnalysisRepository`, `models.report → AnalysisReport, ReportSection`, `models.analysis → AnalysisResult`, `core.exceptions → ReportError, PDFGenerationError`, `core.config → settings` |
| **External Libraries** | `weasyprint` (or `reportlab`), `jinja2` (HTML templating) |
| **Design Pattern** | Template Method Pattern — skeleton for report generation, subclasses for PDF vs JSON |

---

## 7. `core/` — Core Infrastructure Layer

### `core/__init__.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Package marker. Exports core infrastructure classes. |
| **Responsibilities** | Make `core` a proper package; re-export key classes for convenient importing |

### `core/config.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Centralized application configuration. Single source of truth for all settings. |
| **Responsibilities** | — Load env vars via `pydantic-settings`<br>— Validate required config (OPENAI_API_KEY)<br>— Provide typed access to all settings<br>— Support `.env` file loading<br>— Define defaults for optional settings<br>— Freeze settings after initialization (immutable) |
| **Dependencies** | `pydantic-settings`, `python-dotenv` |
| **Imports From** | `pydantic_settings import BaseSettings`, `pydantic import Field, SecretStr` |
| **Design Pattern** | Singleton Pattern — settings loaded once, accessible globally |

**Key Configuration Fields:**
```python
class Settings(BaseSettings):
    openai_api_key: SecretStr
    openai_model: str = "gpt-4o"
    openai_max_tokens: int = 4096
    openai_temperature: float = 0.3
    openai_retry_count: int = 3
    openai_timeout: int = 30
    database_url: str = "sqlite:///data/analyzer.db"
    max_file_size_mb: int = 10
    log_level: str = "INFO"
    log_format: str = "json"
    upload_dir: str = "data/uploads"
    report_dir: str = "data/reports"
    job_db_path: str = "data/job_database.json"
    job_cache_ttl_hours: int = 24
    max_analysis_per_session: int = 10
```

### `core/ai_client.py`

| Attribute | Detail |
|---|---|
| **Purpose** | OpenAI API client wrapper. Singleton with retry, rate-limiting, and token management. |
| **Responsibilities** | — Initialize OpenAI client with API key<br>— Implement exponential backoff retry (3 attempts)<br>— Track token usage per session<br>— Enforce rate limits (RPM/TPM)<br>— Support structured output (JSON mode)<br>— Provide methods: `extract_skills()`, `evaluate_experience()`, `generate_summary()`, `generate_improvements()`<br>— Log all API calls with duration and token count<br>— Handle API errors gracefully (timeout, rate limit, invalid request) |
| **Dependencies** | `core/config.py`, `core/exceptions.py`, `core/logging_config.py` |
| **Imports From** | `core.config → settings`, `core.exceptions → OpenAITimeoutError, OpenAIRateLimitError, OpenAITokenLimitError, OpenAISchemaError`, `core.logging_config → get_logger` |
| **External Libraries** | `openai` (OpenAI Python SDK) |
| **Design Pattern** | Singleton Pattern + Decorator Pattern (retry decorator) |

### `core/db.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Database access layer. SQLite connection manager with repository pattern. |
| **Responsibilities** | — Manage SQLite connection lifecycle<br>— Provide context manager for sessions<br>— Run database migrations on startup<br>— Implement repository classes for each entity:<br>  &nbsp;&nbsp;• `AnalysisRepository` — CRUD for analysis results<br>  &nbsp;&nbsp;• `JobRepository` — CRUD for job roles<br>  &nbsp;&nbsp;• `SessionRepository` — CRUD for user sessions<br>  &nbsp;&nbsp;• `FeedbackRepository` — CRUD for user feedback<br>— Use parameterized queries exclusively (no SQL injection)<br>— Support in-memory SQLite for testing |
| **Dependencies** | `core/config.py`, `core/exceptions.py`, `core/logging_config.py`, `models/*.py` |
| **Imports From** | `core.config → settings`, `core.exceptions → DatabaseError, ConnectionError, MigrationError, IntegrityError`, `models.analysis → AnalysisResult`, `models.job → JobRole`, `models.user → UserSession, UserFeedback` |
| **External Libraries** | `sqlite3` (stdlib), `sqlalchemy` (optional, for future migration) |
| **Design Pattern** | Repository Pattern — abstracts data access behind interfaces |

### `core/logging_config.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Structured logging setup for the entire application. |
| **Responsibilities** | — Configure root logger<br>— Set up JSON formatter (structured logs)<br>— Set up console handler (stdout)<br>— Set up rotating file handler (logs/analyzer.log)<br>— Set up error file handler (logs/errors.log, ERROR+ only)<br>— Create `get_logger(correlation_id)` factory<br>— Sanitize log messages (strip PII, mask API keys)<br>— Provide performance logging context manager |
| **Dependencies** | `core/config.py` |
| **Imports From** | `core.config → settings` |
| **External Libraries** | `logging` (stdlib), `python-json-logger` |

### `core/exceptions.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Custom exception hierarchy for the application. |
| **Responsibilities** | — Define base `ResumeAnalyzerError` exception<br>— Define all subclasses per error taxonomy<br>— Provide error codes for client-facing messages<br>— Include correlation ID in all exceptions<br>— Support serialization for logging |
| **Dependencies** | None (stdlib only) |
| **Imports From** | None |

**Exception Hierarchy (defined in this file):**
```
ResumeAnalyzerError
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

### `core/utils.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Shared utility functions used across the application. |
| **Responsibilities** | — File type detection via magic bytes<br>— Text sanitization (strip control chars, normalize whitespace)<br>— UUID v4 generation<br>— File size formatting<br>— Text chunking (for large resumes)<br>— Email/phone number regex extraction<br>— Date parsing utilities<br>— Jaccard similarity computation |
| **Dependencies** | None (stdlib only) |
| **Imports From** | `uuid`, `re`, `pathlib`, `mimetypes` (stdlib) |

---

## 8. `models/` — Domain Models Layer

### `models/__init__.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Package marker. Re-exports all model classes. |
| **Responsibilities** | Make `models` a proper package; provide convenient imports |

### `models/resume.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Resume-related domain models. |
| **Responsibilities** | Define: `Resume`, `ParsedResume`, `ResumeSection`, `Education`, `Project`, `Certification` |
| **Dependencies** | `pydantic` |
| **Design** | Pydantic BaseModel with validators for field constraints |

### `models/skills.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Skills-related domain models. |
| **Responsibilities** | Define: `Skill`, `SkillCategory` (enum), `SkillProficiency` (enum), `SkillInventory` |
| **Dependencies** | `pydantic` |
| **Design** | Pydantic BaseModel + Enum for categories |

### `models/experience.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Experience-related domain models. |
| **Responsibilities** | Define: `WorkExperience`, `ExperienceEvaluation`, `TimelineGap`, `ExperienceSummary` |
| **Dependencies** | `pydantic` |
| **Design** | Pydantic BaseModel with date validators |

### `models/analysis.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Analysis result domain models. Central model for the entire pipeline. |
| **Responsibilities** | Define: `AnalysisResult`, `ResumeScore`, `SectionScore`, `AnalysisContext`<br>Provide `from_gpt_response()` factory method<br>Provide `to_db_row()` / `from_db_row()` serialization |
| **Dependencies** | `pydantic`, `models/skills.py`, `models/experience.py`, `models/resume.py` |
| **Design Pattern** | Factory Pattern — `from_gpt_response()` constructs validated model from raw GPT JSON |

### `models/job.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Job-related domain models. |
| **Responsibilities** | Define: `JobRole`, `JobRecommendation`, `MatchResult`, `MissingSkill`, `JobFilter` |
| **Dependencies** | `pydantic`, `models/skills.py` |
| **Design** | Pydantic BaseModel with computed fields for match percentage |

### `models/report.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Report-related domain models. |
| **Responsibilities** | Define: `AnalysisReport`, `ReportSection`, `ReportMetadata`, `ReportFormat` (enum) |
| **Dependencies** | `pydantic`, `models/analysis.py` |
| **Design** | Pydantic BaseModel with serialization methods |

### `models/user.py`

| Attribute | Detail |
|---|---|
| **Purpose** | User session and feedback models. |
| **Responsibilities** | Define: `UserSession`, `UserFeedback`, `SessionState` |
| **Dependencies** | `pydantic` |
| **Design** | Pydantic BaseModel with timestamp auto-generation |

---

## 9. `data/` — Runtime Data

### `data/uploads/`

| Attribute | Detail |
|---|---|
| **Purpose** | Temporary storage for uploaded resume files. |
| **Responsibilities** | — Store uploaded files temporarily<br>— Auto-clean files after text extraction<br>— Encrypt files at rest (AES-256-GCM) |
| **Dependencies** | `services/parser_service.py`, `core/config.py` |
| **Gitignore** | YES — entire directory ignored |

### `data/reports/`

| Attribute | Detail |
|---|---|
| **Purpose** | Storage for generated PDF reports. |
| **Responsibilities** | — Store generated PDF files<br>— TTL-based cleanup (delete reports older than 24 hours)<br>— Serve files for download |
| **Dependencies** | `services/report_generator_service.py`, `core/config.py` |
| **Gitignore** | YES — entire directory ignored |

### `data/job_database.json`

| Attribute | Detail |
|---|---|
| **Purpose** | Curated job role dataset with required skills. |
| **Responsibilities** | — Provide structured job role data<br>— Each entry: job title, industry, required skills, experience level, description<br>— Used by `job_recommendation_service.py` for matching |
| **Dependencies** | `services/job_recommendation_service.py`, `services/missing_skills_service.py`, `models/job.py` |
| **Gitignore** | NO — committed to version control as seed data |

---

## 10. `db/` — Database Artifacts

### `db/schema.sql`

| Attribute | Detail |
|---|---|
| **Purpose** | Complete DDL for the SQLite database schema. |
| **Responsibilities** | Define all tables: `analyses`, `skills`, `work_experiences`, `job_roles`, `user_sessions`, `user_feedback`, `analysis_jobs` |
| **Dependencies** | Executed by `core/db.py` on first run |

### `db/migrations/001_initial_schema.sql`

| Attribute | Detail |
|---|---|
| **Purpose** | Initial database schema migration. |
| **Responsibilities** | Create all tables for v1.0 |

### `db/migrations/002_add_job_feedback.sql`

| Attribute | Detail |
|---|---|
| **Purpose** | Add job feedback table for user ratings on recommendations. |
| **Responsibilities** | Create `job_feedback` table with FK to `analyses` and `job_roles` |

### `db/seed.sql`

| Attribute | Detail |
|---|---|
| **Purpose** | Seed data for job roles and skill categories. |
| **Responsibilities** | Insert initial set of 50+ job roles with required skills across industries |

---

## 11. `tests/` — Test Suite

### `tests/conftest.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Pytest configuration and shared fixtures. |
| **Responsibilities** | — Override settings for test environment (mock API key, in-memory DB)<br>— Provide `sample_resume_text` fixture<br>— Provide `mock_openai_client` fixture<br>— Provide `in_memory_db` fixture<br>— Provide `sample_analysis_result` fixture<br>— Auto-clean temp files after tests |
| **Dependencies** | `pytest`, `pytest-mock`, `core/config.py`, `core/db.py`, `core/ai_client.py` |

### `tests/unit/` — Unit Tests

| File | Tests | Depends On |
|---|---|---|
| `test_parser_service.py` | Text extraction, file type detection, error handling, sanitization | `services/parser_service.py`, `fixtures/sample_resume.pdf/docx/txt` |
| `test_scoring_service.py` | Score calculation, edge cases, normalization | `services/scoring_service.py`, `models/analysis.py` |
| `test_skill_extraction.py` | GPT response parsing, categorization, deduplication, validation | `services/skill_extraction_service.py`, `fixtures/mock_openai_responses.py` |
| `test_experience_service.py` | Year extraction, gap detection, quality scoring | `services/experience_service.py`, `fixtures/mock_openai_responses.py` |
| `test_job_matching.py` | Jaccard similarity, threshold filtering, ranking | `services/job_recommendation_service.py`, `data/job_database.json` |
| `test_missing_skills.py` | Diff logic, relevance ranking, resource generation | `services/missing_skills_service.py` |
| `test_improvement_service.py` | Suggestion generation, formatting, prioritization | `services/improvement_service.py`, `fixtures/mock_openai_responses.py` |
| `test_report_generator.py` | PDF/JSON generation, structure, error handling | `services/report_generator_service.py`, `test_models.py` |
| `test_models.py` | Pydantic validation, serialization, factory methods | `models/*.py` |
| `test_utils.py` | File detection, sanitization, UUID, Jaccard | `core/utils.py` |

### `tests/integration/` — Integration Tests

| File | Tests | Depends On |
|---|---|---|
| `test_analyzer_pipeline.py` | Full pipeline orchestration, DB persistence, error propagation | `services/parser_service.py`, `services/analyzer_service.py`, `core/db.py`, `conftest.py` |
| `test_job_recommendation_flow.py` | Skills → Recommendations → Missing skills end-to-end | `services/job_recommendation_service.py`, `services/missing_skills_service.py`, `core/db.py` |
| `test_report_generation.py` | AnalysisResult → PDF/JSON, file structure, content validation | `services/report_generator_service.py`, `core/db.py` |
| `test_db_repository.py` | CRUD operations, migrations, constraints, edge cases | `core/db.py`, `db/migrations/`, `models/*.py` |

### `tests/e2e/` — End-to-End Tests

| File | Tests | Depends On |
|---|---|---|
| `test_upload_flow.py` | Upload PDF → Progress → Analysis results displayed | `app.py`, `pages/1_upload_resume.py`, Streamlit test runner |
| `test_analysis_flow.py` | Navigate pages → View skills → View recommendations → View improvements | `app.py`, `pages/2_analysis_results.py`, `pages/3_job_recommendations.py` |
| `test_download_flow.py` | Click download → PDF generated → File saved successfully | `app.py`, `pages/4_report_download.py` |

### `tests/fixtures/` — Test Data

| File | Purpose | Used By |
|---|---|---|
| `sample_resume.pdf` | Sample PDF resume for parser tests | `test_parser_service.py`, `test_analyzer_pipeline.py`, `test_upload_flow.py` |
| `sample_resume.docx` | Sample DOCX resume for parser tests | `test_parser_service.py`, `test_analyzer_pipeline.py` |
| `sample_resume.txt` | Sample plain text resume for parser tests | `test_parser_service.py`, `test_skill_extraction.py`, `conftest.py` |
| `parsed_resume_fixture.json` | Pre-parsed resume JSON for service tests | `test_scoring_service.py`, `test_job_matching.py`, `test_missing_skills.py` |
| `mock_openai_responses.py` | Mock GPT response fixtures for all AI-dependent services | `test_skill_extraction.py`, `test_experience_service.py`, `test_improvement_service.py`, `test_analyzer_pipeline.py` |

---

## 12. Dependency Relationship Map

### Layer Dependency Rule

```
pages/  ──────▶  ui/  ──────▶  components/
   │                              │
   │                              │
   └──────────▶  services/  ──────┘
                      │
                      │
                      ├──────▶  models/
                      │
                      └──────▶  core/
                                  │
                                  ├──────▶  config.py
                                  ├──────▶  ai_client.py  ──▶  OpenAI API
                                  ├──────▶  db.py  ──▶  SQLite
                                  ├──────▶  logging_config.py
                                  ├──────▶  exceptions.py
                                  └──────▶  utils.py
```

**Rules:**
1. `pages/` may import from `ui/`, `components/`, `services/`, `models/`, and `core/`
2. `ui/` may import from `components/` and `streamlit` only
3. `components/` may import from `models/` and `core/` only
4. `services/` may import from `models/` and `core/` only
5. `models/` may import from `pydantic` only (no project dependencies)
6. `core/` may import from `models/` and external libraries only
7. No layer may import from a higher layer (e.g., `services/` never imports from `pages/`)

### Detailed Dependency Matrix

```
┌───────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────┐
│ Module                            │ Depends On                                                                          │
├───────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────┤
│ app.py                            │ core.config, core.logging_config, pages.*                                            │
│ pages/1_upload_resume.py          │ ui.upload_widgets, services.parser_service, services.analyzer_service, models.analysis│
│ pages/2_analysis_results.py       │ ui.analysis_display, services.summary_service, services.improvement_service          │
│ pages/3_job_recommendations.py    │ ui.recommendation_display, services.job_recommendation_service, missing_skills       │
│ pages/4_report_download.py        │ ui.report_ui, services.report_generator_service, models.report                       │
│ ui/upload_widgets.py              │ components.sidebar, streamlit                                                         │
│ ui/analysis_display.py            │ components.score_gauge, components.skill_chart, streamlit                             │
│ ui/recommendation_display.py      │ components.job_card, streamlit                                                        │
│ ui/report_ui.py                   │ streamlit                                                                             │
│ ui/styles.py                      │ streamlit                                                                             │
│ components/sidebar.py             │ streamlit                                                                             │
│ components/score_gauge.py         │ streamlit                                                                             │
│ components/skill_chart.py         │ streamlit, plotly/matplotlib                                                          │
│ components/job_card.py            │ streamlit                                                                             │
│ components/feedback_form.py       │ core.db, models.user, streamlit                                                       │
│ services/parser_service.py        │ core.exceptions, core.utils, core.config, pdfplumber, python-docx, python-magic       │
│ services/analyzer_service.py      │ services.*_service, core.db, core.ai_client, core.exceptions, models.analysis         │
│ services/scoring_service.py       │ models.analysis, models.skills, models.experience                                     │
│ services/skill_extraction_service │ core.ai_client, models.skills, core.exceptions                                        │
│ services/experience_service.py    │ core.ai_client, models.experience, core.exceptions                                    │
│ services/summary_service.py       │ core.ai_client, core.exceptions                                                       │
│ services/job_recommendation.py    │ core.db, models.job, models.skills, core.config, core.exceptions                      │
│ services/missing_skills_service.py│ models.skills, models.job                                                              │
│ services/improvement_service.py   │ core.ai_client, core.exceptions                                                       │
│ services/report_generator.py      │ core.db, models.report, models.analysis, core.exceptions, weasyprint, jinja2          │
│ core/config.py                    │ pydantic-settings, pydantic                                                            │
│ core/ai_client.py                 │ core.config, core.exceptions, core.logging_config, openai                              │
│ core/db.py                        │ core.config, core.exceptions, core.logging_config, models.*, sqlite3                  │
│ core/logging_config.py            │ core.config, logging, python-json-logger                                              │
│ core/exceptions.py                │ (stdlib only)                                                                         │
│ core/utils.py                     │ (stdlib only)                                                                         │
│ models/resume.py                  │ pydantic                                                                               │
│ models/skills.py                  │ pydantic                                                                               │
│ models/experience.py              │ pydantic                                                                               │
│ models/analysis.py                │ pydantic, models.skills, models.experience, models.resume                              │
│ models/job.py                     │ pydantic, models.skills                                                                │
│ models/report.py                  │ pydantic, models.analysis                                                              │
│ models/user.py                    │ pydantic                                                                               │
└───────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Module Responsibility Summary

```
                               ┌──────────────────────────────────────────────────────────────┐
                               │                   app.py (Entry Point)                       │
                               │  Bootstrap, session state, page routing, lifecycle hooks      │
                               └──────────────────────────────────────────────────────────────┘
                                               │
            ┌──────────────────────────────────┼──────────────────────────────────┐
            ▼                                  ▼                                  ▼
┌──────────────────────────┐  ┌──────────────────────────────┐  ┌──────────────────────────────┐
│     pages/ (4 pages)     │  │      ui/ (5 modules)         │  │   components/ (5 modules)     │
│  User-facing page logic  │  │  Pure rendering, no logic    │  │  Reusable Streamlit widgets  │
│  Orchestrates UI + calls │  │  Only imports streamlit +    │  │  Charts, cards, gauges,      │
│  services for each step  │  │  components/                 │  │  sidebar, feedback           │
└──────────────────────────┘  └──────────────────────────────┘  └──────────────────────────────┘
         │                                                              │
         └──────────────────────────┬───────────────────────────────────┘
                                    ▼
          ┌─────────────────────────────────────────────────────────────┐
          │                  services/ (10 modules)                     │
          │  All business logic lives here                              │
          │  Parser → Analyzer → Scorer → Extractor → Evaluator →      │
          │  Summarizer → Recommender → MissingSkills → Improver →     │
          │  ReportGenerator                                            │
          │  No Streamlit imports allowed                               │
          └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
          ┌─────────────────────────────────────────────────────────────┐
          │                    models/ (7 modules)                      │
          │  Pydantic domain models — type safety, validation, DTOs     │
          │  Zero dependencies except pydantic                          │
          └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
          ┌─────────────────────────────────────────────────────────────┐
          │                    core/ (6 modules)                        │
          │  Infrastructure: config, AI client, DB, logging,           │
          │  exceptions, utils                                          │
          │  No business logic — pure infrastructure                    │
          └─────────────────────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
┌──────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│  OpenAI API      │   │  SQLite Database     │   │  Filesystem          │
│  GPT-4o          │   │  (analyses, jobs,    │   │  (uploads, reports,  │
│                  │   │   sessions, feedback)│   │   job_database.json) │
└──────────────────┘   └──────────────────────┘   └──────────────────────┘
```

---

## 14. Key Architectural Principles

| Principle | How It's Enforced |
|---|---|
| **Separation of Concerns** | Strict layering: `pages/` → `ui/` + `components/` → `services/` → `models/` → `core/`. No layer imports from a higher layer. |
| **Dependency Injection** | All services receive dependencies via constructor injection (`AIClient`, `DatabaseManager`, `Settings`). Enables trivial mocking in tests. |
| **Testability** | Every service is testable with mocked AI client and in-memory SQLite. Pure functions (scoring, matching) have no external deps. |
| **Single Responsibility** | Each file has exactly one well-defined responsibility. 10 services = 10 distinct business capabilities. |
| **Open/Closed** | New file formats → new parser strategy. New scoring criteria → new pipeline stage. No modification of existing code. |
| **Fail Fast** | Configuration validation at startup. File validation before processing. Schema validation on GPT responses. |
| **Defense in Depth** | File validation (magic bytes + extension + size). Input sanitization. Output schema validation. Parameterized queries. |
| **Observability** | Structured JSON logging with correlation IDs across all layers. Performance metrics on all AI calls. |