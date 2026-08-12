# REST API Reference

**Base URL:** `http://localhost:5000`

All endpoints return JSON. Successful responses usually include a `data` key. Errors include an `error` key.

## Common Error Responses
| Status | Meaning |
|---|---|
| `400` | Bad request (missing required fields, validation error) |
| `401` | Authentication required |
| `403` | Forbidden (User lacks necessary role) |
| `404` | Not found |
| `409` | Conflict (e.g., duplicate unique constraint violation) |
| `500` | Internal server error |

---

## Authentication

### GET `/api/auth/me`
- **Requires Auth:** Yes
- **Roles:** All
- **Description:** Returns details of the currently authenticated user session.
- **Response `200`:**
  ```json
  {
    "id": 1,
    "username": "admin",
    "email": "admin@test.com",
    "role": "admin"
  }
  ```

---

## Students

### GET `/api/students`
- **Requires Auth:** Yes
- **Roles:** Admin, Teacher
- **Parameters:** `search` (string), `page` (int), `per_page` (int)
- **Response `200`:**
  ```json
  {
    "data": [ { "id": 1, "student_code": "SV001", "first_name": "John" } ],
    "page": 1, "per_page": 20, "total": 1, "pages": 1
  }
  ```

### GET `/api/students/<id>`
- **Requires Auth:** Yes
- **Roles:** Admin, Teacher
- **Response `200`:** Student JSON object.

### POST `/api/students`
- **Requires Auth:** Yes
- **Roles:** Admin
- **Body:** `student_code`, `first_name`, `last_name`, `email` (all required)
- **Response `201`:** Created Student object.

### PUT `/api/students/<id>`
- **Requires Auth:** Yes
- **Roles:** Admin
- **Body:** Editable student fields.
- **Response `200`:** Updated Student object.

### DELETE `/api/students/<id>`
- **Requires Auth:** Yes
- **Roles:** Admin
- **Response `204`:** No Content.

### GET `/api/students/<id>/gpa`
- **Requires Auth:** Yes
- **Roles:** Admin, Teacher
- **Response `200`:**
  ```json
  {
    "student_id": 1,
    "student_code": "SV001",
    "gpa": 8.5,
    "total_credits": 3,
    "courses_counted": 1
  }
  ```

---

## Courses

### GET `/api/courses`
- **Requires Auth:** Yes
- **Roles:** All
- **Parameters:** `search`
- **Response `200`:**
  ```json
  { "data": [ { "id": 1, "course_code": "CS101", "name": "Intro" } ] }
  ```

### GET `/api/courses/<id>`
- **Requires Auth:** Yes
- **Roles:** All
- **Response `200`:** Course JSON object.

### POST `/api/courses`
- **Requires Auth:** Yes
- **Roles:** Admin
- **Body:** `course_code`, `name`, `credits` (all required)
- **Response `201`:** Created Course object.

### PUT `/api/courses/<id>`
- **Requires Auth:** Yes
- **Roles:** Admin
- **Body:** Editable course fields.
- **Response `200`:** Updated Course object.

### DELETE `/api/courses/<id>`
- **Requires Auth:** Yes
- **Roles:** Admin
- **Response `204`:** No Content.

---

## Semesters

### GET `/api/semesters`
- **Requires Auth:** Yes
- **Roles:** All
- **Response `200`:** Array of Semesters inside a `data` key.

### GET `/api/semesters/<id>`
- **Requires Auth:** Yes
- **Roles:** All
- **Response `200`:** Semester JSON object.

### POST `/api/semesters`
- **Requires Auth:** Yes
- **Roles:** Admin
- **Body:** `name`, `start_date`, `end_date` (all required)
- **Response `201`:** Created Semester object.

### PUT `/api/semesters/<id>`
- **Requires Auth:** Yes
- **Roles:** Admin
- **Body:** Editable semester fields.
- **Response `200`:** Updated Semester object.

### DELETE `/api/semesters/<id>`
- **Requires Auth:** Yes
- **Roles:** Admin
- **Response `204`:** No Content.

---

## Enrollments

### GET `/api/enrollments`
- **Requires Auth:** Yes
- **Roles:** All (Students can only see their own enrollments)
- **Parameters:** `student_id`, `course_id`, `semester_id`
- **Response `200`:** Array of Enrollments inside a `data` key.

### GET `/api/enrollments/<id>`
- **Requires Auth:** Yes
- **Roles:** All
- **Response `200`:** Enrollment JSON object.

### POST `/api/enrollments`
- **Requires Auth:** Yes
- **Roles:** Admin
- **Body:** `student_id`, `course_id`, `semester_id` (all required)
- **Response `201`:** Created Enrollment object.

### PUT `/api/enrollments/<id>`
- **Requires Auth:** Yes
- **Roles:** Admin, Teacher (Teachers can update `grade` and `status`)
- **Body:** `grade`, `status`
- **Response `200`:** Updated Enrollment object.

### DELETE `/api/enrollments/<id>`
- **Requires Auth:** Yes
- **Roles:** Admin
- **Response `204`:** No Content.

---

## Users

### GET `/api/users`
- **Requires Auth:** Yes
- **Roles:** Admin
- **Response `200`:** Array of Users.

*(Note: Create/Update/Delete endpoints exist for Admins mirroring the standard CRUD structure).*
