"""Flask application factory."""

import os
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv not installed, but that's OK if env vars are set via systemd
    pass

from .config import Config
from .extensions import bcrypt, db, migrate, generate_csrf_token


def create_app(config_class=Config):
    """Create and configure Flask application.

    Args:
        config_class: Configuration class to use (defaults to Config)

    Returns:
        Flask application instance
    """
    # Create Flask application
    app = Flask("blog")

    # Load configuration
    config_instance = config_class()
    app.config.from_object(config_instance)

    # Validate configuration
    config_class.validate()

    # Initialize extensions
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Configure session settings
    # Session expires on browser close (per user decision)
    app.config["SESSION_PERMANENT"] = False
    # For local development - set to True in production with HTTPS
    app.config["SESSION_COOKIE_SECURE"] = False
    # Prevent JavaScript access to session cookie (security)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    # Balance security and functionality for cross-site requests
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    # Fallback timeout if browser doesn't respect SESSION_PERMANENT
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

    # Register database teardown (handled by SQLAlchemy)
    # from .db import close_db
    # app.teardown_appcontext(close_db)

    # Register blueprints
    from .blog import bp as blog_bp
    from .todo import bp as todo_bp
    from .auth import bp as auth_bp
    from .admin import bp as admin_bp

    app.register_blueprint(blog_bp, url_prefix="/blog")
    app.register_blueprint(todo_bp, url_prefix="/todo")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp)

    # Register routes
    @app.route("/")
    def index():
        """Homepage — terminal-themed blog landing page."""
        from .blog.utils import get_db_articles

        articles = get_db_articles(status="published")
        return render_template("home.html", articles=articles)

    @app.route("/health")
    def health():
        """Health check endpoint returning application status."""
        from .utils import health_check

        return jsonify(health_check())

    @app.route("/config-test")
    def config_test():
        """Configuration test endpoint showing loaded config (excluding secrets)."""
        return jsonify(
            {
                "debug": app.config["DEBUG"],
                "database_url": app.config["DATABASE_URL"],
                "log_level": app.config["LOG_LEVEL"],
                "config_source": "Environment variables validated successfully",
            }
        )

    @app.route("/db-test")
    def db_test():
        """Database test endpoint showing connection status and WAL mode."""
        # Use SQLAlchemy connection for WAL mode check
        from .extensions import db

        result = db.session.execute("PRAGMA journal_mode;")
        journal_mode = result.fetchone()[0]

        return jsonify(
            {
                "status": "connected",
                "wal_mode": journal_mode == "wal",
                "database": app.config["DATABASE_PATH"],
                "journal_mode": journal_mode,
            }
        )

    # Context processor to make 'now' available in all templates
    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow()}

    # Context processor to make CSRF token available in all templates
    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": generate_csrf_token()}

    @app.errorhandler(404)
    def global_page_not_found(error):
        """全局 404 错误处理"""
        # 检查是否是博客相关的 URL
        from flask import request

        if request.path.startswith("/blog/"):
            # 让博客蓝图处理
            return error

        # 对于非博客 URL，返回简单 404
        return render_template("errors/404.html"), 404

    return app
