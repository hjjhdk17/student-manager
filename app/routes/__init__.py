"""
API Routes Package
==================
This package contains Flask Blueprints for each API entity:
- students.py    → /api/students/...
- courses.py     → /api/courses/...
- semesters.py   → /api/semesters/...
- enrollments.py → /api/enrollments/...

Each blueprint handles CRUD operations for one entity.
Blueprints are registered in the app factory (app/__init__.py).
"""

from app.routes.students import students_bp
from app.routes.courses import courses_bp
from app.routes.semesters import semesters_bp
from app.routes.enrollments import enrollments_bp
from app.routes.auth import auth_bp

__all__ = ['students_bp', 'courses_bp', 'semesters_bp', 'enrollments_bp', 'auth_bp']
