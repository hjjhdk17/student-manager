/**
 * Students Page (Phase 5)
 * =======================
 * Full CRUD UI for student management.
 *
 * Hooks into the Phase 4 router via:
 *   _renderStudentsPage()  — returns HTML
 *   _mountStudentsPage()   — attaches event listeners after render
 *
 * API endpoints used:
 *   GET    /api/students           (list + search + pagination)
 *   POST   /api/students           (create)
 *   GET    /api/students/<id>      (fetch for edit)
 *   PUT    /api/students/<id>      (update)
 *   DELETE /api/students/<id>      (delete)
 *   GET    /api/students/<id>/gpa  (view GPA)
 */

/* --------------------------------------------------------------------------
   State
   -------------------------------------------------------------------------- */

/** Current page state so we can re-render the table without a full page reload. */
let _studentsState = {
    search: '',
    page: 1,
    perPage: 10,
    total: 0,
    pages: 0,
    data: [],
    loading: false,
};

/* --------------------------------------------------------------------------
   Page Renderer (called by app.js router)
   -------------------------------------------------------------------------- */

function _renderStudentsPage() {
    return `
        <div class="toolbar">
            ${buildSearchBar('Search by code, name, or email…', 'students-search')}
            ${window.currentUser.role === 'admin' ? '<button class="btn btn-primary" id="btn-add-student">+ Add Student</button>' : ''}
        </div>
        <div id="students-table-area">
            <div class="empty-state"><div class="loading-spinner"></div><p style="margin-top:12px;color:var(--text-muted)">Loading students…</p></div>
        </div>
        <div id="students-pagination" class="pagination"></div>
    `;
}

/* --------------------------------------------------------------------------
   Mount (called after HTML is injected into the DOM)
   -------------------------------------------------------------------------- */

function _mountStudentsPage() {
    // Reset state for fresh load
    _studentsState.page = 1;
    _studentsState.search = '';

    // Load data
    _loadStudents();

    // Search: trigger on Enter key
    const searchInput = document.getElementById('students-search');
    if (searchInput) {
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                _studentsState.search = searchInput.value.trim();
                _studentsState.page = 1;
                _loadStudents();
            }
        });
        // Also trigger on the built-in search clear (X button in some browsers)
        searchInput.addEventListener('search', () => {
            _studentsState.search = searchInput.value.trim();
            _studentsState.page = 1;
            _loadStudents();
        });
    }

    // Add student button (if available)
    const addBtn = document.getElementById('btn-add-student');
    if (addBtn) {
        addBtn.addEventListener('click', () => _showStudentFormModal());
    }
}

/* --------------------------------------------------------------------------
   Load Students (GET /api/students)
   -------------------------------------------------------------------------- */

async function _loadStudents() {
    _studentsState.loading = true;
    _renderStudentsTable(); // show loading spinner

    try {
        const params = new URLSearchParams({
            page: _studentsState.page,
            per_page: _studentsState.perPage,
        });
        if (_studentsState.search) {
            params.set('search', _studentsState.search);
        }

        const result = await apiFetch(`/api/students?${params}`);

        _studentsState.data = result.data;
        _studentsState.total = result.total;
        _studentsState.pages = result.pages;
        _studentsState.page = result.page;
    } catch (err) {
        showToast('Failed to load students: ' + err.message, 'error');
        _studentsState.data = [];
    } finally {
        _studentsState.loading = false;
        _renderStudentsTable();
        _renderStudentsPagination();
    }
}

/* --------------------------------------------------------------------------
   Render Table
   -------------------------------------------------------------------------- */

