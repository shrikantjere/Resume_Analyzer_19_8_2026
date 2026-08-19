"""
Custom CSS styles for the AI Resume Analyzer.

Provides professional styling overrides and custom
component styles for the Streamlit app.
"""

from __future__ import annotations

import streamlit as st


def apply_custom_styles() -> None:
    """Apply custom CSS styles to the Streamlit app."""
    st.markdown(
        """
        <style>
        /* ── Global Styles ───────────────────────────────────────────── */
        .stApp {
            background: #fafafa;
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1000px;
        }

        /* ── Typography ──────────────────────────────────────────────── */
        h1, h2, h3 {
            color: #1a1a1a;
            font-weight: 600;
        }

        h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        h2 {
            font-size: 1.5rem;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }

        h3 {
            font-size: 1.2rem;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        /* ── Metrics ─────────────────────────────────────────────────── */
        [data-testid="stMetric"] {
            background: white;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            border: 1px solid #e8e8e8;
        }

        [data-testid="stMetric"] > div {
            text-align: center;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.85rem;
            color: #666;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1a73e8;
        }

        /* ── Buttons ─────────────────────────────────────────────────── */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            padding: 0.5rem 1.5rem;
            transition: all 0.2s ease;
        }

        .stButton > button[kind="primary"] {
            background: #1a73e8;
            color: white;
            border: none;
        }

        .stButton > button[kind="primary"]:hover {
            background: #1557b0;
            box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);
        }

        /* ── Expanders ───────────────────────────────────────────────── */
        .streamlit-expanderHeader {
            font-weight: 500;
            color: #333;
            background: white;
            border-radius: 8px;
        }

        .streamlit-expander {
            border: 1px solid #e8e8e8;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            background: white;
        }

        /* ── Tabs ────────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: white;
            padding: 0.5rem;
            border-radius: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            background: #1a73e8;
            color: white;
        }

        /* ── File Uploader ───────────────────────────────────────────── */
        [data-testid="stFileUploader"] {
            border: 2px dashed #1a73e8;
            border-radius: 16px;
            padding: 1rem;
            background: #f8f9fa;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: #1557b0;
            background: #f0f4ff;
        }

        /* ── Text Area ───────────────────────────────────────────────── */
        .stTextArea textarea {
            border-radius: 8px;
            border: 1px solid #ddd;
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .stTextArea textarea:focus {
            border-color: #1a73e8;
            box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.1);
        }

        /* ── Status / Progress ───────────────────────────────────────── */
        .stStatus {
            background: white;
            border-radius: 12px;
            border: 1px solid #e8e8e8;
        }

        /* ── Dividers ────────────────────────────────────────────────── */
        hr {
            margin: 2rem 0;
            border-color: #e8e8e8;
        }

        /* ── Info / Success / Warning / Error ────────────────────────── */
        .stAlert {
            border-radius: 8px;
            border: none;
        }

        /* ── Sidebar ─────────────────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: #f8f9fa;
            border-right: 1px solid #e8e8e8;
        }

        section[data-testid="stSidebar"] .stButton button {
            width: 100%;
            justify-content: flex-start;
            background: transparent;
            border: none;
            color: #333;
            font-weight: 400;
        }

        section[data-testid="stSidebar"] .stButton button[kind="primary"] {
            background: #e8f0fe;
            color: #1a73e8;
            font-weight: 500;
        }

        /* ── Cards (containers with border) ──────────────────────────── */
        div[data-testid="stContainer"] {
            border-radius: 12px;
        }

        /* ── Responsive adjustments ──────────────────────────────────── */
        @media (max-width: 768px) {
            .main .block-container {
                padding-top: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            [data-testid="column"] {
                min-width: 100%;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )