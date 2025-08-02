// Shop page functionality - localStorage-based view toggle

// Debounce timer for view toggle
let viewToggleDebounceTimer = null;
let isViewToggling = false;

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

// Switch view without changing URL (with debouncing)
function switchView(newView) {
  // Prevent multiple simultaneous requests
  if (isViewToggling) {
    return;
  }
  
  // Clear any existing debounce timer
  if (viewToggleDebounceTimer) {
    clearTimeout(viewToggleDebounceTimer);
  }
  
  // Save preference
  saveViewPreference(newView);
  
  // Update button states
  updateViewToggleState(newView);
  
  // Apply styling immediately for instant feedback
  applyViewStyling(newView);
  
  // Debounce the HTMX request to prevent race conditions
  viewToggleDebounceTimer = setTimeout(() => {
    isViewToggling = true;
    
    // Get current category from container data attributes
    const productListContainer = document.getElementById('product-list-container');
    let targetUrl;
    
    if (productListContainer) {
      const currentCategory = productListContainer.dataset.currentCategory || productListContainer.getAttribute('data-current-category');
      
      if (currentCategory && currentCategory !== 'all') {
        // We're in a specific category - use category URL
        targetUrl = `/${currentCategory}/`;
        console.log(`🎯 View toggle for category: ${currentCategory}`);
      } else {
        // We're in "All Products" view - use shop URL
        targetUrl = '/sklep/';
        console.log(`🎯 View toggle for all products`);
      }
    } else {
      // Fallback to current URL
      const currentUrl = new URL(window.location.href);
      currentUrl.searchParams.delete('view');
      targetUrl = currentUrl.toString();
      console.log(`🎯 View toggle fallback to current URL: ${targetUrl}`);
    }
    
    // Use HTMX to fetch new content with view preference in headers
    htmx.ajax('GET', targetUrl, {
      target: '#product-list-container',
      swap: 'outerHTML',
      headers: {
        'X-View-Preference': newView
      }
    }).then(() => {
      isViewToggling = false;
    }).catch((error) => {
      console.error('View toggle request failed:', error);
      isViewToggling = false;
    });
  }, 150); // 150ms debounce delay
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
  // Get current category from the product list container data attribute
  const productListContainer = document.getElementById('product-list-container');
  
  // Try multiple ways to get the category
  let currentCategory = null;
  if (productListContainer) {
    // Try dataset first (preferred)
    currentCategory = productListContainer.dataset.currentCategory;
    
    // Fallback to getAttribute
    if (!currentCategory) {
      currentCategory = productListContainer.getAttribute('data-current-category');
    }
    
    // If still null, check if the container was just swapped
    if (!currentCategory) {
      console.log('⚠️ No category found in attributes, checking HTML...');
      const outerHTML = productListContainer.outerHTML.substring(0, 200);
      console.log('🔍 Container HTML start:', outerHTML);
    }
  }
  
  console.log(`🎯 Updating sidebar active states for category: ${currentCategory}`);
  console.log(`🔍 Product container exists:`, !!productListContainer);
  console.log(`🔍 Dataset:`, productListContainer ? productListContainer.dataset : 'No container');
  console.log(`🔍 All attributes:`, productListContainer ? productListContainer.attributes : 'No container');
  
  // Remove ALL active classes from sidebar links (including server-rendered ones)
  const allSidebarLinks = document.querySelectorAll('.sidebar-categories .category-link');
  console.log(`🔍 Found ${allSidebarLinks.length} sidebar links to process`);
  
  allSidebarLinks.forEach((link, index) => {
    const wasActive = link.classList.contains('active');
    link.classList.remove('active');
    if (wasActive) {
      console.log(`🧹 [${index}] Removed active from: "${link.textContent.trim()}" (${link.href})`);
    }
  });
  
  // Also remove from menu links
  const allMenuLinks = document.querySelectorAll('.category-menu-link, .category-menu a');
  allMenuLinks.forEach(link => {
    link.classList.remove('active');
  });
  
  // Find and activate the matching links based on category
  if (currentCategory) {
    if (currentCategory === 'all') {
      // Activate "All Products" link - look for the specific link in sidebar
      allSidebarLinks.forEach((link, index) => {
        try {
          const linkUrl = new URL(link.href);
          const urlSlug = linkUrl.pathname.replace(/^\/+|\/+$/g, '');
          
          // Check if this is the "All Products" link (typically "sklep" or "shop")
          if (urlSlug === 'sklep' || urlSlug === 'shop' || link.textContent.trim().includes('All Products')) {
            link.classList.add('active');
            console.log(`✅ [${index}] Activated "All Products" link: "${link.textContent.trim()}" (URL: ${linkUrl.pathname})`);
          }
        } catch (error) {
          console.warn(`❌ [${index}] Error processing "All Products" link: ${error.message}`);
        }
      });
      
      // Update category dropdown
      const categoryDropdown = document.getElementById('category-filter');
      if (categoryDropdown) {
        categoryDropdown.value = '';
      }
    } else {
      // Activate category-specific links - check ALL sidebar links
      let activatedCount = 0;
      allSidebarLinks.forEach((link, index) => {
        try {
          const linkUrl = new URL(link.href);
          // Extract slug from URL path - format is /<slug>/ or /<slug>
          const urlSlug = linkUrl.pathname.replace(/^\/+|\/+$/g, ''); // Remove leading/trailing slashes
          
          console.log(`🔍 [${index}] Checking link: "${link.textContent.trim()}" | URL slug: "${urlSlug}" | Current: "${currentCategory}"`);
          
          // Exact match for category slug
          if (urlSlug === currentCategory) {
            link.classList.add('active');
            activatedCount++;
            console.log(`✅ [${index}] Activated link for category: ${currentCategory} - "${link.textContent.trim()}" (URL: ${linkUrl.pathname})`);
          }
        } catch (error) {
          console.warn(`❌ [${index}] Error processing link: ${error.message}`);
        }
      });
      
      console.log(`📊 Total links activated: ${activatedCount}`);
      
      // Update category dropdown
      const categoryDropdown = document.getElementById('category-filter');
      if (categoryDropdown) {
        categoryDropdown.value = currentCategory;
      }
    }
  } else {
    console.log('⚠️ No current category found, using fallback URL matching');
    // Fallback to URL-based matching
    const currentPath = window.location.pathname;
    allSidebarLinks.forEach(link => {
      try {
        const linkPath = new URL(link.href).pathname;
        if (linkPath === currentPath) {
          link.classList.add('active');
          console.log(`✅ Activated link via URL matching: ${link.textContent.trim()}`);
        }
      } catch (error) {
        // Silently handle invalid links
      }
    });
  }
}

