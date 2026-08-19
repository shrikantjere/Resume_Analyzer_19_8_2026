"""
Analysis results display components.

Renders the detailed analysis results including score gauges,
skills inventory, experience evaluation, summary, and improvements.
"""

from __future__ import annotations

from typing import Any, Optional

import streamlit as st

from components.score_gauge import render_score_bar, render_score_gauge
from components.skill_chart import render_skill_chart, render_skill_tags


def render_analysis_results(analysis: Any) -> None:
    """Render the complete analysis results page.

    Args:
        analysis: AnalysisResult object with all analysis data.
    """
    if not analysis:
        st.warning("No analysis data available. Please upload a resume first.")
        return

    # Header with overview
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        render_score_gauge(
            score=analysis.overall_score,
            label="Overall Resume Score",
            size="large",
        )

    # Quick stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Technical Skills",
            len(analysis.technical_skills),
        )
    with col2:
        st.metric(
            "Soft Skills",
            len(analysis.soft_skills),
        )
    with col3:
        exp_years = analysis.total_experience_years
        st.metric(
            "Experience",
            f"{exp_years:.0f} years" if exp_years > 0 else "N/A",
        )
    with col4:
        st.metric(
            "Experience Level",
            analysis.experience_level,
        )

    st.divider()

    # Section scores
    render_section_scores(analysis)

    # Skills section
    render_skills_section(analysis)

    # Experience section
    render_experience_section(analysis)

    # Summary section
    render_summary_section(analysis)

    # Improvements section
    render_improvements_section(analysis)


def render_section_scores(analysis: Any) -> None:
    """Render section-wise score breakdown.

    Args:
        analysis: AnalysisResult object.
    """
    st.subheader("📊 Section Scores")

    score = analysis.resume_score
    if not score or not score.section_scores:
        st.caption("No section scores available.")
        return

    cols = st.columns(2)
    for i, section in enumerate(score.section_scores):
        with cols[i % 2]:
            render_score_bar(
                score=section.score,
                label=section.section_name,
                show_value=True,
            )
            if section.feedback:
                st.caption(section.feedback)

    st.divider()

    # Additional scores
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ATS Optimization", f"{score.ats_optimization_score:.0f}/100")
    with col2:
        st.metric("Completeness", f"{score.completeness_score:.0f}/100")
    with col3:
        st.metric("Formatting", f"{score.formatting_score:.0f}/100")


def render_skills_section(analysis: Any) -> None:
    """Render the skills inventory section.

    Args:
        analysis: AnalysisResult object.
    """
    st.subheader("🎯 Skills Inventory")

    inv = analysis.skill_inventory
    if not inv:
        st.caption("No skills extracted.")
        return

    # Category distribution
    if inv.by_category:
        render_skill_chart(inv.by_category, chart_type="bar")

    # Technical skills
    st.markdown("#### 💻 Technical Skills")
    if inv.technical_skills:
        tech_names = [s.name for s in inv.technical_skills]
        # Group by category for display
        tech_by_cat: dict[str, list[str]] = {}
        for s in inv.technical_skills:
            cat = s.category.value
            if cat not in tech_by_cat:
                tech_by_cat[cat] = []
            tech_by_cat[cat].append(s.name)

        for cat, skills in tech_by_cat.items():
            with st.expander(f"{cat} ({len(skills)})", expanded=False):
                render_skill_tags(skills, category=cat)
    else:
        st.caption("No technical skills detected.")

    # Soft skills
    st.markdown("#### 🤝 Soft Skills")
    if inv.soft_skills:
        soft_names = [s.name for s in inv.soft_skills]
        render_skill_tags(soft_names, category="Soft Skill")
    else:
        st.caption("No soft skills detected.")

    st.divider()


def render_experience_section(analysis: Any) -> None:
    """Render the experience evaluation section.

    Args:
        analysis: AnalysisResult object.
    """
    st.subheader("💼 Experience Assessment")

    exp = analysis.experience_evaluation
    if not exp:
        st.caption("No experience data available.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Experience", f"{exp.total_years:.1f} years")
    with col2:
        st.metric("Quality Score", f"{exp.quality_score:.0f}/100")
    with col3:
        st.metric("Level", exp.experience_level)

    if exp.has_quantified_achievements:
        st.success("✅ Your resume includes quantified achievements — great for ATS!")

    if exp.gaps:
        with st.expander("📅 Employment Timeline Gaps", expanded=False):
            for gap in exp.gaps:
                st.markdown(
                    f"- **{gap.get('start_date', '?')}** to **{gap.get('end_date', '?')}** "
                    f"({gap.get('duration_months', 0)} months)"
                )
                if gap.get("description"):
                    st.caption(gap["description"])

    st.divider()


def render_summary_section(analysis: Any) -> None:
    """Render the generated professional summary.

    Args:
        analysis: AnalysisResult object.
    """
    st.subheader("📝 Professional Summary")

    if not analysis.summary:
        st.caption("No summary generated.")
        return

    st.markdown(
        f"""
        <div style="
            background: #f0f7ff;
            border-left: 4px solid #1a73e8;
            padding: 1rem 1.5rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
            font-style: italic;
            line-height: 1.6;
        ">
            {analysis.summary}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()


def render_improvements_section(analysis: Any) -> None:
    """Render the improvement suggestions.

    Args:
        analysis: AnalysisResult object.
    """
    st.subheader("✨ Improvement Suggestions")

    if not analysis.improvements:
        st.caption("No suggestions available.")
        return

    for i, imp in enumerate(analysis.improvements):
        section = imp.get("section", "General")
        suggestion = imp.get("suggestion", "")
        priority = imp.get("priority", "Medium")
        example = imp.get("example", "")

        # Priority icon
        priority_icons = {
            "High": "🔴",
            "Medium": "🟡",
            "Low": "🟢",
        }
        icon = priority_icons.get(priority, "⚪")

        with st.expander(
            f"{icon} [{priority}] {section}: {suggestion[:60]}{'...' if len(suggestion) > 60 else ''}",
            expanded=priority == "High",
        ):
            st.markdown(f"**Suggestion:** {suggestion}")
            if example:
                st.markdown(
                    f"""
                    <div style="
                        background: #f8f9fa;
                        padding: 0.75rem;
                        border-radius: 8px;
                        margin-top: 0.5rem;
                        font-size: 0.9rem;
                    ">
                        <strong>Example:</strong><br>
                        {example.replace(chr(10), '<br>')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )