import os
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


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    if _mysql_is_available():
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

    connection.commit()
    connection.close()


def save_result(data):
    connection = get_connection()
    cursor = connection.cursor()

    if _mysql_is_available():
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
                feedback
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                feedback
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            ),
        )
        submission_id = cursor.lastrowid

    connection.commit()
    connection.close()
    return submission_id
