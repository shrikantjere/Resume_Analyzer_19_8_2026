"""
Skill chart component.

Renders skill category visualizations using Plotly
for radar/bar charts and category distribution.
"""

from __future__ import annotations

from typing import Optional

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_skill_chart(
    categories: dict[str, list[str]],
    chart_type: str = "bar",
) -> None:
    """Render a skill category distribution chart.

    Args:
        categories: Dictionary mapping category names to
            lists of skill names.
        chart_type: Chart type - 'bar' or 'radar'.
    """
    if not categories:
        st.info("No skills to display.")
        return

    # Prepare data
    category_counts = {cat: len(skills) for cat, skills in categories.items()}
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

    if chart_type == "bar":
        _render_bar_chart(sorted_categories)
    else:
        _render_radar_chart(sorted_categories)


def render_skill_tags(
    skills: list[str],
    category: Optional[str] = None,
    max_display: int = 20,
) -> None:
    """Render skills as colored tag badges.

    Args:
        skills: List of skill names to display.
        category: Optional category for color coding.
        max_display: Maximum number of skills to show.
    """
    if not skills:
        st.caption("No skills detected.")
        return

    display_skills = skills[:max_display]
    remaining = len(skills) - max_display

    color_map = {
        "Programming": "#1a73e8",
        "Data Science": "#2ecc71",
        "Web Development": "#e67e22",
        "Database": "#9b59b6",
        "DevOps": "#e74c3c",
        "Cloud Computing": "#3498db",
        "AI & Machine Learning": "#1abc9c",
        "Design": "#f39c12",
        "Soft Skill": "#95a5a6",
        "Tool & Platform": "#34495e",
        "Framework": "#16a085",
        "Domain Knowledge": "#7f8c8d",
    }

    tag_color = color_map.get(category, "#1a73e8") if category else "#1a73e8"

    # Build HTML for tags
    tags_html = ""
    for skill in display_skills:
        tags_html += (
            f'<span style="'
            f'display: inline-block;'
            f'background: {tag_color}15;'
            f'color: {tag_color};'
            f'padding: 0.2rem 0.6rem;'
            f'margin: 0.2rem;'
            f'border-radius: 15px;'
            f'font-size: 0.85rem;'
            f'border: 1px solid {tag_color}30;'
            f'">{skill}</span>'
        )

    if remaining > 0:
        tags_html += (
            f'<span style="'
            f'display: inline-block;'
            f'padding: 0.2rem 0.6rem;'
            f'margin: 0.2rem;'
            f'font-size: 0.85rem;'
            f'color: #666;'
            f'">+{remaining} more</span>'
        )

    st.markdown(
        f'<div style="line-height: 2;">{tags_html}</div>',
        unsafe_allow_html=True,
    )


def _render_bar_chart(
    sorted_categories: list[tuple[str, int]],
) -> None:
    """Render a horizontal bar chart.

    Args:
        sorted_categories: List of (category, count) tuples.
    """
    categories, counts = zip(*sorted_categories) if sorted_categories else ([], [])

    fig = go.Figure(
        go.Bar(
            x=list(counts),
            y=list(categories),
            orientation="h",
            marker=dict(
                color=["#1a73e8", "#2ecc71", "#e67e22", "#9b59b6",
                       "#e74c3c", "#3498db", "#1abc9c", "#f39c12"],
                opacity=0.8,
            ),
            text=list(counts),
            textposition="outside",
        )
    )

    fig.update_layout(
        title="Skills by Category",
        xaxis_title="Number of Skills",
        yaxis_title=None,
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)


def _render_radar_chart(
    sorted_categories: list[tuple[str, int]],
) -> None:
    """Render a radar chart for skill distribution.

    Args:
        sorted_categories: List of (category, count) tuples.
    """
    categories, counts = zip(*sorted_categories) if sorted_categories else ([], [])

    fig = go.Figure(
        go.Scatterpolar(
            r=list(counts),
            theta=list(categories),
            fill="toself",
            name="Skills",
            line=dict(color="#1a73e8", width=2),
            marker=dict(color="#1a73e8"),
        )
    )

    fig.update_layout(
        title="Skill Distribution",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(counts) + 1 if counts else 5],
            )
        ),
        height=400,
        margin=dict(l=80, r=80, t=30, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)