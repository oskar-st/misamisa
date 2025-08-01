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
        {
            trigger: '.third-level-item.has-children',
            dropdown: '.fourth-level-canvas',
            showClass: 'dropdown-show'
        },
        {
            trigger: '.fourth-level-item.has-children',
            dropdown: '.fifth-level-canvas',
            showClass: 'dropdown-show'
        }
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
                dropdown.addEventListener('mouseleave', startHideTimer);
                
                // Add event listeners to all child elements to prevent hiding
                const childElements = dropdown.querySelectorAll('*');
                childElements.forEach(child => {
                    child.removeEventListener('mouseenter', cancelHide);
                    child.removeEventListener('mouseleave', startHideTimer);
                    child.addEventListener('mouseenter', cancelHide);
                    child.addEventListener('mouseleave', startHideTimer);
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
    setTimeout(() => {
        if (typeof initializeDropdownThemeToggle === 'function') {
            initializeDropdownThemeToggle();
        }
    }, 50);
});

// Export for use in main.js
export { setupDropdownBehavior }; 