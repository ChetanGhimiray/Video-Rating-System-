import json
import os
import sqlite3
from pathlib import Path

import mysql.connector
from mysql.connector import Error


BASE_DIR = Path(__file__).resolve().parent.parent
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "video_rating_system"),
    "autocommit": True,
}

SQLITE_PATH = str(BASE_DIR / "database" / "video_rating.db")

SCORING_COLUMNS = {
    "speaking_style": "VARCHAR(32)",
    "pitch_range_semitones": "DOUBLE",
    "intensity_range_db": "DOUBLE",
    "pause_ratio": "DOUBLE",
    "long_pause_count": "INT",
    "content_style_score": "DOUBLE",
    "vocal_delivery_score": "DOUBLE",
    "score_breakdown": "TEXT",
}


def _mysql_is_available():
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        connection.close()
        return True
    except Error:
        return False


def get_connection():
    if _mysql_is_available():
        return mysql.connector.connect(**MYSQL_CONFIG)

    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    connection = sqlite3.connect(SQLITE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _column_names(cursor, table_name, is_mysql):
    if is_mysql:
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        return {row[0] for row in cursor.fetchall()}
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}


def _ensure_scoring_columns(cursor, is_mysql):
    existing_columns = _column_names(cursor, "submissions", is_mysql)
    for column, column_type in SCORING_COLUMNS.items():
        if column not in existing_columns:
            if not is_mysql and column_type == "DOUBLE":
                column_type = "REAL"
            elif not is_mysql and column_type == "INT":
                column_type = "INTEGER"
            elif not is_mysql and column == "speaking_style":
                column_type = "TEXT"
            cursor.execute(f"ALTER TABLE submissions ADD COLUMN {column} {column_type}")


def _ensure_user_columns(cursor, is_mysql):
    if is_mysql:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    else:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    existing_columns = _column_names(cursor, "submissions", is_mysql)
    if "user_id" not in existing_columns:
        if is_mysql:
            cursor.execute("ALTER TABLE submissions ADD COLUMN user_id INT")
        else:
            cursor.execute("ALTER TABLE submissions ADD COLUMN user_id INTEGER")


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()
    is_mysql = not isinstance(connection, sqlite3.Connection)

    if is_mysql:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                video_filename VARCHAR(255) NOT NULL,
                video_source VARCHAR(255),
                wpm DOUBLE,
                filler_count INT,
                pause_count INT,
                eye_contact_percentage DOUBLE,
                face_detected_ratio DOUBLE,
                final_score DOUBLE,
                transcript TEXT,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    else:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                video_filename TEXT NOT NULL,
                video_source TEXT,
                wpm REAL,
                filler_count INTEGER,
                pause_count INTEGER,
                eye_contact_percentage REAL,
                face_detected_ratio REAL,
                final_score REAL,
                transcript TEXT,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    _ensure_user_columns(cursor, is_mysql)
    _ensure_scoring_columns(cursor, is_mysql)
    connection.commit()
    connection.close()


