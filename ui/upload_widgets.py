"""
Upload form UI components.

Renders the resume upload form with file uploader,
text paste area, and validation feedback.
"""

from __future__ import annotations

import streamlit as st


def render_upload_form() -> None:
    """Render the resume file upload form with drag-and-drop."""
    st.markdown("### 📤 Upload Your Resume")

    st.markdown(
        """
        <div style="
            border: 2px dashed #1a73e8;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            background: #f8f9fa;
            margin: 1rem 0;
        ">
            <p style="font-size: 1.1rem; color: #333; margin: 0;">
                Drag and drop your resume here
            </p>
            <p style="font-size: 0.85rem; color: #666; margin: 0.5rem 0;">
                Supports PDF, DOCX, TXT — Max 10 MB
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt"],
        help="Upload your resume in PDF, DOCX, or TXT format",
        label_visibility="collapsed",
    )

    return uploaded_file


def render_text_paste_area() -> tuple[str, bool]:
    """Render the text paste area for manual resume input.

    Returns:
        tuple[str, bool]: (pasted_text, submitted) where submitted
            is True when the user clicks Submit.
    """
    st.markdown("### ✍️ Or Paste Your Resume Text")

    resume_text = st.text_area(
        "Paste your resume content here",
        placeholder="Paste your full resume text here...",
        height=300,
        help="Copy and paste your entire resume content",
        key="resume_text_area",
    )

    submitted = st.button(
        "🔍 Analyze Resume",
        type="primary",
        use_container_width=True,
        disabled=not resume_text.strip(),
        help="Click to analyze your resume",
    )

    return resume_text, submitted


def render_upload_requirements() -> None:
    """Render the upload requirements and tips."""
    with st.expander("📋 Requirements & Tips", expanded=False):
        st.markdown("""
        **Accepted Formats:**
        - PDF (.pdf) — Recommended
        - Word Document (.docx)
        - Plain Text (.txt)

        **File Requirements:**
        - Maximum file size: **10 MB**
        - Text must be selectable (not scanned images)

        **Tips for Best Results:**
        - Include your full work history with dates
        - List all relevant skills and technologies
        - Add project descriptions with technologies used
        - Include education details and certifications
        """)


def render_upload_error(error_message: str) -> None:
    """Render an upload error message.

    Args:
        error_message: The error message to display.
    """
    st.error(f"❌ {error_message}", icon="🚨")


def render_upload_progress() -> None:
    """Render an upload progress indicator."""
    with st.status("Analyzing your resume...", expanded=True) as status:
        st.markdown("📄 Extracting text from resume...")
        st.markdown("🔍 Analyzing skills and experience...")
        st.markdown("📊 Calculating resume score...")
        st.markdown("💡 Generating recommendations...")
        status.update(label="Analysis complete!", state="complete")