// Main JavaScript entry point for frontend
// Import all frontend JavaScript modules

// Import components
import { initializeDropdowns } from './components/dropdown.js';
import { initializeTabs } from './components/tabs.js';
import { initializeForms } from './components/forms.js';
import { initializeThemeToggle } from './components/theme-toggle.js';
import { initializeUserMenu } from './components/user-menu.js';
import './components/dropdown-management.js';
import './components/notifications.js';
import './components/htmx-navigation.js';

// Import page-specific functionality
import { initializeShop } from './pages/shop.js';
import { initializeAdmin } from './admin/productimage_single_primary.js';

// Initialize frontend functionality
document.addEventListener('DOMContentLoaded', function() {
  // Initialize components
  initializeDropdowns();
  initializeTabs();
  initializeForms();
  initializeThemeToggle();
  initializeUserMenu();
  
  // Initialize page-specific functionality
  if (document.querySelector('.shop-page') || document.querySelector('#product-list-container')) {
    if (window.initializeShop) {
      window.initializeShop();
    }
  }
  
  if (document.querySelector('.admin-page') || document.querySelector('input[name$="-is_primary"]')) {
    initializeAdmin();
  }
  
  if (document.querySelector('.home-page')) {
    initializeHomePage();
  }
  
  if (document.querySelector('.products-page')) {
    initializeProductsPage();
  }
  
  if (document.querySelector('.contact-page')) {
    initializeContactPage();
  }
});

// Page-specific initialization functions
function initializeHomePage() {
  // Homepage specific functionality
}

function initializeProductsPage() {
  // Products page specific functionality
}

function initializeContactPage() {
  // Contact page specific functionality
}
