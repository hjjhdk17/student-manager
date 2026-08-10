"""
Enrollment Model
================
Junction table linking Student, Course, and Semester. Stores the grade.

Database table: 'enrollment'

This is the most important table in the schema because it captures the
many-to-many relationship between students and courses, scoped by semester.

Key design decisions:
- Three foreign keys (student_id, course_id, semester_id) reference the
  parent tables. Each has an index for fast lookups.
- A composite UNIQUE constraint on (student_id, course_id, semester_id)
  prevents a student from enrolling in the same course twice in the same
  semester. See the design walkthrough for why this must be at the DB level.
- grade uses Numeric(4,2) instead of Float for exact decimal storage.
  This returns Python Decimal objects, ensuring GPA calculations are precise.
- grade is nullable: when a student first enrolls, they don't have a grade yet.
  NULL means "not yet graded", which is different from 0.00 (a real grade).
- CHECK(grade >= 0 AND grade <= 10) validates the Vietnamese 10-point scale.
- status tracks the enrollment lifecycle: enrolled → completed/dropped.

Relationships (the "many" side of three one-to-many relationships):
- enrollment.student → the Student who is enrolled
- enrollment.course  → the Course they're enrolled in
- enrollment.semester → the Semester of enrollment
"""

from datetime import datetime, timezone

from app import db


class Enrollment(db.Model):
    __tablename__ = 'enrollment'

    # ------------------------------------------------------------------
    # Table-level constraints
    # ------------------------------------------------------------------
    __table_args__ = (
        # Composite unique constraint: the combination of these three columns
        # must be unique across the entire table.
        #
        # Individual uniqueness is NOT what we want:
        #   - student_id alone being unique → a student can only enroll once ever
        #   - course_id alone being unique → only one student per course ever
        #
        # The COMPOSITE constraint allows:
        #   ✅ Same student, same course, different semester (retake)
        #   ✅ Same student, different course, same semester (multiple courses)
        #   ✅ Different student, same course, same semester (classmates)
        #   ❌ Same student, same course, same semester (duplicate)
        db.UniqueConstraint(
            'student_id', 'course_id', 'semester_id',
            name='uq_enrollment_student_course_semester'
        ),

        # Grade range constraint: 0.00 to 10.00 (Vietnamese grading scale).
        # NULL is allowed (not yet graded) — CHECK constraints do not reject NULL.
        # This is correct because NULL means "unknown/not yet assigned",
        # which is different from any specific grade value.
        db.CheckConstraint(
            'grade >= 0 AND grade <= 10',
            name='ck_enrollment_grade_range'
        ),
    )

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys: these are actual database columns that store integer IDs.
    # db.ForeignKey('table.column') tells the database to enforce referential
    # integrity: you can't insert a student_id that doesn't exist in the
    # student table.
    #
    # index=True on each FK: creates a B-tree index for fast lookups.
    # Without indexes, queries like "find all enrollments for student 5"
    # require scanning every row in the enrollment table (O(n)).
    # With an index, it's O(log n).
    student_id = db.Column(
        db.Integer,
        db.ForeignKey('student.id'),
        nullable=False,
        index=True
    )
    course_id = db.Column(
        db.Integer,
        db.ForeignKey('course.id'),
        nullable=False,
        index=True
    )
    semester_id = db.Column(
        db.Integer,
        db.ForeignKey('semester.id'),
        nullable=False,
        index=True
    )

    # Grade: Numeric(4,2) = 4 total digits, 2 after the decimal point.
    # Max representable value: 99.99 (but CHECK constraint limits to 10.00).
    # Min representable value: -99.99 (but CHECK constraint limits to 0.00).
    #
    # Why Numeric instead of Float:
    # Float uses IEEE 754 binary representation which cannot exactly represent
    # most decimal fractions (e.g., 0.1 + 0.2 = 0.30000000000000004).
    # Numeric stores exact decimal values, crucial for grade calculations.
    #
    # asdecimal=True (default for Numeric): SQLAlchemy returns Python Decimal
    # objects instead of floats, preserving precision in Python code too.
    #
    # nullable=True: a student may be enrolled but not yet graded.
    grade = db.Column(db.Numeric(4, 2), nullable=True)

    # Enrollment status: tracks the lifecycle.
    # - 'enrolled': currently taking the course
    # - 'completed': finished the course (grade should be set)
    # - 'dropped': withdrew from the course (grade should be NULL)
    status = db.Column(db.String(20), nullable=False, default='enrolled')

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
    # Relationships (ORM-level navigation)
    # ------------------------------------------------------------------
    # These create navigable Python attributes, NOT database columns.
    # They let you write enrollment.student instead of manually querying
    # the student table with enrollment.student_id.

    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')
    semester = db.relationship('Semester', back_populates='enrollments')

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------
    def to_dict(self):
        """Serialize to dict, including nested student/course/semester names.

        The nested data is included so the frontend can display
        "Nguyen Van A enrolled in CS101 during Fall 2025" without
        making separate API calls for each related entity.
        """
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'semester_id': self.semester_id,
            # Convert Decimal to float for JSON serialization.
            # JSON doesn't have a Decimal type, so we must convert.
            # The precision is already guaranteed by the database constraint.
            'grade': float(self.grade) if self.grade is not None else None,
            'status': self.status,
            # Include related entity details for convenience.
            # This avoids N+1 query problems on the frontend
            # (no need for separate requests to get student/course names).
            'student_code': self.student.student_code if self.student else None,
            'student_name': f'{self.student.last_name} {self.student.first_name}' if self.student else None,
            'course_code': self.course.course_code if self.course else None,
            'course_name': self.course.name if self.course else None,
            'semester_name': self.semester.name if self.semester else None,
            'course_credits': self.course.credits if self.course else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return (
            f'<Enrollment student={self.student_id} '
            f'course={self.course_id} '
            f'semester={self.semester_id} '
            f'grade={self.grade}>'
        )
