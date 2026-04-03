"""Test authentication utilities.

TDD tests for password hashing, user creation, and verification functions.
"""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add app to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock dotenv loading to prevent .env file interference
@patch('dotenv.load_dotenv')
class TestAuthUtils(unittest.TestCase):
    """Test authentication utility functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # Set environment variables for testing
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        # SECRET_KEY must be at least 64 characters for validation
        os.environ['SECRET_KEY'] = 'test-secret-key-' * 5  # Makes 75 characters
        os.environ['DEBUG'] = 'true'
        os.environ['LOG_LEVEL'] = 'DEBUG'

        # Clear module cache to ensure fresh imports
        if 'app' in sys.modules:
            del sys.modules['app']
        if 'app.auth.utils' in sys.modules:
            del sys.modules['app.auth.utils']
        if 'app.extensions' in sys.modules:
            del sys.modules['app.extensions']

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary database file
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

        # Clear environment variables
        for key in ['DATABASE_URL', 'SECRET_KEY', 'DEBUG', 'LOG_LEVEL']:
            if key in os.environ:
                del os.environ[key]

    def test_hash_password_returns_bcrypt_hash(self, mock_dotenv):
        """Test 1: hash_password() returns bcrypt hash string."""
        # Import after environment is set up
        from app.auth.utils import hash_password

        # Test password hashing
        password = 'testpassword123'
        hashed = hash_password(password)

        # Verify it's a string
        self.assertIsInstance(hashed, str)
        # Verify it looks like a bcrypt hash (starts with $2b$)
        self.assertTrue(hashed.startswith('$2b$'))
        # Verify length is reasonable for bcrypt hash
        self.assertGreater(len(hashed), 50)

    def test_check_password_verifies_correct_password(self, mock_dotenv):
        """Test 2: check_password() returns True for correct password, False for incorrect."""
        # Import after environment is set up
        from app.auth.utils import hash_password, check_password

        # Test password verification
        password = 'testpassword123'
        hashed = hash_password(password)

        # Correct password should return True
        self.assertTrue(check_password(hashed, password))
        # Incorrect password should return False
        self.assertFalse(check_password(hashed, 'wrongpassword'))

    def test_create_user_inserts_into_database(self, mock_dotenv):
        """Test 3: create_user() inserts user into database with hashed password."""
        # Import after environment is set up
        from app import create_app
        from app.auth.utils import create_user
        from app.db import get_db

        # Create app and push context
        app = create_app()

        with app.app_context():
            # Initialize database with users table
            from init_db import init_database
            init_database()

            # Create a test user
            username = 'testuser'
            password = 'testpass123'
            user_id = create_user(username, password)

            # Verify user was created
            self.assertIsNotNone(user_id)
            self.assertIsInstance(user_id, int)

            # Verify user exists in database
            db = get_db()
            cursor = db.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()

            self.assertIsNotNone(user)
            self.assertEqual(user[1], username)  # username column
            # Password should be hashed (not plain text)
            password_hash = user[2]
            self.assertTrue(password_hash.startswith('$2b$'))

    def test_verify_user_returns_user_for_valid_credentials(self, mock_dotenv):
        """Test 4: verify_user() returns user record for valid credentials, None for invalid."""
        # Import after environment is set up
        from app import create_app
        from app.auth.utils import create_user, verify_user

        # Create app and push context
        app = create_app()

        with app.app_context():
            # Initialize database with users table
            from init_db import init_database
            init_database()

            # Create a test user
            username = 'testuser'
            password = 'testpass123'
            create_user(username, password)

            # Verify valid credentials return user record
            user = verify_user(username, password)
            self.assertIsNotNone(user)
            self.assertEqual(user['username'], username)
            self.assertIn('id', user)
            self.assertIn('created_at', user)

            # Verify invalid username returns None
            invalid_user = verify_user('nonexistent', password)
            self.assertIsNone(invalid_user)

            # Verify invalid password returns None
            wrong_pass_user = verify_user(username, 'wrongpassword')
            self.assertIsNone(wrong_pass_user)

    def test_password_hashing_uses_bcrypt_not_plain_text(self, mock_dotenv):
        """Test 5: Password hashing uses bcrypt (not plain text)."""
        # Import after environment is set up
        from app import create_app
        from app.auth.utils import create_user
        from app.db import get_db

        # Create app and push context
        app = create_app()

        with app.app_context():
            # Initialize database with users table
            from init_db import init_database
            init_database()

            # Create a test user
            username = 'testuser'
            password = 'testpass123'
            create_user(username, password)

            # Check database directly to ensure password is hashed
            db = get_db()
            cursor = db.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
            password_hash = cursor.fetchone()[0]

            # Verify it's a bcrypt hash, not plain text
            self.assertTrue(password_hash.startswith('$2b$'))
            self.assertNotEqual(password_hash, password)
            # bcrypt hash should be much longer than plain password
            self.assertGreater(len(password_hash), len(password) * 2)

    def test_init_db_creates_admin_user_with_flag(self, mock_dotenv):
        """Test 6: init_db.py creates admin user when run with --create-admin flag."""
        # Import after environment is set up
        from app import create_app

        # Create app and push context
        app = create_app()

        with app.app_context():
            # Initialize database first
            from init_db import init_database
            init_database()

            # Test admin user creation
            from init_db import create_admin_user

            # Create admin user
            username = 'testadmin'
            password = 'testadmin123'
            success = create_admin_user(username, password)

            self.assertTrue(success)

            # Verify user was created in database
            from app.db import get_db
            db = get_db()
            cursor = db.execute('SELECT username FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

            self.assertIsNotNone(user)
            self.assertEqual(user[0], username)

            # Test that duplicate user creation fails
            success_duplicate = create_admin_user(username, password)
            self.assertFalse(success_duplicate)


if __name__ == '__main__':
    unittest.main()