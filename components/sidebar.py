"""
Navigation sidebar component.

Renders the app navigation menu with page links,
session info, and theme controls.
"""

from __future__ import annotations

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx


def render_sidebar() -> None:
    """Render the navigation sidebar with page links and session info."""
    with st.sidebar:
        # App branding
        st.markdown(
            """
            <div style="text-align: center; padding: 1rem 0;">
                <h1 style="font-size: 1.5rem; margin: 0;">📄</h1>
                <h2 style="font-size: 1.1rem; margin: 0.5rem 0 0 0; color: #1a73e8;">
                    AI Resume Analyzer
                </h2>
                <p style="font-size: 0.8rem; color: #666; margin: 0.2rem 0;">
                    Analyze & Improve Your Resume
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Navigation
        st.subheader("Navigation", divider="gray")

        nav_items = {
            "upload": {"label": "📤 Upload Resume", "page": "1_upload_resume"},
            "analysis": {"label": "📊 Analysis Results", "page": "2_analysis_results"},
            "recommendations": {"label": "💡 Job Recommendations", "page": "3_job_recommendations"},
            "report": {"label": "📥 Download Report", "page": "4_report_download"},
        }

        # Determine current page
        ctx = get_script_run_ctx()
        current_page = "upload"
        if ctx and ctx.page_script_hash:
            pass  # Streamlit handles page routing

        # Use session state for current page tracking
        current_page = st.session_state.get("current_page", "upload")

        for key, item in nav_items.items():
            is_active = current_page == key
            disabled = key != "upload" and not st.session_state.get("analysis_complete", False)

            if disabled:
                st.button(
                    item["label"],
                    key=f"nav_{key}",
                    disabled=True,
                    use_container_width=True,
                )
            elif is_active:
                st.button(
                    f"👉 {item['label']}",
                    key=f"nav_{key}_active",
                    use_container_width=True,
                    type="primary",
                )
            else:
                if st.button(
                    item["label"],
                    key=f"nav_{key}",
                    use_container_width=True,
                ):
                    st.session_state["current_page"] = key
                    st.rerun()

        st.divider()

        # Session info
        st.subheader("Session Info", divider="gray")
        analysis_count = st.session_state.get("analysis_count", 0)
        st.caption(f"Analyses this session: **{analysis_count}**")

        if st.session_state.get("correlation_id"):
            with st.expander("Debug Info", expanded=False):
                st.code(
                    f"Analysis ID: {st.session_state.get('correlation_id', 'N/A')}",
                    language="text",
                )

        # Feedback link
        st.divider()
        st.caption(
            "Powered by **OpenAI GPT-4o** | "
            "[Report Issue](mailto:support@resumeanalyzer.com)"
        )