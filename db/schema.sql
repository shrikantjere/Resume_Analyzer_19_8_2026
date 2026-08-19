-- AI Resume Analyzer — Database Schema
-- SQLite DDL for all application tables

-- ── Migration Tracking ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS _migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Analysis Results ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlation_id TEXT NOT NULL,
    resume_text TEXT,
    resume_score REAL,
    skills_json TEXT,
    experience_json TEXT,
    summary TEXT,
    job_recommendations_json TEXT,
    missing_skills_json TEXT,
    improvements_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analyses_correlation_id ON analyses(correlation_id);
CREATE INDEX idx_analyses_created_at ON analyses(created_at);

-- ── Job Roles ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    industry TEXT,
    required_skills_json TEXT NOT NULL,
    experience_level TEXT DEFAULT 'Mid',
    description TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_job_roles_industry ON job_roles(industry);
CREATE INDEX idx_job_roles_active ON job_roles(is_active);

-- ── User Sessions ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    ip_address TEXT,
    user_agent TEXT,
    analysis_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_sessions_session_id ON user_sessions(session_id);

-- ── User Feedback ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER REFERENCES analyses(id) ON DELETE SET NULL,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedback_analysis_id ON user_feedback(analysis_id);

-- ── Job Feedback ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER REFERENCES analyses(id) ON DELETE CASCADE,
    job_title TEXT,
    was_relevant INTEGER CHECK(was_relevant IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_job_feedback_analysis_id ON job_feedback(analysis_id);