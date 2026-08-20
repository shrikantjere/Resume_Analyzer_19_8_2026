"""
AI Resume Analyzer — Main Entry Point.

A Streamlit application that analyzes resumes using AI,
extracts skills, evaluates experience, and provides
job recommendations and improvement suggestions.

Usage:
    streamlit run app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

# Ensure the project root is in the Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.config import get_settings
from core.db import DatabaseManager
from core.exceptions import ConfigurationError, MissingAPIKeyError
from core.logging_config import get_logger
from core.utils import generate_id
from ui.styles import apply_custom_styles

logger = get_logger(__name__)


# ── Page Configuration ──────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Session State Initialization ─────────────────────────────────────────

def init_session_state() -> None:
    """Initialize all session state variables."""
    defaults = {
        "session_id": generate_id(),
        "analysis_result": None,
        "analysis_complete": False,
        "correlation_id": None,
        "analysis_count": 0,
        "current_page": "upload",
        "initialized": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ── Application Bootstrap ────────────────────────────────────────────────

def bootstrap() -> None:
    """Initialize application components on first run."""
    try:
        # Validate configuration
        settings = get_settings()
        _ = settings.openai_api_key  # Will raise if missing

        # Initialize database
        db = DatabaseManager()
        db.run_migrations()

        # Ensure data directories exist
        Path(settings.upload_path).mkdir(parents=True, exist_ok=True)
        Path(settings.report_path).mkdir(parents=True, exist_ok=True)

        logger.info("Application bootstrap complete")

    except ConfigurationError as e:
        st.error(
            f"⚠️ Configuration Error: {e}\n\n"
            "Please ensure your `.env` file is properly configured.",
            icon="🚨",
        )
        st.stop()
    except Exception as e:
        logger.error("Bootstrap failed: %s", e, exc_info=True)
        st.error(
            "⚠️ Application initialization failed. Please check the logs.",
            icon="🚨",
        )
        st.stop()


# ── Main Application ─────────────────────────────────────────────────────

def main() -> None:
    """Main application entry point."""
    # Initialize
    init_session_state()
    apply_custom_styles()

    # Bootstrap on first run
    if "bootstrapped" not in st.session_state:
        bootstrap()
        st.session_state["bootstrapped"] = True

    # Render sidebar
    from components.sidebar import render_sidebar
    render_sidebar()

    # Page routing
    current_page = st.session_state.get("current_page", "upload")

    # Header
    st.markdown(
        """
        <div style="text-align: center; padding: 1rem 0 0.5rem 0;">
            <h1 style="font-size: 2.2rem; color: #1a73e8; margin: 0;">
                📄 AI Resume Analyzer
            </h1>
            <p style="font-size: 1rem; color: #666; margin: 0.3rem 0 0 0;">
                Upload your resume and get AI-powered insights, job recommendations, and improvement suggestions
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    # Route to the appropriate page
    if current_page == "upload" or not st.session_state.get("analysis_complete"):
        import importlib
        page_upload = importlib.import_module("views.1_upload_resume")
        page_upload.run()
    elif current_page == "analysis":
        import importlib
        page_analysis = importlib.import_module("views.2_analysis_results")
        page_analysis.run()
    elif current_page == "recommendations":
        import importlib
        page_recommendations = importlib.import_module("views.3_job_recommendations")
        page_recommendations.run()
    elif current_page == "report":
        import importlib
        page_report = importlib.import_module("views.4_report_download")
        page_report.run()
    else:
        import importlib
        page_upload = importlib.import_module("views.1_upload_resume")
        page_upload.run()

    # Footer
    st.divider()
    st.markdown(
        """
        <div style="text-align: center; padding: 1rem 0; color: #999; font-size: 0.8rem;">
            <p>
                AI Resume Analyzer v1.0.0 | Powered by OpenAI GPT-4o |
                <a href="https://github.com/yourusername/resume-analyzer" style="color: #1a73e8;">GitHub</a>
            </p>
            <p>
                Your data is processed securely and not stored permanently.
                See our <a href="#" style="color: #1a73e8;">Privacy Policy</a> for details.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()