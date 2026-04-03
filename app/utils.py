"""Utility functions for the application."""

from functools import wraps
from datetime import datetime
from flask import abort, request, current_app
from .extensions import validate_csrf_token, refresh_csrf_token, db


def csrf_protected(f):
    """Decorator to require valid CSRF token for POST requests.

    Checks CSRF token in form data against session token.
    Returns 403 if validation fails. Token is refreshed after successful validation.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "POST":
            token = request.form.get("csrf_token")
            if not token or not validate_csrf_token(token):
                abort(403, "CSRF token validation failed")
            refresh_csrf_token()
        return f(*args, **kwargs)

    return decorated_function


def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        from sqlalchemy import text

        db.session.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check application status
    app_status = "healthy" if current_app else "unhealthy"

    return {
        "status": "ok"
        if db_status == "healthy" and app_status == "healthy"
        else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {"database": db_status, "application": app_status},
        "version": "1.0",
    }
