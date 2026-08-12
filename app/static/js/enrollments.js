/**
 * Enrollments Page (Phase 5)
 * ==========================
 * Full CRUD UI for enrollment management with relationship handling.
 *
 * Hooks into the Phase 4 router via:
 *   _renderEnrollmentsPage()  — returns HTML
 *   _mountEnrollmentsPage()   — attaches event listeners after render
 *
 * API endpoints used:
 *   GET    /api/enrollments                 (list + filters)
 *   POST   /api/enrollments                 (create)
 *   GET    /api/enrollments/<id>            (fetch for edit)
 *   PUT    /api/enrollments/<id>            (update grade/status)
 *   DELETE /api/enrollments/<id>            (delete)
 *   GET    /api/students                    (populate dropdowns)
 *   GET    /api/courses                     (populate dropdowns)
 *   GET    /api/semesters                   (populate dropdowns)
 */

/* --------------------------------------------------------------------------
   State
   -------------------------------------------------------------------------- */

let _enrollmentsState = {
    data: [],
    loading: false,
    // Filter selections
    studentId: '',
    courseId: '',
    semesterId: '',
    // Cached dropdown data (loaded once per page mount)
    students: [],
    courses: [],
    semesters: [],
};

/* --------------------------------------------------------------------------
   Page Renderer
   -------------------------------------------------------------------------- */

function _renderEnrollmentsPage() {
    return `
        <div class="filter-bar" id="enrollments-filter-bar">
            <div class="form-group">
                <label class="form-label" for="ef-student">Student</label>
                <select class="form-input form-select" id="ef-student">
                    <option value="">All Students</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label" for="ef-course">Course</label>
                <select class="form-input form-select" id="ef-course">
                    <option value="">All Courses</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label" for="ef-semester">Semester</label>
                <select class="form-input form-select" id="ef-semester">
                    <option value="">All Semesters</option>
                </select>
            </div>
            <div class="form-group" style="justify-content:flex-end">
                <label class="form-label">&nbsp;</label>
                <button class="btn btn-secondary btn-sm" id="btn-clear-filters">Clear Filters</button>
            </div>
        </div>
        <div class="toolbar">
            <span id="enrollments-count" class="pagination-info"></span>
            ${window.currentUser.role === 'admin' ? '<button class="btn btn-primary" id="btn-add-enrollment">+ Add Enrollment</button>' : ''}
        </div>
        <div id="enrollments-table-area">
            <div class="empty-state"><div class="loading-spinner"></div><p style="margin-top:12px;color:var(--text-muted)">Loading enrollments…</p></div>
        </div>
    `;
}

/* --------------------------------------------------------------------------
   Mount
   -------------------------------------------------------------------------- */

async function _mountEnrollmentsPage() {
    // Reset filters
    _enrollmentsState.studentId = '';
    _enrollmentsState.courseId = '';
    _enrollmentsState.semesterId = '';

    // Load dropdown data in parallel, then load enrollments
    await _loadEnrollmentDropdowns();
    _loadEnrollments();

    // Filter change listeners — apply filter immediately on selection
    document.getElementById('ef-student').addEventListener('change', (e) => {
        _enrollmentsState.studentId = e.target.value;
        _loadEnrollments();
    });
    document.getElementById('ef-course').addEventListener('change', (e) => {
        _enrollmentsState.courseId = e.target.value;
        _loadEnrollments();
    });
    document.getElementById('ef-semester').addEventListener('change', (e) => {
        _enrollmentsState.semesterId = e.target.value;
        _loadEnrollments();
    });

    // Clear filters
    document.getElementById('btn-clear-filters').addEventListener('click', () => {
        _enrollmentsState.studentId = '';
        _enrollmentsState.courseId = '';
        _enrollmentsState.semesterId = '';
        document.getElementById('ef-student').value = '';
        document.getElementById('ef-course').value = '';
        document.getElementById('ef-semester').value = '';
        _loadEnrollments();
    });

    // Add enrollment button (if available)
    const addBtn = document.getElementById('btn-add-enrollment');
    if (addBtn) {
        addBtn.addEventListener('click', () => _showEnrollmentFormModal());
    }
}

/* --------------------------------------------------------------------------
   Load Dropdown Data
   -------------------------------------------------------------------------- */

