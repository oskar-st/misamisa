// Checkout page functionality

export function initialize() {
    console.log('Checkout page initialized');
    
    // Add checkout-page class to body for styling
    document.body.classList.add('checkout-page');
    
    // Respect the current global theme - don't override it
    // Listen for theme changes to ensure checkout stays in sync
    document.addEventListener('themeChanged', function(event) {
        console.log('Checkout page: Theme changed to', event.detail.theme);
        // The theme is already applied to document.documentElement by the theme toggle
        // No additional action needed - CSS variables will handle the styling
    });
    
    // Move checkout navigation to header inline with logo
    const headerInner = document.querySelector('.site-header .header-inner');
    const template = document.getElementById('checkout-nav-template');
    
    if (headerInner && template) {
        // Clone the checkout navigation
        const checkoutNav = template.querySelector('.checkout-progress').cloneNode(true);
        
        // Add the navigation to header
        headerInner.appendChild(checkoutNav);
        
        console.log('Checkout navigation added to header inline with logo');
    }
}

// Only initialize when called by main.js for checkout pages
// No auto-initialization to prevent running on all pages

// Handle HTMX reinitialization
document.addEventListener('htmx:reinitialize-checkout', function() {
    initialize();
});