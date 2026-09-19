import sqlite3
import os


DATABASE = "database/presentation.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():

    os.makedirs("database", exist_ok=True)

    connection = get_connection()

    cursor = connection.cursor()

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        )
    """)

    # Presentations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS presentations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id TEXT NOT NULL,

            presentation_number INTEGER NOT NULL,

            video_name TEXT NOT NULL,

            video_hash TEXT,

            duration REAL,

            speaker_score REAL,
            fluency_score REAL,
            eye_contact_score REAL,
            structure_score REAL,

            overall_score REAL,

            feedback TEXT,

            upload_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def add_student(student_id, name):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO students
        (student_id, name)
        VALUES (?, ?)
    """, (student_id, name))

    connection.commit()
    connection.close()


def get_student(student_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM students
        WHERE student_id = ?
    """, (student_id,))

    student = cursor.fetchone()

    connection.close()

    return student


def get_next_presentation_number(student_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT MAX(presentation_number)
        FROM presentations
        WHERE student_id = ?
    """, (student_id,))

    result = cursor.fetchone()

    connection.close()

    if result[0] is None:
        return 1

    return result[0] + 1


def add_presentation(data):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO presentations
        (
            student_id,
            presentation_number,
            video_name,
            video_hash,
            duration,
            speaker_score,
            fluency_score,
            eye_contact_score,
            structure_score,
            overall_score,
            feedback
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["student_id"],
        data["presentation_number"],
        data["video_name"],
        data["video_hash"],
        data["duration"],
        data["speaker_score"],
        data["fluency_score"],
        data["eye_contact_score"],
        data["structure_score"],
        data["overall_score"],
        data["feedback"]
    ))

    presentation_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return presentation_id


def get_presentations(student_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM presentations
        WHERE student_id = ?
        ORDER BY presentation_number ASC
    """, (student_id,))

    presentations = cursor.fetchall()

    connection.close()

    return presentations


def get_presentation(presentation_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM presentations
        WHERE id = ?
    """, (presentation_id,))

    presentation = cursor.fetchone()

    connection.close()

    return presentation