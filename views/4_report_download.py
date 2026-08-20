"""
Report download page.

Provides report preview, download buttons (PDF/JSON),
and export options for the analysis results.
"""

from __future__ import annotations

import streamlit as st

from core.logging_config import get_logger
from ui.report_ui import render_report_page

logger = get_logger(__name__)


def run() -> None:
    """Render the report download page."""
    st.title("📥 Download Report")

    analysis = st.session_state.get("analysis_result")

    if analysis is None:
        st.warning(
            "No analysis data available. Please analyze your resume first.",
            icon="⚠️",
        )
        if st.button("📤 Go to Upload Page", type="primary"):
            st.session_state["current_page"] = "upload"
            st.rerun()
        return

    render_report_page(analysis)

    # Navigation buttons
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀️ Back to Recommendations", use_container_width=True):
            st.session_state["current_page"] = "recommendations"
            st.rerun()
    with col2:
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state["analysis_complete"] = False
            st.session_state["current_page"] = "upload"
            st.rerun()