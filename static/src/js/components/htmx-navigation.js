// HTMX Navigation and Configuration
// Handles smooth navigation, history management, and content verification

// Import notification functions
import { showLoginMessage, showLogoutMessage } from './notifications.js';

// Enhanced htmx initialization with debugging
function setupHtmxNavigation() {
    // Check if HTMX is available
    if (typeof htmx === 'undefined') {
        console.error('HTMX is not loaded!');
        return;
    }
    
    // Prevent multiple setups
    if (window.htmxNavigationSetup) {
        console.log('HTMX navigation already setup, skipping...');
        return;
    }
    
    console.log('Setting up HTMX navigation...');
    
    // Re-enable HTMX for sidebar category links (these are needed for shop functionality)
    const categoryLinks = document.querySelectorAll('.category-link');
    console.log('Found category links:', categoryLinks.length);
    
    categoryLinks.forEach((link, index) => {
        // Only add HTMX to internal links that don't already have complete HTMX setup
        if (link.href && link.href.startsWith(window.location.origin)) {
            // Check if link already has HTMX attributes
            const hasHtmx = link.hasAttribute('hx-get') && link.hasAttribute('hx-target');
            
            if (!hasHtmx) {
                // Only add HTMX to links that don't already have it
                link.setAttribute('hx-get', link.href);
                link.setAttribute('hx-target', '#main-content');
                link.setAttribute('hx-push-url', 'true');
                link.setAttribute('hx-swap', 'innerHTML');
                link.setAttribute('hx-indicator', '#loading-indicator');
                link.setAttribute('hx-preserve-scroll', 'true');
                console.log(`Added htmx to category link ${index + 1}:`, link.href);
            } else {
                console.log(`Category link ${index + 1} already has HTMX:`, link.href);
            }
            
            // Add click event listener to monitor clicks (only once)
            if (!link.hasAttribute('data-click-monitored')) {
                link.setAttribute('data-click-monitored', 'true');
                link.addEventListener('click', function(e) {
                    console.log('Category link clicked:', link.href);
                    console.log('HTMX attributes:', {
                        'hx-get': link.getAttribute('hx-get'),
                        'hx-target': link.getAttribute('hx-target'),
                        'hx-swap': link.getAttribute('hx-swap')
                    });
                });
            }
        }
    });
    
    // Disable HTMX for product links to prevent flickering
    // const productLinks = document.querySelectorAll('.product-link');
    // console.log('Found product links:', productLinks.length);
    
    // productLinks.forEach((link, index) => {
    //     // Only add HTMX to internal links
    //     if (link.href && link.href.startsWith(window.location.origin)) {
    //         const hasHtmx = link.hasAttribute('hx-get') && link.hasAttribute('hx-target');
            
    //         if (!hasHtmx) {
    //             link.setAttribute('hx-get', link.href);
    //             link.setAttribute('hx-target', '#main-content');
    //             link.setAttribute('hx-push-url', 'true');
    //             link.setAttribute('hx-swap', 'innerHTML');
    //             link.setAttribute('hx-indicator', '#loading-indicator');
    //             link.setAttribute('hx-preserve-scroll', 'true');
    //             console.log(`Added htmx to product link ${index + 1}:`, link.href);
    //         }
    //     }
    // });
    
    // Disable HTMX for pagination links to prevent flickering
    // const paginationLinks = document.querySelectorAll('.pagination-link');
    // console.log('Found pagination links:', paginationLinks.length);
    
    // paginationLinks.forEach((link, index) => {
    //     // Only add HTMX to internal links
    //     if (link.href && link.href.startsWith(window.location.origin)) {
    //         const hasHtmx = link.hasAttribute('hx-get') && link.hasAttribute('hx-target');
            
    //         if (!hasHtmx) {
    //             link.setAttribute('hx-get', link.href);
    //             link.setAttribute('hx-target', '#main-content');
    //             link.setAttribute('hx-push-url', 'true');
    //             link.setAttribute('hx-swap', 'innerHTML');
    //             link.setAttribute('hx-indicator', '#loading-indicator');
    //             link.setAttribute('hx-preserve-scroll', 'true');
    //             console.log(`Added htmx to pagination link ${index + 1}:`, link.href);
    //         }
    //     }
    // });
    
    // Disable HTMX for shop links to prevent flickering
    // const shopLinks = document.querySelectorAll('.shop-link');
    // console.log('Found shop links:', shopLinks.length);
    
    // shopLinks.forEach((link, index) => {
    //     // Only add HTMX to internal links and exclude cart/checkout
    //     if (link.href && link.href.startsWith(window.location.origin) && 
    //         !link.href.includes('/cart/') && !link.href.includes('/checkout/')) {
    //         const hasHtmx = link.hasAttribute('hx-get') && link.hasAttribute('hx-target');
            
    //         if (!hasHtmx) {
    //             link.setAttribute('hx-get', link.href);
    //             link.setAttribute('hx-target', '#main-content');
    //             link.setAttribute('hx-push-url', 'true');
    //             link.setAttribute('hx-swap', 'innerHTML');
    //             link.setAttribute('hx-indicator', '#loading-indicator');
    //             link.setAttribute('hx-preserve-scroll', 'true');
    //             console.log(`Added htmx to shop link ${index + 1}:`, link.href);
    //         }
    //     }
    // });
    
    window.htmxNavigationSetup = true;
    console.log('HTMX navigation setup completed - category links enabled, others disabled');
}