async function _loadEnrollmentDropdowns() {
    try {
        // Fetch all three lists in parallel.
        // For students, request a large per_page since the dropdown needs all students.
        const [studentsRes, coursesRes, semestersRes] = await Promise.all([
            apiFetch('/api/students?per_page=100'),
            apiFetch('/api/courses'),
            apiFetch('/api/semesters'),
        ]);

        _enrollmentsState.students = studentsRes.data;
        _enrollmentsState.courses = coursesRes.data;
        _enrollmentsState.semesters = semestersRes.data;

        // Populate filter dropdowns
        _populateSelect('ef-student', _enrollmentsState.students, (s) => ({
            value: s.id,
            label: `${s.student_code} — ${s.last_name} ${s.first_name}`,
        }));
        _populateSelect('ef-course', _enrollmentsState.courses, (c) => ({
            value: c.id,
            label: `${c.course_code} — ${c.name}`,
        }));
        _populateSelect('ef-semester', _enrollmentsState.semesters, (s) => ({
            value: s.id,
            label: s.name,
        }));
    } catch (err) {
        showToast('Failed to load filter options: ' + err.message, 'error');
    }
}

/**
 * Populate a <select> element with options while preserving the first "All …" option.
 */
function _populateSelect(selectId, items, mapper) {
    const select = document.getElementById(selectId);
    if (!select) return;

    // Keep the first option (the "All …" placeholder)
    const firstOption = select.options[0];
    select.innerHTML = '';
    select.appendChild(firstOption);

    items.forEach((item) => {
        const { value, label } = mapper(item);
        const opt = document.createElement('option');
        opt.value = value;
        opt.textContent = label;
        select.appendChild(opt);
    });
}

/* --------------------------------------------------------------------------
   Load Enrollments (GET /api/enrollments)
   -------------------------------------------------------------------------- */

async function _loadEnrollments() {
    _enrollmentsState.loading = true;
    _renderEnrollmentsTable();

    try {
        const params = new URLSearchParams();
        if (_enrollmentsState.studentId) params.set('student_id', _enrollmentsState.studentId);
        if (_enrollmentsState.courseId) params.set('course_id', _enrollmentsState.courseId);
        if (_enrollmentsState.semesterId) params.set('semester_id', _enrollmentsState.semesterId);

        const result = await apiFetch(`/api/enrollments?${params}`);
        _enrollmentsState.data = result.data;
    } catch (err) {
        showToast('Failed to load enrollments: ' + err.message, 'error');
        _enrollmentsState.data = [];
    } finally {
        _enrollmentsState.loading = false;
        _renderEnrollmentsTable();

        // Update count
        const countEl = document.getElementById('enrollments-count');
        if (countEl) {
            const total = _enrollmentsState.data.length;
            countEl.textContent = `${total} enrollment${total !== 1 ? 's' : ''}`;
        }
    }
}

/* --------------------------------------------------------------------------
   Render Table
   -------------------------------------------------------------------------- */

/** Map status values to badge CSS classes. */
function _statusBadge(status) {
    const map = {
        enrolled: 'badge-info',
        completed: 'badge-success',
        dropped: 'badge-danger',
    };
    const cls = map[status] || 'badge-default';
    return `<span class="badge ${cls}">${escapeHtml(status)}</span>`;
}

function _renderEnrollmentsTable() {
    const area = document.getElementById('enrollments-table-area');
    if (!area) return;

    if (_enrollmentsState.loading) {
        area.innerHTML = `
            <div class="empty-state">
                <div class="loading-spinner"></div>
                <p style="margin-top:12px;color:var(--text-muted)">Loading enrollments…</p>
            </div>`;
        return;
    }

    const enrollments = _enrollmentsState.data;

    if (enrollments.length === 0) {
        const hasFilters = _enrollmentsState.studentId || _enrollmentsState.courseId || _enrollmentsState.semesterId;
        const msg = hasFilters
            ? 'No enrollments match the selected filters.'
            : 'No enrollments yet. Add your first enrollment!';
        area.innerHTML = `
            <div class="card">
                <div class="empty-state">
                    <div class="empty-state-icon">📝</div>
                    <div class="empty-state-title">No enrollments found</div>
                    <div class="empty-state-text">${escapeHtml(msg)}</div>
                </div>
            </div>`;
        return;
    }

    const columns = ['Student', 'Course', 'Semester', 'Grade', 'Status', 'Actions'];
    const rows = enrollments.map((e) => [
        `<span title="${escapeHtml(e.student_code)}">${escapeHtml(e.student_code)} — ${escapeHtml(e.student_name || '')}</span>`,
        `<span title="${escapeHtml(e.course_code)}">${escapeHtml(e.course_code)} — ${escapeHtml(e.course_name || '')}</span>`,
        escapeHtml(e.semester_name || '—'),
        e.grade !== null ? `<strong>${e.grade.toFixed(2)}</strong>` : '<span style="color:var(--text-muted)">—</span>',
        _statusBadge(e.status),
        `<div class="table-actions">
            ${window.currentUser.role === 'admin' || window.currentUser.role === 'teacher' ? `
            <button class="btn btn-sm btn-secondary" onclick="_editEnrollment(${e.id})" title="Edit grade/status">✏️ Edit</button>
            ` : ''}
            ${window.currentUser.role === 'admin' ? `
            <button class="btn btn-sm btn-danger" onclick="_confirmDeleteEnrollment(${e.id})" title="Delete">🗑️</button>
            ` : ''}
            ${window.currentUser.role === 'student' ? '<span style="color:var(--text-muted);font-size:0.8rem">View Only</span>' : ''}
        </div>`,
    ]);

    area.innerHTML = buildTable(columns, rows);
}

