// Main JavaScript entry point for frontend
// Centralized initialization system with dynamic loading

// --- Import main SCSS for Vite ---
import '../scss/main.scss';  // <-- add this at the top

// Import core components
import { HTMXManager } from './components/htmx-manager.js';
import { initializeDropdowns } from './components/dropdown.js';
import { initializeTabs } from './components/tabs.js';
import { initializeForms } from './components/forms.js';
import { initializeThemeToggle } from './components/theme-toggle.js';
import { initializeUserMenu, forceThemeSync } from './components/user-menu.js';
import CartManager from './components/cart-manager.js';
import './components/dropdown-management.js';
import './components/notifications.js';

// Import page-specific functionality
import { initializeShop } from './pages/shop.js';
import { initialize as initializeCheckout } from './pages/checkout.js';

// Page initializers map for dynamic loading
const pageInitializers = {
  'shop-page': () => initializeShop(),
  'admin-page': () => import('./admin/productimage_single_primary.js').then(m => m.initializeAdmin?.()),
  'home-page': () => { console.log('Home page initialized'); },
  'products-page': () => { console.log('Products page initialized'); },
  'contact-page': () => { console.log('Contact page initialized'); },
  'checkout-page': () => initializeCheckout(),
};

// Global HTMX manager instance
let htmxManager;
let cartManager;

// Initialize frontend functionality
document.addEventListener('DOMContentLoaded', function() {
  // Initialize HTMX manager first
  htmxManager = new HTMXManager();
  
  // Initialize cart manager
  cartManager = new CartManager();
  
  // Export for global access
  window.htmxManager = htmxManager;
  window.cartManager = cartManager;
  
  // Initialize core components
  initializeDropdowns();
  initializeTabs();
  initializeForms();
  initializeThemeToggle();
  initializeUserMenu();
  
  // Export sync function to window for cross-component access
  window.forceThemeSync = forceThemeSync;
  
  // Initialize page-specific functionality dynamically
  initializePageComponents();
  
  // Set up HTMX reinitialization handlers
  setupReinitializationHandlers();
});

// Initialize page-specific components based on page class
function initializePageComponents() {
  for (const [pageClass, initializer] of Object.entries(pageInitializers)) {
    if (document.querySelector(`.${pageClass}`) || 
        (pageClass === 'shop-page' && document.querySelector('#product-list-container')) ||
        (pageClass === 'admin-page' && document.querySelector('input[name$="-is_primary"]'))) {
      try {
        const result = initializer();
        if (result instanceof Promise) {
          result.catch(error => console.warn(`Failed to load ${pageClass} module:`, error));
        }
      } catch (error) {
        console.warn(`Failed to initialize ${pageClass}:`, error);
      }
    }
  }
}

// Set up handlers for component reinitialization after HTMX swaps
function setupReinitializationHandlers() {
  document.addEventListener('htmx:reinitialize-dropdowns', () => initializeDropdowns());
  document.addEventListener('htmx:reinitialize-shop', () => initializeShop());
  document.addEventListener('htmx:reinitialize-forms', () => initializeForms());
}
