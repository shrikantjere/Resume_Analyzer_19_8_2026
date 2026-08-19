# AI Resume Analyzer

An intelligent application that uses AI to analyze resumes, extract skills, evaluate experience, provide job recommendations, and suggest improvements.

## Features

- **Resume Upload**: Upload PDF, DOCX, or paste text directly
- **AI-Powered Analysis**: Extract skills, experience, education, and more using OpenAI GPT-4o
- **Resume Scoring**: Get a comprehensive score with section-wise breakdown
- **Job Recommendations**: Match your skills to relevant job roles
- **Skill Gap Analysis**: Identify missing skills for your target roles
- **Improvement Suggestions**: Actionable tips to improve your resume
- **Download Reports**: Export analysis as PDF or JSON

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd resume_analyzer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Run

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

## Project Structure

```
resume_analyzer/
├── app.py                 # Main entry point
├── pages/                 # Streamlit multi-page app
├── ui/                    # Presentation layer
├── components/            # Reusable UI components
├── services/              # Business logic layer
├── core/                  # Infrastructure (config, AI, DB, logging)
├── models/                # Pydantic domain models
├── data/                  # Runtime data directory
├── db/                    # Database schema and migrations
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## Architecture

The application follows a **layered architecture**:
- **Presentation Layer**: Streamlit UI (`ui/`, `components/`, `pages/`)
- **Service Layer**: Business logic (`services/`)
- **Domain Layer**: Pydantic models (`models/`)
- **Core Layer**: Infrastructure (`core/`)

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **AI**: OpenAI GPT-4o
- **Database**: SQLite
- **Parsing**: pdfplumber, python-docx
- **Reports**: WeasyPrint
- **Testing**: pytest

## License

MIT