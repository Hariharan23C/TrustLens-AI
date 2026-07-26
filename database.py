"""
database.py
Tiny SQLite wrapper for TrustLens AI.

No ORM on purpose -- this project is small enough that raw SQL keeps it
readable, and it's easy to swap for SQLAlchemy later if the project grows.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance", "trustlens.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the scans table if it doesn't exist yet. Safe to call on every boot."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            check_type TEXT NOT NULL,
            input_summary TEXT NOT NULL,
            verdict TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            reasons TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_scan(check_type, input_summary, verdict, risk_score, reasons):
    """reasons is stored as a '||'-joined string to avoid adding a JSON column dependency."""
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO scans (check_type, input_summary, verdict, risk_score, reasons, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            check_type,
            input_summary[:200],
            verdict,
            risk_score,
            "||".join(reasons),
            datetime.utcnow().isoformat(timespec="seconds") + "Z",
        ),
    )
    conn.commit()
    conn.close()


def get_recent_scans(limit=25):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM scans ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) AS c FROM scans").fetchone()["c"]
    flagged = conn.execute(
        "SELECT COUNT(*) AS c FROM scans WHERE verdict != 'safe'"
    ).fetchone()["c"]
    by_type = conn.execute(
        "SELECT check_type, COUNT(*) AS c FROM scans GROUP BY check_type"
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "flagged": flagged,
        "by_type": {r["check_type"]: r["c"] for r in by_type},
    }
