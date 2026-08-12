"""
Database Seed Script
====================
Populates the database with realistic sample data for development and testing.

Usage:
    source venv/bin/activate
    python seed.py

What it does:
1. Clears all existing data (enrollments first due to foreign keys, then
   students/courses/semesters).
2. Inserts sample students, courses, semesters, and enrollments.
3. Commits the transaction.

Why clear data first?
The script is idempotent — you can run it multiple times without duplicating
data. This is important during development when you might want to reset
the database to a known state.

Why delete in that order?
Foreign key constraints prevent deleting a student who has enrollments.
By deleting enrollments first, we remove the FK references, allowing
the parent records to be deleted safely. This is called "respecting
referential integrity."

Note on SQLite foreign key enforcement:
SQLite does NOT enforce foreign keys by default. You must run
    PRAGMA foreign_keys = ON;
to enable enforcement. SQLAlchemy does this automatically when configured
correctly, but it's worth knowing.
"""

from datetime import date
from decimal import Decimal

from app import create_app, db
from app.models import Student, Course, Semester, Enrollment, User


def seed():
    """Populate the database with sample data."""

    app = create_app()

    # app.app_context() is required because SQLAlchemy needs to know which
    # Flask app (and therefore which database) to use. Outside of a request
    # (like in this script), we must manually push an application context.
    with app.app_context():

        print('Clearing existing data...')
        # Delete in order: children first, then parents.
        # This respects foreign key constraints.
        Enrollment.query.delete()
        Student.query.delete()
        Course.query.delete()
        Semester.query.delete()
        User.query.delete()
        db.session.commit()

        # ------------------------------------------------------------------
        # Development Users
        # ------------------------------------------------------------------
        print('Creating development users...')

        # IMPORTANT: These credentials are for LOCAL DEVELOPMENT ONLY.
        # Do NOT use these in production.
        admin_user = User(
            username='admin',
            email='admin@example.com',
            role='admin',
        )
        admin_user.set_password('admin123')

        student_user = User(
            username='student',
            email='student@example.com',
            role='student',
        )
        student_user.set_password('student123')

        teacher_user = User(
            username='teacher',
            email='teacher@example.com',
            role='teacher',
        )
        teacher_user.set_password('teacher123')

        db.session.add_all([admin_user, student_user, teacher_user])

        # ------------------------------------------------------------------
        # Students
        # ------------------------------------------------------------------
        print('Creating students...')
        students = [
            Student(
                student_code='SV001',
                first_name='An',
                last_name='Nguyen Van',
                email='an.nguyen@university.edu.vn',
                date_of_birth=date(2003, 3, 15),
                gender='Male',
                phone='0901234567',
                address='123 Le Loi, District 1, Ho Chi Minh City'
            ),
            Student(
                student_code='SV002',
                first_name='Binh',
                last_name='Tran Thi',
                email='binh.tran@university.edu.vn',
                date_of_birth=date(2003, 7, 22),
                gender='Female',
                phone='0912345678',
                address='456 Nguyen Hue, District 1, Ho Chi Minh City'
            ),
            Student(
                student_code='SV003',
                first_name='Cuong',
                last_name='Le Minh',
                email='cuong.le@university.edu.vn',
                date_of_birth=date(2004, 1, 10),
                gender='Male',
                phone='0923456789',
                address='789 Hai Ba Trung, District 3, Ho Chi Minh City'
            ),
            Student(
                student_code='SV004',
                first_name='Dung',
                last_name='Pham Hoang',
                email='dung.pham@university.edu.vn',
                date_of_birth=date(2003, 11, 5),
                gender='Female',
                phone='0934567890',
                address='321 Vo Van Tan, District 3, Ho Chi Minh City'
            ),
            Student(
                student_code='SV005',
                first_name='Em',
                last_name='Hoang Thi',
                email='em.hoang@university.edu.vn',
                date_of_birth=date(2004, 5, 20),
                gender='Female',
                phone='0945678901',
                address='654 Pasteur, District 1, Ho Chi Minh City'
            ),
            Student(
                student_code='SV999',
                first_name='Student',
                last_name='Test',
                email='student@example.com',
                date_of_birth=date(2000, 1, 1),
                gender='Other',
                phone='0999999999',
                address='Test Address'
            ),
        ]

        # db.session.add_all() adds multiple objects to the session in one call.
        # They are not written to the database yet — that happens on commit().
        db.session.add_all(students)

        # ------------------------------------------------------------------
        # Courses
        # ------------------------------------------------------------------
        print('Creating courses...')
        courses = [
            Course(
                course_code='CS101',
                name='Introduction to Programming',
                description='Fundamentals of programming using Python. Covers variables, '
                            'control flow, functions, and basic data structures.',
                credits=3
            ),
            Course(
                course_code='CS201',
                name='Data Structures and Algorithms',
                description='Arrays, linked lists, trees, graphs, sorting, and searching '
                            'algorithms. Time and space complexity analysis.',
                credits=4
            ),
            Course(
                course_code='CS301',
                name='Database Systems',
                description='Relational database design, SQL, normalization, indexing, '
                            'transactions, and query optimization.',
                credits=3
            ),
            Course(
                course_code='MATH101',
                name='Calculus I',
                description='Limits, derivatives, integrals, and their applications.',
                credits=3
            ),
            Course(
                course_code='MATH201',
                name='Linear Algebra',
                description='Vectors, matrices, linear transformations, eigenvalues, '
                            'and eigenvectors.',
                credits=3
            ),
            Course(
                course_code='ENG101',
                name='English Communication',
                description='Academic English skills: reading, writing, listening, '
                            'and presentation.',
                credits=2
            ),
        ]
        db.session.add_all(courses)

        # ------------------------------------------------------------------
        # Semesters
        # ------------------------------------------------------------------
        print('Creating semesters...')
        semesters = [
            Semester(
                name='Fall 2025',
                start_date=date(2025, 9, 1),
                end_date=date(2025, 12, 31)
            ),
            Semester(
                name='Spring 2026',
                start_date=date(2026, 1, 15),
                end_date=date(2026, 5, 31)
            ),
            Semester(
                name='Fall 2026',
                start_date=date(2026, 9, 1),
                end_date=date(2026, 12, 31)
            ),
        ]
        db.session.add_all(semesters)

        # Flush to get the auto-generated IDs assigned.
        # flush() writes the INSERT statements to the database but does NOT
        # commit the transaction. This means the IDs are available (populated
        # by SQLite's autoincrement) but can still be rolled back if something
        # goes wrong later.
        db.session.flush()

        # Now we can reference students[0].id, courses[0].id, etc.
        # because flush() triggered the INSERT and populated the PKs.

        # ------------------------------------------------------------------
        # Enrollments
        # ------------------------------------------------------------------
        print('Creating enrollments...')

        # Use Decimal() for grade values since the column is Numeric(4,2).
        # This ensures exact decimal representation — no floating-point
        # rounding issues.
        enrollments = [
            # --- Fall 2025 ---
            # SV001 (An) takes CS101, MATH101, ENG101
            Enrollment(
                student_id=students[0].id,
                course_id=courses[0].id,   # CS101
                semester_id=semesters[0].id,  # Fall 2025
                grade=Decimal('8.50'),
                status='completed'
            ),
            Enrollment(
                student_id=students[0].id,
                course_id=courses[3].id,   # MATH101
                semester_id=semesters[0].id,
                grade=Decimal('7.25'),
                status='completed'
            ),
            Enrollment(
                student_id=students[0].id,
                course_id=courses[5].id,   # ENG101
                semester_id=semesters[0].id,
                grade=Decimal('9.00'),
                status='completed'
            ),

            # SV002 (Binh) takes CS101, MATH101
            Enrollment(
                student_id=students[1].id,
                course_id=courses[0].id,   # CS101
                semester_id=semesters[0].id,
                grade=Decimal('9.25'),
                status='completed'
            ),
            Enrollment(
                student_id=students[1].id,
                course_id=courses[3].id,   # MATH101
                semester_id=semesters[0].id,
                grade=Decimal('6.50'),
                status='completed'
            ),

            # SV003 (Cuong) takes CS101, ENG101
            Enrollment(
                student_id=students[2].id,
                course_id=courses[0].id,   # CS101
                semester_id=semesters[0].id,
                grade=Decimal('5.75'),
                status='completed'
            ),
            Enrollment(
                student_id=students[2].id,
                course_id=courses[5].id,   # ENG101
                semester_id=semesters[0].id,
                grade=Decimal('7.00'),
                status='completed'
            ),

            # SV004 (Dung) takes MATH101, ENG101
            Enrollment(
                student_id=students[3].id,
                course_id=courses[3].id,   # MATH101
                semester_id=semesters[0].id,
                grade=Decimal('8.00'),
                status='completed'
            ),
            Enrollment(
                student_id=students[3].id,
                course_id=courses[5].id,   # ENG101
                semester_id=semesters[0].id,
                grade=Decimal('8.75'),
                status='completed'
            ),

            # --- Spring 2026 ---
            # SV001 (An) takes CS201, MATH201
            Enrollment(
                student_id=students[0].id,
                course_id=courses[1].id,   # CS201
                semester_id=semesters[1].id,  # Spring 2026
                grade=Decimal('7.75'),
                status='completed'
            ),
            Enrollment(
                student_id=students[0].id,
                course_id=courses[4].id,   # MATH201
                semester_id=semesters[1].id,
                grade=Decimal('6.50'),
                status='completed'
            ),

            # SV002 (Binh) takes CS201, CS301
            Enrollment(
                student_id=students[1].id,
                course_id=courses[1].id,   # CS201
                semester_id=semesters[1].id,
                grade=Decimal('8.50'),
                status='completed'
            ),
            Enrollment(
                student_id=students[1].id,
                course_id=courses[2].id,   # CS301
                semester_id=semesters[1].id,
                grade=Decimal('9.00'),
                status='completed'
            ),

            # SV003 (Cuong) takes CS201 — dropped
            Enrollment(
                student_id=students[2].id,
                course_id=courses[1].id,   # CS201
                semester_id=semesters[1].id,
                grade=None,  # No grade — dropped
                status='dropped'
            ),

            # --- Fall 2026 (current — no grades yet) ---
            # SV001 (An) takes CS301
            Enrollment(
                student_id=students[0].id,
                course_id=courses[2].id,   # CS301
                semester_id=semesters[2].id,  # Fall 2026
                grade=None,  # Not yet graded
                status='enrolled'
            ),

            # SV004 (Dung) takes CS101, CS201
            Enrollment(
                student_id=students[3].id,
                course_id=courses[0].id,   # CS101
                semester_id=semesters[2].id,
                grade=None,
                status='enrolled'
            ),
            Enrollment(
                student_id=students[3].id,
                course_id=courses[1].id,   # CS201
                semester_id=semesters[2].id,
                grade=None,
                status='enrolled'
            ),

            # SV005 (Em) takes CS101, MATH101, ENG101
            Enrollment(
                student_id=students[4].id,
                course_id=courses[0].id,   # CS101
                semester_id=semesters[2].id,
                grade=None,
                status='enrolled'
            ),
            Enrollment(
                student_id=students[4].id,
                course_id=courses[3].id,   # MATH101
                semester_id=semesters[2].id,
                grade=None,
                status='enrolled'
            ),
            Enrollment(
                student_id=students[4].id,
                course_id=courses[5].id,   # ENG101
                semester_id=semesters[2].id,
                grade=None,
                status='enrolled'
            ),

            # SV999 (Test Student) takes CS101
            Enrollment(
                student_id=students[5].id,
                course_id=courses[0].id,   # CS101
                semester_id=semesters[0].id,
                grade=Decimal('8.00'),
                status='completed'
            ),
        ]
        db.session.add_all(enrollments)

        # Commit the transaction: all INSERTs are finalized atomically.
        # If any INSERT fails (e.g., duplicate key, check constraint violation),
        # ALL changes are rolled back — the database stays consistent.
        db.session.commit()

        # ------------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------------
        print()
        print(f'Seeded {User.query.count()} users')
        print(f'Seeded {Student.query.count()} students')
        print(f'Seeded {Course.query.count()} courses')
        print(f'Seeded {Semester.query.count()} semesters')
        print(f'Seeded {Enrollment.query.count()} enrollments')
        print()
        print('Development login credentials (LOCAL DEVELOPMENT ONLY):')
        print('  Admin:   username=admin    password=admin123')
        print('  Teacher: username=teacher  password=teacher123')
        print('  Student: username=student  password=student123')
        print()
        print('Done! Database is ready for development.')


if __name__ == '__main__':
    seed()
