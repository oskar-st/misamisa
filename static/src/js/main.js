// Main JavaScript entry point for frontend
// Import all frontend JavaScript modules

// Import components
import { initializeDropdowns } from './components/dropdown.js';
import { initializeTabs } from './components/tabs.js';
import { initializeForms } from './components/forms.js';
import { initializeThemeToggle } from './components/theme-toggle.js';
import './components/htmx-navigation.js';
import { initializeUserMenu } from './components/user-menu.js';
import './components/dropdown-management.js';
import './components/notifications.js';

// Import page-specific functionality
import { initializeShop, reinitializeShopAfterHtmx } from './pages/shop.js';
import { initializeAdmin } from './admin/productimage_single_primary.js';

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
  console.log('Checking for shop page elements...');
  const shopPage = document.querySelector('.shop-page');
  const productListContainer = document.querySelector('#product-list-container');
  console.log('Shop elements found:', {
    shopPage: !!shopPage,
    productListContainer: !!productListContainer
  });
  
  if (shopPage || productListContainer) {
    console.log('Initializing shop functionality...');
    initializeShop();
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
