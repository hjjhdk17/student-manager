/**
 * Semesters Page (Phase 5)
 * ========================
 * Full CRUD UI for semester management.
 *
 * Hooks into the Phase 4 router via:
 *   _renderSemestersPage()  — returns HTML
 *   _mountSemestersPage()   — attaches event listeners after render
 *
 * API endpoints used:
 *   GET    /api/semesters           (list)
 *   POST   /api/semesters           (create)
 *   GET    /api/semesters/<id>      (fetch for edit)
 *   PUT    /api/semesters/<id>      (update)
 *   DELETE /api/semesters/<id>      (delete)
 */

/* --------------------------------------------------------------------------
   State
   -------------------------------------------------------------------------- */

let _semestersState = {
    data: [],
    loading: false,
};

/* --------------------------------------------------------------------------
   Page Renderer
   -------------------------------------------------------------------------- */

function _renderSemestersPage() {
    return `
        <div class="toolbar">
            <div></div>
            ${window.currentUser.role === 'admin' ? '<button class="btn btn-primary" id="btn-add-semester">+ Add Semester</button>' : ''}
        </div>
        <div id="semesters-table-area">
            <div class="empty-state"><div class="loading-spinner"></div><p style="margin-top:12px;color:var(--text-muted)">Loading semesters…</p></div>
        </div>
    `;
}

/* --------------------------------------------------------------------------
   Mount
   -------------------------------------------------------------------------- */

function _mountSemestersPage() {
    _loadSemesters();

    const addBtn = document.getElementById('btn-add-semester');
    if (addBtn) {
        addBtn.addEventListener('click', () => _showSemesterFormModal());
    }
}

/* --------------------------------------------------------------------------
   Load Semesters (GET /api/semesters)
   -------------------------------------------------------------------------- */

async function _loadSemesters() {
    _semestersState.loading = true;
    _renderSemestersTable();

    try {
        const result = await apiFetch('/api/semesters');
        _semestersState.data = result.data;
    } catch (err) {
        showToast('Failed to load semesters: ' + err.message, 'error');
        _semestersState.data = [];
    } finally {
        _semestersState.loading = false;
        _renderSemestersTable();
    }
}

/* --------------------------------------------------------------------------
   Render Table
   -------------------------------------------------------------------------- */

function _renderSemestersTable() {
    const area = document.getElementById('semesters-table-area');
    if (!area) return;

    if (_semestersState.loading) {
        area.innerHTML = `
            <div class="empty-state">
                <div class="loading-spinner"></div>
                <p style="margin-top:12px;color:var(--text-muted)">Loading semesters…</p>
            </div>`;
        return;
    }

    const semesters = _semestersState.data;

    if (semesters.length === 0) {
        area.innerHTML = `
            <div class="card">
                <div class="empty-state">
                    <div class="empty-state-icon">📅</div>
                    <div class="empty-state-title">No semesters found</div>
                    <div class="empty-state-text">Add your first semester to get started!</div>
                    ${window.currentUser.role === 'admin' ? '<button class="btn btn-primary" style="margin-top:16px" onclick="_showSemesterFormModal()">Add Semester</button>' : ''}
                </div>
            </div>`;
        return;
    }

    const columns = ['Name', 'Start Date', 'End Date', 'Actions'];
    const rows = semesters.map((s) => [
        escapeHtml(s.name),
        s.start_date || '—',
        s.end_date || '—',
        `<div class="table-actions">
            ${window.currentUser.role === 'admin' ? `
            <button class="btn btn-sm btn-secondary" onclick="_editSemester(${s.id})" title="Edit">✏️ Edit</button>
            <button class="btn btn-sm btn-danger" onclick="_confirmDeleteSemester(${s.id}, '${escapeHtml(s.name)}')" title="Delete">🗑️</button>
            ` : '<span style="color:var(--text-muted);font-size:0.8rem">View Only</span>'}
        </div>`,
    ]);

    area.innerHTML = buildTable(columns, rows);
}

/* --------------------------------------------------------------------------
   Add / Edit Modal
   -------------------------------------------------------------------------- */

