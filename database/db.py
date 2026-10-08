import os
import json
import sqlite3

import mysql.connector
from mysql.connector import Error


MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "video_rating_system"),
    "autocommit": True,
}

SQLITE_PATH = "database/video_rating.db"

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

    os.makedirs("database", exist_ok=True)
    connection = sqlite3.connect(SQLITE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _ensure_scoring_columns(cursor, is_mysql):
    if is_mysql:
        cursor.execute("SHOW COLUMNS FROM submissions")
        existing_columns = {row[0] for row in cursor.fetchall()}
    else:
        cursor.execute("PRAGMA table_info(submissions)")
        existing_columns = {row[1] for row in cursor.fetchall()}

    for column, column_type in SCORING_COLUMNS.items():
        if column not in existing_columns:
            if not is_mysql and column_type == "DOUBLE":
                column_type = "REAL"
            elif not is_mysql and column_type == "INT":
                column_type = "INTEGER"
            elif not is_mysql and column == "speaking_style":
                column_type = "TEXT"
            cursor.execute(f"ALTER TABLE submissions ADD COLUMN {column} {column_type}")


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()
    is_mysql = not isinstance(connection, sqlite3.Connection)

    if is_mysql:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
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

    _ensure_scoring_columns(cursor, is_mysql)
    connection.commit()
    connection.close()


def save_result(data):
    connection = get_connection()
    cursor = connection.cursor()
    is_mysql = not isinstance(connection, sqlite3.Connection)

    if is_mysql:
        cursor.execute(
            """
            INSERT INTO submissions (
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
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