function _renderStudentsTable() {
    const area = document.getElementById('students-table-area');
    if (!area) return;

    if (_studentsState.loading) {
        area.innerHTML = `
            <div class="empty-state">
                <div class="loading-spinner"></div>
                <p style="margin-top:12px;color:var(--text-muted)">Loading students…</p>
            </div>`;
        return;
    }

    const students = _studentsState.data;

    if (students.length === 0) {
        const msg = _studentsState.search
            ? 'No students match your search.'
            : 'No students yet. Add your first student!';
        area.innerHTML = `
            <div class="card">
                <div class="empty-state">
                    <div class="empty-state-icon">👤</div>
                    <div class="empty-state-title">No students found</div>
                    <div class="empty-state-text">${escapeHtml(msg)}</div>
                </div>
            </div>`;
        return;
    }

    const columns = ['Student Code', 'Name', 'Email', 'Phone', 'Date of Birth', 'Actions'];
    const rows = students.map((s) => [
        escapeHtml(s.student_code),
        escapeHtml(s.last_name + ' ' + s.first_name),
        escapeHtml(s.email),
        escapeHtml(s.phone || '—'),
        s.date_of_birth || '—',
        `<div class="table-actions">
            <button class="btn btn-sm btn-secondary" onclick="_viewStudentGpa(${s.id})" title="View GPA">📊 GPA</button>
            ${window.currentUser.role === 'admin' ? `
            <button class="btn btn-sm btn-secondary" onclick="_editStudent(${s.id})" title="Edit">✏️ Edit</button>
            <button class="btn btn-sm btn-danger" onclick="_confirmDeleteStudent(${s.id}, '${escapeHtml(s.student_code)}')" title="Delete">🗑️</button>
            ` : ''}
        </div>`,
    ]);

    area.innerHTML = buildTable(columns, rows);
}

/* --------------------------------------------------------------------------
   Pagination
   -------------------------------------------------------------------------- */

function _renderStudentsPagination() {
    const container = document.getElementById('students-pagination');
    if (!container) return;

    const { page, pages, total, perPage } = _studentsState;
    if (pages <= 1 && total <= perPage) {
        // Show record count but no pagination buttons when everything fits on one page
        container.innerHTML = total > 0
            ? `<span class="pagination-info">Showing ${total} student${total !== 1 ? 's' : ''}</span>`
            : '';
        return;
    }

    const start = (page - 1) * perPage + 1;
    const end = Math.min(page * perPage, total);

    container.innerHTML = `
        <span class="pagination-info">Showing ${start}–${end} of ${total} students</span>
        <div class="pagination-buttons">
            <button class="btn btn-sm btn-secondary" id="students-prev" ${page <= 1 ? 'disabled' : ''}>← Previous</button>
            <span class="pagination-current">Page ${page} of ${pages}</span>
            <button class="btn btn-sm btn-secondary" id="students-next" ${page >= pages ? 'disabled' : ''}>Next →</button>
        </div>
    `;

    document.getElementById('students-prev')?.addEventListener('click', () => {
        if (_studentsState.page > 1) {
            _studentsState.page--;
            _loadStudents();
        }
    });
    document.getElementById('students-next')?.addEventListener('click', () => {
        if (_studentsState.page < _studentsState.pages) {
            _studentsState.page++;
            _loadStudents();
        }
    });
}

/* --------------------------------------------------------------------------
   Add / Edit Modal
   -------------------------------------------------------------------------- */

/**
 * Show the student form modal for adding or editing.
 * @param {object|null} student — If provided, pre-fill for editing. Null = add.
 */
