"""Tests for Flask application factory and configuration."""
import os
import sys
import tempfile
import pytest
from flask import Flask


def test_create_app_returns_flask_instance():
    """Test 1: create_app() returns Flask application instance."""
    # Set up environment variables
    os.environ['SECRET_KEY'] = 'x' * 64
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'INFO'

    # Clear module cache
    if 'app' in sys.modules:
        del sys.modules['app']

    # Mock dotenv.load_dotenv to prevent loading from .env file
    import unittest.mock as mock
    with mock.patch('dotenv.load_dotenv'):
        try:
            from app import create_app
            app = create_app()
            assert isinstance(app, Flask)
            assert app.name == 'blog'
        finally:
            # Clean up
            for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
                os.environ.pop(key, None)


def test_configuration_loads_from_env():
    """Test 2: Configuration loads SECRET_KEY, DATABASE_URL, DEBUG, LOG_LEVEL from .env."""
    # Set up environment variables
    os.environ['SECRET_KEY'] = 'test-secret-key-1234567890-test-secret-key-1234567890-extra-chars'
    os.environ['DATABASE_URL'] = 'sqlite:///test-config.db'
    os.environ['DEBUG'] = 'true'
    os.environ['LOG_LEVEL'] = 'DEBUG'

    # Clear module cache
    if 'app' in sys.modules:
        del sys.modules['app']

    # Mock dotenv.load_dotenv to prevent loading from .env file
    import unittest.mock as mock
    with mock.patch('dotenv.load_dotenv'):
        try:
            from app import create_app
            app = create_app()

            # Check configuration
            assert app.config['SECRET_KEY'] == 'test-secret-key-1234567890-test-secret-key-1234567890-extra-chars'
            assert app.config['DEBUG'] is True
            assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///test-config.db'
            assert app.config['LOG_LEVEL'] == 'DEBUG'
        finally:
            # Clean up
            for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
                os.environ.pop(key, None)


def test_configuration_validation_fails_with_missing_secret_key():
    """Test 3: Configuration validation fails with missing SECRET_KEY."""
    # Clear any existing SECRET_KEY first
    os.environ.pop('SECRET_KEY', None)

    # Set up environment variables except SECRET_KEY
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'INFO'

    # Clear module cache
    if 'app' in sys.modules:
        del sys.modules['app']

    # Mock dotenv.load_dotenv to prevent loading from .env file
    import unittest.mock as mock
    with mock.patch('dotenv.load_dotenv'):
        try:
            from app import create_app
            with pytest.raises(RuntimeError) as exc_info:
                app = create_app()

            error_msg = str(exc_info.value).lower()
            assert 'secret_key' in error_msg
            assert 'not set' in error_msg or 'missing' in error_msg
        finally:
            # Clean up
            for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
                os.environ.pop(key, None)


def test_configuration_validation_fails_with_invalid_database_url():
    """Test 4: Configuration validation fails with invalid DATABASE_URL."""
    # Clear any existing values first
    for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
        os.environ.pop(key, None)

    # Set up environment variables with invalid DATABASE_URL
    os.environ['SECRET_KEY'] = 'x' * 64
    os.environ['DATABASE_URL'] = 'invalid:///test.db'  # Not sqlite:///
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'INFO'

    # Clear module cache
    if 'app' in sys.modules:
        del sys.modules['app']

    # Mock dotenv.load_dotenv to prevent loading from .env file
    import unittest.mock as mock
    with mock.patch('dotenv.load_dotenv'):
        try:
            from app import create_app
            with pytest.raises(RuntimeError) as exc_info:
                app = create_app()

            error_msg = str(exc_info.value).lower()
            assert 'database_url' in error_msg
            assert 'must start with' in error_msg or 'invalid' in error_msg
        finally:
            # Clean up
            for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
                os.environ.pop(key, None)


def test_app_factory_registers_teardown():
    """Test 5: Application factory registers teardown for database connection."""
    # Set up environment variables
    os.environ['SECRET_KEY'] = 'x' * 64
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'INFO'

    # Clear module cache
    if 'app' in sys.modules:
        del sys.modules['app']

    try:
        from app import create_app
        app = create_app()

        # Check that teardown_appcontext is registered
        # We can check by looking at app.teardown_appcontext_funcs
        # It should have at least one function registered
        assert hasattr(app, 'teardown_appcontext_funcs')
        # The exact structure might vary, but we can check it's not empty
        assert len(app.teardown_appcontext_funcs) > 0
    finally:
        # Clean up
        for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
            os.environ.pop(key, None)