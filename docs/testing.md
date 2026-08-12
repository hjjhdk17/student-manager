# Testing Strategy

## Overview
Student Manager utilizes manual regression testing to verify end-to-end functionality across Authentication, Authorization (RBAC), UI/UX (Themes), and CRUD operations. Automated tests are not currently present in the repository.

## Test Cases Executed

### 1. Authentication Tests
| ID | Feature | Test Action | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| AUTH-01 | Login Valid | Attempt login with valid seed credentials. | Session created, redirected to `/`. | Redirected. | PASS |
| AUTH-02 | Login Invalid | Attempt login with bad password. | Render error message. | Error displayed. | PASS |
| AUTH-03 | API Protection | Use cURL on `/api/students` without session. | 401 Unauthorized JSON response. | Returned 401. | PASS |
| AUTH-04 | Logout | Click Log out -> Confirm. | Session cleared, redirected to `/login`. | Redirected. | PASS |
| AUTH-05 | Logout Cancel | Click Log out -> Cancel. | Modal closes, session persists. | Session persists. | PASS |

### 2. Authorization (RBAC) Tests
| ID | Feature | Test Action | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| RBAC-01 | Admin Rights | Login as Admin, view Users. | Users visible. | Visible. | PASS |
| RBAC-02 | Admin Rights | Login as Admin, delete a student. | Student deleted. | Deleted. | PASS |
| RBAC-03 | Teacher Limits | Login as Teacher, try to add course. | "Add" button hidden. | Hidden. | PASS |
| RBAC-04 | Teacher Limits | Login as Teacher, `POST /api/courses` via cURL. | 403 Forbidden. | Returned 403. | PASS |
| RBAC-05 | Student Isolation | Login as Student, view enrollments. | Only own enrollments visible. | Isolated. | PASS |

### 3. Theme System Tests
| ID | Feature | Test Action | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| UI-01 | Theme Persistence | Select "Dark", refresh page. | Dark theme remains immediately. | Persistent. | PASS |
| UI-02 | Light Theme | Select "Light". | UI transitions to Light variables. | Applied. | PASS |
| UI-03 | System Theme | Select "System", change OS preference. | UI matches OS preference. | Dynamic. | PASS |

### 4. CRUD Tests
| ID | Feature | Test Action | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| CRUD-01 | Create | Add new Student with missing fields. | Client-side validation blocks. | Blocked. | PASS |
| CRUD-02 | Create | Add new Student with valid fields. | Success toast, table updates. | Successful. | PASS |
| CRUD-03 | Delete | Delete Student. | Student and enrollments removed. | Cascaded delete. | PASS |
| CRUD-04 | Logic | Add Semester where start > end. | Backend constraint blocks. | API Error. | PASS |
| CRUD-05 | Logic | Add duplicate Enrollment. | Backend constraint blocks. | API Error. | PASS |

## Security & Regression Sign-off
Before merging Phase 8, regression checks successfully ensured that previous endpoints, GPA calculators, and database structures remained perfectly intact.
