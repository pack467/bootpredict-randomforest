/**
 * Global Theme Manager
 * Handles switching between light and dark modes, persists state in localStorage
 */

const ThemeManager = {
    init() {
        this.themeToggleBtn = document.getElementById('theme-toggle');
        this.themeIcon = document.getElementById('theme-icon');
        
        // Load saved theme or system preference
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        this.currentTheme = savedTheme ? savedTheme : (systemPrefersDark ? 'dark' : 'light');
        
        this.applyTheme(this.currentTheme);
        
        if (this.themeToggleBtn) {
            this.themeToggleBtn.addEventListener('click', () => this.toggleTheme());
        }
    },

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
    },

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        if (this.themeIcon) {
            if (theme === 'dark') {
                this.themeIcon.className = 'bi bi-moon-stars-fill theme-icon';
                // Optional rotation effect
                this.themeIcon.style.transform = 'rotate(360deg)';
            } else {
                this.themeIcon.className = 'bi bi-sun-fill theme-icon';
                this.themeIcon.style.transform = 'rotate(0deg)';
            }
        }
    }
};

// Initialize theme as early as possible to prevent flash
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
});
