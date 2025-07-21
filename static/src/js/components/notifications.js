// Notification system for login/logout messages
function showLoginMessage() {
    // Create a temporary notification for login success
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: absolute;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #28a745;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        font-weight: 500;
        opacity: 0;
        transition: opacity 0.3s ease;
        max-width: 400px;
        text-align: center;
    `;
    notification.textContent = 'Logged in successfully!';
    
    // Append to main content container instead of body
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        // Make main-content relative if not already
        if (getComputedStyle(mainContent).position === 'static') {
            mainContent.style.position = 'relative';
        }
        mainContent.appendChild(notification);
    } else {
        document.body.appendChild(notification);
    }
    
    // Show notification
    setTimeout(() => notification.style.opacity = '1', 100);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function showLogoutMessage() {
    // Clear cart display from header
    const cartBadge = document.querySelector('.cart-badge');
    if (cartBadge) {
        cartBadge.textContent = '0';
        cartBadge.style.display = 'none';
    }
    
    const cartTotal = document.querySelector('.cart-total');
    if (cartTotal) {
        cartTotal.textContent = '0.00 zł';
    }
    
    // If user is on cart page, refresh it to show empty cart
    if (window.location.pathname === '/cart/' || window.location.pathname.includes('/cart/')) {
        // Use HTMX to refresh the cart page content
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            htmx.ajax('GET', '/cart/', {
                target: '#main-content',
                swap: 'innerHTML'
            });
        }
    }
    
    // Create a temporary notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: absolute;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #dc3545;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        font-weight: 500;
        opacity: 0;
        transition: opacity 0.3s ease;
        max-width: 400px;
        text-align: center;
    `;
    notification.textContent = 'Logged out successfully!';
    
    // Append to main content container instead of body
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        // Make main-content relative if not already
        if (getComputedStyle(mainContent).position === 'static') {
            mainContent.style.position = 'relative';
        }
        mainContent.appendChild(notification);
    } else {
        document.body.appendChild(notification);
    }
    
    // Show notification
    setTimeout(() => notification.style.opacity = '1', 100);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Export for use in main.js
export { showLoginMessage, showLogoutMessage }; 