def create_user(username, password_hash):
    connection = get_connection()
    cursor = connection.cursor()
    is_mysql = not isinstance(connection, sqlite3.Connection)
    placeholder = "%s" if is_mysql else "?"
    try:
        cursor.execute(
            f"INSERT INTO users (username, password_hash) VALUES ({placeholder}, {placeholder})",
            (username, password_hash),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def get_user_by_username(username):
    connection = get_connection()
    cursor = connection.cursor()
    is_mysql = not isinstance(connection, sqlite3.Connection)
    placeholder = "%s" if is_mysql else "?"
    try:
        cursor.execute(
            f"SELECT * FROM users WHERE username = {placeholder}",
            (username,),
        )
        row = cursor.fetchone()
        return _result_as_dict(cursor, row, is_mysql)
    finally:
        connection.close()


def save_result(data):
    connection = get_connection()
    cursor = connection.cursor()
    is_mysql = not isinstance(connection, sqlite3.Connection)
    placeholder = "%s" if is_mysql else "?"
    user_id = data.get("user_id")

    if is_mysql:
        cursor.execute(
            f"""
            INSERT INTO submissions (
                user_id,
                video_filename,
                video_source,
                wpm,
                filler_count,
                pause_count,
                eye_contact_percentage,
                face_detected_ratio,
                final_score,
                transcript,
                feedback,
                speaking_style,
                pitch_range_semitones,
                intensity_range_db,
                pause_ratio,
                long_pause_count,
                content_style_score,
                vocal_delivery_score,
                score_breakdown
            )
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            """,
            (
                user_id,
                data["video_filename"],
                data["video_source"],
                data["wpm"],
                data["filler_count"],
                data["pause_count"],
                data["eye_contact_percentage"],
                data["face_detected_ratio"],
                data["final_score"],
                data["transcript"],
                data["feedback"],
                data["speaking_style"],
                data["pitch_range_semitones"],
                data["intensity_range_db"],
                data["pause_ratio"],
                data["long_pause_count"],
                data["content_style_score"],
                data["vocal_delivery_score"],
                json.dumps(data["score_breakdown"]),
            ),
        )
        submission_id = cursor.lastrowid
    else:
        cursor.execute(
            """
            INSERT INTO submissions (
                user_id,
                video_filename,
                video_source,
                wpm,
                filler_count,
                pause_count,
                eye_contact_percentage,
                face_detected_ratio,
                final_score,
                transcript,
                feedback,
                speaking_style,
                pitch_range_semitones,
                intensity_range_db,
                pause_ratio,
                long_pause_count,
                content_style_score,
                vocal_delivery_score,
                score_breakdown
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                data["video_filename"],
                data["video_source"],
                data["wpm"],
                data["filler_count"],
                data["pause_count"],
                data["eye_contact_percentage"],
                data["face_detected_ratio"],
                data["final_score"],
                data["transcript"],
                data["feedback"],
                data["speaking_style"],
                data["pitch_range_semitones"],
                data["intensity_range_db"],
                data["pause_ratio"],
                data["long_pause_count"],
                data["content_style_score"],
                data["vocal_delivery_score"],
                json.dumps(data["score_breakdown"]),
            ),
        )
        submission_id = cursor.lastrowid

    connection.commit()
    connection.close()
    return submission_id


def _result_as_dict(cursor, row, is_mysql):
    if row is None:
        return None
    if not is_mysql:
        return dict(row)
    return dict(zip((column[0] for column in cursor.description), row))


def get_recent_results(limit=30, user_id=None):
    limit = max(1, min(int(limit), 100))
    connection = get_connection()
    cursor = connection.cursor()
    is_mysql = not isinstance(connection, sqlite3.Connection)
    placeholder = "%s" if is_mysql else "?"
    query = "SELECT * FROM submissions"
    params = []
    if user_id is not None:
        query += f" WHERE user_id = {placeholder}"
        params.append(user_id)
    query += f" ORDER BY id DESC LIMIT {placeholder}"
    params.append(limit)
    try:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [_result_as_dict(cursor, row, is_mysql) for row in rows]
    finally:
        connection.close()


def get_submission(submission_id, user_id=None):
    connection = get_connection()
    cursor = connection.cursor()
    is_mysql = not isinstance(connection, sqlite3.Connection)
    placeholder = "%s" if is_mysql else "?"
    query = "SELECT * FROM submissions WHERE id = " + placeholder
    params = [submission_id]
    if user_id is not None:
        query += " AND user_id = " + placeholder
        params.append(user_id)
    try:
        cursor.execute(query, tuple(params))
        return _result_as_dict(cursor, cursor.fetchone(), is_mysql)
    finally:
        connection.close()


def get_submission_summary(user_id=None):
    connection = get_connection()
    cursor = connection.cursor()
    is_mysql = not isinstance(connection, sqlite3.Connection)
    placeholder = "%s" if is_mysql else "?"
    query = """
        SELECT
            COUNT(*),
            AVG(final_score),
            AVG(eye_contact_percentage),
            AVG(face_detected_ratio)
        FROM submissions
    """
    params = []
    if user_id is not None:
        query += " WHERE user_id = " + placeholder
        params.append(user_id)
    try:
        cursor.execute(query, tuple(params))
        total, average_score, average_eye_contact, average_face_presence = cursor.fetchone()
        return {
            "total_submissions": total or 0,
            "average_score": round(average_score or 0, 1),
            "average_eye_contact": round(average_eye_contact or 0, 1),
            "average_face_presence": round(average_face_presence or 0, 1),
        }
    finally:
        connection.close()


def get_user_improvement(user_id):
    rows = get_recent_results(limit=10, user_id=user_id)
    if len(rows) < 2:
        return {
            "status": "No trend yet",
            "message": "Submit a few more videos to see whether you are improving.",
            "change": 0,
        }

    first_score = float(rows[-1].get("final_score") or 0)
    latest_score = float(rows[0].get("final_score") or 0)
    change = latest_score - first_score

    if change > 5:
        return {
            "status": "Improving",
            "message": f"Your latest score is {change:.1f} points higher than your earlier review.",
            "change": change,
        }
    if change < -5:
        return {
            "status": "Needs attention",
            "message": f"Your latest score is {abs(change):.1f} points lower than your earlier review.",
            "change": change,
        }
    return {
        "status": "Stable",
        "message": "Your performance is holding steady across recent reviews.",
        "change": change,
    }
