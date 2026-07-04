"""
db.py
All SQLite database setup and helper functions for FarmAI.
"""

import sqlite3
import hashlib
from contextlib import closing

DB_PATH = "farmers.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they don't already exist."""
    with closing(get_conn()) as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT UNIQUE NOT NULL,
                password      TEXT NOT NULL,
                first_name    TEXT NOT NULL,
                last_name     TEXT NOT NULL,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS fields (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                field_number  TEXT NOT NULL,
                crop_type     TEXT NOT NULL,
                date_planted  DATE NOT NULL,
                field_size    REAL NOT NULL,
                size_unit     TEXT NOT NULL,
                location      TEXT NOT NULL,
                latitude      REAL,
                longitude     REAL,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                field_id      INTEGER,
                crop_type     TEXT NOT NULL,
                image_name    TEXT,
                diagnosis     TEXT NOT NULL,
                severity      TEXT,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (field_id) REFERENCES fields (id)
            )
        """)

        conn.commit()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(username: str, password: str, first_name: str, last_name: str):
    """
    Attempts to create a new user.
    Returns (bool success, str message)
    """
    username = username.strip()
    first_name = first_name.strip()
    last_name = last_name.strip()

    if not username or not password or not first_name or not last_name:
        return False, "All fields are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            return False, "Username already taken."

        cur.execute(
            """INSERT INTO users (username, password, first_name, last_name)
               VALUES (?, ?, ?, ?)""",
            (username, hash_password(password), first_name, last_name),
        )
        conn.commit()

    return True, "Account created successfully."


def login_user(username: str, password: str):
    """
    Returns a farmer dict on success, or None on failure.
    """
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, username, password, first_name, last_name
               FROM users WHERE username = ?""",
            (username.strip(),),
        )
        row = cur.fetchone()

    if not row:
        return None

    user_id, uname, pw_hash, first_name, last_name = row
    if pw_hash != hash_password(password):
        return None

    return {
        "id": user_id,
        "username": uname,
        "first_name": first_name,
        "last_name": last_name,
    }


def add_field(user_id, field_number, crop_type, date_planted,
              field_size, size_unit, location, lat, lng):
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO fields
               (user_id, field_number, crop_type, date_planted,
                field_size, size_unit, location, latitude, longitude)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, field_number, crop_type, date_planted,
             field_size, size_unit, location, lat, lng),
        )
        conn.commit()


def get_fields(user_id):
    """
    Returns list of tuples:
    (id, user_id, field_number, crop_type, date_planted,
     field_size, size_unit, location, latitude, longitude, created_at)
    """
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, user_id, field_number, crop_type, date_planted,
                      field_size, size_unit, location, latitude, longitude, created_at
               FROM fields WHERE user_id = ? ORDER BY created_at DESC""",
            (user_id,),
        )
        return cur.fetchall()


def delete_field(field_id, user_id):
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM fields WHERE id = ? AND user_id = ?",
            (field_id, user_id),
        )
        conn.commit()


def save_scan(user_id, field_id, crop_type, image_name, diagnosis, severity):
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO scan_history
               (user_id, field_id, crop_type, image_name, diagnosis, severity)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, field_id, crop_type, image_name, diagnosis, severity),
        )
        conn.commit()


def get_scans(user_id, limit=10, field_id="ALL"):
    """
    Returns list of tuples:
    (id, user_id, field_id, crop_type, image_name, diagnosis, severity, created_at)

    field_id options:
      "ALL"  -> all scans (default)
      None   -> only scans not linked to any field
      <int>  -> only scans for that field
    """
    query = """SELECT id, user_id, field_id, crop_type, image_name,
                      diagnosis, severity, created_at
               FROM scan_history WHERE user_id = ?"""
    params = [user_id]

    if field_id is None:
        query += " AND field_id IS NULL"
    elif field_id != "ALL":
        query += " AND field_id = ?"
        params.append(field_id)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()


def get_scan_count(user_id) -> int:
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM scan_history WHERE user_id = ?",
            (user_id,),
        )
        return cur.fetchone()[0]
