"""
Semester Model
==============
Represents an academic semester/term with a date range.

Database table: 'semester'

Key design decisions:
- name is unique (e.g., "Fall 2025") — you can't have two semesters with
  the same name, which would be confusing.
- A CHECK constraint enforces end_date >= start_date at the database level.
  Without this, you could accidentally create a semester that ends before
  it starts (e.g., start=2026-01-01, end=2025-06-01).
- No updated_at column: semesters are mostly static once created.
  You rarely update a semester's dates after the fact. If you do need to
  track changes, you can add it later.

Relationships:
- One Semester has many Enrollments (one-to-many).
  Access via: semester.enrollments → list of Enrollment objects
"""

from datetime import datetime, timezone

from app import db


class Semester(db.Model):
    __tablename__ = 'semester'

    __table_args__ = (
        # Ensures the semester's end date is not before its start date.
        # This is a logical invariant: a time period can't end before it begins.
        # The database enforces this even if the application code has a bug.
        db.CheckConstraint('end_date >= start_date', name='ck_semester_date_order'),
    )

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    id = db.Column(db.Integer, primary_key=True)

    # Semester name: e.g., "Fall 2025", "Spring 2026".
    # Unique constraint prevents confusion from duplicate names.
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Date range defining when the semester runs.
    # db.Date stores only the date part (no time), which is appropriate
    # for semester boundaries (you don't need hour-level precision).
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    created_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    enrollments = db.relationship(
        'Enrollment',
        back_populates='semester',
        cascade='all, delete-orphan',
        lazy='select'
    )

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Semester {self.name}>'