function _showStudentFormModal(student = null) {
    const isEdit = !!student;
    const title = isEdit ? 'Edit Student' : 'Add Student';

    const bodyHtml = `
        <form id="student-form" novalidate>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="sf-code">Student Code *</label>
                <input class="form-input" id="sf-code" type="text" required
                       value="${isEdit ? escapeHtml(student.student_code) : ''}"
                       placeholder="e.g. SV001">
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px">
                <div class="form-group">
                    <label class="form-label" for="sf-first">First Name *</label>
                    <input class="form-input" id="sf-first" type="text" required
                           value="${isEdit ? escapeHtml(student.first_name) : ''}"
                           placeholder="First name">
                </div>
                <div class="form-group">
                    <label class="form-label" for="sf-last">Last Name *</label>
                    <input class="form-input" id="sf-last" type="text" required
                           value="${isEdit ? escapeHtml(student.last_name) : ''}"
                           placeholder="Last name">
                </div>
            </div>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="sf-email">Email *</label>
                <input class="form-input" id="sf-email" type="email" required
                       value="${isEdit ? escapeHtml(student.email) : ''}"
                       placeholder="student@example.com">
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px">
                <div class="form-group">
                    <label class="form-label" for="sf-dob">Date of Birth</label>
                    <input class="form-input" id="sf-dob" type="date"
                           value="${isEdit && student.date_of_birth ? student.date_of_birth : ''}">
                </div>
                <div class="form-group">
                    <label class="form-label" for="sf-gender">Gender</label>
                    <select class="form-input form-select" id="sf-gender">
                        <option value="">— Select —</option>
                        <option value="Male"   ${isEdit && student.gender === 'Male'   ? 'selected' : ''}>Male</option>
                        <option value="Female" ${isEdit && student.gender === 'Female' ? 'selected' : ''}>Female</option>
                        <option value="Other"  ${isEdit && student.gender === 'Other'  ? 'selected' : ''}>Other</option>
                    </select>
                </div>
            </div>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="sf-phone">Phone</label>
                <input class="form-input" id="sf-phone" type="tel"
                       value="${isEdit && student.phone ? escapeHtml(student.phone) : ''}"
                       placeholder="Phone number">
            </div>
            <div class="form-group">
                <label class="form-label" for="sf-address">Address</label>
                <input class="form-input" id="sf-address" type="text"
                       value="${isEdit && student.address ? escapeHtml(student.address) : ''}"
                       placeholder="Address">
            </div>
            <div id="sf-error" class="form-error" style="margin-top:10px"></div>
        </form>
    `;

    const footerHtml = `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" id="sf-submit">${isEdit ? 'Update' : 'Create'}</button>
    `;

    showModal({
        title,
        bodyHtml,
        footerHtml,
        onOpen: () => {
            document.getElementById('sf-submit')
                .addEventListener('click', () => _submitStudentForm(isEdit ? student.id : null));
            // Allow Enter key to submit
            document.getElementById('student-form')
                .addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        _submitStudentForm(isEdit ? student.id : null);
                    }
                });
        },
    });
}

/* --------------------------------------------------------------------------
   Submit Student Form
   -------------------------------------------------------------------------- */

async function _submitStudentForm(studentId) {
    const errorEl = document.getElementById('sf-error');
    const submitBtn = document.getElementById('sf-submit');

    // Gather values
    const code      = document.getElementById('sf-code').value.trim();
    const firstName = document.getElementById('sf-first').value.trim();
    const lastName  = document.getElementById('sf-last').value.trim();
    const email     = document.getElementById('sf-email').value.trim();
    const dob       = document.getElementById('sf-dob').value;
    const gender    = document.getElementById('sf-gender').value;
    const phone     = document.getElementById('sf-phone').value.trim();
    const address   = document.getElementById('sf-address').value.trim();

    // Basic client-side validation
    const missing = [];
    if (!code)      missing.push('Student Code');
    if (!firstName) missing.push('First Name');
    if (!lastName)  missing.push('Last Name');
    if (!email)     missing.push('Email');

    if (missing.length > 0) {
        errorEl.textContent = 'Required: ' + missing.join(', ');
        return;
    }

    // Disable button to prevent double-submit
    submitBtn.disabled = true;
    submitBtn.textContent = studentId ? 'Updating…' : 'Creating…';
    errorEl.textContent = '';

    const payload = {
        student_code: code,
        first_name: firstName,
        last_name: lastName,
        email,
        date_of_birth: dob || null,
        gender: gender || null,
        phone: phone || null,
        address: address || null,
    };

    try {
        if (studentId) {
            await apiFetch(`/api/students/${studentId}`, { method: 'PUT', body: payload });
            showToast('Student updated successfully.', 'success');
        } else {
            await apiFetch('/api/students', { method: 'POST', body: payload });
            showToast('Student created successfully.', 'success');
        }
        closeModal();
        _loadStudents();
    } catch (err) {
        errorEl.textContent = err.message;
        submitBtn.disabled = false;
        submitBtn.textContent = studentId ? 'Update' : 'Create';
    }
}

