/**
 * Users Page
 * ==========
 * Full CRUD UI for user management. Available to Admin only.
 */

let _usersState = {
    data: [],
    loading: false,
};

function _renderUsersPage() {
    return `
        <div class="toolbar">
            <div></div>
            <button class="btn btn-primary" id="btn-add-user">+ Add User</button>
        </div>
        <div id="users-table-area">
            <div class="empty-state"><div class="loading-spinner"></div><p style="margin-top:12px;color:var(--text-muted)">Loading users…</p></div>
        </div>
    `;
}

function _mountUsersPage() {
    if (window.currentUser.role !== 'admin') {
        navigate('dashboard');
        return;
    }
    _loadUsers();
    document.getElementById('btn-add-user').addEventListener('click', () => _showUserFormModal());
}

async function _loadUsers() {
    _usersState.loading = true;
    _renderUsersTable();

    try {
        const result = await apiFetch('/api/users');
        _usersState.data = result.data;
    } catch (err) {
        showToast('Failed to load users: ' + err.message, 'error');
        _usersState.data = [];
    } finally {
        _usersState.loading = false;
        _renderUsersTable();
    }
}

function _renderUsersTable() {
    const area = document.getElementById('users-table-area');
    if (!area) return;

    if (_usersState.loading) {
        area.innerHTML = `
            <div class="empty-state">
                <div class="loading-spinner"></div>
                <p style="margin-top:12px;color:var(--text-muted)">Loading users…</p>
            </div>`;
        return;
    }

    const users = _usersState.data;

    if (users.length === 0) {
        area.innerHTML = `
            <div class="card">
                <div class="empty-state">
                    <div class="empty-state-icon">🛡️</div>
                    <div class="empty-state-title">No users found</div>
                </div>
            </div>`;
        return;
    }

    const columns = ['ID', 'Username', 'Email', 'Role', 'Actions'];
    const rows = users.map((u) => {
        const isSelf = u.id === window.currentUser.id;
        let roleBadge = 'badge-default';
        if (u.role === 'admin') roleBadge = 'badge-danger';
        if (u.role === 'teacher') roleBadge = 'badge-info';
        if (u.role === 'student') roleBadge = 'badge-success';

        return [
            u.id,
            escapeHtml(u.username) + (isSelf ? ' <span class="badge badge-info" style="font-size:0.6rem">You</span>' : ''),
            escapeHtml(u.email),
            `<span class="badge ${roleBadge}">${escapeHtml(u.role)}</span>`,
            `<div class="table-actions">
                <button class="btn btn-sm btn-secondary" onclick="_editUser(${u.id})" title="Edit">✏️ Edit</button>
                <button class="btn btn-sm btn-danger" onclick="_confirmDeleteUser(${u.id}, '${escapeHtml(u.username)}')" title="Delete" ${isSelf ? 'disabled' : ''}>🗑️</button>
            </div>`,
        ];
    });

    area.innerHTML = buildTable(columns, rows);
}

