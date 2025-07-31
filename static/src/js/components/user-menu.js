// User menu functionality and theme toggle integration
function initializeDropdownThemeToggle() {
    const dropdownThemeToggle = document.getElementById('theme-toggle-dropdown');
    if (dropdownThemeToggle) {
        // Remove existing listener to prevent duplicates
        dropdownThemeToggle.removeEventListener('click', handleDropdownThemeToggle);
        dropdownThemeToggle.addEventListener('click', handleDropdownThemeToggle);
    }
}

function handleDropdownThemeToggle(e) {
    e.preventDefault();
    e.stopPropagation();
    
    const docElement = document.documentElement;
    const currentTheme = docElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    docElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update the main theme toggle button state if it exists
    const mainThemeToggle = document.getElementById('theme-toggle');
    if (mainThemeToggle) {
        if (newTheme === 'dark') {
            mainThemeToggle.classList.add('active');
        } else {
            mainThemeToggle.classList.remove('active');
        }
    }
    
    // Update the dropdown theme toggle text
    const dropdownToggleSpan = e.target.querySelector('span');
    if (dropdownToggleSpan) {
        dropdownToggleSpan.textContent = newTheme === 'dark' ? 'Tryb jasny' : 'Tryb ciemny';
    }
    
    // Update the dropdown theme toggle icon
    const dropdownToggleIcon = e.target.querySelector('svg path');
    if (dropdownToggleIcon) {
        if (newTheme === 'dark') {
            // Sun icon for light mode
            dropdownToggleIcon.setAttribute('d', 'M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42M12 6a6 6 0 0 0 0 12a6 6 0 0 0 0-12z');
        } else {
            // Moon icon for dark mode
            dropdownToggleIcon.setAttribute('d', 'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z');
        }
    }
}

// Initialize user menu functionality
function initializeUserMenu() {
    // Initialize dropdown theme toggle
    initializeDropdownThemeToggle();
    
    // Add any other user menu initialization here
    console.log('User menu initialized');
}

// Initialize dropdown theme toggle on page load
document.addEventListener('DOMContentLoaded', initializeDropdownThemeToggle);

// Export for use in main.js
export { initializeDropdownThemeToggle, handleDropdownThemeToggle, initializeUserMenu }; 