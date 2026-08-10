"""
Student Model
=============
Represents a student in the system.

Database table: 'student'

Key design decisions:
- student_code is the human-readable identifier (e.g., "SV001"), while id is
  the internal primary key. We never expose auto-increment IDs to users because
  they reveal information about the system (e.g., how many students exist).
- email is unique because it's a natural identifier for contact/login purposes.
- Both student_code and email have database indexes for fast lookups.
  When you search by student code or check email uniqueness, the database uses
  these indexes instead of scanning every row.
- date_of_birth, gender, phone, address are nullable — not every student record
  will have all fields filled in, especially during initial data entry.

Relationships:
- One Student has many Enrollments (one-to-many).
  Access via: student.enrollments → list of Enrollment objects
  The cascade='all, delete-orphan' means deleting a student automatically
  deletes all their enrollment records.
"""

from datetime import datetime, timezone

from app import db


class Student(db.Model):
    """ORM model for the 'student' table.

    SQLAlchemy maps this class to a database table. Each instance of Student
    represents one row. Column definitions become table columns with the
    specified types and constraints.
    """

    # Explicit table name. Without this, SQLAlchemy would auto-generate one
    # from the class name (e.g., 'student' from 'Student'). Being explicit
    # avoids surprises and makes foreign key references clearer.
    __tablename__ = 'student'

    # -----------------------------------------------------------------------
    # Columns
    # -----------------------------------------------------------------------

    # Primary key: auto-incremented integer.
    # SQLite auto-increments integer PKs by default — no need for a Sequence.
    id = db.Column(db.Integer, primary_key=True)

    # Student code: the human-facing identifier.
    # unique=True → database enforces no duplicates (creates a unique index).
    # nullable=False → database rejects NULL values (INSERT without this fails).
    # index=True → creates a B-tree index for O(log n) lookups instead of O(n).
    #   Note: unique=True already implies an index in most databases including
    #   SQLite, but being explicit documents intent.
    student_code = db.Column(db.String(20), unique=True, nullable=False, index=True)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    # Email: unique contact identifier.
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    # Optional biographical fields.
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)

    # Audit timestamps.
    # default= is a Python-side default: SQLAlchemy calls this function when
    # creating a new object. It does NOT add a DEFAULT clause to the SQL DDL.
    # onupdate= is also Python-side: called automatically by SQLAlchemy on
    # every UPDATE operation.
    created_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # -----------------------------------------------------------------------
    # Relationships (ORM-level, not database columns)
    # -----------------------------------------------------------------------

    # This does NOT create a column in the 'student' table.
    # It tells SQLAlchemy: "when I access student.enrollments, query the
    # enrollment table WHERE student_id = this student's id."
    #
    # back_populates='student': connects this to Enrollment.student, so both
    #   sides stay in sync (e.g., enrollment.student = some_student also adds
    #   the enrollment to some_student.enrollments).
    #
    # cascade='all, delete-orphan':
    #   - 'all': propagate save, merge, refresh, expunge to enrollments
    #   - 'delete-orphan': if an enrollment is removed from this list
    #     (student.enrollments.remove(e)), delete it from the database too
    #   - Combined with the delete part of 'all': deleting a student deletes
    #     all their enrollments
    #
    # lazy='select' (default): enrollments are loaded with a SELECT query
    #   the first time you access student.enrollments. Not loaded upfront.
    enrollments = db.relationship(
        'Enrollment',
        back_populates='student',
        cascade='all, delete-orphan',
        lazy='select'
    )

    # -----------------------------------------------------------------------
    # Methods
    # -----------------------------------------------------------------------

    def to_dict(self):
        """Convert this model instance to a dictionary for JSON serialization.

        Flask's jsonify() can't serialize SQLAlchemy objects directly, so we
        need this conversion method. Each model defines its own to_dict()
        because each model knows its own columns.

        Dates are converted to ISO 8601 strings (e.g., "2025-03-15") which
        are universally parseable by JavaScript's Date constructor.
        """
        return {
            'id': self.id,
            'student_code': self.student_code,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        """Developer-friendly string representation.
        Shown in the Python REPL and in debug logs.
        Example: <Student SV001: Nguyen Van A>
        """
        return f'<Student {self.student_code}: {self.last_name} {self.first_name}>'
