// HTMX Navigation - simplified version
// Only handles essential functionality, no dynamic attribute setting

import { showLoginMessage, showLogoutMessage } from './notifications.js';

// HTMX event handlers for state management
document.addEventListener('htmx:beforeSwap', function(evt) {
  // Add swapping class to prevent transitions
  const mainContent = document.getElementById('main-content');
  if (mainContent) {
    mainContent.classList.add('htmx-swapping');
  }
});

document.addEventListener('htmx:afterSwap', function(evt) {
  // Handle logout success
  if (evt.detail.target.id === 'user-menu-dropdown') {
    showLogoutMessage();
  }
  
  // Remove swapping class
  const mainContent = document.getElementById('main-content');
  if (mainContent) {
    mainContent.classList.remove('htmx-swapping');
  }
});

// Check for login success notification
document.addEventListener('DOMContentLoaded', function() {
  const showLoginSuccess = document.body.getAttribute('data-show-login');
  if (showLoginSuccess === 'true') {
    showLoginMessage();
  }
}); 