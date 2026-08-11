"""
Semester API Routes
===================
Blueprint handling all /api/semesters endpoints.

Endpoints:
    GET    /api/semesters          — List all semesters
    GET    /api/semesters/<id>     — Get one semester
    POST   /api/semesters          — Create a semester
    PUT    /api/semesters/<id>     — Update a semester
    DELETE /api/semesters/<id>     — Delete a semester
"""

from datetime import date

# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Semester

semesters_bp = Blueprint('semesters', __name__, url_prefix='/api/semesters')


# ---------------------------------------------------------------------------
# GET /api/semesters — List all semesters
# ---------------------------------------------------------------------------
@semesters_bp.route('', methods=['GET'])
def list_semesters():
    """Return all semesters, ordered by start date."""
    semesters = Semester.query.order_by(Semester.start_date).all()

    return jsonify({
        'data': [s.to_dict() for s in semesters],
        'total': len(semesters),
    })


# ---------------------------------------------------------------------------
# GET /api/semesters/<id> — Get one semester
# ---------------------------------------------------------------------------
@semesters_bp.route('/<int:semester_id>', methods=['GET'])
def get_semester(semester_id):
    """Return a single semester by ID."""
    semester = db.session.get(Semester, semester_id)
    if not semester:
        return jsonify({'error': 'Semester not found'}), 404

    return jsonify(semester.to_dict())


# ---------------------------------------------------------------------------
# POST /api/semesters — Create a semester
# ---------------------------------------------------------------------------
@semesters_bp.route('', methods=['POST'])
def create_semester():
    """Create a new semester.

    Required JSON fields: name, start_date, end_date
    Validates: end_date >= start_date, unique name
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # --- Validate required fields ---
    errors = {}

    name = data.get('name')
    if not name or not str(name).strip():
        errors['name'] = 'name is required'
    else:
        name = name.strip()

    start_date = _parse_date(data.get('start_date'))
    end_date = _parse_date(data.get('end_date'))

    if not data.get('start_date'):
        errors['start_date'] = 'start_date is required'
    elif start_date is None:
        errors['start_date'] = 'start_date must be in YYYY-MM-DD format'

    if not data.get('end_date'):
        errors['end_date'] = 'end_date is required'
    elif end_date is None:
        errors['end_date'] = 'end_date must be in YYYY-MM-DD format'

    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 422

    # --- Validate date range ---
    if end_date < start_date:
        return jsonify({'error': 'end_date must be greater than or equal to start_date'}), 422

    # --- Check uniqueness ---
    if Semester.query.filter_by(name=name).first():
        return jsonify({'error': 'Semester name already exists'}), 409

    semester = Semester(
        name=name,
        start_date=start_date,
        end_date=end_date,
    )

    try:
        db.session.add(semester)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A semester with this name already exists'}), 409

    return jsonify(semester.to_dict()), 201


# ---------------------------------------------------------------------------
# PUT /api/semesters/<id> — Update a semester
# ---------------------------------------------------------------------------
@semesters_bp.route('/<int:semester_id>', methods=['PUT'])
def update_semester(semester_id):
    """Update an existing semester."""
    semester = db.session.get(Semester, semester_id)
    if not semester:
        return jsonify({'error': 'Semester not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # --- Validate required fields ---
    errors = {}

    name = data.get('name')
    if not name or not str(name).strip():
        errors['name'] = 'name is required'
    else:
        name = name.strip()

    start_date = _parse_date(data.get('start_date'))
    end_date = _parse_date(data.get('end_date'))

    if not data.get('start_date'):
        errors['start_date'] = 'start_date is required'
    elif start_date is None:
        errors['start_date'] = 'start_date must be in YYYY-MM-DD format'

    if not data.get('end_date'):
        errors['end_date'] = 'end_date is required'
    elif end_date is None:
        errors['end_date'] = 'end_date must be in YYYY-MM-DD format'

    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 422

    # --- Validate date range ---
    if end_date < start_date:
        return jsonify({'error': 'end_date must be greater than or equal to start_date'}), 422

    # --- Check uniqueness (exclude current semester) ---
    existing = Semester.query.filter(
        Semester.name == name,
        Semester.id != semester_id
    ).first()
    if existing:
        return jsonify({'error': 'Semester name already exists'}), 409

    # --- Apply updates ---
    semester.name = name
    semester.start_date = start_date
    semester.end_date = end_date

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A semester with this name already exists'}), 409

    return jsonify(semester.to_dict())


# ---------------------------------------------------------------------------
# DELETE /api/semesters/<id> — Delete a semester
# ---------------------------------------------------------------------------
@semesters_bp.route('/<int:semester_id>', methods=['DELETE'])
def delete_semester(semester_id):
    """Delete a semester and cascade-delete related enrollments."""
    semester = db.session.get(Semester, semester_id)
    if not semester:
        return jsonify({'error': 'Semester not found'}), 404

    db.session.delete(semester)
    db.session.commit()

    return jsonify({'message': 'Semester deleted successfully'})


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _parse_date(date_string):
    """Parse a date string in ISO 8601 format (YYYY-MM-DD).

    Returns None if the input is None, empty, or invalid.
    """
    if not date_string:
        return None
    try:
        return date.fromisoformat(date_string)
    except (ValueError, TypeError):
        return None
