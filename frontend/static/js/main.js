/**
 * Main Applicaton Utilities
 * Handles toasts, loading overlays, and generic UI functions.
 */

const AppUtil = {
    /**
     * Show a custom toast notification.
     * @param {string} type - 'success', 'error', 'warning'
     * @param {string} title - The title of the toast
     * @param {string} message - The message body
     */
    showToast(type, title, message) {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const icons = {
            'success': 'bi-check-circle-fill',
            'error': 'bi-x-circle-fill',
            'warning': 'bi-exclamation-triangle-fill'
        };

        const toast = document.createElement('div');
        toast.className = `toast-custom ${type}`;
        
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="bi ${icons[type]}"></i>
            </div>
            <div class="toast-content">
                <div class="fw-bold mb-1" style="font-size: 0.9rem;">${title}</div>
                <div class="text-muted-custom" style="font-size: 0.8rem; line-height: 1.3;">${message}</div>
            </div>
        `;

        container.appendChild(toast);

        // Trigger animation
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                toast.classList.add('show');
            });
        });

        // Auto remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300); // Wait for transition
        }, 4000);
    },

    /**
     * Show the global fullscreen loading overlay
     * @param {string} text - The loading text to show (e.g., 'Memproses...')
     */
    showLoading(text = 'Loading...') {
        let overlay = document.getElementById('global-loading');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'global-loading';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner"></div>
                <div class="loading-text" id="loading-text-elem">${text}</div>
            `;
            document.body.appendChild(overlay);
        } else {
            document.getElementById('loading-text-elem').textContent = text;
        }
        
        // Small delay to ensure render
        setTimeout(() => {
            overlay.classList.add('active');
        }, 10);
    },

    /**
     * Hide the global loading overlay
     */
    hideLoading() {
        const overlay = document.getElementById('global-loading');
        if (overlay) {
            overlay.classList.remove('active');
        }
    },

    /**
     * Set the current year in the footer
     */
    setFooterYear() {
        const span = document.getElementById('current-year');
        if (span) span.textContent = new Date().getFullYear();
    },

    /**
     * Toggle password visibility for an input
     */
    togglePassword(inputId, iconId) {
        const input = document.getElementById(inputId);
        const icon = document.getElementById(iconId);
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.replace('bi-eye', 'bi-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.replace('bi-eye-slash', 'bi-eye');
        }
    }
};

// Initialize common features
document.addEventListener('DOMContentLoaded', () => {
    AppUtil.setFooterYear();
});