function _showUserFormModal(user = null) {
    const isEdit = !!user;
    const title = isEdit ? 'Edit User' : 'Add User';
    
    // For editing, we don't require the password
    const passwordRequired = isEdit ? '' : 'required';
    const passwordPlaceholder = isEdit ? 'Leave blank to keep unchanged' : 'Minimum 6 characters';

    const bodyHtml = `
        <form id="user-form" novalidate>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="uf-username">Username *</label>
                <input class="form-input" id="uf-username" type="text" required
                       value="${isEdit ? escapeHtml(user.username) : ''}"
                       placeholder="e.g. admin_jane">
            </div>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="uf-email">Email *</label>
                <input class="form-input" id="uf-email" type="email" required
                       value="${isEdit ? escapeHtml(user.email) : ''}"
                       placeholder="jane@example.com">
            </div>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="uf-role">Role *</label>
                <select class="form-input form-select" id="uf-role" required>
                    <option value="student" ${isEdit && user.role === 'student' ? 'selected' : ''}>Student</option>
                    <option value="teacher" ${isEdit && user.role === 'teacher' ? 'selected' : ''}>Teacher</option>
                    <option value="admin"   ${isEdit && user.role === 'admin' ? 'selected' : ''}>Admin</option>
                </select>
            </div>
            <div class="form-group" style="margin-bottom:14px">
                <label class="form-label" for="uf-password">Password ${isEdit ? '' : '*'}</label>
                <input class="form-input" id="uf-password" type="password" ${passwordRequired}
                       placeholder="${passwordPlaceholder}">
            </div>
            <div id="uf-error" class="form-error"></div>
        </form>
    `;

    const footerHtml = `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" id="uf-submit">${isEdit ? 'Update' : 'Create'}</button>
    `;

    showModal({
        title,
        bodyHtml,
        footerHtml,
        onOpen: () => {
            document.getElementById('uf-submit').addEventListener('click', () => _submitUserForm(isEdit ? user.id : null));
        },
    });
}

async function _submitUserForm(userId) {
    const errorEl = document.getElementById('uf-error');
    const submitBtn = document.getElementById('uf-submit');

    const username = document.getElementById('uf-username').value.trim();
    const email    = document.getElementById('uf-email').value.trim();
    const role     = document.getElementById('uf-role').value;
    const password = document.getElementById('uf-password').value;

    const missing = [];
    if (!username) missing.push('Username');
    if (!email)    missing.push('Email');
    if (!userId && !password) missing.push('Password'); // Password required for create

    if (missing.length > 0) {
        errorEl.textContent = 'Required: ' + missing.join(', ');
        return;
    }

    if (password && password.length < 6) {
        errorEl.textContent = 'Password must be at least 6 characters.';
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = userId ? 'Updating…' : 'Creating…';
    errorEl.textContent = '';

    const payload = { username, email, role };
    if (password) {
        payload.password = password;
    }

    try {
        if (userId) {
            await apiFetch(`/api/users/${userId}`, { method: 'PUT', body: payload });
            showToast('User updated successfully.', 'success');
        } else {
            await apiFetch('/api/users', { method: 'POST', body: payload });
            showToast('User created successfully.', 'success');
        }
        closeModal();
        _loadUsers();
    } catch (err) {
        errorEl.textContent = err.message;
        submitBtn.disabled = false;
        submitBtn.textContent = userId ? 'Update' : 'Create';
    }
}

async function _editUser(id) {
    try {
        const user = await apiFetch(`/api/users/${id}`);
        _showUserFormModal(user);
    } catch (err) {
        showToast('Failed to load user: ' + err.message, 'error');
    }
}

function _confirmDeleteUser(id, username) {
    if (id === window.currentUser.id) {
        showToast('You cannot delete your own account.', 'error');
        return;
    }

    showModal({
        title: 'Delete User',
        bodyHtml: `
            <p style="color:var(--text-secondary);margin-bottom:8px">
                Are you sure you want to delete user <strong>${escapeHtml(username)}</strong>?
            </p>
            <p style="color:var(--text-muted);font-size:0.85rem">
                This action cannot be undone.
            </p>
        `,
        footerHtml: `
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-danger" id="confirm-delete-user">Delete</button>
        `,
        onOpen: () => {
            document.getElementById('confirm-delete-user')
                .addEventListener('click', () => _deleteUser(id));
        },
    });
}

async function _deleteUser(id) {
    const btn = document.getElementById('confirm-delete-user');
    if (btn) { btn.disabled = true; btn.textContent = 'Deleting…'; }

    try {
        await apiFetch(`/api/users/${id}`, { method: 'DELETE' });
        showToast('User deleted successfully.', 'success');
        closeModal();
        _loadUsers();
    } catch (err) {
        showToast('Failed to delete user: ' + err.message, 'error');
        if (btn) { btn.disabled = false; btn.textContent = 'Delete'; }
    }
}
