# Student Manager

A web-based student management application built with Flask and SQLite.

## Features

- Manage students, courses, semesters, and enrollments
- CRUD operations for all entities
- Search and filtering
- Student GPA calculation (Vietnamese 10-point scale)
- RESTful JSON API
- Modern single-page frontend

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite |
| ORM | SQLAlchemy |
| Migrations | Flask-Migrate (Alembic) |
| Frontend | Vanilla HTML, CSS, JavaScript |

## Getting Started

### Prerequisites

- Python 3.10 or later
- pip (Python package manager)

### Installation

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

4. **Initialize the database:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Run the application:**
   ```bash
   python run.py
   ```

6. **Open your browser:**
   Navigate to [http://localhost:5000](http://localhost:5000)

## Project Structure

```
student-manager/
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── models/            # SQLAlchemy ORM models
│   ├── routes/            # Flask Blueprint API routes
│   ├── static/            # CSS, JavaScript
│   └── templates/         # HTML templates
├── migrations/            # Database migration scripts
├── instance/              # SQLite database (gitignored)
├── config.py              # Application configuration
├── run.py                 # Entry point
├── requirements.txt       # Python dependencies
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/students` | List students |
| `POST` | `/api/students` | Create student |
| `GET` | `/api/students/:id` | Get student |
| `PUT` | `/api/students/:id` | Update student |
| `DELETE` | `/api/students/:id` | Delete student |
| `GET` | `/api/students/:id/gpa` | Calculate GPA |
| `GET` | `/api/courses` | List courses |
| `POST` | `/api/courses` | Create course |
| `PUT` | `/api/courses/:id` | Update course |
| `DELETE` | `/api/courses/:id` | Delete course |
| `GET` | `/api/semesters` | List semesters |
| `POST` | `/api/semesters` | Create semester |
| `PUT` | `/api/semesters/:id` | Update semester |
| `DELETE` | `/api/semesters/:id` | Delete semester |
| `GET` | `/api/enrollments` | List enrollments |
| `POST` | `/api/enrollments` | Create enrollment |
| `PUT` | `/api/enrollments/:id` | Update enrollment |
| `DELETE` | `/api/enrollments/:id` | Delete enrollment |

## License

This project is for educational purposes.