// Listen for HTMX after-swap events to update button states and reinitialize
document.addEventListener('htmx:afterSwap', function(event) {
  // Check if this is a product list container update or main content update
  if (event.target.id === 'product-list-container' || event.target.id === 'main-content') {
    // Reset all state flags
    isViewToggling = false;
    isPaginationJumping = false;
    
    console.log('🎯 HTMX afterSwap detected, target:', event.target.id);
    
    // Small delay to ensure DOM is ready after swap
    setTimeout(() => {
      // Re-initialize ALL shop functionality after container swap
      initializeShop(); // This calls both setupPaginationJump() and initializeViewToggle()
      
      // Update sidebar active states after navigation (no extra delay needed for outerHTML)
      updateSidebarActiveStates();
    }, 50);
  }
});

// Add error handling for HTMX swap errors
document.addEventListener('htmx:swapError', function(event) {
  console.error('HTMX swap error:', event.detail);
  isViewToggling = false; // Reset state on error
});

// Add error handling for HTMX response errors
document.addEventListener('htmx:responseError', function(event) {
  console.error('HTMX response error:', event.detail);
  isViewToggling = false; // Reset state on error
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

// Prevent multiple event listeners with a flag
let paginationListenersAttached = false;
let isPaginationJumping = false;

function setupPaginationJump() {
  // Setup both top and bottom pagination inputs
  const topInput = document.getElementById('pagination-jump-input-top');
  const bottomInput = document.getElementById('pagination-jump-input-bottom');
  
  // Function to setup a single pagination input
  function setupSingleInput(input, position) {
    if (!input) return;
    
    // Check if listeners are already attached to this specific element
    if (input.dataset.listenersAttached === 'true') {
      return;
    }
    
    // Mark this element as having listeners
    input.dataset.listenersAttached = 'true';
    
    // Create the event handler
    input.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        
        // Prevent multiple simultaneous pagination requests
        if (isPaginationJumping) {
          return;
        }
        
        const page = parseInt(this.value);
        const maxPages = parseInt(this.getAttribute('max'));
        
        // Validate page number
        if (isNaN(page) || page < 1 || page > maxPages) {
          this.value = ''; // Clear invalid input
          return;
        }
        
        isPaginationJumping = true;
        
        // Sync the value to the other pagination input
        const otherInput = position === 'top' ? bottomInput : topInput;
        if (otherInput) {
          otherInput.value = page;
        }
        
        // Build URL for HTMX request
        const url = new URL(window.location);
        url.searchParams.set('page', page);
        
        // Use HTMX for pagination jump to maintain consistency
        htmx.ajax('GET', url.toString(), {
          target: '#product-list-container',
          swap: 'outerHTML',
          headers: {
            'X-View-Preference': getViewPreference()
          }
        }).then(() => {
          isPaginationJumping = false;
          // Update URL in browser
          window.history.pushState({}, '', url.toString());
        }).catch((error) => {
          console.error('Pagination jump failed:', error);
          isPaginationJumping = false;
        });
      }
    });
  }
  
  // Setup both inputs
  setupSingleInput(topInput, 'top');
  setupSingleInput(bottomInput, 'bottom');
}

// Export for use in main.js
export { initializeShop };