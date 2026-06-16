/**
 * Glow Guide AI — Shared Auth Module
 * Handles login, register, logout, token refresh, and profile loading.
 * Include this script on every Glow Guide page.
 */

const GlowAuth = (() => {
    'use strict';

    const API       = 'https://makuup-backend.onrender.com/api/glow-guide';
    const KEYS      = {
        access:  'gg_access_token',
        refresh: 'gg_refresh_token',
        user:    'gg_user',
    };

    // ── Token helpers ──────────────────────────────────────────────────────
    function getToken()    { return localStorage.getItem(KEYS.access) || ''; }
    function getRefresh()  { return localStorage.getItem(KEYS.refresh) || ''; }
    function getUser()     {
        try { return JSON.parse(localStorage.getItem(KEYS.user) || 'null'); }
        catch { return null; }
    }
    function isLoggedIn()  { return !!getToken() && !!getUser(); }

    function saveSession(data) {
        localStorage.setItem(KEYS.access,  data.access);
        localStorage.setItem(KEYS.refresh, data.refresh);
        localStorage.setItem(KEYS.user,    JSON.stringify(data.user));
    }

    function clearSession() {
        Object.values(KEYS).forEach(k => localStorage.removeItem(k));
    }

    // ── Authenticated fetch (auto-attaches Bearer token) ──────────────────
    async function authFetch(url, options = {}) {
        const token = getToken();
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        };
        let res = await fetch(url, { ...options, headers });

        // Token expired — try refresh
        if (res.status === 401 && getRefresh()) {
            const refreshed = await _refreshToken();
            if (refreshed) {
                headers['Authorization'] = `Bearer ${getToken()}`;
                res = await fetch(url, { ...options, headers });
            }
        }
        return res;
    }

    async function _refreshToken() {
        try {
            const res = await fetch(`${API}/token-refresh/`, {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ refresh: getRefresh() }),
            });
            if (!res.ok) { clearSession(); return false; }
            const data = await res.json();
            localStorage.setItem(KEYS.access, data.access);
            return true;
        } catch {
            return false;
        }
    }

    // ── Register ──────────────────────────────────────────────────────────
    async function register(name, email, password) {
        const res = await fetch(`${API}/register/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                name, email, password,
                session_id: localStorage.getItem('gg_session_id') || '',
            }),
        });
        const data = await res.json();
        if (res.ok && data.success) {
            saveSession(data);
            window.dispatchEvent(new CustomEvent('gg:login', { detail: data.user }));
            return { success: true, user: data.user };
        }
        const err = typeof data.error === 'object'
            ? Object.values(data.error).flat().join(' ')
            : (data.error || 'Registration failed.');
        return { success: false, error: err };
    }

    // ── Login ─────────────────────────────────────────────────────────────
    async function login(email, password) {
        const res = await fetch(`${API}/login/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                email, password,
                session_id: localStorage.getItem('gg_session_id') || '',
            }),
        });
        const data = await res.json();
        if (res.ok && data.success) {
            saveSession(data);
            window.dispatchEvent(new CustomEvent('gg:login', { detail: data.user }));
            return { success: true, user: data.user };
        }
        return { success: false, error: data.error || 'Login failed.' };
    }

    // ── Logout ────────────────────────────────────────────────────────────
    async function logout() {
        try {
            await authFetch(`${API}/logout/`, { method: 'POST' });
        } catch {}
        clearSession();
        window.dispatchEvent(new CustomEvent('gg:logout'));
        window.location.href = '/glow-guide/';
    }

    // ── Profile ───────────────────────────────────────────────────────────
    async function getProfile() {
        const res  = await authFetch(`${API}/profile/`);
        const data = await res.json();
        return data.success ? data : null;
    }

    // ── Modal control ─────────────────────────────────────────────────────
    function openModal(tab = 'login') {
        _ensureModal();
        const modal = document.getElementById('gg-auth-modal');
        if (!modal) return;
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
        _switchTab(tab);
    }

    function closeModal() {
        const modal = document.getElementById('gg-auth-modal');
        if (modal) modal.classList.remove('open');
        document.body.style.overflow = '';
    }

    function _switchTab(tab) {
        document.querySelectorAll('.gg-auth-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
        document.querySelectorAll('.gg-auth-panel').forEach(p => p.classList.toggle('active', p.dataset.panel === tab));
        _clearErrors();
    }

    function _clearErrors() {
        document.querySelectorAll('.gg-auth-error').forEach(el => { el.textContent = ''; el.style.display = 'none'; });
        document.querySelectorAll('.gg-auth-success').forEach(el => { el.textContent = ''; el.style.display = 'none'; });
    }

    // ── Inject modal HTML ─────────────────────────────────────────────────
    function _ensureModal() {
        if (document.getElementById('gg-auth-modal')) return;

        const modal = document.createElement('div');
        modal.id = 'gg-auth-modal';
        modal.innerHTML = `
        <div class="gg-auth-overlay" id="gg-auth-overlay"></div>
        <div class="gg-auth-box" role="dialog" aria-modal="true" aria-label="Glow Guide Account">

            <!-- Header -->
            <button class="gg-auth-close" id="gg-auth-close" aria-label="Close">✕</button>
            <div class="gg-auth-logo">✨</div>
            <h2 class="gg-auth-title">Glow Guide AI</h2>
            <p class="gg-auth-subtitle">Save your results &amp; access them anytime</p>

            <!-- Tabs -->
            <div class="gg-auth-tabs">
                <button class="gg-auth-tab active" data-tab="login">Sign In</button>
                <button class="gg-auth-tab" data-tab="register">Create Account</button>
            </div>

            <!-- Login Panel -->
            <div class="gg-auth-panel active" data-panel="login">
                <div class="gg-auth-error" id="login-error"></div>
                <div class="gg-auth-success" id="login-success"></div>
                <div class="gg-auth-field">
                    <label for="login-email">Email</label>
                    <input type="email" id="login-email" placeholder="your@email.com" autocomplete="email">
                </div>
                <div class="gg-auth-field">
                    <label for="login-password">Password</label>
                    <input type="password" id="login-password" placeholder="Your password" autocomplete="current-password">
                    <button type="button" class="gg-auth-eye" data-target="login-password">👁</button>
                </div>
                <button class="gg-auth-btn" id="login-submit">
                    <span class="gg-auth-btn-text">Sign In</span>
                    <span class="gg-auth-spinner" style="display:none">⏳</span>
                </button>
                <p class="gg-auth-switch">Don't have an account? <button type="button" data-tab="register">Create one</button></p>
            </div>

            <!-- Register Panel -->
            <div class="gg-auth-panel" data-panel="register">
                <div class="gg-auth-error" id="register-error"></div>
                <div class="gg-auth-success" id="register-success"></div>
                <div class="gg-auth-field">
                    <label for="reg-name">Full Name</label>
                    <input type="text" id="reg-name" placeholder="Your name" autocomplete="name">
                </div>
                <div class="gg-auth-field">
                    <label for="reg-email">Email</label>
                    <input type="email" id="reg-email" placeholder="your@email.com" autocomplete="email">
                </div>
                <div class="gg-auth-field">
                    <label for="reg-password">Password <span class="gg-auth-hint">(min 6 characters)</span></label>
                    <input type="password" id="reg-password" placeholder="Create a password" autocomplete="new-password">
                    <button type="button" class="gg-auth-eye" data-target="reg-password">👁</button>
                </div>
                <button class="gg-auth-btn" id="register-submit">
                    <span class="gg-auth-btn-text">Create Account</span>
                    <span class="gg-auth-spinner" style="display:none">⏳</span>
                </button>
                <p class="gg-auth-switch">Already have an account? <button type="button" data-tab="login">Sign in</button></p>
            </div>

            <!-- Guest note -->
            <p class="gg-auth-guest">
                <button type="button" id="gg-auth-skip">Continue as Guest →</button>
            </p>
        </div>`;

        document.body.appendChild(modal);
        _bindModalEvents(modal);
    }

    function _bindModalEvents(modal) {
        // Close
        modal.querySelector('#gg-auth-close').addEventListener('click', closeModal);
        modal.querySelector('#gg-auth-overlay').addEventListener('click', closeModal);
        modal.querySelector('#gg-auth-skip').addEventListener('click', closeModal);

        // Tabs
        modal.querySelectorAll('.gg-auth-tab, .gg-auth-switch button').forEach(btn => {
            btn.addEventListener('click', () => _switchTab(btn.dataset.tab));
        });

        // Show/hide password
        modal.querySelectorAll('.gg-auth-eye').forEach(btn => {
            btn.addEventListener('click', () => {
                const inp = document.getElementById(btn.dataset.target);
                inp.type = inp.type === 'password' ? 'text' : 'password';
            });
        });

        // Login submit
        modal.querySelector('#login-submit').addEventListener('click', async () => {
            const email    = document.getElementById('login-email').value.trim();
            const password = document.getElementById('login-password').value;
            const errEl    = document.getElementById('login-error');
            const btn      = modal.querySelector('#login-submit');

            if (!email || !password) { _showError(errEl, 'Please fill in all fields.'); return; }
            _setLoading(btn, true);
            const result = await login(email, password);
            _setLoading(btn, false);

            if (result.success) {
                _showSuccess(modal.querySelector('#login-success'), `Welcome back, ${result.user.name}! ✨`);
                setTimeout(() => { closeModal(); _updateNavAuth(); _showSaveToast(result.user.name); }, 1200);
            } else {
                _showError(errEl, result.error);
            }
        });

        // Enter key on login
        ['login-email','login-password'].forEach(id => {
            document.getElementById(id).addEventListener('keydown', e => {
                if (e.key === 'Enter') modal.querySelector('#login-submit').click();
            });
        });

        // Register submit
        modal.querySelector('#register-submit').addEventListener('click', async () => {
            const name     = document.getElementById('reg-name').value.trim();
            const email    = document.getElementById('reg-email').value.trim();
            const password = document.getElementById('reg-password').value;
            const errEl    = document.getElementById('register-error');
            const btn      = modal.querySelector('#register-submit');

            if (!name || !email || !password) { _showError(errEl, 'Please fill in all fields.'); return; }
            if (password.length < 6)           { _showError(errEl, 'Password must be at least 6 characters.'); return; }

            _setLoading(btn, true);
            const result = await register(name, email, password);
            _setLoading(btn, false);

            if (result.success) {
                _showSuccess(modal.querySelector('#register-success'), `Account created! Welcome, ${result.user.name} ✨`);
                setTimeout(() => { closeModal(); _updateNavAuth(); _showSaveToast(result.user.name); }, 1400);
            } else {
                _showError(errEl, result.error);
            }
        });

        // ESC key
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') closeModal();
        }, { once: false });
    }

    // ── Nav update after login ────────────────────────────────────────────
    function _updateNavAuth() {
        const container = document.getElementById('gg-auth-nav-slot');
        if (!container) return;
        const user = getUser();
        if (user) {
            container.innerHTML = `
            <div class="gg-nav-user-wrap">
                <button class="gg-nav-user-btn" id="gg-nav-user-btn">
                    <span class="gg-nav-avatar">${user.name.charAt(0).toUpperCase()}</span>
                    <span class="gg-nav-username">${user.name.split(' ')[0]}</span>
                    <span class="gg-nav-caret">▾</span>
                </button>
                <div class="gg-nav-dropdown" id="gg-nav-dropdown">
                    <a href="/glow-guide/profile/" class="gg-nav-dd-item">👤 My Profile</a>
                    <a href="/glow-guide/profile/" class="gg-nav-dd-item">📊 My Reports</a>
                    <button class="gg-nav-dd-item gg-nav-dd-logout" id="gg-nav-logout">🚪 Sign Out</button>
                </div>
            </div>`;

            document.getElementById('gg-nav-user-btn')?.addEventListener('click', (e) => {
                e.stopPropagation();
                document.getElementById('gg-nav-dropdown')?.classList.toggle('open');
            });
            document.getElementById('gg-nav-logout')?.addEventListener('click', () => logout());
            document.addEventListener('click', () => {
                document.getElementById('gg-nav-dropdown')?.classList.remove('open');
            });
        } else {
            container.innerHTML = `<button class="gg-nav-link gg-auth-trigger" id="gg-nav-login-btn">Sign In</button>`;
            document.getElementById('gg-nav-login-btn')?.addEventListener('click', () => openModal('login'));
        }
    }

    // ── Toast notification after login ────────────────────────────────────
    function _showSaveToast(name) {
        const toast = document.createElement('div');
        toast.className = 'gg-auth-toast';
        toast.innerHTML = `✨ Signed in as <strong>${name}</strong> — your beauty data is saved!`;
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add('visible'), 50);
        setTimeout(() => { toast.classList.remove('visible'); setTimeout(() => toast.remove(), 400); }, 4000);
    }

    function _showError(el, msg)   { if (!el) return; el.textContent = msg; el.style.display = 'block'; }
    function _showSuccess(el, msg) { if (!el) return; el.textContent = msg; el.style.display = 'block'; }
    function _setLoading(btn, on)  {
        btn.disabled = on;
        btn.querySelector('.gg-auth-btn-text').style.display = on ? 'none' : '';
        btn.querySelector('.gg-auth-spinner').style.display  = on ? 'inline' : 'none';
    }

    // ── Init (called on every Glow Guide page load) ───────────────────────
    function init() {
        // Inject nav slot + set state
        _updateNavAuth();

        // Bind any existing .gg-auth-trigger buttons on the page
        document.querySelectorAll('.gg-auth-trigger').forEach(btn => {
            btn.addEventListener('click', () => openModal(btn.dataset.tab || 'login'));
        });
    }

    // Public API
    return { init, openModal, closeModal, login, register, logout, getProfile, isLoggedIn, getUser, getToken, authFetch, _updateNavAuth };
})();

// Auto-init when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', GlowAuth.init);
} else {
    GlowAuth.init();
}
