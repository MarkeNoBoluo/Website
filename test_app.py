"""Tests for Flask application with configuration validation."""
import os
import sys
import tempfile
from unittest.mock import patch
import pytest


def test_app_starts_with_all_env_vars():
    """Test 1: Flask app starts without errors when all required environment variables are set."""
    # Set up required environment variables
    os.environ['SECRET_KEY'] = 'x' * 64  # 64 characters
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'INFO'

    # Import app - should not raise any errors
    try:
        from app import app
        assert app is not None
        assert app.name == 'blog'
    except Exception as e:
        pytest.fail(f"App failed to start with all env vars: {e}")
    finally:
        # Clean up environment
        for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
            os.environ.pop(key, None)


def test_app_fails_with_missing_secret_key():
    """Test 2: Flask app fails with clear error message when SECRET_KEY is missing."""
    # Set up environment variables except SECRET_KEY
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'INFO'

    # Import should raise RuntimeError with clear message
    with pytest.raises(RuntimeError) as exc_info:
        from app import app

    error_msg = str(exc_info.value).lower()
    assert 'secret_key' in error_msg
    assert 'missing' in error_msg or 'required' in error_msg or 'not set' in error_msg

    # Clean up
    for key in ['DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
        os.environ.pop(key, None)


def test_root_route_returns_hello_world():
    """Test 3: Root route '/' returns 'Hello, world!' with 200 status."""
    # Set up environment
    os.environ['SECRET_KEY'] = 'x' * 64
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'INFO'

    try:
        from app import app

        # Create test client
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            assert response.data.decode('utf-8') == 'Hello, world!'
    finally:
        # Clean up
        for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
            os.environ.pop(key, None)


def test_debug_mode_disabled_when_debug_false():
    """Test 4: Debug mode is disabled when DEBUG=false in environment."""
    os.environ['SECRET_KEY'] = 'x' * 64
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'INFO'

    try:
        from app import app
        assert app.config['DEBUG'] is False
        assert app.config['SECRET_KEY'] == 'x' * 64
    finally:
        for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
            os.environ.pop(key, None)


def test_debug_mode_enabled_when_debug_true():
    """Test 4b: Debug mode is enabled when DEBUG=true in environment."""
    os.environ['SECRET_KEY'] = 'x' * 64
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'true'
    os.environ['LOG_LEVEL'] = 'INFO'

    try:
        from app import app
        assert app.config['DEBUG'] is True
    finally:
        for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
            os.environ.pop(key, None)


def test_config_loaded_from_dotenv():
    """Test 5: Configuration is loaded from .env file via python-dotenv."""
    # Create a temporary .env file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write('SECRET_KEY=dotenv-test-key-1234567890-dotenv-test-key-1234567890-extra-chars\n')
        f.write('DATABASE_URL=sqlite:///dotenv-test.db\n')
        f.write('DEBUG=true\n')
        f.write('LOG_LEVEL=DEBUG\n')
        env_file = f.name

    try:
        # Mock dotenv loading to use our temp file
        with patch('app.load_dotenv') as mock_load_dotenv:
            # Make load_dotenv actually load our test file
            def side_effect():
                from dotenv import load_dotenv as real_load_dotenv
                real_load_dotenv(env_file)
            mock_load_dotenv.side_effect = side_effect

            # Clear any existing env vars
            for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
                os.environ.pop(key, None)

            # Import should load from .env file
            from app import app

            # Verify values from .env file
            assert app.config['SECRET_KEY'] == 'dotenv-test-key-1234567890-dotenv-test-key-1234567890-extra-chars'
            assert app.config['DEBUG'] is True
    finally:
        # Clean up
        os.unlink(env_file)
        for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
            os.environ.pop(key, None)


def test_health_check_route():
    """Additional test: Health check route returns JSON status."""
    os.environ['SECRET_KEY'] = 'x' * 64
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'INFO'

    try:
        from app import app

        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'ok'
            assert 'timestamp' in data
    finally:
        for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
            os.environ.pop(key, None)


def test_config_test_route():
    """Additional test: Config test route shows loaded config (excluding SECRET_KEY)."""
    os.environ['SECRET_KEY'] = 'x' * 64
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'INFO'

    try:
        from app import app

        with app.test_client() as client:
            response = client.get('/config-test')
            assert response.status_code == 200
            data = response.get_json()
            assert 'debug' in data
            assert data['debug'] is False
            assert 'database_url' in data
            assert data['database_url'] == 'sqlite:///test.db'
            assert 'log_level' in data
            assert data['log_level'] == 'INFO'
            # SECRET_KEY should not be exposed
            assert 'secret_key' not in data
    finally:
        for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
            os.environ.pop(key, None)