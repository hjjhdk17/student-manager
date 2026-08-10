"""
Application Configuration
=========================
Centralized configuration for the Flask application.
All settings are defined as class attributes so Flask can load them with:
    app.config.from_object(Config)

Key settings:
- SECRET_KEY: Used by Flask to sign session cookies. Must be random in production.
- SQLALCHEMY_DATABASE_URI: Connection string for SQLAlchemy. Format for SQLite:
    sqlite:///relative/path/to/db.file
- SQLALCHEMY_TRACK_MODIFICATIONS: Disables the deprecated event system that
    tracks every ORM object change (wastes memory, not needed).
"""

import os

# Get the absolute path to this file's directory.
# This ensures the database path is always correct regardless of where you
# run the app from (e.g., `python run.py` vs `flask run`).
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class.

    In a larger project, you'd create subclasses like DevelopmentConfig,
    TestingConfig, and ProductionConfig. For now, a single Config is sufficient.
    """

    # Flask uses this to cryptographically sign session cookies.
    # os.environ.get() checks for an environment variable first,
    # falling back to a hardcoded default for development.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # SQLAlchemy database connection string.
    # The database file is stored in instance/ which is gitignored.
    # This keeps the database out of version control while the schema
    # (tracked via migrations) stays in Git.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'instance', 'student_manager.db')
    )

    # Disable the Flask-SQLAlchemy event system.
    # This feature is deprecated and consumes extra memory by tracking
    # every change to every ORM object. Always set to False.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
