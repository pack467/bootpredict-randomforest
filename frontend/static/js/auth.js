/**
 * Authentication Module
 * Handles login and registration form submissions.
 */

// API_BASE is defined in config.js

/**
 * Cookie Sync & Admin Link Visibility
 * Runs immediately on every page load to:
 * 1. Keep access_token cookie in sync with localStorage (for Jinja2 server-side auth)
 * 2. Show the admin nav link if the user is an admin
 */
(function syncAuthState() {
    const token = localStorage.getItem('token');
    if (token) {
        document.cookie = `access_token=${token}; path=/; max-age=86400; SameSite=Lax`;
    }

    // Show admin link in navbar (works on all pages)
    try {
        const user = JSON.parse(localStorage.getItem('user'));
        if (user && user.role === 'admin') {
            // Standalone pages use id="admin-link"
            const adminLink = document.getElementById('admin-link');
            if (adminLink) adminLink.style.display = 'block';
            // Jinja2 pages use id="nav-admin-link"
            const navAdminLink = document.getElementById('nav-admin-link');
            if (navAdminLink) navAdminLink.classList.remove('d-none');
        }
    } catch (e) { /* ignore parse errors */ }
})();

/**
 * Save auth token and user data to localStorage.
 */
function saveAuth(data) {
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    // Set cookie for Jinja2 templates (1 day expiry)
    document.cookie = `access_token=${data.access_token}; path=/; max-age=86400; SameSite=Lax`;
}

/**
 * Get the stored auth token.
 */
function getToken() {
    return localStorage.getItem('token');
}

/**
 * Get the stored user object.
 */
function getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

/**
 * Check if user is authenticated, redirect to login if not.
 */
function requireAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

/**
 * Check if the current user is an admin.
 */
function requireAdmin() {
    const user = getUser();
    if (!user || user.role !== 'admin') {
        window.location.href = '/dashboard';
        return false;
    }
    return true;
}

/**
 * Logout: clear stored data and redirect.
 */
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    // Clear cookie
    document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    window.location.href = '/login';
}

/**
 * Show an error message via toast notification.
 */
function showError(containerId, message) {
    if (window.AppUtil) {
        AppUtil.showToast('error', 'Error', message);
    } else {
        alert(message);
    }
}

/**
 * Show a success message via toast notification.
 */
function showSuccess(containerId, message) {
    if (window.AppUtil) {
        AppUtil.showToast('success', 'Berhasil', message);
    } else {
        alert(message);
    }
}

/**
 * Handle login form submission.
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const submitBtn = document.getElementById('btn-login');
    
    if (!username || !password) {
        showError('alert-container', 'Username dan password harus diisi');
        return;
    }
    
    // Show loading state
    submitBtn.disabled = true;
    if (window.AppUtil) AppUtil.showLoading('Memproses Login...');
    
    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Login gagal');
        }
        
        saveAuth(data);
        
        // Redirect based on role
        if (data.user.role === 'admin') {
            window.location.href = '/admin';
        } else {
            window.location.href = '/dashboard';
        }
        
    } catch (error) {
        showError('alert-container', error.message);
    } finally {
        if (window.AppUtil) AppUtil.hideLoading();
        submitBtn.disabled = false;
    }
}

/**
 * Handle registration form submission.
 */
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const submitBtn = document.getElementById('btn-register');
    
    if (!username || !password || !confirmPassword) {
        showError('alert-container', 'Semua field harus diisi');
        return;
    }
    
    if (password !== confirmPassword) {
        showError('alert-container', 'Password dan konfirmasi password tidak cocok');
        return;
    }
    
    if (username.length < 3) {
        showError('alert-container', 'Username minimal 3 karakter');
        return;
    }
    
    if (password.length < 4) {
        showError('alert-container', 'Password minimal 4 karakter');
        return;
    }
    
    submitBtn.disabled = true;
    if (window.AppUtil) AppUtil.showLoading('Mendaftarkan Akun...');
    
    try {
        const response = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Registrasi gagal');
        }
        
        saveAuth(data);
        window.location.href = '/dashboard';
        
    } catch (error) {
        showError('alert-container', error.message);
    } finally {
        if (window.AppUtil) AppUtil.hideLoading();
        submitBtn.disabled = false;
    }
}
