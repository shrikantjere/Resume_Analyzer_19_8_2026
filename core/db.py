"""
Database access layer for the AI Resume Analyzer.

Manages SQLite connections, migrations, and provides
repository classes for data access.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

from core.config import get_settings
from core.exceptions import (
    ConnectionError as DBConnectionError,
    DatabaseError,
    IntegrityError,
    MigrationError,
)
from core.logging_config import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and schema migrations.

    Provides a context manager for database sessions and
    repository classes for entity-specific data access.
    """

    def __init__(self, db_url: Optional[str] = None) -> None:
        """Initialize the database manager.

        Args:
            db_url: Optional database URL. Defaults to settings value.
        """
        self.settings = get_settings()
        self.db_url = db_url or self.settings.database_url
        self._db_path = self._parse_db_path()
        self._ensure_directories()

    def _parse_db_path(self) -> str:
        """Extract the file path from the database URL.

        Returns:
            str: The filesystem path to the SQLite database file.

        Raises:
            DatabaseError: If the URL format is invalid.
        """
        # Handle sqlite:///path format
        if self.db_url.startswith("sqlite:///"):
            path = self.db_url[len("sqlite:///"):]
            # Handle :memory: special case
            if path == ":memory:":
                return ":memory:"
            return path

        # Handle :memory: directly
        if self.db_url == ":memory:":
            return ":memory:"

        # Assume it's a file path
        return self.db_url

    def _ensure_directories(self) -> None:
        """Ensure the database directory exists."""
        if self._db_path != ":memory:":
            db_dir = Path(self._db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def session(self) -> Generator[sqlite3.Connection, None, None]:
        """Provide a database session context manager.

        Yields:
            sqlite3.Connection: A database connection.

        Raises:
            DBConnectionError: If connection fails.
        """
        conn: Optional[sqlite3.Connection] = None
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DBConnectionError(
                f"Database connection error: {e}",
            ) from e
        finally:
            if conn:
                conn.close()

    # ── Migrations ────────────────────────────────────────────────────

    def run_migrations(self) -> None:
        """Run all pending database migrations.

        Creates the schema if it doesn't exist and applies
        any pending migration files in order.

        Raises:
            MigrationError: If migrations fail.
        """
        try:
            with self.session() as conn:
                # Create migration tracking table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS _migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL UNIQUE,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Get applied migrations
                applied = set(
                    row["filename"]
                    for row in conn.execute(
                        "SELECT filename FROM _migrations ORDER BY id"
                    ).fetchall()
                )

                # Find migration files
                migrations_dir = Path("db/migrations")
                if not migrations_dir.exists():
                    logger.info("No migrations directory found, skipping.")
                    return

                migration_files = sorted(
                    migrations_dir.glob("*.sql"),
                    key=lambda p: p.name,
                )

                for migration_file in migration_files:
                    if migration_file.name in applied:
                        continue

                    logger.info(
                        "Applying migration: %s", migration_file.name
                    )
                    sql = migration_file.read_text()
                    conn.executescript(sql)
                    conn.execute(
                        "INSERT INTO _migrations (filename) VALUES (?)",
                        (migration_file.name,),
                    )
                    logger.info(
                        "Migration applied: %s", migration_file.name
                    )

        except (sqlite3.Error, OSError) as e:
            raise MigrationError(f"Migration failed: {e}") from e

    def init_schema(self) -> None:
        """Initialize the database schema from schema.sql.

        This is used for first-time setup or testing.
        """
        schema_path = Path("db/schema.sql")
        if not schema_path.exists():
            logger.warning("Schema file not found: %s", schema_path)
            return

        try:
            with self.session() as conn:
                conn.executescript(schema_path.read_text())
                logger.info("Database schema initialized successfully.")
        except (sqlite3.Error, OSError) as e:
            raise MigrationError(f"Schema initialization failed: {e}") from e


# ── Repository Classes ──────────────────────────────────────────────────


class AnalysisRepository:
    """Repository for analysis result CRUD operations."""

    def __init__(self, db: DatabaseManager) -> None:
        """Initialize the repository.

        Args:
            db: DatabaseManager instance.
        """
        self.db = db

    def save_analysis(self, analysis_data: dict[str, Any]) -> int:
        """Save an analysis result to the database.

        Args:
            analysis_data: Dictionary of analysis data to persist.

        Returns:
            int: The ID of the inserted analysis record.

        Raises:
            IntegrityError: If the data violates constraints.
        """
        try:
            with self.db.session() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO analyses (
                        correlation_id, resume_text, resume_score,
                        skills_json, experience_json, summary,
                        job_recommendations_json, missing_skills_json,
                        improvements_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (
                        analysis_data.get("correlation_id"),
                        analysis_data.get("resume_text", "")[:500],
                        analysis_data.get("resume_score"),
                        json.dumps(analysis_data.get("skills", {})),
                        json.dumps(analysis_data.get("experience", {})),
                        analysis_data.get("summary", ""),
                        json.dumps(analysis_data.get("job_recommendations", [])),
                        json.dumps(analysis_data.get("missing_skills", [])),
                        json.dumps(analysis_data.get("improvements", [])),
                    ),
                )
                return cursor.lastrowid  # type: ignore[return-value]
        except sqlite3.IntegrityError as e:
            raise IntegrityError(f"Failed to save analysis: {e}") from e

    def get_analysis_by_id(self, analysis_id: int) -> Optional[dict[str, Any]]:
        """Retrieve an analysis result by ID.

        Args:
            analysis_id: The ID of the analysis to retrieve.

        Returns:
            Optional[dict]: Analysis data dict, or None if not found.
        """
        try:
            with self.db.session() as conn:
                row = conn.execute(
                    "SELECT * FROM analyses WHERE id = ?",
                    (analysis_id,),
                ).fetchone()

                if row is None:
                    return None

                return dict(row)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to retrieve analysis: {e}") from e

    def get_analyses_by_session(
        self,
        session_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Retrieve analyses for a given session.

        Args:
            session_id: The session ID to filter by.
            limit: Maximum number of results to return.

        Returns:
            list[dict]: List of analysis data dicts.
        """
        try:
            with self.db.session() as conn:
                rows = conn.execute(
                    """
                    SELECT * FROM analyses
                    WHERE correlation_id LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (f"{session_id}%", limit),
                ).fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(
                f"Failed to retrieve analyses: {e}"
            ) from e


class JobRepository:
    """Repository for job role data access."""

    def __init__(self, db: DatabaseManager) -> None:
        """Initialize the repository.

        Args:
            db: DatabaseManager instance.
        """
        self.db = db

    def save_job_role(self, job_data: dict[str, Any]) -> int:
        """Save a job role to the database.

        Args:
            job_data: Dictionary of job role data.

        Returns:
            int: The ID of the inserted job role.
        """
        try:
            with self.db.session() as conn:
                cursor = conn.execute(
                    """
                    INSERT OR REPLACE INTO job_roles (
                        title, industry, required_skills_json,
                        experience_level, description, is_active
                    ) VALUES (?, ?, ?, ?, ?, 1)
                    """,
                    (
                        job_data.get("title"),
                        job_data.get("industry"),
                        json.dumps(job_data.get("required_skills", [])),
                        job_data.get("experience_level"),
                        job_data.get("description", ""),
                    ),
                )
                return cursor.lastrowid  # type: ignore[return-value]
        except sqlite3.IntegrityError as e:
            raise IntegrityError(f"Failed to save job role: {e}") from e

    def get_all_active_roles(self) -> list[dict[str, Any]]:
        """Retrieve all active job roles.

        Returns:
            list[dict]: List of job role data dicts.
        """
        try:
            with self.db.session() as conn:
                rows = conn.execute(
                    "SELECT * FROM job_roles WHERE is_active = 1"
                ).fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(
                f"Failed to retrieve job roles: {e}"
            ) from e

    def get_roles_by_industry(self, industry: str) -> list[dict[str, Any]]:
        """Retrieve job roles for a specific industry.

        Args:
            industry: The industry to filter by.

        Returns:
            list[dict]: List of matching job role data dicts.
        """
        try:
            with self.db.session() as conn:
                rows = conn.execute(
                    "SELECT * FROM job_roles WHERE industry = ? AND is_active = 1",
                    (industry,),
                ).fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(
                f"Failed to retrieve job roles: {e}"
            ) from e


class FeedbackRepository:
    """Repository for user feedback CRUD operations."""

    def __init__(self, db: DatabaseManager) -> None:
        """Initialize the repository.

        Args:
            db: DatabaseManager instance.
        """
        self.db = db

    def save_feedback(self, feedback_data: dict[str, Any]) -> int:
        """Save user feedback.

        Args:
            feedback_data: Dictionary of feedback data.

        Returns:
            int: The ID of the inserted feedback record.
        """
        try:
            with self.db.session() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO user_feedback (
                        analysis_id, rating, comment, created_at
                    ) VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (
                        feedback_data.get("analysis_id"),
                        feedback_data.get("rating"),
                        feedback_data.get("comment", ""),
                    ),
                )
                return cursor.lastrowid  # type: ignore[return-value]
        except sqlite3.IntegrityError as e:
            raise IntegrityError(f"Failed to save feedback: {e}") from e