"""
Resume upload page.

This is the first page users see. It handles file uploads,
text pasting, and triggers the initial analysis pipeline.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import streamlit as st

from core.exceptions import (
    FileCorruptedError,
    FileTooLargeError,
    ResumeAnalyzerError,
    TextExtractionError,
    UnsupportedFileTypeError,
)
from core.logging_config import get_logger
from services.analyzer_service import AnalyzerService
from ui.upload_widgets import (
    render_text_paste_area,
    render_upload_error,
    render_upload_form,
    render_upload_progress,
    render_upload_requirements,
)

logger = get_logger(__name__)


def run() -> None:
    """Render the upload page."""
    st.title("📄 Upload Your Resume")
    st.markdown(
        "Get a comprehensive AI-powered analysis of your resume, "
        "including skill extraction, job recommendations, and improvement suggestions."
    )

    st.divider()

    # Two input methods
    tab1, tab2 = st.tabs(["📁 Upload File", "✍️ Paste Text"])

    with tab1:
        uploaded_file = render_upload_form()

        if uploaded_file is not None:
            _handle_file_upload(uploaded_file)

    with tab2:
        resume_text, submitted = render_text_paste_area()

        if submitted and resume_text.strip():
            _handle_text_analysis(resume_text)

    # Requirements
    st.divider()
    render_upload_requirements()


def _handle_file_upload(uploaded_file) -> None:
    """Handle an uploaded resume file.

    Args:
        uploaded_file: The uploaded file object from Streamlit.
    """
    if st.button(
        "🔍 Analyze Uploaded Resume",
        type="primary",
        use_container_width=True,
        key="analyze_uploaded",
    ):
        try:
            # Save uploaded file to temp location
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=Path(uploaded_file.name).suffix,
            ) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            # Run analysis
            progress_placeholder = st.empty()
            with progress_placeholder.container():
                render_upload_progress()

            analyzer = AnalyzerService()
            result = analyzer.analyze_file(
                file_path=tmp_path,
                session_id=st.session_state.get("session_id", "default"),
            )

            # Clean up temp file
            os.unlink(tmp_path)

            # Store result in session state
            st.session_state["analysis_result"] = result
            st.session_state["analysis_complete"] = True
            st.session_state["correlation_id"] = result.correlation_id
            st.session_state["analysis_count"] = (
                st.session_state.get("analysis_count", 0) + 1
            )
            st.session_state["current_page"] = "analysis"

            progress_placeholder.empty()
            st.success("✅ Analysis complete! View your results below.")
            st.page_link("pages/2_analysis_results.py", label="📊 View Analysis Results")

        except UnsupportedFileTypeError as e:
            render_upload_error(str(e))
        except FileTooLargeError as e:
            render_upload_error(str(e))
        except FileCorruptedError as e:
            render_upload_error(str(e))
        except TextExtractionError as e:
            render_upload_error(str(e))
        except ResumeAnalyzerError as e:
            render_upload_error(str(e))
        except Exception as e:
            logger.error("Unexpected upload error: %s", e, exc_info=True)
            render_upload_error(f"An unexpected error occurred: {e}")


def _handle_text_analysis(resume_text: str) -> None:
    """Handle analysis of pasted resume text.

    Args:
        resume_text: The pasted resume text.
    """
    try:
        progress_placeholder = st.empty()
        with progress_placeholder.container():
            render_upload_progress()

        analyzer = AnalyzerService()
        result = analyzer.analyze_text(
            resume_text=resume_text,
            session_id=st.session_state.get("session_id", "default"),
        )

        # Store result in session state
        st.session_state["analysis_result"] = result
        st.session_state["analysis_complete"] = True
        st.session_state["correlation_id"] = result.correlation_id
        st.session_state["analysis_count"] = (
            st.session_state.get("analysis_count", 0) + 1
        )
        st.session_state["current_page"] = "analysis"

        progress_placeholder.empty()
        st.success("✅ Analysis complete! View your results below.")
        st.page_link("pages/2_analysis_results.py", label="📊 View Analysis Results")

    except ResumeAnalyzerError as e:
        render_upload_error(str(e))
    except Exception as e:
        logger.error("Unexpected text analysis error: %s", e, exc_info=True)
        render_upload_error(f"An unexpected error occurred: {e}")