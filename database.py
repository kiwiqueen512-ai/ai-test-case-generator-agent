import sqlite3
import json
from datetime import datetime

DB_NAME = "test_cases.db"


def init_db():
    """Initialize SQLite database and create history table if not exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_case_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requirement TEXT NOT NULL,
            feature_summary TEXT,
            test_cases_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_test_cases(requirement: str, feature_summary: str, test_cases: list):
    """Save a requirement and its generated/edited test cases into SQLite."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO test_case_runs (requirement, feature_summary, test_cases_json, created_at)
        VALUES (?, ?, ?, ?)
    """, (requirement, feature_summary, json.dumps(test_cases), created_at))
    conn.commit()
    conn.close()


def get_all_history():
    """Fetch all saved test case runs ordered by latest first."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, requirement, feature_summary, test_cases_json, created_at
        FROM test_case_runs
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "id": row[0],
            "requirement": row[1],
            "feature_summary": row[2],
            "test_cases": json.loads(row[3]),
            "created_at": row[4]
        })
    return history


def delete_history_item(record_id: int):
    """Delete a saved history record by ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM test_case_runs WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()