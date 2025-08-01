// Shop page functionality - HTMX-based view toggle

// Handle active button state after HTMX updates
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
  
  // Update all sidebar links to preserve the current view
  updateSidebarLinks(view);
}

// Update all sidebar links with the current view parameter
function updateSidebarLinks(view) {
  const sidebarLinks = document.querySelectorAll('.sidebar-categories a[hx-get]');
  
  console.log(`Found ${sidebarLinks.length} sidebar links to update with view: ${view}`);
  
  sidebarLinks.forEach((link, index) => {
    const currentHxGet = link.getAttribute('hx-get');
    console.log(`Link ${index}: current hx-get = ${currentHxGet}`);
    
    if (currentHxGet) {
      // Parse the current URL
      const url = new URL(currentHxGet, window.location.origin);
      // Update the view parameter
      url.searchParams.set('view', view);
      const newHxGet = url.pathname + url.search;
      // Update the hx-get attribute
      link.setAttribute('hx-get', newHxGet);
      console.log(`Link ${index}: updated hx-get = ${newHxGet}`);
      
      // Force HTMX to re-process this element to pick up the new attribute
      if (window.htmx) {
        htmx.process(link);
      }
    }
  });
  
  console.log(`Updated ${sidebarLinks.length} sidebar links with view: ${view}`);
  
  // Verify the updates actually took effect
  setTimeout(() => {
    const verifyLinks = document.querySelectorAll('.sidebar-categories a[hx-get]');
    console.log('VERIFICATION - Checking if sidebar links were updated:');
    verifyLinks.forEach((link, index) => {
      console.log(`Verify Link ${index}: hx-get = ${link.getAttribute('hx-get')}`);
    });
  }, 100);
}

// Get the current view from the DOM element (server-rendered)
function getCurrentViewFromDOM() {
  const productList = document.getElementById('product-list');
  if (productList) {
    console.log('Product list classes:', productList.className);
    if (productList.classList.contains('product-list')) {
      console.log('Detected list view from DOM');
      return 'list';
    } else if (productList.classList.contains('product-grid')) {
      console.log('Detected grid view from DOM');
      return 'grid';
    }
  }
  console.log('No view classes found, defaulting to grid');
  return 'grid'; // Default fallback
}

// Intercept HTMX requests before they're sent to modify view parameter
document.addEventListener('htmx:configRequest', function(event) {
  console.log('HTMX configRequest event fired:', event.detail);
  
  // Check if this is a sidebar category navigation request
  const triggerElement = event.detail.elt;
  console.log('Trigger element:', triggerElement);
  console.log('Is in sidebar?:', triggerElement && triggerElement.closest('.sidebar-categories'));
  
  if (triggerElement && triggerElement.closest('.sidebar-categories')) {
    // Get current view from DOM
    const currentView = getCurrentViewFromDOM();
    console.log(`🎯 Intercepting sidebar request, forcing view to: ${currentView}`);
    
    // Parse the current URL and update the view parameter
    const url = new URL(event.detail.path, window.location.origin);
    url.searchParams.set('view', currentView);
    event.detail.path = url.pathname + url.search;
    
    console.log(`🎯 Modified sidebar request URL to: ${event.detail.path}`);
  }
});

// Listen for HTMX after-swap events to update button states and reinitialize
document.addEventListener('htmx:afterSwap', function(event) {
  console.log('HTMX after-swap event for target:', event.target.id);
  
  // Check if this is a product list container update
  if (event.target.id === 'product-list-container') {
    console.log('Product list container updated, reinitializing...');
    // Re-initialize shop functionality after container swap
    // NO setTimeout - update immediately to prevent race condition
    initializeShop();
  }
  
  // Check if this is a product list update
  if (event.target.id === 'product-list') {
    const view = getCurrentViewFromDOM();
    console.log('Updating button states for view:', view);
    updateViewToggleState(view);
  }
});

// Listen for HTMX before-swap events to check if target exists
document.addEventListener('htmx:beforeSwap', function(event) {
  console.log('HTMX before-swap event for target:', event.target.id);
  if (!event.target) {
    console.error('HTMX target not found:', event.detail.target);
  }
});

// Listen for HTMX after-request events to handle navigation
document.addEventListener('htmx:afterRequest', function(event) {
  // If this was a full page navigation (not just a swap), re-initialize
  if (event.detail.xhr.responseURL && event.detail.xhr.responseURL !== window.location.href) {
    // This was a full page navigation, shop will be initialized by the new page
    return;
  }
});

// Initialize shop functionality
function initializeShop() {
  console.log('Initializing shop functionality');
  
  // Setup pagination jump form
  setupPaginationJump();
  
  // Set initial button state based on DOM (server-rendered classes)
  const view = getCurrentViewFromDOM();
  console.log('Setting button states for view:', view);
  updateViewToggleState(view);
}

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