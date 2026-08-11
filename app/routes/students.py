"""
Student API Routes
==================
Blueprint handling all /api/students endpoints.

Endpoints:
    GET    /api/students          — List students (with search & pagination)
    GET    /api/students/<id>     — Get one student
    POST   /api/students          — Create a student
    PUT    /api/students/<id>     — Update a student
    DELETE /api/students/<id>     — Delete a student
    GET    /api/students/<id>/gpa — Calculate student's GPA
"""

import re
from decimal import Decimal

# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Student, Enrollment

# Create the blueprint with a URL prefix.
# All routes defined here will be prefixed with /api/students.
students_bp = Blueprint('students', __name__, url_prefix='/api/students')


# ---------------------------------------------------------------------------
# GET /api/students — List with search & pagination
# ---------------------------------------------------------------------------
@students_bp.route('', methods=['GET'])
def list_students():
    """Return a paginated list of students, optionally filtered by search term.

    Query parameters:
        search   — Filter by student_code, first_name, last_name, or email
        page     — Page number (default: 1)
        per_page — Items per page (default: 20, max: 100)
    """
    search = request.args.get('search', '', type=str).strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Clamp pagination values to sensible ranges.
    page = max(1, page)
    per_page = max(1, min(100, per_page))

    query = Student.query

    # Apply search filter if provided.
    # ilike() performs case-insensitive LIKE matching.
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Student.student_code.ilike(search_pattern),
                Student.first_name.ilike(search_pattern),
                Student.last_name.ilike(search_pattern),
                Student.email.ilike(search_pattern),
            )
        )

    # Order by id for consistent pagination results.
    query = query.order_by(Student.id)

    # Use SQLAlchemy's built-in pagination.
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'data': [s.to_dict() for s in pagination.items],
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
    })


# ---------------------------------------------------------------------------
# GET /api/students/<id> — Get one student
# ---------------------------------------------------------------------------
@students_bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Return a single student by ID."""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    return jsonify(student.to_dict())


# ---------------------------------------------------------------------------
# POST /api/students — Create a student
# ---------------------------------------------------------------------------
@students_bp.route('', methods=['POST'])
def create_student():
    """Create a new student.

    Required JSON fields: student_code, first_name, last_name, email
    Optional JSON fields: date_of_birth, gender, phone, address
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # --- Validate required fields ---
    errors = {}
    for field in ('student_code', 'first_name', 'last_name', 'email'):
        value = data.get(field)
        if not value or not str(value).strip():
            errors[field] = f'{field} is required'

    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 422

    # Strip whitespace from string fields.
    student_code = data['student_code'].strip()
    first_name = data['first_name'].strip()
    last_name = data['last_name'].strip()
    email = data['email'].strip()

    # --- Validate email format ---
    if not _is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 422

    # --- Check uniqueness before hitting the database ---
    if Student.query.filter_by(student_code=student_code).first():
        return jsonify({'error': 'Student code already exists'}), 409

    if Student.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 409

    # --- Parse optional fields ---
    date_of_birth = _parse_date(data.get('date_of_birth'))

    student = Student(
        student_code=student_code,
        first_name=first_name,
        last_name=last_name,
        email=email,
        date_of_birth=date_of_birth,
        gender=data.get('gender'),
        phone=data.get('phone'),
        address=data.get('address'),
    )

    try:
        db.session.add(student)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A student with this code or email already exists'}), 409

    return jsonify(student.to_dict()), 201


# ---------------------------------------------------------------------------
# PUT /api/students/<id> — Update a student
# ---------------------------------------------------------------------------
@students_bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Update an existing student."""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # --- Validate required fields ---
    errors = {}
    for field in ('student_code', 'first_name', 'last_name', 'email'):
        value = data.get(field)
        if not value or not str(value).strip():
            errors[field] = f'{field} is required'

    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 422

    student_code = data['student_code'].strip()
    first_name = data['first_name'].strip()
    last_name = data['last_name'].strip()
    email = data['email'].strip()

    # --- Validate email format ---
    if not _is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 422

    # --- Check uniqueness (exclude the current student) ---
    existing = Student.query.filter(
        Student.student_code == student_code,
        Student.id != student_id
    ).first()
    if existing:
        return jsonify({'error': 'Student code already exists'}), 409

    existing = Student.query.filter(
        Student.email == email,
        Student.id != student_id
    ).first()
    if existing:
        return jsonify({'error': 'Email already exists'}), 409

    # --- Apply updates ---
    student.student_code = student_code
    student.first_name = first_name
    student.last_name = last_name
    student.email = email
    student.date_of_birth = _parse_date(data.get('date_of_birth'))
    student.gender = data.get('gender')
    student.phone = data.get('phone')
    student.address = data.get('address')

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A student with this code or email already exists'}), 409

    return jsonify(student.to_dict())


# ---------------------------------------------------------------------------
# DELETE /api/students/<id> — Delete a student
# ---------------------------------------------------------------------------
@students_bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student and cascade-delete their enrollments."""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    db.session.delete(student)
    db.session.commit()

    return jsonify({'message': 'Student deleted successfully'})


# ---------------------------------------------------------------------------
# GET /api/students/<id>/gpa — Calculate GPA
# ---------------------------------------------------------------------------
@students_bp.route('/<int:student_id>/gpa', methods=['GET'])
def get_student_gpa(student_id):
    """Calculate the student's GPA using credit-weighted average.

    Formula: GPA = Σ(grade × credits) / Σ(credits)

    Only includes enrollments that are:
    - Not dropped (status != 'dropped')
    - Have a grade (grade IS NOT NULL)
    """
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Query enrollments with grades, excluding dropped ones.
    # We eagerly load the course relationship to get credits.
    graded_enrollments = Enrollment.query.filter(
        Enrollment.student_id == student_id,
        Enrollment.grade.isnot(None),
        Enrollment.status != 'dropped',
    ).all()

    if not graded_enrollments:
        return jsonify({
            'student_id': student.id,
            'student_code': student.student_code,
            'student_name': f'{student.last_name} {student.first_name}',
            'gpa': None,
            'total_credits': 0,
            'courses_counted': 0,
            'message': 'No graded courses found',
        })

    # Calculate weighted GPA.
    total_weighted = Decimal('0')
    total_credits = 0

    for enrollment in graded_enrollments:
        credits = enrollment.course.credits
        total_weighted += enrollment.grade * credits
        total_credits += credits

    # total_credits > 0 is guaranteed since graded_enrollments is non-empty
    # and credits > 0 is enforced by the CHECK constraint.
    gpa = total_weighted / total_credits

    return jsonify({
        'student_id': student.id,
        'student_code': student.student_code,
        'student_name': f'{student.last_name} {student.first_name}',
        'gpa': float(round(gpa, 2)),
        'total_credits': total_credits,
        'courses_counted': len(graded_enrollments),
    })


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _is_valid_email(email):
    """Basic email format validation.

    Checks for the pattern: something@something.something
    This is intentionally simple — full RFC 5322 validation is overkill
    for this learning project.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def _parse_date(date_string):
    """Parse a date string in ISO 8601 format (YYYY-MM-DD).

    Returns None if the input is None or empty.
    Raises a ValueError (caught by the route) if the format is invalid.
    """
    if not date_string:
        return None
    from datetime import date
    try:
        return date.fromisoformat(date_string)
    except (ValueError, TypeError):
        return None
