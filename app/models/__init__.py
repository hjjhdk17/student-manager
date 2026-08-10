"""
Database Models Package
=======================
This package will contain all SQLAlchemy ORM models:
- Student
- Course
- Semester
- Enrollment

Each model is defined in its own file for clarity.
This __init__.py will import and re-export all models so that
other parts of the app can do:
    from app.models import Student, Course, Semester, Enrollment

Models will be added in Phase 2.
"""
