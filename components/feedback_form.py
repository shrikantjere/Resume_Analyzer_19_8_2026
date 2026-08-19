"""
Feedback form component.

Renders a user feedback widget with star rating
and optional text comment.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st


def render_feedback_form(
    analysis_id: Optional[int] = None,
    key: str = "feedback",
) -> None:
    """Render a feedback form with star rating.

    Args:
        analysis_id: Optional analysis ID to associate feedback.
        key: Unique key for the Streamlit widget.
    """
    feedback_key = f"feedback_submitted_{key}"

    if st.session_state.get(feedback_key, False):
        st.success(
            "Thank you for your feedback! 🙏",
            icon="✅",
        )
        return

    st.markdown("### 📝 Rate This Analysis")

    rating = st.feedback("stars", key=f"star_rating_{key}")

    if rating is not None:
        st.markdown(f"Your rating: **{'⭐' * (rating + 1)}**")

    with st.expander("Add a comment (optional)"):
        comment = st.text_area(
            "What did you think?",
            placeholder="Tell us what you liked or how we can improve...",
            key=f"feedback_comment_{key}",
            max_chars=500,
        )

    if st.button("Submit Feedback", key=f"submit_feedback_{key}", type="primary"):
        if rating is not None:
            # Store feedback in session state
            st.session_state[feedback_key] = True

            feedback_data = {
                "analysis_id": analysis_id or 0,
                "rating": rating + 1,
                "comment": comment,
            }

            # Try to save to database if available
            try:
                from core.db import DatabaseManager, FeedbackRepository

                db = DatabaseManager()
                repo = FeedbackRepository(db)
                repo.save_feedback(feedback_data)
                st.success("Feedback saved! Thank you! 🎉")
            except Exception as e:
                # Log but don't show error to user
                st.success("Thank you for your feedback! 🎉")

            st.rerun()
        else:
            st.warning("Please select a star rating before submitting.")