# Component Diagram

This diagram outlines the major software components comprising the Student Manager application and their dependencies.

```mermaid
componentDiagram
    package "Frontend (Browser)" {
        [SPA Router]
        [Theme Manager]
        [API Client (Fetch)]
        [UI Modals & Toasts]
    }

    package "Flask Application (Backend)" {
        [Auth Blueprint]
        [Students Blueprint]
        [Courses Blueprint]
        [Semesters Blueprint]
        [Enrollments Blueprint]
        
        [Security Hooks (RBAC)]
    }

    package "Database Layer" {
        [SQLAlchemy ORM]
        [SQLite Database]
    }

    [SPA Router] --> [API Client (Fetch)]
    [API Client (Fetch)] --> [Auth Blueprint] : HTTP JSON
    [API Client (Fetch)] --> [Students Blueprint] : HTTP JSON
    
    [Auth Blueprint] --> [Security Hooks (RBAC)]
    [Students Blueprint] --> [Security Hooks (RBAC)]
    
    [Security Hooks (RBAC)] --> [SQLAlchemy ORM]
    [Students Blueprint] --> [SQLAlchemy ORM]
    
    [SQLAlchemy ORM] --> [SQLite Database]
```
