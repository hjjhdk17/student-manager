"""
Course Model
============
Represents an academic course that students can enroll in.

Database table: 'course'

Key design decisions:
- course_code (e.g., "CS101") is the human-readable identifier.
- credits is an integer > 0 enforced by a CHECK constraint at the database level.
  This means even raw SQL INSERTs (outside the ORM) cannot insert invalid data.
- description uses db.Text instead of db.String because it has no length limit.
  In SQLite, String and Text behave the same, but in PostgreSQL/MySQL, Text
  allows unlimited length while String(n) is capped at n characters.

Constraints:
- CHECK(credits > 0): a course must be worth at least 1 credit.
  This is defined in __table_args__ because CHECK constraints apply to
  the table, not individual columns (even though this one references
  only one column).

Relationships:
- One Course has many Enrollments (one-to-many).
  Access via: course.enrollments → list of Enrollment objects
"""

from datetime import datetime, timezone

from app import db


class Course(db.Model):
    __tablename__ = 'course'

    # ------------------------------------------------------------------
    # Table-level constraints
    # ------------------------------------------------------------------
    # __table_args__ is a special SQLAlchemy attribute for table-level
    # constraints that can't be expressed as column-level attributes.
    # It must be a tuple (note the trailing comma for single-element tuples).
    __table_args__ = (
        # CHECK constraint: enforced by the database engine.
        # If any INSERT or UPDATE tries to set credits <= 0, the database
        # raises an IntegrityError. The 'name' parameter gives the constraint
        # a human-readable name for error messages and migration scripts.
        db.CheckConstraint('credits > 0', name='ck_course_credits_positive'),
    )

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    id = db.Column(db.Integer, primary_key=True)

    course_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Credits: used to weight grades in GPA calculation.
    # A 3-credit course counts 3x more than a 1-credit course.
    # CHECK constraint above ensures this is always > 0.
    credits = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    enrollments = db.relationship(
        'Enrollment',
        back_populates='course',
        cascade='all, delete-orphan',
        lazy='select'
    )

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------
    def to_dict(self):
        return {
            'id': self.id,
            'course_code': self.course_code,
            'name': self.name,
            'description': self.description,
            'credits': self.credits,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Course {self.course_code}: {self.name}>'
