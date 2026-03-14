"""Application configuration."""
import os


class Config:
    """Base configuration class."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        # Load from environment variables
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
        self.DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

        # Derived values
        if self.SQLALCHEMY_DATABASE_URI and self.SQLALCHEMY_DATABASE_URI.startswith('sqlite:///'):
            self.DATABASE_PATH = self.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
        else:
            self.DATABASE_PATH = None

    @classmethod
    def validate(cls):
        """Validate all required environment variables."""
        errors = []
        config = cls()  # Create instance to access attributes

        # SECRET_KEY validation
        secret_key = config.SECRET_KEY
        if not secret_key:
            errors.append("SECRET_KEY is not set")
        elif len(secret_key) < 64:
            errors.append(f"SECRET_KEY must be at least 64 characters (got {len(secret_key)})")

        # DATABASE_URL validation
        database_url = config.SQLALCHEMY_DATABASE_URI
        if not database_url:
            errors.append("DATABASE_URL is not set")
        elif not database_url.startswith('sqlite:///'):
            errors.append(f"DATABASE_URL must start with 'sqlite:///' (got '{database_url}')")

        # DEBUG validation
        debug_value = os.getenv('DEBUG', '').lower()
        if debug_value not in ('true', 'false'):
            errors.append(f"DEBUG must be 'true' or 'false' (got '{debug_value}')")

        # LOG_LEVEL validation
        log_level = config.LOG_LEVEL.upper()
        valid_log_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if log_level not in valid_log_levels:
            errors.append(f"LOG_LEVEL must be one of {sorted(valid_log_levels)} (got '{log_level}')")

        if errors:
            error_msg = "Configuration errors:\n" + "\n".join(f"  - {error}" for error in errors)
            raise RuntimeError(error_msg)