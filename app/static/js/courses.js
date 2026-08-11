/**
 * Courses Page (Phase 5)
 * ======================
 * Full CRUD UI for course management.
 *
 * Hooks into the Phase 4 router via:
 *   _renderCoursesPage()  — returns HTML
 *   _mountCoursesPage()   — attaches event listeners after render
 *
 * API endpoints used:
 *   GET    /api/courses           (list + search)
 *   POST   /api/courses           (create)
 *   GET    /api/courses/<id>      (fetch for edit)
 *   PUT    /api/courses/<id>      (update)
 *   DELETE /api/courses/<id>      (delete)
 */

/* --------------------------------------------------------------------------
   State
   -------------------------------------------------------------------------- */

let _coursesState = {
    search: '',
    data: [],
    loading: false,
};

/* --------------------------------------------------------------------------
   Page Renderer
   -------------------------------------------------------------------------- */

function _renderCoursesPage() {
    return `
        <div class="toolbar">
            ${buildSearchBar('Search by code or name…', 'courses-search')}
            <button class="btn btn-primary" id="btn-add-course">+ Add Course</button>
        </div>
        <div id="courses-table-area">
            <div class="empty-state"><div class="loading-spinner"></div><p style="margin-top:12px;color:var(--text-muted)">Loading courses…</p></div>
        </div>
    `;
}

/* --------------------------------------------------------------------------
   Mount
   -------------------------------------------------------------------------- */

function _mountCoursesPage() {
    _coursesState.search = '';
    _loadCourses();

    const searchInput = document.getElementById('courses-search');
    if (searchInput) {
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                _coursesState.search = searchInput.value.trim();
                _loadCourses();
            }
        });
        searchInput.addEventListener('search', () => {
            _coursesState.search = searchInput.value.trim();
            _loadCourses();
        });
    }

    document.getElementById('btn-add-course')
        .addEventListener('click', () => _showCourseFormModal());
}

/* --------------------------------------------------------------------------
   Load Courses (GET /api/courses)
   -------------------------------------------------------------------------- */

async function _loadCourses() {
    _coursesState.loading = true;
    _renderCoursesTable();

    try {
        const params = new URLSearchParams();
        if (_coursesState.search) params.set('search', _coursesState.search);

        const result = await apiFetch(`/api/courses?${params}`);
        _coursesState.data = result.data;
    } catch (err) {
        showToast('Failed to load courses: ' + err.message, 'error');
        _coursesState.data = [];
    } finally {
        _coursesState.loading = false;
        _renderCoursesTable();
    }
}

/* --------------------------------------------------------------------------
   Render Table
   -------------------------------------------------------------------------- */

function _renderCoursesTable() {
    const area = document.getElementById('courses-table-area');
    if (!area) return;

    if (_coursesState.loading) {
        area.innerHTML = `
            <div class="empty-state">
                <div class="loading-spinner"></div>
                <p style="margin-top:12px;color:var(--text-muted)">Loading courses…</p>
            </div>`;
        return;
    }

    const courses = _coursesState.data;

    if (courses.length === 0) {
        const msg = _coursesState.search
            ? 'No courses match your search.'
            : 'No courses yet. Add your first course!';
        area.innerHTML = `
            <div class="card">
                <div class="empty-state">
                    <div class="empty-state-icon">📚</div>
                    <div class="empty-state-title">No courses found</div>
                    <div class="empty-state-text">${escapeHtml(msg)}</div>
                </div>
            </div>`;
        return;
    }

    const columns = ['Course Code', 'Name', 'Credits', 'Description', 'Actions'];
    const rows = courses.map((c) => [
        escapeHtml(c.course_code),
        escapeHtml(c.name),
        `<span class="badge badge-info">${c.credits}</span>`,
        escapeHtml(c.description || '—'),
        `<div class="table-actions">
            <button class="btn btn-sm btn-secondary" onclick="_editCourse(${c.id})" title="Edit">✏️ Edit</button>
            <button class="btn btn-sm btn-danger" onclick="_confirmDeleteCourse(${c.id}, '${escapeHtml(c.course_code)}')" title="Delete">🗑️</button>
        </div>`,
    ]);

    area.innerHTML = buildTable(columns, rows);
}

/* --------------------------------------------------------------------------
   Add / Edit Modal
   -------------------------------------------------------------------------- */

