"""Pytest configuration and shared fixtures."""
import os
import pytest

# Set test environment variables before importing the app
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-64-characters-long-for-testing-only")
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("LOG_LEVEL", "ERROR")

from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    test_app = create_app()
    test_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture()
def client(app):
    """Create test client."""
    return app.test_client()
