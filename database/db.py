import sqlite3
import os


DATABASE_PATH = "database/video_rating.db"


def get_connection():

    os.makedirs("database", exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
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

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    connection.close()


def save_result(data):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
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
    """, (

        data["video_filename"],
        data["video_source"],
        data["wpm"],
        data["filler_count"],
        data["pause_count"],
        data["eye_contact_percentage"],
        data["face_detected_ratio"],
        data["final_score"],
        data["transcript"],
        data["feedback"]

    ))

    connection.commit()

    submission_id = cursor.lastrowid

    connection.close()

    return submission_id
