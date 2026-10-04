"""Database package for the video rating system.

This project uses MySQL when available and falls back to SQLite for local testing
if MySQL is not running on the machine.
"""

from .db import get_connection, initialize_database, save_result
