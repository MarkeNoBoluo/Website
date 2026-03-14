"""Test authentication routes and session management.

TDD tests for login/logout routes, session configuration, and login_required decorator.
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
class TestAuthRoutes(unittest.TestCase):
    """Test authentication routes and session management."""

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
        modules_to_clear = ['app', 'app.auth.utils', 'app.extensions', 'app.auth.routes']
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary database file
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

        # Clear environment variables
        for key in ['DATABASE_URL', 'SECRET_KEY', 'DEBUG', 'LOG_LEVEL']:
            if key in os.environ:
                del os.environ[key]

    def test_login_required_decorator_redirects_when_no_session(self, mock_dotenv):
        """Test 1: login_required decorator redirects to login when no session."""
        # Import after environment is set up
        from app import create_app

        app = create_app()

        # This test will fail initially because login_required decorator doesn't exist yet
        # We need to import the decorator and test it
        from app.auth.utils import login_required

        # Create a test route with the decorator
        @app.route('/protected-test')
        @login_required
        def protected_test():
            return 'This is a protected route'

        with app.test_client() as client:
            # Access protected route without session
            response = client.get('/protected-test', follow_redirects=False)

            # Should redirect to login page
            self.assertEqual(response.status_code, 302)
            self.assertIn('/auth/login', response.location)

    def test_login_required_allows_access_when_session_exists(self, mock_dotenv):
        """Test 2: login_required allows access when session exists."""
        # Import after environment is set up
        from app import create_app

        app = create_app()

        # This test will fail initially because login_required decorator doesn't exist yet
        from app.auth.utils import login_required

        # Create a test route with the decorator
        @app.route('/protected-test')
        @login_required
        def protected_test():
            return 'This is a protected route'

        with app.test_client() as client:
            # Set session manually
            with client.session_transaction() as session:
                session['user_id'] = 'testuser'

            # Access protected route with session
            response = client.get('/protected-test')

            # Should allow access
            self.assertEqual(response.status_code, 200)
            self.assertIn('This is a protected route', response.get_data(as_text=True))

    def test_protected_route_returns_expected_content_when_authenticated(self, mock_dotenv):
        """Test 3: Protected route returns expected content when authenticated."""
        # Import after environment is set up
        from app import create_app

        app = create_app()

        # This test will fail initially because login_required decorator doesn't exist yet
        from app.auth.utils import login_required

        # Create a test route with the decorator
        @app.route('/protected-test')
        @login_required
        def protected_test():
            return 'This is a protected route'

        with app.test_client() as client:
            # Set session manually
            with client.session_transaction() as session:
                session['user_id'] = 'testuser'

            # Access protected route
            response = client.get('/protected-test')

            # Should return expected content
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_data(as_text=True), 'This is a protected route')

    def test_session_destruction_on_logout_removes_user_id(self, mock_dotenv):
        """Test 4: Session destruction on logout removes user_id."""
        # Import after environment is set up
        from app import create_app

        app = create_app()

        # This test will fail initially because logout route doesn't exist yet
        with app.test_client() as client:
            # Set session first
            with client.session_transaction() as session:
                session['user_id'] = 'testuser'

            # Verify session exists
            with client.session_transaction() as session:
                self.assertEqual(session.get('user_id'), 'testuser')

            # Call logout (POST request)
            response = client.post('/auth/logout', follow_redirects=False)

            # Should redirect
            self.assertEqual(response.status_code, 302)

            # Verify session is cleared
            with client.session_transaction() as session:
                self.assertIsNone(session.get('user_id'))

    def test_session_expires_on_browser_close(self, mock_dotenv):
        """Test 5: Session expires on browser close (SESSION_PERMANENT = False)."""
        # Import after environment is set up
        from app import create_app

        app = create_app()

        # Check that session is configured to expire on browser close
        self.assertFalse(app.config.get('SESSION_PERMANENT', True))
        self.assertEqual(app.config.get('PERMANENT_SESSION_LIFETIME').total_seconds(), 30 * 60)  # 30 minutes


if __name__ == '__main__':
    unittest.main()