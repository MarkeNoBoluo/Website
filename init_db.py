#!/usr/bin/env python3
"""Database initialization script.

Creates the users table for authentication.
Only creates auth tables (users), not comments or todos (deferred to later phases).
"""
import argparse
import os
import sqlite3
import sys

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed
    pass


def init_database():
    """Initialize database with users table."""
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL environment variable is not set.")
        print("Please set DATABASE_URL in your .env file or environment.")
        sys.exit(1)

    if not database_url.startswith('sqlite:///'):
        print(f"Error: DATABASE_URL must start with 'sqlite:///' (got '{database_url}')")
        sys.exit(1)

    # Extract database file path
    db_path = database_url.replace('sqlite:///', '')
    print(f"Initializing database: {db_path}")

    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA busy_timeout=5000;")

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index on username for faster lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")

        conn.commit()
        print("Database initialized successfully.")
        print("- Created users table")
        print("- Created index on username")
        print("- Enabled WAL journal mode")

        # Show table structure
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        print("\nUsers table structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()


def create_admin_user(username, password):
    """Create an admin user in the database.

    Args:
        username: Admin username
        password: Admin password (will be hashed)

    Returns:
        True if user created successfully, False otherwise
    """
    try:
        # Import here to avoid circular imports and ensure app context
        from app import create_app
        from app.auth.utils import create_user

        # Create app and context
        app = create_app()
        with app.app_context():
            # Check if user already exists
            db = sqlite3.connect(os.getenv('DATABASE_URL').replace('sqlite:///', ''))
            cursor = db.execute('SELECT id FROM users WHERE username = ?', (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                print(f"Warning: User '{username}' already exists (ID: {existing_user[0]})")
                return False

            # Create admin user
            user_id = create_user(username, password)
            print(f"Admin user '{username}' created successfully (ID: {user_id})")
            return True

    except ImportError as e:
        print(f"Error: Cannot import application modules: {e}")
        print("Make sure you're running from the project root directory.")
        return False
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description='Initialize database for Flask blog application'
    )
    parser.add_argument(
        '--create-admin',
        action='store_true',
        help='Create an admin user after database initialization'
    )
    parser.add_argument(
        '--username',
        default='admin',
        help='Admin username (default: admin)'
    )
    parser.add_argument(
        '--password',
        default='admin123',
        help='Admin password (default: admin123)'
    )

    args = parser.parse_args()

    print("Initializing database for Flask blog application...")
    init_database()

    if args.create_admin:
        print("\nCreating admin user...")
        print(f"Username: {args.username}")
        print(f"Password: {'*' * len(args.password)}")

        # Warn about default password
        if args.password == 'admin123':
            print("\n⚠️  WARNING: Using default password 'admin123'")
            print("   Change this password immediately after first login!")

        success = create_admin_user(args.username, args.password)
        if not success:
            print("Failed to create admin user.")
            sys.exit(1)

    print("\nDone. You can now run the application with:")
    print("  python -m flask run")
    print("Or with Gunicorn:")
    print("  gunicorn --bind unix:/tmp/blog.sock wsgi:app")


if __name__ == '__main__':
    main()