"""Flask application factory."""
import os
from datetime import datetime, timedelta
from flask import Flask, jsonify

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, but that's OK if env vars are set via systemd
    pass

from .config import Config
from .extensions import bcrypt


def create_app(config_class=Config):
    """Create and configure Flask application.

    Args:
        config_class: Configuration class to use (defaults to Config)

    Returns:
        Flask application instance
    """
    # Create Flask application
    app = Flask('blog')

    # Load configuration
    config_instance = config_class()
    app.config.from_object(config_instance)

    # Validate configuration
    config_class.validate()

    # Initialize extensions
    bcrypt.init_app(app)

    # Configure session settings
    # Session expires on browser close (per user decision)
    app.config['SESSION_PERMANENT'] = False
    # For local development - set to True in production with HTTPS
    app.config['SESSION_COOKIE_SECURE'] = False
    # Prevent JavaScript access to session cookie (security)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    # Balance security and functionality for cross-site requests
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # Fallback timeout if browser doesn't respect SESSION_PERMANENT
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

    # Register database teardown
    from .db import close_db
    app.teardown_appcontext(close_db)

    # Register blueprints
    from .blog import bp as blog_bp
    from .todo import bp as todo_bp
    from .auth import bp as auth_bp
    app.register_blueprint(blog_bp, url_prefix='/blog')
    app.register_blueprint(todo_bp, url_prefix='/todo')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Register routes
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
            'database_url': app.config['DATABASE_URL'],
            'log_level': app.config['LOG_LEVEL'],
            'config_source': 'Environment variables validated successfully'
        })

    @app.route('/db-test')
    def db_test():
        """Database test endpoint showing connection status and WAL mode."""
        from .db import get_db
        db = get_db()
        cursor = db.execute("PRAGMA journal_mode;")
        journal_mode = cursor.fetchone()[0]

        return jsonify({
            'status': 'connected',
            'wal_mode': journal_mode == 'wal',
            'database': app.config['DATABASE_PATH'],
            'journal_mode': journal_mode
        })

    return app