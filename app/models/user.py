"""
User Model
==========
Represents a user account in the system.

Database table: 'user'

Key design decisions:
- username is the primary login identifier, must be unique.
- email is also unique, used as an alternative login identifier.
- password_hash stores the hashed password using Werkzeug's security module.
  Plaintext passwords are NEVER stored.
- role stores the user's role (e.g., 'student', 'admin'). Defaults to 'student'.
  Full role-based authorization will be implemented in Phase 7.

Security:
- Passwords are hashed using werkzeug.security.generate_password_hash
  (which uses scrypt by default in modern Werkzeug).
- check_password() verifies a plaintext password against the stored hash.
"""

from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(db.Model):
    """ORM model for the 'user' table."""

    __tablename__ = 'user'

    # -----------------------------------------------------------------------
    # Columns
    # -----------------------------------------------------------------------

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80), unique=True, nullable=False, index=True
    )

    email = db.Column(
        db.String(120), unique=True, nullable=False, index=True
    )

    password_hash = db.Column(db.String(256), nullable=False)

    # Role field for future Phase 7 authorization.
    # Default is 'student'; 'admin' and other roles can be assigned.
    role = db.Column(db.String(20), nullable=False, default='student')

    # Audit timestamps.
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
    # Password Methods
    # -----------------------------------------------------------------------

    def set_password(self, password):
        """Hash and store the given plaintext password.

        Uses Werkzeug's generate_password_hash() which defaults to scrypt.
        The result includes the algorithm, salt, and hash — all in one string.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a plaintext password against the stored hash.

        Returns True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    # -----------------------------------------------------------------------
    # Serialization
    # -----------------------------------------------------------------------

    def to_dict(self):
        """Convert to dictionary for JSON serialization.

        IMPORTANT: Never include password_hash in the output.
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        """Developer-friendly string representation."""
        return f'<User {self.username}>'