/* --------------------------------------------------------------------------
   Add Enrollment Modal
   -------------------------------------------------------------------------- */

function _showEnrollmentFormModal() {
    const { students, courses, semesters } = _enrollmentsState;

    // Build option strings for the dropdowns
    const studentOpts = students.map((s) =>
        `<option value="${s.id}">${escapeHtml(s.student_code)} — ${escapeHtml(s.last_name + ' ' + s.first_name)}</option>`
    ).join('');

    const courseOpts = courses.map((c) =>
        `<option value="${c.id}">${escapeHtml(c.course_code)} — ${escapeHtml(c.name)}</option>`
    ).join('');

    const semesterOpts = semesters.map((s) =>
        `<option value="${s.id}">${escapeHtml(s.name)}</option>`
    ).join('');

    const bodyHtml = `
        <form id="enrollment-form" novalidate>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="enf-student">Student *</label>
                <select class="form-input form-select" id="enf-student" required>
                    <option value="">— Select Student —</option>
                    ${studentOpts}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="enf-course">Course *</label>
                <select class="form-input form-select" id="enf-course" required>
                    <option value="">— Select Course —</option>
                    ${courseOpts}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="enf-semester">Semester *</label>
                <select class="form-input form-select" id="enf-semester" required>
                    <option value="">— Select Semester —</option>
                    ${semesterOpts}
                </select>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px">
                <div class="form-group">
                    <label class="form-label" for="enf-grade">Grade (0–10)</label>
                    <input class="form-input" id="enf-grade" type="number" step="0.01" min="0" max="10"
                           placeholder="e.g. 8.50">
                </div>
                <div class="form-group">
                    <label class="form-label" for="enf-status">Status *</label>
                    <select class="form-input form-select" id="enf-status" required>
                        <option value="enrolled" selected>enrolled</option>
                        <option value="completed">completed</option>
                        <option value="dropped">dropped</option>
                    </select>
                </div>
            </div>
            <div id="enf-error" class="form-error"></div>
        </form>
    `;

    const footerHtml = `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" id="enf-submit">Create</button>
    `;

    showModal({
        title: 'Add Enrollment',
        bodyHtml,
        footerHtml,
        onOpen: () => {
            document.getElementById('enf-submit')
                .addEventListener('click', _submitNewEnrollment);
        },
    });
}

/* --------------------------------------------------------------------------
   Submit New Enrollment
   -------------------------------------------------------------------------- */

