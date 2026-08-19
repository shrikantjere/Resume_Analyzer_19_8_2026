"""UI rendering package for the AI Resume Analyzer."""

from ui.upload_widgets import render_upload_form, render_text_paste_area
from ui.analysis_display import render_analysis_results
from ui.recommendation_display import render_recommendations_page
from ui.report_ui import render_report_page
from ui.styles import apply_custom_styles

__all__ = [
    "render_upload_form",
    "render_text_paste_area",
    "render_analysis_results",
    "render_recommendations_page",
    "render_report_page",
    "apply_custom_styles",
]