#!/usr/bin/env python
"""Simple authentication functionality test."""
import os
import sys

# Set up environment for testing
os.environ['SECRET_KEY'] = 'test-secret-key-' * 5  # 75 characters
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['DEBUG'] = 'true'
os.environ['LOG_LEVEL'] = 'DEBUG'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock dotenv loading
import unittest.mock
with unittest.mock.patch('dotenv.load_dotenv'):
    from app import create_app

def test_session_config():
    """Test session configuration."""
    print("Testing session configuration...")
    app = create_app()

    # Check session settings
    assert app.config['SESSION_PERMANENT'] == False, "SESSION_PERMANENT should be False"
    assert app.config['SESSION_COOKIE_HTTPONLY'] == True, "SESSION_COOKIE_HTTPONLY should be True"
    assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax', "SESSION_COOKIE_SAMESITE should be 'Lax'"

    print("[OK] Session configuration correct")

def test_login_required_decorator():
    """Test login_required decorator."""
    print("Testing login_required decorator...")
    app = create_app()

    # Import the decorator
    from app.auth.utils import login_required

    # Create a test route
    @app.route('/test-protected')
    @login_required
    def test_protected():
        return 'Protected'

    with app.test_client() as client:
        # Without session - should redirect
        response = client.get('/test-protected', follow_redirects=False)
        assert response.status_code == 302, "Should redirect when not logged in"
        assert '/auth/login' in response.location, "Should redirect to login page"

        # With session - should succeed
        with client.session_transaction() as session:
            session['user_id'] = 'testuser'

        response = client.get('/test-protected')
        assert response.status_code == 200, "Should allow access with session"
        assert b'Protected' in response.data

    print("[OK] login_required decorator works")

def test_routes_exist():
    """Test that auth routes exist."""
    print("Testing auth routes exist...")
    app = create_app()

    with app.test_client() as client:
        # Check login page
        response = client.get('/auth/login')
        assert response.status_code == 200, "Login page should exist"

        # Check logout page
        response = client.get('/auth/logout')
        assert response.status_code == 200, "Logout page should exist"

        # Check protected route
        response = client.get('/auth/protected-test', follow_redirects=False)
        assert response.status_code == 302, "Protected route should redirect when not logged in"

    print("[OK] Auth routes exist")

def main():
    """Run all tests."""
    print("Running simple authentication tests...")
    try:
        test_session_config()
        test_login_required_decorator()
        test_routes_exist()
        print("\n[SUCCESS] All simple tests passed!")
        return 0
    except Exception as e:
        print(f"\n[FAILED] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())