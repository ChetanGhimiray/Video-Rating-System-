"""Database package for the video rating system.

This project uses MySQL when available and falls back to SQLite for local testing
if MySQL is not running on the machine.
"""

from .db import (
    create_user,
    get_connection,
    get_recent_results,
    get_submission,
    get_submission_summary,
    get_user_by_username,
    get_user_improvement,
    initialize_database,
    save_result,
)
