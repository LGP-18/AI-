import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "records.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS plate_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_filename TEXT NOT NULL,
                processed_filename TEXT NOT NULL,
                crop_filename TEXT NOT NULL,
                plate_text TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def insert_record(record):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO plate_records (
                original_filename,
                processed_filename,
                crop_filename,
                plate_text,
                status,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record["original_filename"],
                record["processed_filename"],
                record["crop_filename"],
                record["plate_text"],
                record["status"],
                record["created_at"],
            ),
        )
        conn.commit()


def fetch_records(limit=20):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM plate_records
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return rows
