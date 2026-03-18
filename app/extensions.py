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
from flask import session


def generate_csrf_token():
    """Generate and store CSRF token in session if not already present."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']


def validate_csrf_token(token):
    """Validate CSRF token against session token."""
    return token == session.get('_csrf_token')