"""Flask blog application with configuration validation."""
import os
from datetime import datetime
from flask import Flask, jsonify

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, but that's OK if env vars are set via systemd
    pass


def validate_environment():
    """Validate all required environment variables."""
    errors = []

    # SECRET_KEY validation
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        errors.append("SECRET_KEY is not set")
    elif len(secret_key) < 64:
        errors.append(f"SECRET_KEY must be at least 64 characters (got {len(secret_key)})")

    # DATABASE_URL validation
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        errors.append("DATABASE_URL is not set")
    elif not database_url.startswith('sqlite:///'):
        errors.append(f"DATABASE_URL must start with 'sqlite:///' (got '{database_url}')")

    # DEBUG validation
    debug_value = os.getenv('DEBUG', '').lower()
    if debug_value not in ('true', 'false'):
        errors.append(f"DEBUG must be 'true' or 'false' (got '{debug_value}')")

    # LOG_LEVEL validation
    log_level = os.getenv('LOG_LEVEL', '').upper()
    valid_log_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
    if log_level not in valid_log_levels:
        errors.append(f"LOG_LEVEL must be one of {sorted(valid_log_levels)} (got '{log_level}')")

    if errors:
        error_msg = "Configuration errors:\n" + "\n".join(f"  - {error}" for error in errors)
        raise RuntimeError(error_msg)


# Create Flask application
app = Flask('blog')

# Validate environment before configuring app
validate_environment()

# Configure Flask app from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = os.getenv('DEBUG', 'false').lower() == 'true'

# Get other configuration values
DATABASE_URL = os.getenv('DATABASE_URL')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


@app.route('/')
def index():
    """Root endpoint returning a simple greeting."""
    return 'Hello, world!'


@app.route('/health')
def health():
    """Health check endpoint returning application status."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'service': 'blog',
        'version': '1.0.0'
    })


@app.route('/config-test')
def config_test():
    """Configuration test endpoint showing loaded config (excluding secrets)."""
    return jsonify({
        'debug': app.config['DEBUG'],
        'database_url': DATABASE_URL,
        'log_level': LOG_LEVEL,
        'config_source': 'Environment variables validated successfully'
    })


if __name__ == '__main__':
    # This block only runs when executing the script directly (not via gunicorn)
    print(f"Starting Flask blog application (DEBUG={app.config['DEBUG']})")
    print(f"Database URL: {DATABASE_URL}")
    print(f"Log level: {LOG_LEVEL}")
    app.run(host='0.0.0.0', port=5000)