# Student Manager

A web-based student management application built with Flask and SQLite. This project is a feature-complete educational system demonstrating full-stack integration, robust REST API design, and strict Server-Side security.

## Overview

Student Manager is a Single Page Application (SPA) designed to handle administrative educational records. It provides interfaces to manage students, academic courses, semesters, and individual enrollments. It calculates GPAs on the Vietnamese 10-point scale and enforces strict Role-Based Access Control (RBAC) to protect sensitive data.

## Features

- **Student Management:** Full CRUD capabilities for student biographical data.
- **Course Management:** Manage academic courses and credit weights.
- **Semester Management:** Define academic terms with strict chronological constraints.
- **Enrollment Management:** Track student progress, assign grades, and manage statuses (enrolled, completed, dropped).
- **User Management:** Create and manage application access for administrators, teachers, and students.
- **Authentication:** Secure session-based login and logout.
- **Authorization (RBAC):** Strict server-side enforcement of Admin, Teacher, and Student permissions.
- **Settings:** Customizable UI interface.
- **Theme System:** Dynamic System, Light, and Dark themes with `localStorage` persistence.
- **UI/UX Polish:** Custom confirmation modals, toast notifications, and responsive loading/empty states.

## Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Flask |
| **Database** | SQLite |
| **ORM** | SQLAlchemy |
| **Migrations** | Flask-Migrate (Alembic) |
| **Frontend** | Vanilla HTML, CSS, JavaScript (ES6) |

## Architecture

Student Manager uses a classic three-tier architecture:
1. **SPA Frontend:** Runs entirely in the browser, communicating asynchronously via the Fetch API.
2. **Flask Backend:** Handles all routing, API endpoints, and acts as the ultimate security boundary.
3. **Database Layer:** SQLite database mapped through SQLAlchemy, utilizing strict schema constraints.

*See `docs/architecture.md` for a detailed breakdown.*

## Project Structure

```text
student-manager/
├── app/
│   ├── models/          # SQLAlchemy ORM models
│   ├── routes/          # Flask Blueprint API routes
│   ├── templates/       # HTML layouts (index, login)
│   └── static/          # CSS, JS, Images
│       ├── css/
│       └── js/
├── migrations/          # Alembic database migrations
├── docs/                # Project Documentation & UML
├── instance/            # SQLite database (gitignored)
├── config.py            # Application configuration
├── run.py               # Entry point
├── seed.py              # Sample data seeder
└── requirements.txt     # Python dependencies
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd student-manager
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # Linux / macOS
   # venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

1. **Initialize the database via migrations:**
   ```bash
   flask db upgrade
   ```

2. **Seed sample data (Generates sample records and dev accounts):**
   ```bash
   python seed.py
   ```

## Running the Application

Start the Flask development server:
```bash
python run.py
```
The application and API will be available at `http://localhost:5000`.

## Development Accounts

> **⚠️ These credentials are for LOCAL DEVELOPMENT ONLY. Do NOT use in production.**

The `seed.py` script provisions the following accounts:

| Username | Email | Password | Role |
|---|---|---|---|
| `admin` | `admin@example.com` | `admin123` | `admin` |
| `teacher` | `teacher@example.com` | `teacher123` | `teacher` |
| `student` | `student@example.com` | `student123` | `student` |

## Authentication & Authorization

- **Authentication:** Managed via Flask signed session cookies. Plaintext passwords are never stored; they are hashed using Werkzeug security functions.
- **Authorization:** Handled exclusively on the backend via a `before_request` hook. 
  - **Admins** have full system access.
  - **Teachers** have global read access and can update grades.
  - **Students** have isolated read-only access to their specific enrollments.

*See `docs/authorization.md` for the complete permission matrix.*

## Settings & Theme

- **Themes:** The UI provides a "Dark" mode (default), "Light" mode, and "System" mode (dynamically mirrors the OS preference using `prefers-color-scheme`).
- **Persistence:** Saved locally in the browser to prevent UI flashing upon reload.
- **Logout:** Handled securely via a confirmation modal inside Settings that triggers a POST request.

## API Documentation

The REST API serves JSON data under the `/api/` prefix.

*See `docs/api.md` for the full endpoint reference and payload structures.*

## Security & Testing

- Security relies on database-level constraints (UNIQUE, CHECK), parameterized ORM queries preventing SQLi, and strict session validation.
- Functionality is verified via comprehensive manual regression testing covering auth, RBAC boundaries, CRUD validations, and theme state management.

*See `docs/security.md` and `docs/testing.md`.*

## Limitations

- Uses SQLite, which restricts horizontal scaling and high concurrency.
- Lacks automated Unit/Integration test suites.
- Student-to-User mapping relies strictly on identical email strings.

## Future Improvements

- Upgrade to PostgreSQL for production deployment.
- Implement explicit CSRF tokens for state-changing API endpoints.
- Develop automated PyTest coverage for core endpoints.

## License

This project is for educational purposes. No open-source license has currently been selected.
