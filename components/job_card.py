"""
Job recommendation card component.

Renders individual job recommendation cards with
match percentage, skills, and expandable details.
"""

from __future__ import annotations

from typing import Any, Optional

import streamlit as st


def render_job_card(
    recommendation: dict[str, Any],
    index: int = 0,
    expanded: bool = False,
) -> None:
    """Render a job recommendation card.

    Args:
        recommendation: Job recommendation data dict.
        index: Card index for unique key generation.
        expanded: Whether to expand the detail section.
    """
    title = recommendation.get("title", "Unknown Role")
    match_pct = recommendation.get("match_percentage", 0)
    description = recommendation.get("description", "")
    industry = recommendation.get("industry", "")
    experience_level = recommendation.get("experience_level", "Mid")
    required_skills = recommendation.get("required_skills", [])
    matched_skills = recommendation.get("matched_skills", [])
    missing_skills = recommendation.get("missing_skills", [])

    # Color based on match percentage
    if match_pct >= 70:
        color = "#2ecc71"
        badge = "🔥 Strong Match"
    elif match_pct >= 50:
        color = "#f1c40f"
        badge = "👍 Good Match"
    elif match_pct >= 30:
        color = "#e67e22"
        badge = "📈 Potential"
    else:
        color = "#95a5a6"
        badge = "🔍 Explore"

    with st.container(border=True):
        # Header row
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {title}")
            st.caption(f"{industry} • {experience_level} Level")
        with col2:
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <div style="font-size: 2rem; font-weight: bold; color: {color};">
                        {match_pct:.0f}%
                    </div>
                    <div style="font-size: 0.75rem; color: #666;">Match</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Match bar
        st.markdown(
            f"""
            <div style="background: #e0e0e0; border-radius: 10px; height: 6px; margin: 0.5rem 0;">
                <div style="width: {match_pct}%; background: {color}; height: 100%; border-radius: 10px;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Badge
        st.markdown(
            f'<span style="color: {color}; font-weight: 500; font-size: 0.9rem;">{badge}</span>',
            unsafe_allow_html=True,
        )

        # Description
        if description:
            st.markdown(description[:200] + ("..." if len(description) > 200 else ""))

        # Expandable details
        with st.expander("View Details", expanded=expanded):
            # Required skills
            if required_skills:
                st.markdown("**Required Skills:**")
                cols = st.columns(4)
                for i, skill in enumerate(required_skills):
                    col_idx = i % 4
                    is_matched = skill in matched_skills
                    if is_matched:
                        cols[col_idx].markdown(
                            f'✅ {skill}',
                            help="Skill found in your resume",
                        )
                    else:
                        cols[col_idx].markdown(
                            f'❌ {skill}',
                            help="Skill missing from your resume",
                        )

            # Missing skills
            if missing_skills:
                st.markdown("---")
                st.markdown("**Skills to Acquire:**")
                missing_html = " ".join(
                    [
                        f'<span style="background: #fce4ec; color: #c62828; '
                        f'padding: 0.1rem 0.5rem; border-radius: 12px; '
                        f'font-size: 0.8rem; margin: 0.1rem;">{s}</span>'
                        for s in missing_skills[:5]
                    ]
                )
                st.markdown(missing_html, unsafe_allow_html=True)


def render_match_distribution(
    recommendations: list[dict[str, Any]],
) -> None:
    """Render a visual distribution of match percentages.

    Args:
        recommendations: List of job recommendation dicts.
    """
    if not recommendations:
        return

    st.markdown("### Match Distribution")

    # Create color-coded segments
    colors = []
    for rec in recommendations:
        pct = rec.get("match_percentage", 0)
        if pct >= 70:
            colors.append("#2ecc71")
        elif pct >= 50:
            colors.append("#f1c40f")
        elif pct >= 30:
            colors.append("#e67e22")
        else:
            colors.append("#95a5a6")

    # Create a gradient bar
    segments = []
    for i, rec in enumerate(recommendations):
        pct = max(5, rec.get("match_percentage", 0))  # Minimum 5% for visibility
        segments.append(
            f'<div style="flex: {pct}; height: 20px; background: {colors[i]}; '
            f'border-radius: {"10px 0 0 10px" if i == 0 else "0 10px 10px 0" if i == len(recommendations)-1 else "0"}; '
            f'min-width: 20px; position: relative;">'
            f'<span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); '
            f'font-size: 0.7rem; color: white; font-weight: bold;">{rec.get("match_percentage", 0):.0f}%</span>'
            f'</div>'
        )

    bar_html = f'<div style="display: flex; gap: 2px; margin: 1rem 0;">{"".join(segments)}</div>'
    st.markdown(bar_html, unsafe_allow_html=True)

    # Legend
    st.caption(
        "🟢 Strong (70%+)  🟡 Good (50-69%)  🟠 Potential (30-49%)  ⚪ Explore (<30%)"
    )