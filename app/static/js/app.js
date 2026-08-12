/**
 * Student Manager — SPA Shell & Client-Side Router
 * =================================================
 * This file contains:
 *   1. Client-side hash router
 *   2. Route definitions and rendering
 *   3. Reusable UI components (modal, toast, search bar, table)
 *   4. API fetch helper
 *   5. Mobile sidebar logic
 */

/* ==========================================================================
   1. API Helper
   ========================================================================== */

/**
 * Generic fetch wrapper for the REST API.
 * Adds JSON headers automatically and parses responses.
 *
 * @param {string} url  — API endpoint, e.g. "/api/students"
 * @param {object} options — fetch options (method, body, etc.)
 * @returns {Promise<object>} Parsed JSON response
 */
async function apiFetch(url, options = {}) {
    const defaults = {
        headers: { 'Content-Type': 'application/json' },
    };

    if (options.body && typeof options.body === 'object') {
        options.body = JSON.stringify(options.body);
    }

    const response = await fetch(url, { ...defaults, ...options });

    // No-content response
    if (response.status === 204) {
        return null;
    }

    const data = await response.json();

    if (!response.ok) {
        const message = data.error || data.message || 'Something went wrong';
        throw new Error(message);
    }

    return data;
}

/* ==========================================================================
   2. Toast Notification System
   ========================================================================== */

const TOAST_ICONS = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
};

/**
 * Show a toast notification.
 *
 * @param {string} message — The message to display
 * @param {string} type    — One of "success", "error", "warning", "info"
 * @param {number} duration — Auto-dismiss time in ms (default 4000)
 */
function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container');

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.setAttribute('role', 'alert');

    toast.innerHTML = `
        <span class="toast-icon" aria-hidden="true">${TOAST_ICONS[type] || 'ℹ'}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
        <button class="toast-close" aria-label="Dismiss">&times;</button>
    `;

    // Close button
    toast.querySelector('.toast-close').addEventListener('click', () => {
        dismissToast(toast);
    });

    container.appendChild(toast);

    // Trigger slide-in animation on next frame
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // Auto-dismiss
    if (duration > 0) {
        setTimeout(() => dismissToast(toast), duration);
    }
}

function dismissToast(toast) {
    toast.classList.remove('show');
    toast.addEventListener('transitionend', () => toast.remove(), { once: true });
    // Fallback removal if transitionend doesn't fire
    setTimeout(() => { if (toast.parentNode) toast.remove(); }, 400);
}

/* ==========================================================================
   3. Modal System
   ========================================================================== */

let _activeModal = null;

/**
 * Show a modal dialog.
 *
 * @param {object} options
 * @param {string} options.title       — Modal title
 * @param {string} options.bodyHtml    — HTML content for the body
 * @param {string} [options.footerHtml] — HTML content for the footer
 * @param {function} [options.onOpen]  — Callback after modal opens
 * @param {function} [options.onClose] — Callback after modal closes
 */
