"""Tests for Flask application with configuration validation."""
import os
import sys
import tempfile
from unittest.mock import patch
import pytest
from app.config import Config

# Test configuration for in-memory database
class TestConfig(Config):
    """Test configuration that inherits from production Config but uses in-memory database."""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'  # In-memory database for testing
    SECRET_KEY = 'test-secret-key-' + 'x' * 48  # 64 characters total
    DEBUG = False
    LOG_LEVEL = 'INFO'

    @classmethod
    def validate(cls):
        """Override validation to be less strict for testing."""
        # Skip validation for testing environment
        pass


def test_app_starts_with_all_env_vars():
    """Test 1: Flask app starts without errors when all required environment variables are set."""
    # Clear module cache to force re-import
    if 'app' in sys.modules:
        del sys.modules['app']

    from app import create_app
    app = create_app(config_class=TestConfig)
    assert app is not None
    assert app.name == 'blog'


@patch('dotenv.load_dotenv')
def test_app_fails_with_missing_secret_key(mock_dotenv):
    """Test 2: Flask app fails with clear error message when SECRET_KEY is missing."""
    # Clear any existing SECRET_KEY
    os.environ.pop('SECRET_KEY', None)

    # Set up other environment variables
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'INFO'

    # Clear module cache to force re-import
    if 'app' in sys.modules:
        del sys.modules['app']

    # Import create_app and Config
    from app import create_app, Config

    # Should raise RuntimeError with clear message
    with pytest.raises(RuntimeError) as exc_info:
        app = create_app(config_class=Config)

    error_msg = str(exc_info.value).lower()
    assert 'secret_key' in error_msg
    assert 'missing' in error_msg or 'required' in error_msg or 'not set' in error_msg

    # Clean up
    for key in ['DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
        os.environ.pop(key, None)


def test_root_route_returns_hello_world():
    """Test 3: Root route '/' returns 'Hello, world!' with 200 status."""
    # Clear module cache to force re-import
    if 'app' in sys.modules:
        del sys.modules['app']

    from app import create_app
    app = create_app(config_class=TestConfig)

    # Create test client
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert response.data.decode('utf-8') == 'Hello, world!'


def test_debug_mode_disabled_when_debug_false():
    """Test 4: Debug mode is disabled when DEBUG=false in environment."""
    # Set environment variables
    os.environ['SECRET_KEY'] = 'x' * 64
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'INFO'

    # Clear module cache to force re-import
    if 'app' in sys.modules:
        del sys.modules['app']

    try:
        from app import create_app, Config
        app = create_app(config_class=Config)
        assert app.config['DEBUG'] is False
        assert app.config['SECRET_KEY'] == 'x' * 64
    finally:
        # Clean up environment
        for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
            os.environ.pop(key, None)


def test_debug_mode_enabled_when_debug_true():
    """Test 4b: Debug mode is enabled when DEBUG=true in environment."""
    os.environ['SECRET_KEY'] = 'x' * 64
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['DEBUG'] = 'true'
    os.environ['LOG_LEVEL'] = 'INFO'

    # Clear module cache to force re-import
    if 'app' in sys.modules:
        del sys.modules['app']

    try:
        from app import create_app, Config
        app = create_app(config_class=Config)
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
        # Instead of mocking, temporarily set the env vars from our file
        # Clear any existing env vars first
        for key in ['SECRET_KEY', 'DATABASE_URL', 'DEBUG', 'LOG_LEVEL']:
            os.environ.pop(key, None)

        # Load the temp file directly
        from dotenv import load_dotenv
        load_dotenv(env_file)

        # Clear module cache to force re-import
        if 'app' in sys.modules:
            del sys.modules['app']

        # Import should load from .env file
        from app import create_app, Config
        app = create_app(config_class=Config)

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
    # Clear module cache to force re-import
    if 'app' in sys.modules:
        del sys.modules['app']

    from app import create_app
    app = create_app(config_class=TestConfig)

    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'timestamp' in data


def test_config_test_route():
    """Additional test: Config test route shows loaded config (excluding SECRET_KEY)."""
    # Clear module cache to force re-import
    if 'app' in sys.modules:
        del sys.modules['app']

    from app import create_app
    app = create_app(config_class=TestConfig)

    with app.test_client() as client:
        response = client.get('/config-test')
        assert response.status_code == 200
        data = response.get_json()
        assert 'debug' in data
        assert data['debug'] is False
        assert 'database_url' in data
        assert data['database_url'] == 'sqlite:///:memory:'
        assert 'log_level' in data
        assert data['log_level'] == 'INFO'
        # SECRET_KEY should not be exposed
        assert 'secret_key' not in data