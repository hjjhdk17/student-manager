# Application Security

## Overview
Security in Student Manager is enforced through multiple layers, from secure credential storage to strict server-side authorization enforcement. 

## Implemented Security Mechanisms

### 1. Password Protection
- **Mechanism:** Passwords are never stored in plaintext. They are hashed using `werkzeug.security.generate_password_hash()`, which utilizes modern algorithms (scrypt) with automatic salting.
- **Verification:** Verified at login using `check_password_hash()`, preventing timing attacks.

### 2. Session Management
- **Mechanism:** Flask uses secure, signed session cookies. The data inside the cookie is cryptographically signed using the application's `SECRET_KEY`.
- **Protections:**
  - Users cannot tamper with the session cookie; if altered, the signature verification fails and the cookie is invalidated.
  - The backend relies exclusively on this session for API requests. `window.currentUser` in the frontend is only used for UI presentation, not actual security.
  - Explicit logout (`POST /logout`) clears the session data on the backend.

### 3. Server-Side Authorization (RBAC)
- **Mechanism:** The `@role_required` decorator and `before_request` hooks enforce access control before the route logic is ever executed.
- **Protections:**
  - A user with a `student` role cannot manually execute a `POST /api/courses` using `curl` or Postman. The backend verifies the session role and immediately rejects the request with a `403 Forbidden` status.
  - Prevents Privilege Escalation vulnerabilities.

### 4. Database Security
- **Mechanism:** SQLAlchemy ORM is used for all database queries.
- **Protections:**
  - Prevents SQL Injection (SQLi) attacks by automatically escaping parameters.
  - Database-level constraints (`CHECK`, `UNIQUE`) ensure data integrity even in the event of an application logic bug.

### 5. Frontend UI Protection
- **Mechanism:** Escape HTML entities.
- **Protections:**
  - Prevents Cross-Site Scripting (XSS) by using the custom `escapeHtml()` function before injecting dynamic data into the DOM (e.g., student names or error messages).

## Security Limitations / Future Hardening

* **CSRF Protection:** The application relies on standard session cookies but currently does not implement a dedicated CSRF token mechanism for state-changing API requests. Implementing a CSRF token (or setting `SameSite=Strict` securely) is recommended for production.
* **Rate Limiting:** There is no rate limiting on the `/login` endpoint, making it theoretically vulnerable to brute-force attacks if passwords are weak.
* **HTTPS:** Secure transmission relies on the deployment environment (e.g., Nginx terminating SSL). `SESSION_COOKIE_SECURE` should be explicitly set to `True` in a production config.
* **Audit Logging:** Security-sensitive events (like failed logins or unauthorized access attempts) are not durably logged for audit purposes.
