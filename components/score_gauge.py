"""
Score gauge component.

Renders a visual score gauge using SVG for the overall
resume score and section-wise scores.
"""

from __future__ import annotations

import streamlit as st


def render_score_gauge(
    score: float,
    label: str = "Overall Score",
    max_score: float = 100.0,
    size: str = "large",
    show_label: bool = True,
) -> None:
    """Render a circular score gauge.

    Args:
        score: Current score value.
        label: Label displayed below the gauge.
        max_score: Maximum possible score.
        size: Gauge size - 'small', 'medium', or 'large'.
        show_label: Whether to show the label text.
    """
    percentage = (score / max_score) * 100.0
    color = _get_score_color(percentage)

    if size == "small":
        width, height = 80, 80
        font_size = "1.2rem"
    elif size == "medium":
        width, height = 120, 120
        font_size = "1.8rem"
    else:  # large
        width, height = 160, 160
        font_size = "2.5rem"

    # SVG circle parameters
    cx, cy = width / 2, height / 2
    radius = min(width, height) / 2 - 10
    circumference = 2 * 3.14159 * radius
    offset = circumference * (1 - percentage / 100.0)

    svg = f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <!-- Background circle -->
        <circle
            cx="{cx}" cy="{cy}" r="{radius}"
            fill="none"
            stroke="#e0e0e0"
            stroke-width="8"
        />
        <!-- Score circle -->
        <circle
            cx="{cx}" cy="{cy}" r="{radius}"
            fill="none"
            stroke="{color}"
            stroke-width="8"
            stroke-dasharray="{circumference}"
            stroke-dashoffset="{offset}"
            stroke-linecap="round"
            transform="rotate(-90, {cx}, {cy})"
        />
        <!-- Score text -->
        <text
            x="{cx}" y="{cy}"
            text-anchor="middle"
            dominant-baseline="central"
            font-size="{font_size}"
            font-weight="bold"
            fill="{color}"
        >
            {score:.0f}
        </text>
    </svg>
    """

    st.markdown(
        f"""
        <div style="text-align: center; padding: 0.5rem;">
            {svg}
            {"<p style='margin-top: 0.5rem; font-weight: 500; color: #333;'>" + label + "</p>" if show_label else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_score_bar(
    score: float,
    label: str,
    max_score: float = 100.0,
    show_value: bool = True,
) -> None:
    """Render a horizontal score bar.

    Args:
        score: Current score value.
        label: Label for the bar.
        max_score: Maximum possible score.
        show_value: Whether to show the numeric value.
    """
    percentage = (score / max_score) * 100.0
    color = _get_score_color(percentage)

    bar_html = f"""
    <div style="margin: 0.5rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
            <span style="font-size: 0.9rem; color: #333;">{label}</span>
            {"<span style='font-size: 0.9rem; font-weight: bold; color: " + color + ";'>" + f"{score:.0f}" + "</span>" if show_value else ""}
        </div>
        <div style="background: #e0e0e0; border-radius: 10px; height: 10px; overflow: hidden;">
            <div style="width: {percentage}%; background: {color}; height: 100%; border-radius: 10px; transition: width 0.5s ease;"></div>
        </div>
    </div>
    """

    st.markdown(bar_html, unsafe_allow_html=True)


def _get_score_color(percentage: float) -> str:
    """Get the color for a score percentage.

    Args:
        percentage: Score percentage (0-100).

    Returns:
        str: Hex color code.
    """
    if percentage >= 80:
        return "#2ecc71"  # Green
    if percentage >= 60:
        return "#f1c40f"  # Yellow
    if percentage >= 40:
        return "#e67e22"  # Orange
    return "#e74c3c"  # Red