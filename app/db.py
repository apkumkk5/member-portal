"""Database layer.

Deliberately uses Python's built-in sqlite3 rather than an ORM. For a project
this size an ORM hides more than it helps, and seeing the actual SQL makes the
data layer legible.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "portal.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS members (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    member_number       TEXT    NOT NULL UNIQUE,
    first_name          TEXT    NOT NULL,
    last_name           TEXT    NOT NULL,
    email               TEXT    NOT NULL,
    phone               TEXT,
    address_line1       TEXT,
    city                TEXT,
    state               TEXT,
    postal_code         TEXT,
    language_preference TEXT    NOT NULL DEFAULT 'en',
    updated_at          TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "zh": "Chinese",
    "vi": "Vietnamese",
    "ru": "Russian",
}


def get_connection():
    """Open a connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist. Safe to run repeatedly."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def get_all_members():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM members ORDER BY last_name, first_name"
        ).fetchall()
    return [dict(row) for row in rows]


def get_member(member_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM members WHERE id = ?", (member_id,)
        ).fetchone()
    return dict(row) if row else None


def update_member(member_id: int, fields: dict):
    """Update only the fields a member is allowed to change.

    The allowlist matters: without it, a crafted form post could change
    member_number or id. Never build the column list from user input.
    """
    allowed = {
        "email",
        "phone",
        "address_line1",
        "city",
        "state",
        "postal_code",
        "language_preference",
    }
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return get_member(member_id)

    assignments = ", ".join(f"{col} = ?" for col in updates)
    values = list(updates.values()) + [member_id]

    with get_connection() as conn:
        conn.execute(
            f"UPDATE members SET {assignments}, updated_at = CURRENT_TIMESTAMP"
            " WHERE id = ?",
            values,
        )
    return get_member(member_id)
