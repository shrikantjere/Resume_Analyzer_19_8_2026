"""
Analysis results page.

Displays the detailed analysis results including score,
skills, experience, summary, and improvement suggestions.
"""

from __future__ import annotations

import streamlit as st

from core.logging_config import get_logger
from ui.analysis_display import render_analysis_results

logger = get_logger(__name__)


def run() -> None:
    """Render the analysis results page."""
    st.title("📊 Analysis Results")

    analysis = st.session_state.get("analysis_result")

    if analysis is None:
        st.warning(
            "No analysis data available. Please upload and analyze your resume first.",
            icon="⚠️",
        )
        if st.button("📤 Go to Upload Page", type="primary"):
            st.session_state["current_page"] = "upload"
            st.rerun()
        return

    # Render full analysis
    render_analysis_results(analysis)

    # Navigation buttons
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("◀️ New Analysis", use_container_width=True):
            st.session_state["analysis_complete"] = False
            st.session_state["current_page"] = "upload"
            st.rerun()
    with col2:
        if st.button("💡 View Recommendations ▶️", type="primary", use_container_width=True):
            st.session_state["current_page"] = "recommendations"
            st.rerun()
    with col3:
        if st.button("📥 Download Report", use_container_width=True):
            st.session_state["current_page"] = "report"
            st.rerun()