async function _submitNewEnrollment() {
    const errorEl = document.getElementById('enf-error');
    const submitBtn = document.getElementById('enf-submit');

    const studentId  = document.getElementById('enf-student').value;
    const courseId   = document.getElementById('enf-course').value;
    const semesterId = document.getElementById('enf-semester').value;
    const gradeStr   = document.getElementById('enf-grade').value.trim();
    const status     = document.getElementById('enf-status').value;

    // Validate required fields
    const missing = [];
    if (!studentId)  missing.push('Student');
    if (!courseId)    missing.push('Course');
    if (!semesterId) missing.push('Semester');
    if (!status)     missing.push('Status');

    if (missing.length > 0) {
        errorEl.textContent = 'Required: ' + missing.join(', ');
        return;
    }

    // Validate grade if provided
    let grade = null;
    if (gradeStr !== '') {
        grade = parseFloat(gradeStr);
        if (isNaN(grade) || grade < 0 || grade > 10) {
            errorEl.textContent = 'Grade must be a number between 0 and 10.';
            return;
        }
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating…';
    errorEl.textContent = '';

    const payload = {
        student_id: parseInt(studentId, 10),
        course_id: parseInt(courseId, 10),
        semester_id: parseInt(semesterId, 10),
        grade,
        status,
    };

    try {
        await apiFetch('/api/enrollments', { method: 'POST', body: payload });
        showToast('Enrollment created successfully.', 'success');
        closeModal();
        _loadEnrollments();
    } catch (err) {
        errorEl.textContent = err.message;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create';
    }
}

/* --------------------------------------------------------------------------
   Edit Enrollment (grade + status only)
   -------------------------------------------------------------------------- */

async function _editEnrollment(id) {
    let enrollment;
    try {
        enrollment = await apiFetch(`/api/enrollments/${id}`);
    } catch (err) {
        showToast('Failed to load enrollment: ' + err.message, 'error');
        return;
    }

    const bodyHtml = `
        <form id="edit-enrollment-form" novalidate>
            <p style="color:var(--text-secondary);margin-bottom:16px;font-size:0.85rem">
                <strong>${escapeHtml(enrollment.student_code)}</strong> — ${escapeHtml(enrollment.student_name || '')}<br>
                <strong>${escapeHtml(enrollment.course_code)}</strong> — ${escapeHtml(enrollment.course_name || '')}<br>
                <strong>Semester:</strong> ${escapeHtml(enrollment.semester_name || '')}
            </p>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px">
                <div class="form-group">
                    <label class="form-label" for="eef-grade">Grade (0–10)</label>
                    <input class="form-input" id="eef-grade" type="number" step="0.01" min="0" max="10"
                           value="${enrollment.grade !== null ? enrollment.grade : ''}"
                           placeholder="e.g. 8.50">
                </div>
                <div class="form-group">
                    <label class="form-label" for="eef-status">Status</label>
                    <select class="form-input form-select" id="eef-status">
                        <option value="enrolled"  ${enrollment.status === 'enrolled'  ? 'selected' : ''}>enrolled</option>
                        <option value="completed" ${enrollment.status === 'completed' ? 'selected' : ''}>completed</option>
                        <option value="dropped"   ${enrollment.status === 'dropped'   ? 'selected' : ''}>dropped</option>
                    </select>
                </div>
            </div>
            <div id="eef-error" class="form-error"></div>
        </form>
    `;

    const footerHtml = `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" id="eef-submit">Update</button>
    `;

    showModal({
        title: 'Edit Enrollment',
        bodyHtml,
        footerHtml,
        onOpen: () => {
            document.getElementById('eef-submit')
                .addEventListener('click', () => _submitEditEnrollment(id));
            document.getElementById('edit-enrollment-form')
                .addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') { e.preventDefault(); _submitEditEnrollment(id); }
                });
        },
    });
}

async function _submitEditEnrollment(id) {
    const errorEl = document.getElementById('eef-error');
    const submitBtn = document.getElementById('eef-submit');

    const gradeStr = document.getElementById('eef-grade').value.trim();
    const status   = document.getElementById('eef-status').value;

    // Validate grade if provided
    let grade = null;
    if (gradeStr !== '') {
        grade = parseFloat(gradeStr);
        if (isNaN(grade) || grade < 0 || grade > 10) {
            errorEl.textContent = 'Grade must be a number between 0 and 10.';
            return;
        }
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Updating…';
    errorEl.textContent = '';

    try {
        await apiFetch(`/api/enrollments/${id}`, {
            method: 'PUT',
            body: { grade, status },
        });
        showToast('Enrollment updated successfully.', 'success');
        closeModal();
        _loadEnrollments();
    } catch (err) {
        errorEl.textContent = err.message;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Update';
    }
}

/* --------------------------------------------------------------------------
   Delete Enrollment
   -------------------------------------------------------------------------- */

function _confirmDeleteEnrollment(id) {
    showModal({
        title: 'Delete Enrollment',
        bodyHtml: `
            <p style="color:var(--text-secondary)">
                Are you sure you want to delete this enrollment?
            </p>
            <p style="color:var(--text-muted);font-size:0.85rem;margin-top:8px">
                This action cannot be undone.
            </p>
        `,
        footerHtml: `
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-danger" id="confirm-delete-enrollment">Delete</button>
        `,
        onOpen: () => {
            document.getElementById('confirm-delete-enrollment')
                .addEventListener('click', () => _deleteEnrollment(id));
        },
    });
}

async function _deleteEnrollment(id) {
    const btn = document.getElementById('confirm-delete-enrollment');
    if (btn) { btn.disabled = true; btn.textContent = 'Deleting…'; }

    try {
        await apiFetch(`/api/enrollments/${id}`, { method: 'DELETE' });
        showToast('Enrollment deleted successfully.', 'success');
        closeModal();
        _loadEnrollments();
    } catch (err) {
        showToast('Failed to delete enrollment: ' + err.message, 'error');
        if (btn) { btn.disabled = false; btn.textContent = 'Delete'; }
    }
}
