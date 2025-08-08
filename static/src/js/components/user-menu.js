// User menu functionality and theme toggle integration
function initializeDropdownThemeToggle() {
    const dropdownThemeToggle = document.getElementById('theme-toggle-dropdown');
    if (dropdownThemeToggle) {
        // Remove existing listener to prevent duplicates
        dropdownThemeToggle.removeEventListener('click', handleDropdownThemeToggle);
        dropdownThemeToggle.addEventListener('click', handleDropdownThemeToggle);
        
        // Set initial icon, text and toggle state (like Twitch)
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const dropdownToggleSvg = dropdownThemeToggle.querySelector('svg');
        const dropdownToggleSpan = dropdownThemeToggle.querySelector('span');
        
        // Always show moon icon for "Dark Theme"
        if (dropdownToggleSvg) {
            dropdownToggleSvg.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
        }
        
        // Always show "Ciemny motyw" text
        if (dropdownToggleSpan) {
            dropdownToggleSpan.textContent = 'Ciemny motyw';
        }
        
        // Set toggle state based on current theme
        if (currentTheme === 'dark') {
            dropdownThemeToggle.classList.add('active');
        } else {
            dropdownThemeToggle.classList.remove('active');
        }
    }
}

function handleDropdownThemeToggle(e) {
    e.preventDefault();
    e.stopPropagation();
    
    // Keep dropdown open during theme switch
    const dropdown = document.querySelector('.user-menu');
    const wasOpen = dropdown && dropdown.classList.contains('dropdown-show');
    
    const docElement = document.documentElement;
    const currentTheme = docElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    docElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Dispatch a custom event so other theme toggles can listen and update
    document.dispatchEvent(new CustomEvent('themeChanged', { 
        detail: { theme: newTheme } 
    }));
    
    // Update the main theme toggle button state if it exists
    const mainThemeToggle = document.getElementById('theme-toggle');
    if (mainThemeToggle) {
        if (newTheme === 'dark') {
            mainThemeToggle.classList.add('active');
        } else {
            mainThemeToggle.classList.remove('active');
        }
        // Also trigger the main theme toggle's update function if it exists
        if (typeof window.updateMainThemeToggle === 'function') {
            window.updateMainThemeToggle(newTheme);
        }
    }
    
    // Keep text and icon the same (like Twitch - only toggle state changes)
    const dropdownToggleSpan = e.target.querySelector('span');
    if (dropdownToggleSpan) {
        dropdownToggleSpan.textContent = 'Ciemny motyw';
    }
    
    // Always keep moon icon (like Twitch)
    const dropdownToggleSvg = e.target.querySelector('svg');
    if (dropdownToggleSvg) {
        dropdownToggleSvg.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
    }
    
    // Update toggle state based on new theme
    const dropdownThemeToggle = document.getElementById('theme-toggle-dropdown');
    if (dropdownThemeToggle) {
        if (newTheme === 'dark') {
            dropdownThemeToggle.classList.add('active');
        } else {
            dropdownThemeToggle.classList.remove('active');
        }
    }
    
    // Ensure dropdown stays open after theme switch
    if (wasOpen && dropdown) {
        // Use a small timeout to ensure the dropdown doesn't close
        setTimeout(() => {
            dropdown.classList.add('dropdown-show');
        }, 10);
    }
}

// Listen for theme changes from other sources
function updateDropdownOnThemeChange(event) {
    const newTheme = event.detail.theme;
    console.log('Dropdown updating to theme:', newTheme); // Debug log
    const dropdownThemeToggle = document.getElementById('theme-toggle-dropdown');
    
    if (dropdownThemeToggle) {
        const dropdownToggleSvg = dropdownThemeToggle.querySelector('svg');
        const dropdownToggleSpan = dropdownThemeToggle.querySelector('span');
        
        // Keep icon and text the same (like Twitch)
        if (dropdownToggleSvg) {
            dropdownToggleSvg.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
        }
        
        // Always keep same text
        if (dropdownToggleSpan) {
            dropdownToggleSpan.textContent = 'Ciemny motyw';
        }
        
        // Update toggle state based on theme
        if (newTheme === 'dark') {
            dropdownThemeToggle.classList.add('active');
        } else {
            dropdownThemeToggle.classList.remove('active');
        }
    }
}

// Force synchronization on any theme change
function forceThemeSync() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const dropdownThemeToggle = document.getElementById('theme-toggle-dropdown');
    
    if (dropdownThemeToggle) {
        console.log('Force syncing dropdown to theme:', currentTheme); // Debug log
        if (currentTheme === 'dark') {
            dropdownThemeToggle.classList.add('active');
        } else {
            dropdownThemeToggle.classList.remove('active');
        }
    }
}

// Initialize user menu functionality
function initializeUserMenu() {
    // Initialize dropdown theme toggle
    initializeDropdownThemeToggle();
    
    // Listen for theme changes from other sources
    document.addEventListener('themeChanged', updateDropdownOnThemeChange);
    
    // Force sync on page interactions that might cause state drift
    document.addEventListener('click', forceThemeSync);
    document.addEventListener('htmx:afterSwap', forceThemeSync);
    
    // Add any other user menu initialization here
}

// Remove DOMContentLoaded listener to prevent duplicate initialization
// This will be handled by main.js instead

// Export for use in main.js
export { initializeDropdownThemeToggle, handleDropdownThemeToggle, initializeUserMenu, forceThemeSync }; 