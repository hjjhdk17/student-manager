"""
Database Models Package
=======================
This __init__.py imports all model classes and re-exports them so that
the rest of the application can do:

    from app.models import Student, Course, Semester, Enrollment

Why import here?
1. Convenience: one import statement instead of four.
2. Flask-Migrate needs all models to be imported before it can detect them.
   When Alembic runs `flask db migrate`, it compares the current database
   schema against the models it knows about. If a model isn't imported,
   Alembic won't generate a migration for it.
3. The __all__ list explicitly declares the public API of this package.
"""

from app.models.student import Student
from app.models.course import Course
from app.models.semester import Semester
from app.models.enrollment import Enrollment

# __all__ controls what `from app.models import *` exports.
# It also serves as documentation: these are the public symbols.
__all__ = ['Student', 'Course', 'Semester', 'Enrollment']
