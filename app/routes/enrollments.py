"""
Enrollment API Routes
=====================
Blueprint handling all /api/enrollments endpoints.

Endpoints:
    GET    /api/enrollments          — List enrollments (with filters)
    GET    /api/enrollments/<id>     — Get one enrollment
    POST   /api/enrollments          — Create an enrollment
    PUT    /api/enrollments/<id>     — Update an enrollment (grade/status)
    DELETE /api/enrollments/<id>     — Delete an enrollment
"""

from decimal import Decimal, InvalidOperation

# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Student, Course, Semester, Enrollment

enrollments_bp = Blueprint('enrollments', __name__, url_prefix='/api/enrollments')

# Valid enrollment statuses.
VALID_STATUSES = ('enrolled', 'completed', 'dropped')


# ---------------------------------------------------------------------------
# GET /api/enrollments — List with filters
# ---------------------------------------------------------------------------
@enrollments_bp.route('', methods=['GET'])
def list_enrollments():
    """Return enrollments, optionally filtered by student, course, and/or semester.

    Query parameters (all combinable):
        student_id  — Filter by student ID
        course_id   — Filter by course ID
        semester_id — Filter by semester ID
    """
    query = Enrollment.query

    # Apply filters if provided.
    student_id = request.args.get('student_id', type=int)
    course_id = request.args.get('course_id', type=int)
    semester_id = request.args.get('semester_id', type=int)

    if student_id is not None:
        query = query.filter(Enrollment.student_id == student_id)
    if course_id is not None:
        query = query.filter(Enrollment.course_id == course_id)
    if semester_id is not None:
        query = query.filter(Enrollment.semester_id == semester_id)

    query = query.order_by(Enrollment.id)
    enrollments = query.all()

    return jsonify({
        'data': [e.to_dict() for e in enrollments],
        'total': len(enrollments),
    })


# ---------------------------------------------------------------------------
# GET /api/enrollments/<id> — Get one enrollment
# ---------------------------------------------------------------------------
@enrollments_bp.route('/<int:enrollment_id>', methods=['GET'])
def get_enrollment(enrollment_id):
    """Return a single enrollment by ID."""
    enrollment = db.session.get(Enrollment, enrollment_id)
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    return jsonify(enrollment.to_dict())


# ---------------------------------------------------------------------------
# POST /api/enrollments — Create an enrollment
# ---------------------------------------------------------------------------
@enrollments_bp.route('', methods=['POST'])
def create_enrollment():
    """Create a new enrollment.

    Required JSON fields: student_id, course_id, semester_id
    Optional JSON fields: grade, status (default: 'enrolled')

    Validates:
    - Referenced student, course, and semester exist
    - Grade is null or between 0 and 10
    - Status is one of: enrolled, completed, dropped
    - No duplicate enrollment (student + course + semester)
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    errors = {}

    # --- Validate required foreign keys ---
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    semester_id = data.get('semester_id')

    if student_id is None:
        errors['student_id'] = 'student_id is required'
    if course_id is None:
        errors['course_id'] = 'course_id is required'
    if semester_id is None:
        errors['semester_id'] = 'semester_id is required'

    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 422

    # --- Validate foreign key types ---
    try:
        student_id = int(student_id)
        course_id = int(course_id)
        semester_id = int(semester_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'student_id, course_id, and semester_id must be integers'}), 422

    # --- Validate referenced entities exist ---
    if not db.session.get(Student, student_id):
        return jsonify({'error': 'Student not found'}), 404

    if not db.session.get(Course, course_id):
        return jsonify({'error': 'Course not found'}), 404

    if not db.session.get(Semester, semester_id):
        return jsonify({'error': 'Semester not found'}), 404

    # --- Validate grade ---
    grade = _validate_grade(data.get('grade'))
    if grade == 'invalid':
        return jsonify({'error': 'Grade must be a number between 0 and 10'}), 422

    # --- Validate status ---
    status = data.get('status', 'enrolled')
    if status not in VALID_STATUSES:
        return jsonify({
            'error': f'Invalid status. Must be one of: {", ".join(VALID_STATUSES)}'
        }), 422

    # --- Check for duplicate enrollment ---
    existing = Enrollment.query.filter_by(
        student_id=student_id,
        course_id=course_id,
        semester_id=semester_id,
    ).first()
    if existing:
        return jsonify({'error': 'Student is already enrolled in this course for this semester'}), 409

    enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id,
        semester_id=semester_id,
        grade=grade,
        status=status,
    )

    try:
        db.session.add(enrollment)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Duplicate enrollment or integrity constraint violation'}), 409

    return jsonify(enrollment.to_dict()), 201


# ---------------------------------------------------------------------------
# PUT /api/enrollments/<id> — Update grade and/or status
# ---------------------------------------------------------------------------
@enrollments_bp.route('/<int:enrollment_id>', methods=['PUT'])
def update_enrollment(enrollment_id):
    """Update an existing enrollment's grade and/or status.

    Only grade and status can be updated (not the student/course/semester).
    """
    enrollment = db.session.get(Enrollment, enrollment_id)
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # --- Validate grade if provided ---
    if 'grade' in data:
        grade = _validate_grade(data['grade'])
        if grade == 'invalid':
            return jsonify({'error': 'Grade must be a number between 0 and 10'}), 422
        enrollment.grade = grade

    # --- Validate status if provided ---
    if 'status' in data:
        status = data['status']
        if status not in VALID_STATUSES:
            return jsonify({
                'error': f'Invalid status. Must be one of: {", ".join(VALID_STATUSES)}'
            }), 422
        enrollment.status = status

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Database integrity error'}), 409

    return jsonify(enrollment.to_dict())


# ---------------------------------------------------------------------------
# DELETE /api/enrollments/<id> — Delete an enrollment
# ---------------------------------------------------------------------------
@enrollments_bp.route('/<int:enrollment_id>', methods=['DELETE'])
def delete_enrollment(enrollment_id):
    """Delete an enrollment."""
    enrollment = db.session.get(Enrollment, enrollment_id)
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    db.session.delete(enrollment)
    db.session.commit()

    return jsonify({'message': 'Enrollment deleted successfully'})


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _validate_grade(grade_value):
    """Validate and convert a grade value.

    Returns:
        None          — if grade_value is None (no grade)
        Decimal       — if valid grade between 0 and 10
        'invalid'     — if the grade is invalid
    """
    if grade_value is None:
        return None

    try:
        grade = Decimal(str(grade_value))
    except (InvalidOperation, ValueError, TypeError):
        return 'invalid'

    if grade < 0 or grade > 10:
        return 'invalid'

    return grade
