// HTMX Navigation and Configuration
// Handles smooth navigation, history management, and content verification

// Enhanced htmx initialization with debugging
function setupHtmxNavigation() {
    // Add htmx to category navigation links
    const categoryLinks = document.querySelectorAll('.category-link:not([hx-get])');
    console.log('Found category links:', categoryLinks.length);
    
    categoryLinks.forEach((link, index) => {
        link.setAttribute('hx-get', link.href);
        link.setAttribute('hx-target', '#main-content');
        link.setAttribute('hx-push-url', 'true');
        link.setAttribute('hx-swap', 'innerHTML');
        link.setAttribute('hx-indicator', '#loading-indicator');
        console.log(`Added htmx to category link ${index + 1}:`, link.href);
    });
    
    // Add htmx to product links (for smooth product browsing)
    const productLinks = document.querySelectorAll('.product-link:not([hx-get])');
    console.log('Found product links:', productLinks.length);
    
    productLinks.forEach((link, index) => {
        link.setAttribute('hx-get', link.href);
        link.setAttribute('hx-target', '#main-content');
        link.setAttribute('hx-push-url', 'true');
        link.setAttribute('hx-swap', 'innerHTML');
        link.setAttribute('hx-indicator', '#loading-indicator');
        console.log(`Added htmx to product link ${index + 1}:`, link.href);
    });
    
    // Add htmx to pagination links
    const paginationLinks = document.querySelectorAll('.pagination a:not([hx-get])');
    console.log('Found pagination links:', paginationLinks.length);
    
    paginationLinks.forEach((link, index) => {
        link.setAttribute('hx-get', link.href);
        link.setAttribute('hx-target', '#main-content');
        link.setAttribute('hx-push-url', 'true');
        link.setAttribute('hx-swap', 'innerHTML');
        link.setAttribute('hx-indicator', '#loading-indicator');
        console.log(`Added htmx to pagination link ${index + 1}:`, link.href);
    });
    
    // Add htmx to general shop navigation links (cart, login, etc.)
    const shopLinks = document.querySelectorAll('.shop-link:not([hx-get])');
    console.log('Found shop links:', shopLinks.length);
    
    shopLinks.forEach((link, index) => {
        link.setAttribute('hx-get', link.href);
        link.setAttribute('hx-target', '#main-content');
        link.setAttribute('hx-push-url', 'true');
        link.setAttribute('hx-swap', 'innerHTML');
        link.setAttribute('hx-indicator', '#loading-indicator');
        console.log(`Added htmx to shop link ${index + 1}:`, link.href);
    });
    
    // Add htmx to breadcrumb links
    const breadcrumbLinks = document.querySelectorAll('.breadcrumb a:not([hx-get])');
    console.log('Found breadcrumb links:', breadcrumbLinks.length);
    
    breadcrumbLinks.forEach((link, index) => {
        link.setAttribute('hx-get', link.href);
        link.setAttribute('hx-target', '#main-content');
        link.setAttribute('hx-push-url', 'true');
        link.setAttribute('hx-swap', 'innerHTML');
        link.setAttribute('hx-indicator', '#loading-indicator');
        console.log(`Added htmx to breadcrumb link ${index + 1}:`, link.href);
    });
    
    // Process htmx attributes
    htmx.process(document.body);
    console.log('HTMX processed all new attributes');
}

// Initialize when DOM is ready  
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        setupHtmxNavigation();
        console.log('HTMX navigation initialized after timeout');
    }, 100);
    
    // Check for login success notification
    const showLoginSuccess = document.body.getAttribute('data-show-login');
    if (showLoginSuccess === 'true') {
        showLoginMessage();
    }
    
    // Handle user menu dropdown visibility
    const userMenuTrigger = document.querySelector('.user-menu-trigger');
    const userMenuDropdown = document.querySelector('.user-menu-dropdown');
    
    if (userMenuTrigger && userMenuDropdown) {
        userMenuTrigger.addEventListener('click', function() {
            setTimeout(() => {
                setupHtmxNavigation();
                console.log('HTMX reinitialized after user menu opened');
            }, 50);
        });
    }
});

// Smooth transitions with theme preservation
document.addEventListener('htmx:beforeSwap', function(e) {
    const mainContent = document.getElementById('main-content');
    mainContent.classList.add('htmx-swapping');
    mainContent.style.opacity = '0.7';
});