function _showSemesterFormModal(semester = null) {
    const isEdit = !!semester;
    const title = isEdit ? 'Edit Semester' : 'Add Semester';

    const bodyHtml = `
        <form id="semester-form" novalidate>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="semf-name">Name *</label>
                <input class="form-input" id="semf-name" type="text" required
                       value="${isEdit ? escapeHtml(semester.name) : ''}"
                       placeholder="e.g. Fall 2026">
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px">
                <div class="form-group">
                    <label class="form-label" for="semf-start">Start Date *</label>
                    <input class="form-input" id="semf-start" type="date" required
                           value="${isEdit && semester.start_date ? semester.start_date : ''}">
                </div>
                <div class="form-group">
                    <label class="form-label" for="semf-end">End Date *</label>
                    <input class="form-input" id="semf-end" type="date" required
                           value="${isEdit && semester.end_date ? semester.end_date : ''}">
                </div>
            </div>
            <div id="semf-error" class="form-error"></div>
        </form>
    `;

    const footerHtml = `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" id="semf-submit">${isEdit ? 'Update' : 'Create'}</button>
    `;

    showModal({
        title,
        bodyHtml,
        footerHtml,
        onOpen: () => {
            document.getElementById('semf-submit')
                .addEventListener('click', () => _submitSemesterForm(isEdit ? semester.id : null));
            document.getElementById('semester-form')
                .addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') { e.preventDefault(); _submitSemesterForm(isEdit ? semester.id : null); }
                });
        },
    });
}

/* --------------------------------------------------------------------------
   Submit Semester Form
   -------------------------------------------------------------------------- */

async function _submitSemesterForm(semesterId) {
    const errorEl = document.getElementById('semf-error');
    const submitBtn = document.getElementById('semf-submit');

    const name      = document.getElementById('semf-name').value.trim();
    const startDate = document.getElementById('semf-start').value;
    const endDate   = document.getElementById('semf-end').value;

    // Client-side validation
    const missing = [];
    if (!name)      missing.push('Name');
    if (!startDate) missing.push('Start Date');
    if (!endDate)   missing.push('End Date');

    if (missing.length > 0) {
        errorEl.textContent = 'Required: ' + missing.join(', ');
        return;
    }

    if (endDate < startDate) {
        errorEl.textContent = 'End date must be on or after start date.';
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = semesterId ? 'Updating…' : 'Creating…';
    errorEl.textContent = '';

    const payload = {
        name,
        start_date: startDate,
        end_date: endDate,
    };

    try {
        if (semesterId) {
            await apiFetch(`/api/semesters/${semesterId}`, { method: 'PUT', body: payload });
            showToast('Semester updated successfully.', 'success');
        } else {
            await apiFetch('/api/semesters', { method: 'POST', body: payload });
            showToast('Semester created successfully.', 'success');
        }
        closeModal();
        _loadSemesters();
    } catch (err) {
        errorEl.textContent = err.message;
        submitBtn.disabled = false;
        submitBtn.textContent = semesterId ? 'Update' : 'Create';
    }
}

/* --------------------------------------------------------------------------
   Edit Semester
   -------------------------------------------------------------------------- */

async function _editSemester(id) {
    try {
        const semester = await apiFetch(`/api/semesters/${id}`);
        _showSemesterFormModal(semester);
    } catch (err) {
        showToast('Failed to load semester: ' + err.message, 'error');
    }
}

/* --------------------------------------------------------------------------
   Delete Semester
   -------------------------------------------------------------------------- */

function _confirmDeleteSemester(id, name) {
    showModal({
        title: 'Delete Semester',
        bodyHtml: `
            <p style="color:var(--text-secondary);margin-bottom:8px">
                Are you sure you want to delete semester <strong>${escapeHtml(name)}</strong>?
            </p>
            <p style="color:var(--text-muted);font-size:0.85rem">
                This will permanently remove the semester and all associated enrollment records.
            </p>
        `,
        footerHtml: `
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-danger" id="confirm-delete-semester">Delete</button>
        `,
        onOpen: () => {
            document.getElementById('confirm-delete-semester')
                .addEventListener('click', () => _deleteSemester(id));
        },
    });
}

async function _deleteSemester(id) {
    const btn = document.getElementById('confirm-delete-semester');
    if (btn) { btn.disabled = true; btn.textContent = 'Deleting…'; }

    try {
        await apiFetch(`/api/semesters/${id}`, { method: 'DELETE' });
        showToast('Semester deleted successfully.', 'success');
        closeModal();
        _loadSemesters();
    } catch (err) {
        showToast('Failed to delete semester: ' + err.message, 'error');
        if (btn) { btn.disabled = false; btn.textContent = 'Delete'; }
    }
}
