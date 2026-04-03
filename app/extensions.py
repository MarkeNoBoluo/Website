"""Flask extensions module.

Centralizes extension instances for better organization and avoids circular imports.
"""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# Flask-Bcrypt instance for password hashing
bcrypt = Bcrypt()

# SQLAlchemy ORM instance for database operations
db = SQLAlchemy()

# Flask-Migrate instance for database migrations
migrate = Migrate()


# CSRF protection utilities
import secrets
from datetime import datetime, timedelta
from flask import session

CSRF_TOKEN_LIFETIME = timedelta(minutes=30)


def generate_csrf_token():
    """Generate and store CSRF token in session if not already present or expired."""
    now = datetime.utcnow()
    token_expires_str = session.get("_csrf_token_expires")

    needs_refresh = True
    if "_csrf_token" in session and token_expires_str:
        try:
            token_expires = datetime.fromisoformat(token_expires_str)
            if now < token_expires:
                needs_refresh = False
        except (ValueError, TypeError):
            needs_refresh = True

    if needs_refresh:
        session["_csrf_token"] = secrets.token_hex(32)
        session["_csrf_token_expires"] = (now + CSRF_TOKEN_LIFETIME).isoformat()

    return session["_csrf_token"]


def validate_csrf_token(token):
    """Validate CSRF token against session token."""
    if not token or token != session.get("_csrf_token"):
        return False

    token_expires = session.get("_csrf_token_expires")
    if token_expires and datetime.utcnow() >= datetime.fromisoformat(token_expires):
        return False

    return True


def refresh_csrf_token():
    """Regenerate CSRF token and update expiry."""
    now = datetime.utcnow()
    session["_csrf_token"] = secrets.token_hex(32)
    session["_csrf_token_expires"] = (now + CSRF_TOKEN_LIFETIME).isoformat()
    return session["_csrf_token"]
