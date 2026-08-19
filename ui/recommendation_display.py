"""
Job recommendation display components.

Renders the job recommendations page with match distribution,
recommendation cards, missing skills, and learning suggestions.
"""

from __future__ import annotations

from typing import Any, Optional

import streamlit as st

from components.job_card import render_job_card, render_match_distribution
from components.skill_chart import render_skill_tags


def render_recommendations_page(
    recommendations: list[dict[str, Any]],
    missing_skills: list[dict[str, Any]],
    learning_suggestions: list[dict[str, str]],
    technical_skills: list[str],
    soft_skills: list[str],
) -> None:
    """Render the complete job recommendations page.

    Args:
        recommendations: List of job recommendation dicts.
        missing_skills: List of missing skill dicts.
        learning_suggestions: List of learning suggestion dicts.
        technical_skills: List of technical skill names.
        soft_skills: List of soft skill names.
    """
    if not recommendations:
        st.info(
            "No job recommendations available yet. "
            "Please analyze your resume first.",
            icon="💡",
        )
        return

    st.subheader("💡 Job Recommendations")

    # Match distribution overview
    render_match_distribution(recommendations)

    st.divider()

    # Filters
    with st.expander("🔍 Filter Recommendations", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            industries = list(set(r.get("industry", "") for r in recommendations if r.get("industry")))
            selected_industries = st.multiselect(
                "Industry",
                options=industries,
                default=[],
            )
        with col2:
            levels = list(set(r.get("experience_level", "") for r in recommendations if r.get("experience_level")))
            selected_levels = st.multiselect(
                "Experience Level",
                options=levels,
                default=[],
            )

        min_match = st.slider(
            "Minimum Match %",
            min_value=0,
            max_value=100,
            value=0,
        )

    # Apply filters
    filtered = recommendations
    if selected_industries:
        filtered = [r for r in filtered if r.get("industry") in selected_industries]
    if selected_levels:
        filtered = [r for r in filtered if r.get("experience_level") in selected_levels]
    if min_match > 0:
        filtered = [r for r in filtered if r.get("match_percentage", 0) >= min_match]

    # Display recommendations
    st.markdown(f"### Top {len(filtered)} Job Matches")

    for i, rec in enumerate(filtered):
        render_job_card(rec, index=i, expanded=(i == 0))

    st.divider()

    # Missing skills section
    render_missing_skills_section(missing_skills, learning_suggestions)

    # Skill gap summary
    render_skill_gap_summary(missing_skills, technical_skills, soft_skills)


def render_missing_skills_section(
    missing_skills: list[dict[str, Any]],
    learning_suggestions: list[dict[str, str]],
) -> None:
    """Render the missing skills identification section.

    Args:
        missing_skills: List of missing skill dicts.
        learning_suggestions: List of learning suggestion dicts.
    """
    st.subheader("📚 Skills to Develop")

    if not missing_skills:
        st.success("Your resume covers the key skills for your target roles!")
        return

    # Create a table-like display
    for skill in missing_skills[:10]:
        skill_name = skill.get("skill_name", "")
        relevance = skill.get("relevance_score", 0)
        demand = skill.get("demand_level", "Medium")
        roles = skill.get("related_roles", [])

        # Color coding
        if demand == "High":
            demand_color = "#e74c3c"
        elif demand == "Medium":
            demand_color = "#f39c12"
        else:
            demand_color = "#2ecc71"

        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{skill_name}**")
                if roles:
                    st.caption(f"Required for: {', '.join(roles[:3])}")
            with col2:
                st.markdown(
                    f'<span style="color: {demand_color}; font-weight: bold;">{demand} Demand</span>',
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(f"Relevance: **{relevance:.0%}**")

    # Learning suggestions
    if learning_suggestions:
        st.markdown("#### 🎓 Learning Resources")
        for suggestion in learning_suggestions[:5]:
            skill = suggestion.get("skill", "")
            resource = suggestion.get("resource", "")
            st.markdown(
                f"- **{skill}**: [Learn more]({resource})" if resource
                else f"- **{skill}**: Online courses recommended"
            )


def render_skill_gap_summary(
    missing_skills: list[dict[str, Any]],
    technical_skills: list[str],
    soft_skills: list[str],
) -> None:
    """Render a skill gap summary visualization.

    Args:
        missing_skills: List of missing skill dicts.
        technical_skills: List of technical skill names.
        soft_skills: List of soft skill names.
    """
    st.divider()
    st.subheader("📊 Skill Gap Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Skills You Have**")
        all_current = technical_skills + soft_skills
        if all_current:
            render_skill_tags(all_current, max_display=15)
        else:
            st.caption("No skills detected.")

    with col2:
        st.markdown("**Skills to Acquire**")
        if missing_skills:
            missing_names = [s.get("skill_name", "") for s in missing_skills[:10]]
            render_skill_tags(missing_names, category="Data Science", max_display=10)
        else:
            st.caption("No missing skills identified.")