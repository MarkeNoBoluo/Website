"""Database connection management."""
import sqlite3
from flask import g, current_app


def get_db():
    """Get database connection, creating it if necessary."""
    if 'db' not in g:
        # Get database path from config
        db_path = current_app.config['DATABASE_PATH']
        if not db_path:
            raise RuntimeError("DATABASE_PATH not configured")

        # Connect to database
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row

        # Configure WAL mode and other settings
        g.db.execute("PRAGMA journal_mode=WAL;")
        g.db.execute("PRAGMA synchronous=NORMAL;")
        g.db.execute("PRAGMA busy_timeout=5000;")
        g.db.commit()

    return g.db


def close_db(e=None):
    """Close database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()