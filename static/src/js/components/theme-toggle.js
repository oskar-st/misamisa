// Theme toggle logic for dark/light mode
export function initializeThemeToggle() {
    const html = document.documentElement;
    const toggleBtn = document.getElementById('theme-toggle');
    if (!toggleBtn) return;

    // Get saved theme or system preference
    function getPreferredTheme() {
        const stored = localStorage.getItem('theme');
        if (stored === 'dark' || stored === 'light') return stored;
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    // Set theme and update UI
    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Dispatch a custom event so other theme toggles can listen and update
        document.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: theme } 
        }));
        
        // Optionally update toggle UI (icon, etc.)
        if (toggleBtn) {
            toggleBtn.setAttribute('aria-pressed', theme === 'dark');
            // Add or remove the .active class for animation
            if (theme === 'dark') {
                toggleBtn.classList.add('active');
            } else {
                toggleBtn.classList.remove('active');
            }
        }
    }

    // Toggle theme
    function toggleTheme() {
        const current = html.getAttribute('data-theme') || getPreferredTheme();
        const next = current === 'dark' ? 'light' : 'dark';
        setTheme(next);
        
        // Force synchronization after a short delay
        setTimeout(() => {
            if (typeof window.forceThemeSync === 'function') {
                window.forceThemeSync();
            }
        }, 50);
    }

    // Initialize
    setTheme(getPreferredTheme());
    toggleBtn.addEventListener('click', toggleTheme);
}

// For main.js compatibility (if not using ES modules)
if (typeof window !== 'undefined') {
    window.initializeThemeToggle = initializeThemeToggle;
} 