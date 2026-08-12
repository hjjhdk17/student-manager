# Deployment Diagram

## Current Development Deployment

This reflects the actual current architecture used for developing and running the application locally.

```mermaid
deploymentDiagram
    node "Developer Machine (localhost)" {
        node "Web Browser" {
            component "Student Manager SPA"
        }
        
        node "Python Environment (venv)" {
            component "Flask Dev Server (:5000)"
            component "Werkzeug WSGI"
        }
        
        node "File System" {
            database "instance/app.db (SQLite)"
        }
    }
    
    "Web Browser" -- "HTTP / HTTPs" --> "Flask Dev Server (:5000)"
    "Flask Dev Server (:5000)" --> "instance/app.db (SQLite)"
```

## Proposed Future Production Deployment

This illustrates how the application *should* be deployed if it were to go to a production environment. **Note: This has not been implemented yet.**

```mermaid
deploymentDiagram
    node "Client Device" {
        node "Web Browser" {
            component "SPA"
        }
    }

    node "Cloud Server (VPS / EC2)" {
        node "Nginx Reverse Proxy" {
            component "SSL Termination"
            component "Static File Server"
        }
        
        node "Application Server" {
            component "Gunicorn / uWSGI"
            component "Flask Application"
        }
    }

    node "Managed Database Service" {
        database "PostgreSQL Database"
    }

    "Web Browser" -- "HTTPS (Port 443)" --> "Nginx Reverse Proxy"
    "Nginx Reverse Proxy" -- "FastCGI / HTTP Proxy" --> "Application Server"
    "Application Server" -- "SQL (Port 5432)" --> "PostgreSQL Database"
```
