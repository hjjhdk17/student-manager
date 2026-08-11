"""
Flask Application Factory
==========================
This module contains the `create_app()` factory function — the standard way
to create a Flask application in any non-trivial project.

Why a factory?
1. Avoids circular imports: models and routes can import `db` without
   importing the app itself.
2. Testability: you can create multiple app instances with different configs
   (e.g., a test database vs. the real database).
3. Explicit initialization: every extension (SQLAlchemy, Migrate, CORS) is
   initialized in one place, making the startup sequence easy to understand.

How it works:
    app = create_app()       # Uses default Config
    app = create_app(config) # Uses a custom config class (for testing)
"""

import os
# pyrefly: ignore [missing-import]
from flask import Flask, render_template
# pyrefly: ignore [missing-import]
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from config import Config

# ---------------------------------------------------------------------------
# Extension instances (created WITHOUT an app)
# ---------------------------------------------------------------------------
# These are created at module level so that other modules (models, routes)
# can import them directly:
#     from app import db
#
# They are not bound to any app yet — that happens inside create_app()
# via the init_app() calls. This is called the "lazy initialization" pattern.

db = SQLAlchemy()
"""SQLAlchemy database instance.
Provides:
- db.Model: base class for all ORM models
- db.session: the database session for queries (SELECT, INSERT, UPDATE, DELETE)
- db.Column, db.Integer, db.String, etc.: column type constructors
"""

migrate = Migrate()
"""Flask-Migrate instance.
Wraps Alembic to provide database migration commands:
- flask db init     → create the migrations directory
- flask db migrate  → auto-generate a migration from model changes
- flask db upgrade  → apply pending migrations to the database
"""

cors = CORS()
"""Flask-CORS instance.
Adds Access-Control-Allow-Origin headers to responses so the frontend
can make fetch() requests to the API even if served from a different port.
"""


def create_app(config_class=Config):
    """Create and configure a Flask application instance.

    Args:
        config_class: Configuration class to load. Defaults to Config.
                      Pass a different class for testing.

    Returns:
        A fully configured Flask application.
    """
    # 1. Create the Flask app.
    #    __name__ tells Flask where to find templates and static files
    #    (relative to this package's location: app/).
    app = Flask(__name__)

    # 2. Load configuration from the Config class.
    #    This sets app.config['SECRET_KEY'], app.config['SQLALCHEMY_DATABASE_URI'], etc.
    app.config.from_object(config_class)

    # 3. Ensure the instance directory exists.
    #    SQLite needs the parent directory to exist before it can create the .db file.
    os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)

    # 4. Initialize extensions with this app.
    #    Each extension's init_app() reads config values from app.config
    #    and registers teardown functions (e.g., closing DB connections).
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    # 5. Import models so Flask-Migrate can detect them.
    #    Alembic (which powers Flask-Migrate) discovers models by inspecting
    #    all classes that inherit from db.Model. But Python only knows about
    #    a class after it's been imported. If we skip this import, running
    #    `flask db migrate` would generate an empty migration because Alembic
    #    wouldn't see any models to create tables for.
    #
    #    We import inside create_app() (not at the top of the file) to avoid
    #    circular imports: models import `db` from this module, so this module
    #    can't import models before `db` is defined.
    from app.models import Student, Course, Semester, Enrollment  # noqa: F401

    # 6. Register blueprints (API routes).
    #    Blueprints are Flask's way of organizing routes into modules.
    #    Each blueprint handles one entity (students, courses, etc.).
    from app.routes import students_bp, courses_bp, semesters_bp, enrollments_bp

    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(semesters_bp)
    app.register_blueprint(enrollments_bp)

    # 7. Add a health-check route so we can verify the app is running.
    @app.route('/api/health')
    def health_check():
        """Simple health check endpoint.
        Returns a JSON response confirming the API is running.
        Useful for verifying the server started correctly.
        """
        return {'status': 'ok', 'message': 'Student Manager API is running'}

    # 8. Serve the frontend SPA shell.
    #    This route renders the single-page application. All client-side
    #    routing is handled via hash fragments (#/students, #/courses, etc.)
    #    so only a single server-side route is needed.
    @app.route('/')
    def index():
        """Serve the main single-page application shell."""
        return render_template('index.html')

    # 9. Register centralized JSON error handlers.
    #    Without these, Flask returns HTML error pages by default.
    #    Since this is a JSON API, all errors should return JSON.
    @app.errorhandler(400)
    def bad_request(e):
        return {'error': 'Bad request'}, 400

    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return {'error': 'Method not allowed'}, 405

    @app.errorhandler(409)
    def conflict(e):
        return {'error': 'Conflict'}, 409

    @app.errorhandler(422)
    def unprocessable(e):
        return {'error': 'Unprocessable entity'}, 422

    @app.errorhandler(500)
    def internal_error(e):
        return {'error': 'Internal server error'}, 500

    return app