function _showCourseFormModal(course = null) {
    const isEdit = !!course;
    const title = isEdit ? 'Edit Course' : 'Add Course';

    const bodyHtml = `
        <form id="course-form" novalidate>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="cf-code">Course Code *</label>
                <input class="form-input" id="cf-code" type="text" required
                       value="${isEdit ? escapeHtml(course.course_code) : ''}"
                       placeholder="e.g. CS101">
            </div>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="cf-name">Name *</label>
                <input class="form-input" id="cf-name" type="text" required
                       value="${isEdit ? escapeHtml(course.name) : ''}"
                       placeholder="Course name">
            </div>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="cf-credits">Credits *</label>
                <input class="form-input" id="cf-credits" type="number" min="1" required
                       value="${isEdit ? course.credits : ''}"
                       placeholder="e.g. 3">
            </div>
            <div class="form-group">
                <label class="form-label" for="cf-desc">Description</label>
                <input class="form-input" id="cf-desc" type="text"
                       value="${isEdit && course.description ? escapeHtml(course.description) : ''}"
                       placeholder="Optional description">
            </div>
            <div id="cf-error" class="form-error" style="margin-top:10px"></div>
        </form>
    `;

    const footerHtml = `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" id="cf-submit">${isEdit ? 'Update' : 'Create'}</button>
    `;

    showModal({
        title,
        bodyHtml,
        footerHtml,
        onOpen: () => {
            document.getElementById('cf-submit')
                .addEventListener('click', () => _submitCourseForm(isEdit ? course.id : null));
            document.getElementById('course-form')
                .addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') { e.preventDefault(); _submitCourseForm(isEdit ? course.id : null); }
                });
        },
    });
}

/* --------------------------------------------------------------------------
   Submit Course Form
   -------------------------------------------------------------------------- */

async function _submitCourseForm(courseId) {
    const errorEl = document.getElementById('cf-error');
    const submitBtn = document.getElementById('cf-submit');

    const code    = document.getElementById('cf-code').value.trim();
    const name    = document.getElementById('cf-name').value.trim();
    const credits = document.getElementById('cf-credits').value.trim();
    const desc    = document.getElementById('cf-desc').value.trim();

    // Client-side validation
    const missing = [];
    if (!code) missing.push('Course Code');
    if (!name) missing.push('Name');
    if (!credits) missing.push('Credits');

    if (missing.length > 0) {
        errorEl.textContent = 'Required: ' + missing.join(', ');
        return;
    }

    const creditsNum = parseInt(credits, 10);
    if (isNaN(creditsNum) || creditsNum <= 0) {
        errorEl.textContent = 'Credits must be a positive integer.';
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = courseId ? 'Updating…' : 'Creating…';
    errorEl.textContent = '';

    const payload = {
        course_code: code,
        name,
        credits: creditsNum,
        description: desc || null,
    };

    try {
        if (courseId) {
            await apiFetch(`/api/courses/${courseId}`, { method: 'PUT', body: payload });
            showToast('Course updated successfully.', 'success');
        } else {
            await apiFetch('/api/courses', { method: 'POST', body: payload });
            showToast('Course created successfully.', 'success');
        }
        closeModal();
        _loadCourses();
    } catch (err) {
        errorEl.textContent = err.message;
        submitBtn.disabled = false;
        submitBtn.textContent = courseId ? 'Update' : 'Create';
    }
}

/* --------------------------------------------------------------------------
   Edit Course
   -------------------------------------------------------------------------- */

async function _editCourse(id) {
    try {
        const course = await apiFetch(`/api/courses/${id}`);
        _showCourseFormModal(course);
    } catch (err) {
        showToast('Failed to load course: ' + err.message, 'error');
    }
}

/* --------------------------------------------------------------------------
   Delete Course
   -------------------------------------------------------------------------- */

function _confirmDeleteCourse(id, code) {
    showModal({
        title: 'Delete Course',
        bodyHtml: `
            <p style="color:var(--text-secondary);margin-bottom:8px">
                Are you sure you want to delete course <strong>${escapeHtml(code)}</strong>?
            </p>
            <p style="color:var(--text-muted);font-size:0.85rem">
                This will permanently remove the course and all associated enrollment records.
            </p>
        `,
        footerHtml: `
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-danger" id="confirm-delete-course">Delete</button>
        `,
        onOpen: () => {
            document.getElementById('confirm-delete-course')
                .addEventListener('click', () => _deleteCourse(id));
        },
    });
}

async function _deleteCourse(id) {
    const btn = document.getElementById('confirm-delete-course');
    if (btn) { btn.disabled = true; btn.textContent = 'Deleting…'; }

    try {
        await apiFetch(`/api/courses/${id}`, { method: 'DELETE' });
        showToast('Course deleted successfully.', 'success');
        closeModal();
        _loadCourses();
    } catch (err) {
        showToast('Failed to delete course: ' + err.message, 'error');
        if (btn) { btn.disabled = false; btn.textContent = 'Delete'; }
    }
}
