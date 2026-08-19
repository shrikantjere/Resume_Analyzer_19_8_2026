"""
Report download UI components.

Renders the report download page with preview,
download buttons, and export options.
"""

from __future__ import annotations

from typing import Any, Optional

import streamlit as st


def render_report_page(analysis: Any) -> None:
    """Render the report download page.

    Args:
        analysis: AnalysisResult object with analysis data.
    """
    if not analysis:
        st.info(
            "No analysis data available. Please analyze your resume first.",
            icon="📄",
        )
        return

    st.subheader("📥 Download Analysis Report")

    # Report preview
    render_report_preview(analysis)

    st.divider()

    # Download options
    render_download_buttons(analysis)


def render_report_preview(analysis: Any) -> None:
    """Render a preview of the analysis report.

    Args:
        analysis: AnalysisResult object.
    """
    st.markdown("### 📋 Report Preview")

    with st.container(border=True):
        st.markdown("#### AI Resume Analyzer — Report")
        st.caption("Comprehensive Resume Analysis")

        # Score summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Score", f"{analysis.overall_score:.0f}/100")
        with col2:
            st.metric("Skills Found", len(analysis.all_skill_names))
        with col3:
            st.metric("Experience", analysis.experience_level)

        st.divider()

        # Report sections
        tabs = st.tabs(["📊 Scores", "🎯 Skills", "💼 Experience", "💡 Recommendations", "✨ Improvements"])

        with tabs[0]:
            score = analysis.resume_score
            st.markdown(f"**Overall:** {score.overall:.0f}/100")
            for s in score.section_scores:
                st.markdown(f"- {s.section_name}: {s.score:.0f}/100 — {s.feedback}")

        with tabs[1]:
            st.markdown("**Technical Skills:** " + ", ".join(analysis.technical_skill_names))
            st.markdown("**Soft Skills:** " + ", ".join(analysis.soft_skill_names))

        with tabs[2]:
            exp = analysis.experience_evaluation
            st.markdown(f"**Total Experience:** {exp.total_years:.1f} years")
            st.markdown(f"**Level:** {exp.experience_level}")
            st.markdown(f"**Quality Score:** {exp.quality_score:.0f}/100")

        with tabs[3]:
            if analysis.job_recommendations:
                for rec in analysis.job_recommendations[:3]:
                    st.markdown(
                        f"- **{rec.get('title', '')}** — "
                        f"Match: {rec.get('match_percentage', 0):.0f}%"
                    )
            else:
                st.caption("No recommendations available.")

        with tabs[4]:
            if analysis.improvements:
                for imp in analysis.improvements[:3]:
                    st.markdown(f"- [{imp.get('priority', 'Medium')}] {imp.get('suggestion', '')}")
            else:
                st.caption("No improvements available.")


def render_download_buttons(analysis: Any) -> None:
    """Render the download buttons for PDF and JSON.

    Args:
        analysis: AnalysisResult object.
    """
    st.markdown("### 💾 Download Options")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "📄 Download PDF Report",
            type="primary",
            use_container_width=True,
            help="Download a professional PDF report of your analysis",
        ):
            with st.spinner("Generating PDF report..."):
                try:
                    from services.report_generator_service import ReportGeneratorService

                    generator = ReportGeneratorService()
                    pdf_path = generator.generate_pdf(analysis)

                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 Save PDF",
                            data=f,
                            file_name=f"resume_analysis_{analysis.correlation_id[:8]}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    st.success("✅ PDF report generated!")
                except Exception as e:
                    st.error(f"Failed to generate PDF: {e}")

    with col2:
        if st.button(
            "📊 Download JSON Data",
            use_container_width=True,
            help="Download analysis data in JSON format",
        ):
            with st.spinner("Generating JSON export..."):
                try:
                    from services.report_generator_service import ReportGeneratorService

                    generator = ReportGeneratorService()
                    json_path = generator.generate_json(analysis)

                    with open(json_path, "rb") as f:
                        st.download_button(
                            label="📥 Save JSON",
                            data=f,
                            file_name=f"resume_analysis_{analysis.correlation_id[:8]}.json",
                            mime="application/json",
                            use_container_width=True,
                        )
                    st.success("✅ JSON data exported!")
                except Exception as e:
                    st.error(f"Failed to generate JSON: {e}")

    # Shareable summary
    st.divider()
    with st.expander("🔗 Shareable Summary", expanded=False):
        summary_text = f"""
AI Resume Analyzer Results
--------------------------
Overall Score: {analysis.overall_score:.0f}/100
Technical Skills: {', '.join(analysis.technical_skill_names[:10])}
Experience: {analysis.total_experience_years:.1f} years ({analysis.experience_level})
Top Recommendations: {', '.join([r.get('title', '') for r in analysis.job_recommendations[:3]])}
        """
        st.text_area("Copy this summary to share:", summary_text, height=150)