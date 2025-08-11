// Enhanced Dropdown Management with better nested dropdown support
import { initializeDropdownThemeToggle } from './user-menu.js';

function setupDropdownBehavior() {
    const dropdownItems = [
        {
            trigger: '.user-menu',
            dropdown: '.user-menu-dropdown',
            showClass: 'dropdown-show'
        },
        {
            trigger: '.category-menu-item.has-dropdown',
            dropdown: '.category-dropdown',
            showClass: 'dropdown-show'
        },
        {
            trigger: '.subcategory-item.has-children',
            dropdown: '.subcategory-canvas',
            showClass: 'dropdown-show'
        },
        // Removed 4th and 5th level dropdowns for better UX and accessibility
        // Navigation now supports maximum 3 levels for optimal user experience
    ];

    // Store all active timers globally to prevent conflicts
    const activeTimers = new Map();

    dropdownItems.forEach(config => {
        const triggers = document.querySelectorAll(config.trigger);
        
        triggers.forEach(trigger => {
            const timerId = `${config.showClass}-${Array.from(triggers).indexOf(trigger)}`;
            
            function showDropdown() {
                // Clear any existing timer for this dropdown
                if (activeTimers.has(timerId)) {
                    clearTimeout(activeTimers.get(timerId));
                    activeTimers.delete(timerId);
                }

                // Close ALL other open dropdowns before opening this one
                document.querySelectorAll('.dropdown-show').forEach(el => {
                    if (el !== trigger && !trigger.contains(el) && !el.contains(trigger)) {
                        el.classList.remove('dropdown-show');
                    }
                });

                // Now open the current dropdown
                trigger.classList.add(config.showClass);
            }
            
            function startHideTimer() {
                // Clear any existing timer first
                if (activeTimers.has(timerId)) {
                    clearTimeout(activeTimers.get(timerId));
                }
                
                const timeout = setTimeout(() => {
                    trigger.classList.remove(config.showClass);
                    activeTimers.delete(timerId);
                }, 300); // 300ms delay
                
                activeTimers.set(timerId, timeout);
            }
            
            function cancelHide() {
                if (activeTimers.has(timerId)) {
                    clearTimeout(activeTimers.get(timerId));
                    activeTimers.delete(timerId);
                }
            }
            
            // Remove any existing event listeners to prevent duplicates
            trigger.removeEventListener('mouseenter', showDropdown);
            trigger.removeEventListener('mouseleave', startHideTimer);
            
            // Add event listeners
            trigger.addEventListener('mouseenter', showDropdown);
            trigger.addEventListener('mouseleave', startHideTimer);
            
            // Keep dropdown open when hovering over the dropdown itself
            const dropdown = trigger.querySelector(config.dropdown);
            if (dropdown) {
                // Remove existing listeners first
                dropdown.removeEventListener('mouseenter', cancelHide);
                dropdown.removeEventListener('mouseleave', startHideTimer);
                
                // Add new listeners
                dropdown.addEventListener('mouseenter', cancelHide);
                dropdown.addEventListener('mouseleave', (e) => {
                    // Only hide if we're actually leaving the dropdown area
                    // Check if the mouse is moving to a related target that's still within the dropdown
                    if (!dropdown.contains(e.relatedTarget)) {
                        startHideTimer();
                    }
                });
                
                // Add event listeners to important child elements, but exclude theme toggle elements
                const childElements = dropdown.querySelectorAll('*:not(.theme-toggle-switch):not(.theme-toggle-track):not(.theme-toggle-thumb)');
                childElements.forEach(child => {
                    child.removeEventListener('mouseenter', cancelHide);
                    child.addEventListener('mouseenter', cancelHide);
                    // Don't add mouseleave listeners to child elements to prevent premature hiding
                });
            }
        });
    });
}

// Initialize dropdown behavior
document.addEventListener('DOMContentLoaded', setupDropdownBehavior);

// Reinitialize after HTMX swaps
document.addEventListener('htmx:afterSwap', function() {
    setTimeout(setupDropdownBehavior, 50);
    // Remove dropdown theme toggle initialization from here
    // It's handled in main.js to prevent duplicates
});

// Export for use in main.js
export { setupDropdownBehavior }; 