// Shop page functionality - localStorage-based view toggle

// Get view preference from localStorage
function getViewPreference() {
  return localStorage.getItem('shopViewPreference') || 'grid';
}

// Save view preference to localStorage
function saveViewPreference(view) {
  localStorage.setItem('shopViewPreference', view);
}

// Get the current view from the DOM element (server-rendered)
function getCurrentViewFromDOM() {
  const productList = document.getElementById('product-list');
  if (productList) {
    if (productList.classList.contains('product-list')) {
      return 'list';
    } else if (productList.classList.contains('product-grid')) {
      return 'grid';
    }
  }
  return 'grid'; // Default fallback
}

// Apply view styling to the product list
function applyViewStyling(view) {
  const productList = document.getElementById('product-list');
  if (productList) {
    // Remove existing view classes
    productList.classList.remove('product-grid', 'product-list');
    // Add the appropriate view class
    productList.classList.add(`product-${view}`);
    // Update data attribute
    productList.setAttribute('data-view', view);
  }
}

// Handle active button state after view changes
function updateViewToggleState(view) {
  const gridBtn = document.getElementById('grid-btn');
  const listBtn = document.getElementById('list-btn');
  
  if (gridBtn && listBtn) {
    // Remove active class from both buttons
    gridBtn.classList.remove('active');
    listBtn.classList.remove('active');
    
    // Add active class to the correct button
    if (view === 'list') {
      listBtn.classList.add('active');
    } else {
      gridBtn.classList.add('active');
    }
  }
}

// Switch view without changing URL
function switchView(newView) {
  // Save preference
  saveViewPreference(newView);
  
  // Update button states
  updateViewToggleState(newView);
  
  // Apply styling immediately for instant feedback
  applyViewStyling(newView);
  
  // Get current URL without view parameters
  const currentUrl = new URL(window.location.href);
  currentUrl.searchParams.delete('view'); // Remove view parameter if it exists
  
  // Use HTMX to fetch new content with view preference in headers
  htmx.ajax('GET', currentUrl.toString(), {
    target: '#product-list-container',
    swap: 'outerHTML',
    headers: {
      'X-View-Preference': newView
    }
  });
}

// Initialize view toggle functionality
function initializeViewToggle() {
  const gridBtn = document.getElementById('grid-btn');
  const listBtn = document.getElementById('list-btn');
  
  if (gridBtn && listBtn) {
    // Add event listeners
    gridBtn.addEventListener('click', () => switchView('grid'));
    listBtn.addEventListener('click', () => switchView('list'));
    
    // Apply saved view preference on page load
    const savedView = getViewPreference();
    const currentView = getCurrentViewFromDOM();
    
    // If saved preference differs from server-rendered view, apply the saved preference
    if (savedView !== currentView) {
      updateViewToggleState(savedView);
      applyViewStyling(savedView);
      
      // Fetch content with correct view immediately on page load
      setTimeout(() => {
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.delete('view'); // Remove view parameter if it exists
        
        htmx.ajax('GET', currentUrl.toString(), {
          target: '#product-list-container',
          swap: 'outerHTML',
          headers: {
            'X-View-Preference': savedView
          }
        });
      }, 100); // Small delay to avoid race conditions
    } else {
      // Just update button states to match current view
      updateViewToggleState(currentView);
    }
  }
}

// Add view preference header to all HTMX requests
document.addEventListener('htmx:configRequest', function(event) {
  // Add view preference header to all requests
  const viewPreference = getViewPreference();
  if (!event.detail.headers) {
    event.detail.headers = {};
  }
  event.detail.headers['X-View-Preference'] = viewPreference;
  
  // Add target information to headers for Django to know what template to use
  const triggerElement = event.detail.elt;
  if (triggerElement) {
    const hxTarget = triggerElement.getAttribute('hx-target');
    if (hxTarget) {
      event.detail.headers['X-HX-Target'] = hxTarget;
    }
  }
  
  // Remove view parameter from URL if it exists
  const url = new URL(event.detail.path, window.location.origin);
  if (url.searchParams.has('view')) {
    url.searchParams.delete('view');
    event.detail.path = url.pathname + url.search;
  }
});

// Update sidebar active states based on current URL
function updateSidebarActiveStates() {
  const currentPath = window.location.pathname;
  
  // Remove all active classes from sidebar links
  const sidebarLinks = document.querySelectorAll('.sidebar-categories .category-link');
  sidebarLinks.forEach(link => {
    link.classList.remove('active');
  });
  
  // Find and activate the matching link
  sidebarLinks.forEach(link => {
    const linkPath = new URL(link.href).pathname;
    if (linkPath === currentPath) {
      link.classList.add('active');
    }
  });
  
  // Also update top menu active states if they exist
  const topMenuLinks = document.querySelectorAll('.category-menu-link');
  topMenuLinks.forEach(link => {
    link.classList.remove('active');
    const linkPath = new URL(link.href).pathname;
    if (linkPath === currentPath) {
      link.classList.add('active');
    }
  });
}

// Listen for HTMX after-swap events to update button states and reinitialize
document.addEventListener('htmx:afterSwap', function(event) {
  // Check if this is a product list container update or main content update
  if (event.target.id === 'product-list-container' || event.target.id === 'main-content') {
    // Re-initialize view toggle after container swap
    initializeViewToggle();
    // Update sidebar active states after navigation
    updateSidebarActiveStates();
  }
});

// Initialize shop functionality
function initializeShop() {
  // Setup pagination jump form
  setupPaginationJump();
  
  // Initialize view toggle
  initializeViewToggle();
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeShop);

// Expose initializeShop globally for HTMX navigation
window.initializeShop = initializeShop;

function setupPaginationJump() {
  const jumpInput = document.getElementById('pagination-jump-input');
  if (jumpInput) {
    jumpInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        const page = this.value;
        const url = new URL(window.location);
        url.searchParams.set('page', page);
        window.location.href = url.toString();
      }
    });
  }
}

// Export for use in main.js
export { initializeShop };