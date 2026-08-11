"""
Course API Routes
=================
Blueprint handling all /api/courses endpoints.

Endpoints:
    GET    /api/courses          — List courses (with search)
    GET    /api/courses/<id>     — Get one course
    POST   /api/courses          — Create a course
    PUT    /api/courses/<id>     — Update a course
    DELETE /api/courses/<id>     — Delete a course
"""

# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Course

courses_bp = Blueprint('courses', __name__, url_prefix='/api/courses')


# ---------------------------------------------------------------------------
# GET /api/courses — List with search
# ---------------------------------------------------------------------------
@courses_bp.route('', methods=['GET'])
def list_courses():
    """Return all courses, optionally filtered by search term.

    Query parameters:
        search — Filter by course_code or name
    """
    search = request.args.get('search', '', type=str).strip()

    query = Course.query

    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Course.course_code.ilike(search_pattern),
                Course.name.ilike(search_pattern),
            )
        )

    query = query.order_by(Course.id)
    courses = query.all()

    return jsonify({
        'data': [c.to_dict() for c in courses],
        'total': len(courses),
    })


# ---------------------------------------------------------------------------
# GET /api/courses/<id> — Get one course
# ---------------------------------------------------------------------------
@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Return a single course by ID."""
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    return jsonify(course.to_dict())


# ---------------------------------------------------------------------------
# POST /api/courses — Create a course
# ---------------------------------------------------------------------------
@courses_bp.route('', methods=['POST'])
def create_course():
    """Create a new course.

    Required JSON fields: course_code, name, credits
    Optional JSON fields: description
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # --- Validate required fields ---
    errors = {}
    for field in ('course_code', 'name'):
        value = data.get(field)
        if not value or not str(value).strip():
            errors[field] = f'{field} is required'

    # Validate credits separately since it's numeric.
    credits_val = data.get('credits')
    if credits_val is None:
        errors['credits'] = 'credits is required'
    else:
        try:
            credits_val = int(credits_val)
            if credits_val <= 0:
                errors['credits'] = 'credits must be greater than 0'
        except (ValueError, TypeError):
            errors['credits'] = 'credits must be a positive integer'

    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 422

    course_code = data['course_code'].strip()
    name = data['name'].strip()

    # --- Check uniqueness ---
    if Course.query.filter_by(course_code=course_code).first():
        return jsonify({'error': 'Course code already exists'}), 409

    course = Course(
        course_code=course_code,
        name=name,
        description=data.get('description'),
        credits=credits_val,
    )

    try:
        db.session.add(course)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A course with this code already exists'}), 409

    return jsonify(course.to_dict()), 201


# ---------------------------------------------------------------------------
# PUT /api/courses/<id> — Update a course
# ---------------------------------------------------------------------------
@courses_bp.route('/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """Update an existing course."""
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # --- Validate required fields ---
    errors = {}
    for field in ('course_code', 'name'):
        value = data.get(field)
        if not value or not str(value).strip():
            errors[field] = f'{field} is required'

    credits_val = data.get('credits')
    if credits_val is None:
        errors['credits'] = 'credits is required'
    else:
        try:
            credits_val = int(credits_val)
            if credits_val <= 0:
                errors['credits'] = 'credits must be greater than 0'
        except (ValueError, TypeError):
            errors['credits'] = 'credits must be a positive integer'

    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 422

    course_code = data['course_code'].strip()
    name = data['name'].strip()

    # --- Check uniqueness (exclude current course) ---
    existing = Course.query.filter(
        Course.course_code == course_code,
        Course.id != course_id
    ).first()
    if existing:
        return jsonify({'error': 'Course code already exists'}), 409

    # --- Apply updates ---
    course.course_code = course_code
    course.name = name
    course.description = data.get('description')
    course.credits = credits_val

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A course with this code already exists'}), 409

    return jsonify(course.to_dict())


# ---------------------------------------------------------------------------
# DELETE /api/courses/<id> — Delete a course
# ---------------------------------------------------------------------------
@courses_bp.route('/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete a course and cascade-delete related enrollments."""
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    db.session.delete(course)
    db.session.commit()

    return jsonify({'message': 'Course deleted successfully'})
