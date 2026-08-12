"""
User API Routes (Admin-only)
=============================
Blueprint handling all /api/users endpoints.

All routes require admin role. Teacher and Student receive 403 Forbidden.

Endpoints:
    GET    /api/users          — List users
    GET    /api/users/<id>     — Get one user
    POST   /api/users          — Create a user
    PUT    /api/users/<id>     — Update a user
    DELETE /api/users/<id>     — Delete a user

Security:
- Password hashes are NEVER returned in API responses.
- Passwords are securely hashed using Werkzeug's generate_password_hash.
- Only admin users can access these endpoints.
- Cannot delete the currently logged-in admin account.
- Cannot delete the last remaining admin account.
- Only valid roles can be assigned.
"""

import re

# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify, g
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import IntegrityError

from app import db
from app.models.user import User
from app.routes.auth import login_required, role_required, VALID_ROLES

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


# ---------------------------------------------------------------------------
# GET /api/users — List all users
# ---------------------------------------------------------------------------
@users_bp.route('', methods=['GET'])
@login_required
@role_required('admin')
def list_users():
    """Return all users (without password hashes)."""
    users = User.query.order_by(User.id).all()

    return jsonify({
        'data': [u.to_dict() for u in users],
        'total': len(users),
    })


# ---------------------------------------------------------------------------
# GET /api/users/<id> — Get one user
# ---------------------------------------------------------------------------
@users_bp.route('/<int:user_id>', methods=['GET'])
@login_required
@role_required('admin')
def get_user(user_id):
    """Return a single user by ID."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user.to_dict())


# ---------------------------------------------------------------------------
# POST /api/users — Create a user
# ---------------------------------------------------------------------------
@users_bp.route('', methods=['POST'])
@login_required
@role_required('admin')
def create_user():
    """Create a new user.

    Required JSON fields: username, email, password, role
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # --- Validate required fields ---
    errors = {}
    for field in ('username', 'email', 'password'):
        value = data.get(field)
        if not value or not str(value).strip():
            errors[field] = f'{field} is required'

    role = data.get('role', 'student')
    if role not in VALID_ROLES:
        errors['role'] = f'Invalid role. Must be one of: {", ".join(VALID_ROLES)}'

    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 422

    username = data['username'].strip()
    email = data['email'].strip()
    password = data['password']

    # --- Validate email format ---
    if not _is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 422

    # --- Validate password length ---
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 422

    # --- Check uniqueness ---
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 409

    user = User(
        username=username,
        email=email,
        role=role,
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A user with this username or email already exists'}), 409

    return jsonify(user.to_dict()), 201


# ---------------------------------------------------------------------------
# PUT /api/users/<id> — Update a user
# ---------------------------------------------------------------------------
@users_bp.route('/<int:user_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_user(user_id):
    """Update an existing user.

    Optional JSON fields: username, email, role, password
    Password is only updated if provided and non-empty.
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    errors = {}

    # --- Validate username ---
    username = data.get('username')
    if username is not None:
        username = str(username).strip()
        if not username:
            errors['username'] = 'username is required'

    # --- Validate email ---
    email = data.get('email')
    if email is not None:
        email = str(email).strip()
        if not email:
            errors['email'] = 'email is required'
        elif not _is_valid_email(email):
            errors['email'] = 'Invalid email format'

    # --- Validate role ---
    role = data.get('role')
    if role is not None:
        if role not in VALID_ROLES:
            errors['role'] = f'Invalid role. Must be one of: {", ".join(VALID_ROLES)}'
        # Prevent removing admin role from the last admin
        if user.role == 'admin' and role != 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                errors['role'] = 'Cannot change role of the last admin account'

    # --- Validate password if provided ---
    password = data.get('password')
    if password is not None and password != '':
        if len(password) < 6:
            errors['password'] = 'Password must be at least 6 characters'

    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 422

    # --- Check uniqueness (exclude current user) ---
    if username is not None:
        existing = User.query.filter(
            User.username == username,
            User.id != user_id
        ).first()
        if existing:
            return jsonify({'error': 'Username already exists'}), 409

    if email is not None:
        existing = User.query.filter(
            User.email == email,
            User.id != user_id
        ).first()
        if existing:
            return jsonify({'error': 'Email already exists'}), 409

    # --- Apply updates ---
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if role is not None:
        user.role = role
    if password is not None and password != '':
        user.set_password(password)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A user with this username or email already exists'}), 409

    return jsonify(user.to_dict())


# ---------------------------------------------------------------------------
# DELETE /api/users/<id> — Delete a user
# ---------------------------------------------------------------------------
@users_bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def delete_user(user_id):
    """Delete a user account.

    Safeguards:
    - Cannot delete the currently logged-in account.
    - Cannot delete the last remaining admin account.
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Prevent deleting the currently authenticated admin
    if g.user and g.user.id == user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 409

    # Prevent deleting the last admin
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            return jsonify({'error': 'Cannot delete the last admin account'}), 409

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'})


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _is_valid_email(email):
    """Basic email format validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
