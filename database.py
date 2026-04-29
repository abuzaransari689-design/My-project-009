"""
models/database.py
Handles SQLite database setup and all table creation.
All data (users, routes, emergencies) is stored here.
"""

import sqlite3
from flask import g
import os

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "expressway.db")


def get_db():
    """Open a database connection tied to the current request context."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Rows behave like dicts
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables if they don't already exist."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # ── Users table ──────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT    NOT NULL UNIQUE,
            email     TEXT    NOT NULL UNIQUE,
            password  TEXT    NOT NULL,
            is_admin  INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Route history table ──────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS route_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            source      TEXT    NOT NULL,
            destination TEXT    NOT NULL,
            distance_km REAL    NOT NULL,
            travel_time TEXT    NOT NULL,
            traffic     TEXT    NOT NULL,
            toll_amount REAL    NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Emergency reports table ──────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_reports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            location    TEXT    NOT NULL,
            description TEXT    NOT NULL,
            status      TEXT    DEFAULT 'Pending',
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")
