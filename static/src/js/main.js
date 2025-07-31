// Main JavaScript entry point for frontend
// Import all frontend JavaScript modules

// Import utility libraries
import './lib/utils.js';
import './lib/api.js';
import './lib/validation.js';

// Import components
import { initializeDropdowns } from './components/dropdown.js';
import { initializeTabs } from './components/tabs.js';
import { initializeForms } from './components/forms.js';
import { initializeThemeToggle } from './components/theme-toggle.js';
import './components/htmx-navigation.js';
import './components/dropdown-management.js';
import { initializeUserMenu } from './components/user-menu.js';
import './components/notifications.js';

// Import page-specific scripts
import './pages/home.js';
import './pages/products.js';
import './pages/contact.js';

// Initialize frontend functionality
document.addEventListener('DOMContentLoaded', function() {
  console.log('Frontend JavaScript loaded');
  
  // Initialize components
  initializeDropdowns();
  initializeTabs();
  initializeForms();
  initializeThemeToggle();
  initializeUserMenu();
  
  // Initialize page-specific functionality
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
  console.log('Home page initialized');
}

function initializeProductsPage() {
  // Products page specific functionality
  console.log('Products page initialized');
}

function initializeContactPage() {
  // Contact page specific functionality
  console.log('Contact page initialized');
}
