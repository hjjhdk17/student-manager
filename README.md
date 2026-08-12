# Student Manager

A web-based student management application built with Flask and SQLite.

## Features

- Manage students, courses, semesters, and enrollments
- CRUD operations for all entities
- Search and filtering
- Student GPA calculation (Vietnamese 10-point scale)
- RESTful JSON API

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite |
| ORM | SQLAlchemy |
| Migrations | Flask-Migrate (Alembic) |

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
   flask db upgrade
   ```

5. **Seed sample data (optional):**
   ```bash
   python seed.py
   ```

6. **Run the application:**
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:5000`.

## Project Structure

```
student-manager/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── student.py
│   │   ├── course.py
│   │   ├── semester.py
│   │   └── enrollment.py
│   └── routes/              # Flask Blueprint API routes
│       ├── students.py
│       ├── courses.py
│       ├── semesters.py
│       └── enrollments.py
├── migrations/              # Database migration scripts
├── instance/                # SQLite database (gitignored)
├── config.py                # Application configuration
├── run.py                   # Entry point
├── seed.py                  # Sample data seeder
├── requirements.txt         # Python dependencies
└── README.md
```

## API Reference

**Base URL:** `http://localhost:5000`

All responses are JSON. All errors return JSON with an `error` field.

---

### Health Check

```
GET /api/health
```

```bash
curl http://localhost:5000/api/health
```

```json
{"status": "ok", "message": "Student Manager API is running"}
```

---

### Students

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/students` | List students (with search & pagination) |
| `GET` | `/api/students/:id` | Get one student |
| `POST` | `/api/students` | Create a student |
| `PUT` | `/api/students/:id` | Update a student |
| `DELETE` | `/api/students/:id` | Delete a student |
| `GET` | `/api/students/:id/gpa` | Calculate student GPA |

**List with search & pagination:**

```bash
# List all students
curl http://localhost:5000/api/students

# Search by name, code, or email
curl "http://localhost:5000/api/students?search=An"