document.addEventListener('htmx:afterSwap', function(e) {
    // Handle logout success
    if (e.target.id === 'user-menu-dropdown') {
        console.log('User menu updated after logout');
        showLogoutMessage();
        return;
    }
    
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        mainContent.style.opacity = '1';
        
        // Remove swapping class after transition
        setTimeout(() => {
            mainContent.classList.remove('htmx-swapping');
        }, 200);
    }
    
    console.log('HTMX swap completed, reinitializing...');
    
    // Reinitialize htmx for new content
    setTimeout(() => {
        setupHtmxNavigation();
        
        // Reinitialize shop functionality  
        if (typeof initializeShopFunctionality === 'function') {
            initializeShopFunctionality();
            console.log('Shop functionality reinitialized');
        }
        
        console.log('Content swapped, all functionality reinitialized');
    }, 50);
});

// Enhanced error handling
document.addEventListener('htmx:responseError', function(e) {
    console.warn('HTMX failed, using normal navigation');
    if (e.detail.elt && e.detail.elt.href) {
        window.location.href = e.detail.elt.href;
    }
});

// Handle htmx request errors
document.addEventListener('htmx:sendError', function(e) {
    console.warn('HTMX send error, using normal navigation');
    if (e.detail.elt && e.detail.elt.href) {
        window.location.href = e.detail.elt.href;
    }
});

// Clear any unrelated messages during HTMX navigation
document.addEventListener('htmx:beforeSwap', function(e) {
    // If navigating to login/auth pages, clear any non-auth related messages
    const newContent = e.detail.serverResponse;
    const currentPath = window.location.pathname;
    
    if (currentPath.includes('login') || currentPath.includes('register')) {
        // Remove any existing message displays that don't belong on auth pages
        const existingMessages = document.querySelectorAll('.messages .alert');
        existingMessages.forEach(msg => {
            const msgText = msg.textContent.toLowerCase();
            // If message contains non-auth terms, remove it
            if (msgText.includes('invoice') || msgText.includes('address') || 
                msgText.includes('deleted') || msgText.includes('shipping') ||
                msgText.includes('details for')) {
                msg.style.display = 'none';
            }
        });
    }
});

// Configure HTMX requests and debug
document.addEventListener('htmx:configRequest', function(e) {
    console.log('HTMX request config:', e.detail);
    
    // Add cache control headers to prevent browser caching of partial responses
    e.detail.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
    e.detail.headers['Pragma'] = 'no-cache';
    e.detail.headers['Expires'] = '0';
});

// Prevent HTMX from restoring partial content from history
document.addEventListener('htmx:beforeHistoryRestore', function(e) {
    console.log('Preventing HTMX history restore, using full page reload instead');
    e.preventDefault();
    
    // Immediately hide content to prevent flash
    document.body.classList.add('checking-content');
    document.body.classList.remove('content-verified');
    window.location.reload();
});

// Handle browser back/forward button properly
let isNavigating = false;
window.addEventListener('popstate', function(e) {
    console.log('Browser back/forward detected');
    
    if (isNavigating) return;
    isNavigating = true;
    
    // Immediately hide content to prevent flash
    document.body.classList.add('checking-content');
    document.body.classList.remove('content-verified');
    
    // Always do a full page reload for back/forward navigation
    window.location.reload();
});

// Immediate detection and prevention of double content
(function() {
    // Start with hidden content to prevent flash
    document.body.classList.add('checking-content');
    
    function verifyContent() {
        const headers = document.querySelectorAll('header');
        const footers = document.querySelectorAll('footer');
        
        if (headers.length > 1 || footers.length > 1) {
            console.warn('Double content detected, reloading immediately');
            window.location.reload();
            return false;
        }
        
        // Content is verified as correct, show it
        document.body.classList.remove('checking-content');
        document.body.classList.add('content-verified');
        return true;
    }
    
    // Check immediately when script executes
    if (!verifyContent()) {
        return;
    }
    
    // Also check when DOM is fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        if (!verifyContent()) {
            return;
        }
    });
    
    // Check after any potential DOM changes
    if (window.MutationObserver) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Check for double content after DOM changes
                    setTimeout(verifyContent, 10);
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
})();

// Intercept HTMX history saves to prevent storing partial content
document.addEventListener('htmx:pushedIntoHistory', function(e) {
    console.log('HTMX pushed to history:', e.detail.path);
    
    // Replace the HTMX history entry with a marker that will trigger full reload
    const currentState = history.state || {};
    const newState = {
        ...currentState,
        htmxFullReload: true,
        path: e.detail.path
    };
    
    history.replaceState(newState, '', e.detail.path);
});

// Disable HTMX history for specific problematic pages
document.addEventListener('htmx:beforeRequest', function(e) {
    const targetPath = e.detail.pathInfo.requestPath;
    
    // For cart and profile pages, disable history to prevent caching issues
    if (targetPath.includes('/cart/') || targetPath.includes('/profile/')) {
        console.log('Disabling HTMX history for:', targetPath);
        e.detail.xhr.setRequestHeader('HX-History', 'false');
    }
});

// Export for use in main.js
export { setupHtmxNavigation }; 