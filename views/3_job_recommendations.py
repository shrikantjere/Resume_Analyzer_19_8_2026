"""
Job recommendations page.

Displays job recommendations, missing skills, and
learning suggestions based on the analysis results.
"""

from __future__ import annotations

import streamlit as st

from core.logging_config import get_logger
from ui.recommendation_display import render_recommendations_page

logger = get_logger(__name__)


def run() -> None:
    """Render the job recommendations page."""
    st.title("💡 Job Recommendations & Skill Gaps")

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

    render_recommendations_page(
        recommendations=analysis.job_recommendations,
        missing_skills=analysis.missing_skills,
        learning_suggestions=analysis.learning_suggestions,
        technical_skills=analysis.technical_skill_names,
        soft_skills=analysis.soft_skill_names,
    )

    # Navigation buttons
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("◀️ Back to Analysis", use_container_width=True):
            st.session_state["current_page"] = "analysis"
            st.rerun()
    with col2:
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state["analysis_complete"] = False
            st.session_state["current_page"] = "upload"
            st.rerun()
    with col3:
        if st.button("📥 Download Report ▶️", type="primary", use_container_width=True):
            st.session_state["current_page"] = "report"
            st.rerun()