# Paginate
curl "http://localhost:5000/api/students?page=1&per_page=2"
```

**Response:**

```json
{
  "data": [
    {
      "id": 1,
      "student_code": "SV001",
      "first_name": "An",
      "last_name": "Nguyen Van",
      "email": "an.nguyen@university.edu.vn",
      "date_of_birth": "2003-03-15",
      "gender": "Male",
      "phone": "0901234567",
      "address": "123 Le Loi, District 1, Ho Chi Minh City",
      "created_at": "2026-08-10T16:47:13.133405",
      "updated_at": "2026-08-10T16:47:13.133410"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 5,
  "pages": 1
}
```

**Create a student:**

```bash
curl -X POST http://localhost:5000/api/students \
  -H "Content-Type: application/json" \
  -d '{
    "student_code": "SV006",
    "first_name": "Phuc",
    "last_name": "Vo Thanh",
    "email": "phuc.vo@university.edu.vn",
    "date_of_birth": "2004-02-28",
    "gender": "Male",
    "phone": "0956789012"
  }'
```

Returns `201 Created`.

**Calculate GPA:**

```bash
curl http://localhost:5000/api/students/1/gpa
```

```json
{
  "student_id": 1,
  "student_code": "SV001",
  "student_name": "Nguyen Van An",
  "gpa": 7.72,
  "total_credits": 15,
  "courses_counted": 5
}
```

---

### Courses

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/courses` | List courses (with search) |
| `GET` | `/api/courses/:id` | Get one course |
| `POST` | `/api/courses` | Create a course |
| `PUT` | `/api/courses/:id` | Update a course |
| `DELETE` | `/api/courses/:id` | Delete a course |

```bash
# List all courses
curl http://localhost:5000/api/courses

# Search by code or name
curl "http://localhost:5000/api/courses?search=CS"

# Create a course
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"course_code": "PHY101", "name": "Physics I", "credits": 3, "description": "Mechanics"}'
```

---

### Semesters

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/semesters` | List all semesters |
| `GET` | `/api/semesters/:id` | Get one semester |
| `POST` | `/api/semesters` | Create a semester |
| `PUT` | `/api/semesters/:id` | Update a semester |
| `DELETE` | `/api/semesters/:id` | Delete a semester |

```bash
# List all semesters
curl http://localhost:5000/api/semesters

# Create a semester
curl -X POST http://localhost:5000/api/semesters \
  -H "Content-Type: application/json" \
  -d '{"name": "Spring 2027", "start_date": "2027-01-15", "end_date": "2027-05-31"}'
```

---

### Enrollments

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/enrollments` | List enrollments (with filters) |
| `GET` | `/api/enrollments/:id` | Get one enrollment |
| `POST` | `/api/enrollments` | Create an enrollment |
| `PUT` | `/api/enrollments/:id` | Update grade/status |
| `DELETE` | `/api/enrollments/:id` | Delete an enrollment |

**Filters are combinable:**

```bash
# All enrollments for student 1
curl "http://localhost:5000/api/enrollments?student_id=1"

# Student 1 in semester 1
curl "http://localhost:5000/api/enrollments?student_id=1&semester_id=1"

# All enrollments for course 1
curl "http://localhost:5000/api/enrollments?course_id=1"
```

**Create an enrollment:**

```bash
curl -X POST http://localhost:5000/api/enrollments \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "course_id": 2, "semester_id": 1}'
```

**Update grade and status:**

```bash
curl -X PUT http://localhost:5000/api/enrollments/1 \
  -H "Content-Type: application/json" \
  -d '{"grade": 8.5, "status": "completed"}'
```

---

### Error Responses

All errors return JSON:

```json
{"error": "Student not found"}
```

| Status | Meaning |
|---|---|
| `200` | Success |
| `201` | Created |
| `400` | Bad request |
| `404` | Not found |
| `405` | Method not allowed |
| `401` | Authentication required |
| `409` | Conflict (duplicate) |
| `422` | Validation error |
| `500` | Internal server error |

---

## Authentication

The application uses session-based authentication. All pages and API endpoints (except `/api/health`) require authentication.

### How It Works

1. User navigates to the application.
2. If not authenticated, they are redirected to `/login`.
3. User enters their username (or email) and password.
4. On success, a session cookie is created and the user is redirected to the application.
5. The session persists across requests (default: 8 hours).
6. On logout, the session is cleared and the user is redirected to `/login`.

### Development Users

The `seed.py` script creates three development users:

| Username | Email | Password | Role |
|---|---|---|---|
| `admin` | `admin@example.com` | `admin123` | `admin` |
| `teacher` | `teacher@example.com` | `teacher123` | `teacher` |
| `student` | `student@example.com` | `student123` | `student` |

> **⚠️ These credentials are for LOCAL DEVELOPMENT ONLY. Do NOT use in production.**

To create development users:

```bash
python seed.py
```

### Login / Logout

**Login:**
```
GET  /login     → Display login page
POST /login     → Validate credentials, create session
```

**Logout:**
```
POST /logout    → Clear session, redirect to /login
```

### Authentication API

```
GET /api/auth/me   → Return currently authenticated user (JSON)
```

### Protected Routes

All `/api/students`, `/api/courses`, `/api/semesters`, and `/api/enrollments` endpoints require authentication. Unauthenticated requests return:

```json
{"error": "Authentication required"}
```

with HTTP status `401`.

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Flask session signing key | `dev-secret-key-change-in-production` |

> **⚠️ Set `SECRET_KEY` to a strong random value in production.**

### Database Migration

The `user` table is managed via Flask-Migrate:

```bash
flask db upgrade    # Apply the migration
flask db downgrade  # Revert the migration
```

## Authorization / Role-Based Access Control (RBAC)

The application implements a robust server-side **Role-Based Access Control (RBAC)** system.

### Authentication vs. Authorization
* **Authentication** verifies *who you are* (via username and password, returning a session cookie).
* **Authorization** verifies *what you are allowed to do* (via roles checking if you have permission to access a specific resource or perform an action).

### Available Roles & Permission Matrix

There are three available roles in the system:

| Resource | Admin | Teacher | Student |
|---|---|---|---|
| **Students** | CRUD | Read | - |
| **Courses** | CRUD | Read | Read |
| **Semesters**| CRUD | Read | Read |
| **Enrollments**| CRUD | Read / Update | Read (own only)* |
| **Users** | CRUD | - | - |

*\*Limitation Note: Currently, the system isolates student enrollments by matching the `User.email` to `Student.email`. If no matching student is found, the student sees 0 enrollments.*

### How Authorization Works

1. **Backend Enforcement (The Security Boundary):** 
   Authorization is strictly enforced on the server side using the `@role_required` decorator and a centralized `before_request` handler. Even if a user attempts to bypass the UI using `curl` or Postman, the backend will reject the request with a `403 Forbidden` status code if they lack permission.
2. **Frontend UI:** 
   The frontend UI conditionally renders elements based on the `window.currentUser.role` object provided by the `/api/auth/me` endpoint. It hides administrative navigation items and disables action buttons (like Add/Edit/Delete) to improve User Experience (UX), but this is *not* relied upon for security.
3. **User Management:** 
   Only the `admin` role has access to the `/api/users` endpoints and the Users management interface. Safe-guards are in place to prevent an admin from deleting their own account or deleting the last remaining admin account.

## License

This project is for educational purposes.
