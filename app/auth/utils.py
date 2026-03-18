"""Authentication utility functions.

Password hashing, user creation, and verification utilities.
"""

from ..extensions import bcrypt, db
from ..models import User


def hash_password(password):
    """Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hash string
    """
    # Generate password hash and decode from bytes to string
    return bcrypt.generate_password_hash(password).decode('utf-8')


def check_password(password_hash, password):
    """Check if a password matches a bcrypt hash.

    Args:
        password_hash: Bcrypt hash string
        password: Plain text password to check

    Returns:
        True if password matches hash, False otherwise
    """
    return bcrypt.check_password_hash(password_hash, password)


def create_user(username, password):
    """Create a new user in the database.

    Args:
        username: Unique username
        password: Plain text password (will be hashed)

    Returns:
        User ID if successful, None if failed

    Raises:
        sqlite3.IntegrityError: If username already exists
        SQLAlchemyError: If database operation fails
    """
    # Hash the password
    password_hash = hash_password(password)

    # Create new user instance
    user = User(username=username, password_hash=password_hash)

    # Add to session and commit
    db.session.add(user)
    db.session.commit()

    return user.id


def verify_user(username, password):
    """Verify user credentials.

    Args:
        username: Username to verify
        password: Plain text password to verify

    Returns:
        User dictionary with id, username, created_at if credentials are valid,
        None otherwise
    """
    # Get user from database
    user = User.query.filter_by(username=username).first()

    if not user:
        return None

    # Check password
    if check_password(user.password_hash, password):
        # Return user dictionary
        return {
            'id': user.id,
            'username': user.username,
            'created_at': user.created_at
        }

    return None


def login_required(f):
    """Decorator to require login for protected routes.

    Checks if user_id is in session. If not, redirects to login page
    with a flash message.

    Args:
        f: Function to decorate

    Returns:
        Decorated function
    """
    from functools import wraps
    from flask import flash, redirect, url_for, session

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function