function showModal({ title, bodyHtml, footerHtml = '', onOpen, onClose } = {}) {
    closeModal(); // Close any existing modal first

    const root = document.getElementById('modal-root');

    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.setAttribute('role', 'dialog');
    backdrop.setAttribute('aria-modal', 'true');
    backdrop.setAttribute('aria-label', title);

    backdrop.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">${escapeHtml(title)}</h2>
                <button class="modal-close" aria-label="Close modal">&times;</button>
            </div>
            <div class="modal-body">${bodyHtml}</div>
            ${footerHtml ? `<div class="modal-footer">${footerHtml}</div>` : ''}
        </div>
    `;

    root.appendChild(backdrop);

    // Store reference
    _activeModal = { backdrop, onClose };

    // Animate in on next frame
    requestAnimationFrame(() => {
        backdrop.classList.add('open');
    });

    // Close via X button
    backdrop.querySelector('.modal-close').addEventListener('click', closeModal);

    // Close via backdrop click
    backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) closeModal();
    });

    // Close via Escape key
    document.addEventListener('keydown', _modalEscHandler);

    // Focus the close button for keyboard accessibility
    const closeBtn = backdrop.querySelector('.modal-close');
    if (closeBtn) closeBtn.focus();

    if (onOpen) onOpen(backdrop.querySelector('.modal'));
}

function closeModal() {
    if (!_activeModal) return;

    const { backdrop, onClose } = _activeModal;
    backdrop.classList.remove('open');

    document.removeEventListener('keydown', _modalEscHandler);

    backdrop.addEventListener('transitionend', () => {
        backdrop.remove();
        if (onClose) onClose();
    }, { once: true });

    // Fallback removal
    setTimeout(() => { if (backdrop.parentNode) backdrop.remove(); }, 400);

    _activeModal = null;
}

function _modalEscHandler(e) {
    if (e.key === 'Escape') closeModal();
}

/* ==========================================================================
   4. Reusable HTML Builders
   ========================================================================== */

/**
 * Build a search bar HTML string.
 *
 * @param {string} placeholder — Placeholder text
 * @param {string} id — Input element id
 * @returns {string} HTML
 */
function buildSearchBar(placeholder = 'Search…', id = 'search-input') {
    return `
        <div class="search-bar">
            <span class="search-icon" aria-hidden="true">🔍</span>
            <input type="search" class="form-input" id="${id}"
                   placeholder="${escapeHtml(placeholder)}"
                   aria-label="${escapeHtml(placeholder)}">
        </div>
    `;
}

/**
 * Build a data table HTML string.
 *
 * @param {string[]} columns — Column headers
 * @param {string[][]} rows — 2D array of cell contents (can contain HTML)
 * @param {string} emptyMessage — Message when no rows
 * @returns {string} HTML
 */
function buildTable(columns, rows, emptyMessage = 'No data available') {
    if (!rows || rows.length === 0) {
        return `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <div class="empty-state-title">No records</div>
                <div class="empty-state-text">${escapeHtml(emptyMessage)}</div>
            </div>
        `;
    }

    const ths = columns.map((col) => `<th>${escapeHtml(col)}</th>`).join('');
    const trs = rows
        .map((row) => {
            const tds = row.map((cell) => `<td>${cell}</td>`).join('');
            return `<tr>${tds}</tr>`;
        })
        .join('');

    return `
        <div class="table-wrapper">
            <table class="data-table">
                <thead><tr>${ths}</tr></thead>
                <tbody>${trs}</tbody>
            </table>
        </div>
    `;
}

/* ==========================================================================
   5. Utility Functions
   ========================================================================== */

/**
 * Escape HTML entities to prevent XSS.
 */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/* ==========================================================================
   6. Route Definitions
   ========================================================================== */

/**
 * Each route has:
 *   - title: displayed in the page header
 *   - subtitle: displayed below the title
 *   - render: function returning the HTML for the page content
 *   - onMount: optional callback after the content is injected into the DOM
 */
const routes = {
    dashboard: {
        title: 'Dashboard',
        subtitle: 'Overview of your data',
        render: renderDashboard,
        onMount: mountDashboard,
    },
    students: {
        title: 'Students',
        subtitle: 'Manage student records',
        render: renderStudents,
        onMount: mountStudents,
    },
    courses: {
        title: 'Courses',
        subtitle: 'Manage course catalog',
        render: renderCourses,
        onMount: mountCourses,
    },
    semesters: {
        title: 'Semesters',
        subtitle: 'Manage academic semesters',
        render: renderSemesters,
        onMount: mountSemesters,
    },
    enrollments: {
        title: 'Enrollments',
        subtitle: 'Manage student enrollments',
        render: renderEnrollments,
        onMount: mountEnrollments,
    },
    users: {
        title: 'Users',
        subtitle: 'Manage user accounts',
        render: renderUsers,
        onMount: mountUsers,
    },
};

/* ==========================================================================
   7. Page Renderers
   ========================================================================== */

function renderDashboard() {
    const isAdmin = window.currentUser.role === 'admin';
    const isStudent = window.currentUser.role === 'student';

    return `
        <div class="stat-grid">
            ${isStudent ? '' : `
            <div class="stat-card">
                <div class="stat-icon students" aria-hidden="true">👤</div>
                <div class="stat-info">
                    <span class="stat-label">Students</span>
                    <span class="stat-value" id="dash-students">…</span>
                </div>
            </div>
            `}
            <div class="stat-card">
                <div class="stat-icon courses" aria-hidden="true">📚</div>
                <div class="stat-info">
                    <span class="stat-label">Courses</span>
                    <span class="stat-value" id="dash-courses">…</span>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon semesters" aria-hidden="true">📅</div>
                <div class="stat-info">
                    <span class="stat-label">Semesters</span>
                    <span class="stat-value" id="dash-semesters">…</span>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon enrollments" aria-hidden="true">📝</div>
                <div class="stat-info">
                    <span class="stat-label">Enrollments</span>
                    <span class="stat-value" id="dash-enrollments">…</span>
                </div>
            </div>
            ${isAdmin ? `
            <div class="stat-card">
                <div class="stat-icon" aria-hidden="true" style="background:var(--success-bg);color:var(--success)">🛡️</div>
                <div class="stat-info">
                    <span class="stat-label">Users</span>
                    <span class="stat-value" id="dash-users">…</span>
                </div>
            </div>
            ` : ''}
        </div>

        <div style="margin-top: 28px;">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Quick Navigation</h2>
                </div>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    ${isStudent ? '' : `<button class="btn btn-primary" onclick="navigate('students')">Manage Students</button>`}
                    <button class="btn btn-secondary" onclick="navigate('courses')">View Courses</button>
                    <button class="btn btn-secondary" onclick="navigate('semesters')">View Semesters</button>
                    <button class="btn btn-secondary" onclick="navigate('enrollments')">${isStudent ? 'View' : 'Manage'} Enrollments</button>
                    ${isAdmin ? `<button class="btn btn-secondary" onclick="navigate('users')">Manage Users</button>` : ''}
                </div>
            </div>
        </div>
    `;
}

/**
 * Load live counts into the dashboard stat cards.
 * Uses the existing list endpoints (no new backend endpoint needed).
 */
async function mountDashboard() {
    try {
        // Fetch counts in parallel using existing endpoints
        const promises = [
            apiFetch('/api/courses'),
            apiFetch('/api/semesters'),
            apiFetch('/api/enrollments'),
        ];
        if (window.currentUser.role !== 'student') {
            promises.push(apiFetch('/api/students?per_page=1'));
        } else {
            promises.push(Promise.resolve({ total: 0 }));
        }
        if (window.currentUser.role === 'admin') {
            promises.push(apiFetch('/api/users'));
        } else {
            promises.push(Promise.resolve({ total: 0 }));
        }

        const [courses, semesters, enrollments, students, users] = await Promise.all(promises);

        // Students endpoint returns paginated total; others return total directly
        const el = (id, val) => { const e = document.getElementById(id); if (e) e.textContent = val; };
        el('dash-students', students.total);
        el('dash-courses', courses.total);
        el('dash-semesters', semesters.total);
        el('dash-enrollments', enrollments.total);
        el('dash-users', users.total);
    } catch (err) {
        // Silently degrade — dashboard just shows '…' if the API is unreachable
    }
}

/** Placeholder renderers — these are stubs for Phase 4.
 *  The actual CRUD implementations belong in each entity's JS file (Phase 5). */

function renderStudents() {
    return typeof _renderStudentsPage === 'function'
        ? _renderStudentsPage()
        : _renderPlaceholder('Students', '👤', 'Student management will be implemented in Phase 5.');
}
function mountStudents() {
    if (typeof _mountStudentsPage === 'function') _mountStudentsPage();
}

function renderCourses() {
    return typeof _renderCoursesPage === 'function'
        ? _renderCoursesPage()
        : _renderPlaceholder('Courses', '📚', 'Course management will be implemented in Phase 5.');
}
function mountCourses() {
    if (typeof _mountCoursesPage === 'function') _mountCoursesPage();
}

function renderSemesters() {
    return typeof _renderSemestersPage === 'function'
        ? _renderSemestersPage()
        : _renderPlaceholder('Semesters', '📅', 'Semester management will be implemented in Phase 5.');
}
function mountSemesters() {
    if (typeof _mountSemestersPage === 'function') _mountSemestersPage();
}

function renderEnrollments() {
    return typeof _renderEnrollmentsPage === 'function'
        ? _renderEnrollmentsPage()
        : _renderPlaceholder('Enrollments', '📝', 'Enrollment management will be implemented in Phase 5.');
}
function mountEnrollments() {
    if (typeof _mountEnrollmentsPage === 'function') _mountEnrollmentsPage();
}

function renderUsers() {
    return typeof _renderUsersPage === 'function'
        ? _renderUsersPage()
        : _renderPlaceholder('Users', '🛡️', 'User management module missing.');
}
function mountUsers() {
    if (typeof _mountUsersPage === 'function') _mountUsersPage();
}

/**
 * Render a placeholder page for routes not yet implemented.
 */
function _renderPlaceholder(name, icon, message) {
    return `
        <div class="card">
            <div class="empty-state">
                <div class="empty-state-icon">${icon}</div>
                <div class="empty-state-title">${escapeHtml(name)}</div>
                <div class="empty-state-text">${escapeHtml(message)}</div>
            </div>
        </div>
    `;
}

/* ==========================================================================
   8. Router
   ========================================================================== */

/**
 * Navigate to a hash route programmatically.
 * @param {string} route — Route name, e.g. "students"
 */
function navigate(route) {
    window.location.hash = '#/' + route;
}

/**
 * Get the current route name from the hash.
 * @returns {string} Route name (e.g. "students"), or "dashboard" by default
 */
function getCurrentRoute() {
    const hash = window.location.hash;
    if (!hash || hash === '#' || hash === '#/') return 'dashboard';
    return hash.replace('#/', '');
}

/**
 * Render the current route's view into the page.
 */
function renderRoute() {
    const routeName = getCurrentRoute();
    const route = routes[routeName];

    if (!route) {
        // Unknown route → go to dashboard
        navigate('dashboard');
        return;
    }

    // Update page header
    document.getElementById('page-title').textContent = route.title;
    document.getElementById('page-subtitle').textContent = route.subtitle || '';

    // Update document title
    document.title = `${route.title} — Student Manager`;

    // Render content
    const content = document.getElementById('page-content');
    content.innerHTML = route.render();

    // Update active navigation
    document.querySelectorAll('.nav-link[data-route]').forEach((link) => {
        const isActive = link.dataset.route === routeName;
        link.classList.toggle('active', isActive);
        if (isActive) {
            link.setAttribute('aria-current', 'page');
        } else {
            link.removeAttribute('aria-current');
        }
    });

    // Clear page actions (feature pages can populate this)
    document.getElementById('page-actions').innerHTML = '';

    // Close mobile sidebar after navigation
    closeSidebar();

    // Run onMount callback if defined
    if (route.onMount) route.onMount();
}

/* ==========================================================================
   9. Mobile Sidebar
   ========================================================================== */

function openSidebar() {
    document.getElementById('sidebar').classList.add('open');
    document.getElementById('sidebar-overlay').classList.add('open');
}

function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebar-overlay').classList.remove('open');
}

/* ==========================================================================
   10. Initialization
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // --- Navigation click handlers ---
    document.querySelectorAll('.nav-link[data-route]').forEach((link) => {
        link.addEventListener('click', () => {
            navigate(link.dataset.route);
        });
    });

    // --- Mobile sidebar ---
    document.getElementById('sidebar-toggle').addEventListener('click', () => {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
    });
    document.getElementById('sidebar-overlay').addEventListener('click', closeSidebar);

    // --- Logout confirmation ---
    document.getElementById('nav-logout').addEventListener('click', () => {
        showModal({
            title: 'Confirm Logout',
            bodyHtml: '<p style="color: var(--text-secondary); font-size: 0.9rem;">Are you sure you want to log out?</p>',
            footerHtml: `
                <button class="btn btn-secondary" id="logout-cancel">Cancel</button>
                <button class="btn btn-danger" id="logout-confirm">Log out</button>
            `,
            onOpen: (modal) => {
                modal.querySelector('#logout-cancel').addEventListener('click', closeModal);
                modal.querySelector('#logout-confirm').addEventListener('click', () => {
                    document.getElementById('logout-form').submit();
                });
                // Focus the Cancel button for safety
                modal.querySelector('#logout-cancel').focus();
            },
        });
    });

    // --- Listen for hash changes (browser back/forward) ---
    window.addEventListener('hashchange', renderRoute);

    // --- Initial render ---
    renderRoute();
});


