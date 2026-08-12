# Use Case Specifications

## Use Case Diagram

```mermaid
usecaseDiagram
    actor Admin
    actor Teacher
    actor Student

    usecase "Login / Logout" as UC_Auth
    usecase "Manage Students" as UC_Student
    usecase "Manage Courses" as UC_Course
    usecase "Manage Semesters" as UC_Semester
    usecase "Manage Enrollments" as UC_Enrollment
    usecase "Manage Users" as UC_User
    usecase "View Academic Data" as UC_ViewAcademic
    usecase "Change Theme" as UC_Theme

    Admin --> UC_Auth
    Admin --> UC_Student
    Admin --> UC_Course
    Admin --> UC_Semester
    Admin --> UC_Enrollment
    Admin --> UC_User
    Admin --> UC_Theme

    Teacher --> UC_Auth
    Teacher --> UC_ViewAcademic
    Teacher --> UC_Theme
    Teacher --> (Update Enrollment Grade/Status)

    Student --> UC_Auth
    Student --> (View Own Enrollments)
    Student --> UC_Theme
```
*(Note: Mermaid `usecaseDiagram` is currently experimentally supported in some viewers. A simpler graph approximation is often used if standard usecase diagrams fail to render).*

## Detailed Use Cases

### 1. Login
- **Actor:** Any User
- **Goal:** Authenticate to the system.
- **Preconditions:** User is registered in the database.
- **Main Flow:** User visits `/login`, inputs credentials, submits form. System verifies hash, creates session, and redirects to dashboard.
- **Exception Flow:** Invalid credentials display an error.

### 2. Logout
- **Actor:** Authenticated User
- **Goal:** Terminate session safely.
- **Preconditions:** User is logged in.
- **Main Flow:** User clicks Logout in Settings, confirms modal. System clears session and redirects to `/login`.
- **Alternative Flow:** User cancels the modal. Session remains active.

### 3. Manage Students
- **Actor:** Admin
- **Goal:** Add, edit, or delete student records.
- **Preconditions:** Logged in as Admin.
- **Main Flow:** User navigates to Students, clicks Add Student, inputs details, submits. System saves to DB.
- **Alternative Flow:** User clicks Edit or Delete on an existing student row.

### 4. Manage Users
- **Actor:** Admin
- **Goal:** Manage application access.
- **Preconditions:** Logged in as Admin.
- **Main Flow:** User navigates to Users, creates a new Teacher/Student credential.

### 5. Change Theme
- **Actor:** Authenticated User
- **Goal:** Customize visual interface.
- **Main Flow:** User accesses Settings, selects "Light". System saves preference to `localStorage`, applies CSS immediately.
