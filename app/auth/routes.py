"""Authentication routes for login and logout."""
from flask import render_template, redirect, url_for, flash, session, request
from . import bp
from .utils import verify_user, login_required


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route.

    GET: Display login form.
    POST: Validate credentials and create session.
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Validate credentials
        user = verify_user(username, password)
        if user:
            # Create session
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            # Redirect to todo matrix after login
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            # Re-render form with error
            return render_template('login.html', username=username)

    # GET request - render login form
    return render_template('login.html')


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logout route.

    GET: Display logout confirmation.
    POST: Destroy session and logout.
    """
    if request.method == 'POST':
        # Clear session
        session.pop('user_id', None)
        session.pop('username', None)
        flash('You have been logged out.', 'info')
        return redirect(url_for('auth.login'))

    # GET request - render logout confirmation
    return render_template('logout.html')


@bp.route('/protected-test')
@login_required
def protected_test():
    """Protected route for testing login_required decorator."""
    return 'This is a protected route'