// Initialize when DOM is ready  
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing HTMX...');
    
    // Wait for HTMX to be fully loaded
    function initializeWhenHtmxReady() {
        if (typeof htmx !== 'undefined') {
            console.log('HTMX is ready, setting up navigation...');
            setupHtmxNavigation();
            
            // Reinitialize after a delay to catch any dynamically loaded content
            setTimeout(() => {
                setupHtmxNavigation();
                console.log('HTMX navigation initialized after timeout');
            }, 100);
            
            // Reinitialize after a longer delay for any late-loaded content
            setTimeout(() => {
                setupHtmxNavigation();
                console.log('HTMX navigation reinitialized after longer timeout');
            }, 500);
        } else {
            console.log('HTMX not ready yet, retrying...');
            setTimeout(initializeWhenHtmxReady, 50);
        }
    }
    
    initializeWhenHtmxReady();
    
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

// Enhanced error handling
// document.addEventListener('htmx:responseError', function(e) {
//     console.warn('HTMX failed, using normal navigation');
//     if (e.detail.elt && e.detail.elt.href) {
//         window.location.href = e.detail.elt.href;
//     }
// });

// Handle htmx request errors
// document.addEventListener('htmx:sendError', function(e) {
//     console.warn('HTMX send error, using normal navigation');
//     if (e.detail.elt && e.detail.elt.href) {
//         window.location.href = e.detail.elt.href;
//     }
// });

// Clear any unrelated messages during HTMX navigation
// document.addEventListener('htmx:beforeSwap', function(e) {
//     // If navigating to login/auth pages, clear any non-auth related messages
//     const newContent = e.detail.serverResponse;
//     const currentPath = window.location.pathname;
    
//     if (currentPath.includes('login') || currentPath.includes('register')) {
//         // Remove any existing message displays that don't belong on auth pages
//         const existingMessages = document.querySelectorAll('.messages .alert');
//         existingMessages.forEach(msg => {
//             const msgText = msg.textContent.toLowerCase();
//             // If message contains non-auth terms, remove it
//             if (msgText.includes('invoice') || msgText.includes('address') || 
//                 msgText.includes('deleted') || msgText.includes('shipping') ||
//                 msgText.includes('details for')) {
//                 msg.style.display = 'none';
//             }
//         });
//     }
// });

// Configure HTMX requests and debug
// document.addEventListener('htmx:configRequest', function(e) {
//     console.log('HTMX request config:', e.detail);
    
//     // Add cache control headers to prevent browser caching of partial responses
//     e.detail.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
//     e.detail.headers['Pragma'] = 'no-cache';
//     e.detail.headers['Expires'] = '0';
    
//     // Add CSRF token if available
//     const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
//     if (csrfToken) {
//         e.detail.headers['X-CSRFToken'] = csrfToken;
//     }
// });

// Enhanced HTMX event handlers for better state management
// document.addEventListener('htmx:beforeSwap', function(evt) {
//     // Preserve scroll position and view state
//     const scrollPos = window.scrollY;
//     const viewState = document.getElementById('product-list-container')?.getAttribute('data-view');
//     const currentView = window.shopViewState?.currentView || localStorage.getItem('shop-view-preference') || 'grid';
    
//     evt.detail.xhr.setRequestHeader('X-Scroll-Position', scrollPos);
//     if (viewState) {
//         evt.detail.xhr.setRequestHeader('X-View-State', viewState);
//     }
//     if (currentView && currentView !== 'grid') {
//         evt.detail.xhr.setRequestHeader('X-Current-View', currentView);
//     }
    
//     // Add view state to URL parameters for pagination links
//     if (currentView && currentView !== 'grid') {
//         // Update pagination links to include view parameter
//         const paginationLinks = document.querySelectorAll('.pagination-link');
//         paginationLinks.forEach(link => {
//             if (link.href) {
//                 const url = new URL(link.href);
//                 url.searchParams.set('view', currentView);
//                 link.href = url.toString();
//             }
//         });
//     }
// });

// Smooth transitions with theme preservation
document.addEventListener('htmx:beforeSwap', function(e) {
    console.log('HTMX beforeSwap triggered');
    
    // Reset HTMX setup flag to allow reinitialization after content swap
    window.htmxNavigationSetup = false;
    
    // Remove all visual changes to prevent flickering
    // const mainContent = document.getElementById('main-content');
    // if (mainContent) {
    //     mainContent.classList.add('htmx-swapping');
    // }
});

document.addEventListener('htmx:afterSwap', function(evt) {
    console.log('HTMX afterSwap triggered');
    
    // Restore scroll position if provided
    const scrollPos = evt.detail.xhr.getResponseHeader('X-Scroll-Position');
    if (scrollPos) {
        window.scrollTo(0, parseInt(scrollPos));
    }
    
    // Handle logout success
    if (evt.detail.target.id === 'user-menu-dropdown') {
        console.log('User menu updated after logout');
        showLogoutMessage();
    }
    
    // Remove all visual changes to prevent flickering
    // const mainContent = document.getElementById('main-content');
    // if (mainContent) {
    //     mainContent.classList.remove('htmx-swapping');
    // }
    
    console.log('HTMX swap completed, reinitializing...');
    
    // Reinitialize HTMX navigation
    setupHtmxNavigation();
    
    // Reinitialize shop functionality if we're on a shop page
    if (document.querySelector('.shop-page') || document.querySelector('#product-list-container')) {
        console.log('Shop page detected, reinitializing shop functionality...');
        if (window.reinitializeShopAfterHtmx) {
            window.reinitializeShopAfterHtmx();
        } else if (window.initializeShop) {
            // Fallback to regular initialization
            window.initializeShop();
        }
    }
    
    console.log('Content swapped, all functionality reinitialized');
});

// Export for use in main.js
export { setupHtmxNavigation }; 