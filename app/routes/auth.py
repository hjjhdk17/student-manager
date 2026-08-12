"""
Authentication Routes
=====================
Blueprint handling login, logout, and session management.

Endpoints:
    GET  /login  — Display the login page
    POST /login  — Validate credentials and create session
    POST /logout — Clear session and redirect to login
    GET  /api/auth/me — Return the currently authenticated user (JSON)

Authentication is session-based using Flask's built-in session mechanism.
The user_id is stored in the session after successful login.
"""

import functools

# pyrefly: ignore [missing-import]
from flask import (
    Blueprint, request, render_template, redirect, url_for,
    session, jsonify, g
)

from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


# ---------------------------------------------------------------------------
# Authentication Helper
# ---------------------------------------------------------------------------

def login_required(f):
    """Decorator that protects a route — requires an authenticated session.

    For HTML routes: redirects to /login.
    For API routes (Accept: application/json or /api/ prefix):
        returns 401 JSON response.
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if g.get('user') is None:
            # Check if this is an API request
            if _is_api_request():
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def _is_api_request():
    """Determine if the current request is an API request."""
    # Check the URL path
    if request.path.startswith('/api/'):
        return True
    # Check the Accept header
    accept = request.headers.get('Accept', '')
    if 'application/json' in accept:
        return True
    return False


# ---------------------------------------------------------------------------
# Before-request: load user from session
# ---------------------------------------------------------------------------

def load_user():
    """Load the current user from the session into Flask's g object.

    This runs before every request in the app. It checks if user_id
    exists in the session and loads the corresponding User object.

    The user is stored in g.user so it's accessible in routes and templates.
    """
    user_id = session.get('user_id')
    if user_id is not None:
        g.user = db.session.get(User, user_id)
    else:
        g.user = None


# ---------------------------------------------------------------------------
# GET /login — Display login page
# ---------------------------------------------------------------------------

@auth_bp.route('/login', methods=['GET'])
def login():
    """Render the login page.

    If the user is already authenticated, redirect to the main application.
    """
    if g.get('user') is not None:
        return redirect(url_for('index'))
    return render_template('login.html')


# ---------------------------------------------------------------------------
# POST /login — Validate credentials
# ---------------------------------------------------------------------------

@auth_bp.route('/login', methods=['POST'])
def login_post():
    """Validate login credentials and create an authenticated session.

    Accepts either username or email in the 'username' field.
    Uses a generic error message to avoid revealing whether an account exists.
    """
    username_or_email = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    error = None

    if not username_or_email:
        error = 'Username or email is required.'
    elif not password:
        error = 'Password is required.'
    else:
        # Look up user by username OR email.
        user = User.query.filter(
            db.or_(
                User.username == username_or_email,
                User.email == username_or_email,
            )
        ).first()

        if user is None or not user.check_password(password):
            # Generic message: do not reveal whether the account exists.
            error = 'Invalid username/email or password.'

    if error:
        return render_template('login.html', error=error), 401

    # --- Create authenticated session ---
    session.clear()
    session['user_id'] = user.id
    # Regenerate session to prevent session fixation attacks.
    session.permanent = True

    return redirect(url_for('index'))


# ---------------------------------------------------------------------------
# POST /logout — Clear session
# ---------------------------------------------------------------------------

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Clear the authentication session and redirect to login."""
    session.clear()
    return redirect(url_for('auth.login'))


# ---------------------------------------------------------------------------
# GET /api/auth/me — Current user info (JSON)
# ---------------------------------------------------------------------------

@auth_bp.route('/api/auth/me', methods=['GET'])
def current_user():
    """Return the currently authenticated user as JSON.

    Used by the frontend to display the logged-in username.
    Returns 401 if not authenticated.
    """
    user = g.get('user')
    if user is None:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify(user.to_dict())
