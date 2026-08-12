# Student Manager - Final Project Report

## 1. Introduction

### 1.1 Background
Educational institutions require robust, reliable software to manage student biographical data, academic courses, grading, and term boundaries. Small to medium institutions often struggle with complex, expensive enterprise software.

### 1.2 Problem Statement
There is a need for a lightweight, easily deployable web application capable of managing standard academic records while strictly enforcing role-based access to protect sensitive student data.

### 1.3 Motivation
To build an educational project that demonstrates a full-stack integration utilizing Python, Flask, SQLite, and vanilla JavaScript without relying on heavy frontend frameworks, focusing instead on robust RESTful API design and Server-Side security.

### 1.4 Objectives
- Implement CRUD operations for Students, Courses, Semesters, and Enrollments.
- Calculate GPAs based on the Vietnamese 10-point scale.
- Implement strict Role-Based Access Control (Admin, Teacher, Student).
- Provide a modern, accessible, and themeable Single Page Application (SPA) UI.

### 1.5 Scope
The system handles administrative data entry, enrollment tracking, and grade recording. It does not handle financial billing, attendance tracking, or learning management system (LMS) content delivery.

## 2. Requirements Analysis

### 2.1 Functional Requirements
- The system must authenticate users via username/email and password.
- Administrators must be able to manage all entity types.
- Teachers must be able to update grades for existing enrollments.
- Students must only be able to view their own enrollments.
- The UI must allow filtering enrollments by student, course, or semester.

### 2.2 Non-functional Requirements
- **Security:** Passwords must be hashed. Authorization must be enforced server-side.
- **Usability:** The UI must support System, Light, and Dark themes.
- **Performance:** SPA architecture must load the page once and dynamically swap content without full page reloads.

### 2.3 Actors
- Administrator
- Teacher
- Student

### 2.4 Use Cases
- Login / Logout
- Manage Students / Courses / Semesters / Enrollments / Users
- Calculate GPA
- Change Theme

## 3. Technology Selection
- **Backend:** Python/Flask. Selected for its lightweight nature, excellent routing, and seamless integration with SQLAlchemy.
- **Database:** SQLite. Selected for simplicity and zero-configuration local deployment, ideal for this educational scope.
- **Frontend:** Vanilla HTML/CSS/JS. Selected to demonstrate fundamental Web APIs (Fetch, DOM manipulation) without the overhead of React/Vue.

## 4. System Analysis
(See `docs/architecture.md`, `docs/uml/use-case.md`, `docs/uml/sequence-diagrams.md`, `docs/uml/activity-diagrams.md`).

## 5. System Design
(See `docs/database.md`, `docs/uml/class-diagram.md`, `docs/uml/component-diagram.md`, `docs/uml/deployment-diagram.md`).

## 6. Implementation

### 6.1 Backend
Implemented using Flask Blueprints to separate concerns (`auth`, `students`, `courses`, `semesters`, `enrollments`, `users`).

### 6.2 Database
Implemented via SQLAlchemy models with Alembic (`Flask-Migrate`) handling schema migrations.

### 6.3 REST API
JSON-based REST API returning standardized `{"data": [...]}` wrappers and HTTP status codes representing logical success/failure.

### 6.4 Frontend
Implemented via a custom client-side router (`hashchange`) that dynamically injects HTML templates into a central `#app` container.

### 6.5 Authentication
Session-based authentication using Werkzeug security functions.

### 6.6 Authorization
Role-based restrictions implemented via a central `_enforce_rbac` `before_request` hook.

### 6.7 Settings and Theme
Implemented via CSS Custom Variables (`var(--bg-primary)`) toggled by setting a `data-theme` attribute on the `<html>` element, with persistence handled by `localStorage`.

## 7. Security
- Session cookies cryptographically signed.
- Passwords hashed using scrypt.
- Complete server-side enforcement of authorization limits.
(See `docs/security.md`).

## 8. Testing
Manual regression testing successfully verified all CRUD constraints, RBAC boundaries, and theme rendering.
(See `docs/testing.md`).

## 9. Results
The application successfully fulfills all project phases (1 through 8). It allows admins to fully manage an institution, teachers to securely input grades, and students to view their records in a polished, responsive interface.

## 10. Limitations
- **Scaling:** SQLite restricts the application to a single-node deployment.
- **Student Identity Matching:** The link between a `User` account and a `Student` record relies entirely on matching strings in the `email` field.
- **CSRF:** No explicit CSRF tokens are utilized for the API.

## 11. Future Development
- **Database Migration:** Upgrade to PostgreSQL for production concurrency.
- **Email Service:** Implement automated password resets via email.
- **Data Export:** Add PDF/CSV export functionality for grade reports.

## 12. Conclusion
The Student Manager project successfully demonstrates a cohesive, secure, and performant web application. By enforcing strict separation of concerns—where the backend exclusively handles security and data integrity while the frontend handles presentation—the system achieves a professional grade of software design.
