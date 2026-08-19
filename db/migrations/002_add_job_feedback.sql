-- AI Resume Analyzer — Migration v2: Add Job Feedback Table

CREATE TABLE IF NOT EXISTS job_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER REFERENCES analyses(id) ON DELETE CASCADE,
    job_title TEXT,
    was_relevant INTEGER CHECK(was_relevant IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_job_feedback_analysis_id ON job_feedback(analysis_id);