/* --------------------------------------------------------------------------
   Edit Student
   -------------------------------------------------------------------------- */

async function _editStudent(id) {
    try {
        const student = await apiFetch(`/api/students/${id}`);
        _showStudentFormModal(student);
    } catch (err) {
        showToast('Failed to load student: ' + err.message, 'error');
    }
}

/* --------------------------------------------------------------------------
   Delete Student
   -------------------------------------------------------------------------- */

function _confirmDeleteStudent(id, code) {
    showModal({
        title: 'Delete Student',
        bodyHtml: `
            <p style="color:var(--text-secondary);margin-bottom:8px">
                Are you sure you want to delete student <strong>${escapeHtml(code)}</strong>?
            </p>
            <p style="color:var(--text-muted);font-size:0.85rem">
                This will permanently remove the student and all associated enrollment records.
            </p>
        `,
        footerHtml: `
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-danger" id="confirm-delete-student">Delete</button>
        `,
        onOpen: () => {
            document.getElementById('confirm-delete-student')
                .addEventListener('click', () => _deleteStudent(id));
        },
    });
}

async function _deleteStudent(id) {
    const btn = document.getElementById('confirm-delete-student');
    if (btn) { btn.disabled = true; btn.textContent = 'Deleting…'; }

    try {
        await apiFetch(`/api/students/${id}`, { method: 'DELETE' });
        showToast('Student deleted successfully.', 'success');
        closeModal();
        _loadStudents();
    } catch (err) {
        showToast('Failed to delete student: ' + err.message, 'error');
        if (btn) { btn.disabled = false; btn.textContent = 'Delete'; }
    }
}

/* --------------------------------------------------------------------------
   View GPA
   -------------------------------------------------------------------------- */

async function _viewStudentGpa(id) {
    try {
        const gpa = await apiFetch(`/api/students/${id}/gpa`);

        const gpaDisplay = gpa.gpa !== null
            ? `<span style="font-size:2rem;font-weight:700;color:var(--accent)">${gpa.gpa.toFixed(2)}</span>`
            : `<span style="font-size:1.1rem;color:var(--text-muted)">No graded courses</span>`;

        showModal({
            title: `GPA — ${escapeHtml(gpa.student_code)}`,
            bodyHtml: `
                <div style="text-align:center;padding:16px 0">
                    <p style="color:var(--text-secondary);margin-bottom:12px">${escapeHtml(gpa.student_name)}</p>
                    ${gpaDisplay}
                    <div style="margin-top:16px;display:flex;justify-content:center;gap:24px">
                        <div>
                            <div style="font-size:0.78rem;color:var(--text-muted)">Total Credits</div>
                            <div style="font-weight:600">${gpa.total_credits}</div>
                        </div>
                        <div>
                            <div style="font-size:0.78rem;color:var(--text-muted)">Courses Counted</div>
                            <div style="font-weight:600">${gpa.courses_counted}</div>
                        </div>
                    </div>
                    ${gpa.message ? `<p style="margin-top:12px;font-size:0.85rem;color:var(--text-muted)">${escapeHtml(gpa.message)}</p>` : ''}
                </div>
            `,
            footerHtml: `<button class="btn btn-secondary" onclick="closeModal()">Close</button>`,
        });
    } catch (err) {
        showToast('Failed to load GPA: ' + err.message, 'error');
    }
}
