"""
Application Entry Point
========================
This is the file you run to start the development server:
    python run.py

It does three things:
1. Imports the app factory from the app package
2. Creates a configured Flask application instance
3. Starts the Flask development server

The development server features:
- debug=True: auto-reloads when you change code, shows detailed error pages
- host='0.0.0.0': listens on all network interfaces (not just localhost)
- port=5000: the default Flask port

In production, you would NOT use this file. Instead, you'd use a production
WSGI server like Gunicorn:
    gunicorn -w 4 'app:create_app()'
"""

from app import create_app

# Create the Flask application using the factory.
# This calls create_app() which:
#   1. Creates the Flask instance
#   2. Loads config from config.py
#   3. Initializes SQLAlchemy, Migrate, CORS
#   4. Registers blueprints (once we add them)
app = create_app()

if __name__ == '__main__':
    # This block only runs when you execute this file directly (python run.py).
    # It does NOT run when imported by another module or by a WSGI server.
    app.run(debug=True, host='0.0.0.0', port=5000)
