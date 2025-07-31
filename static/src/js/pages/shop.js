// Shop page functionality

// Global view management
window.shopViewState = {
    currentView: 'grid',
    initialized: false
};

function setView(view) {
    console.log('setView called with:', view);
    
    const list = document.getElementById('product-list');
    const gridBtn = document.getElementById('grid-btn');
    const listBtn = document.getElementById('list-btn');
    
    console.log('Elements found:', {
        list: !!list,
        gridBtn: !!gridBtn,
        listBtn: !!listBtn
    });
    
    if (!list || !gridBtn || !listBtn) {
        console.log('Missing elements for view toggle');
        return;
    }
    
    console.log('Switching to view:', view);
    
    // Update global state
    window.shopViewState.currentView = view;
    
    // Store view preference in localStorage
    localStorage.setItem('shop-view-preference', view);
    
    // Update URL parameters (only if not grid to keep URLs clean)
    if (view !== 'grid') {
        const url = new URL(window.location);
        url.searchParams.set('view', view);
        window.history.replaceState({}, '', url);
    } else {
        // Remove view parameter if switching to grid
        const url = new URL(window.location);
        url.searchParams.delete('view');
        window.history.replaceState({}, '', url);
    }
    
    // Update the container's data-view attribute
    const container = document.getElementById('product-list-container');
    if (container) {
        container.setAttribute('data-view', view);
    }
    
    // Apply the view using CSS classes only
    if (view === 'list') {
        list.classList.remove('product-grid');
        list.classList.add('product-list');
        listBtn.classList.add('active');
        gridBtn.classList.remove('active');
        console.log('Applied list view classes');
    } else {
        list.classList.remove('product-list');
        list.classList.add('product-grid');
        gridBtn.classList.add('active');
        listBtn.classList.remove('active');
        
        // Check if there's only one product and add single-product class
        const productCards = list.querySelectorAll('.product-card');
        console.log('Product cards in setView:', productCards.length);
        
        if (productCards.length === 1) {
            list.classList.add('single-product');
            console.log('Single product detected in setView, adding single-product class');
        } else {
            // Remove single-product class if not single product
            list.classList.remove('single-product');
            console.log('Multiple products detected, removing single-product class');
        }
        console.log('Applied grid view classes');
    }
    
    console.log('View switched successfully to:', view);
}

function applyViewFromContainer() {
    const container = document.getElementById('product-list-container');
    if (!container) {
        console.log('No product-list-container found');
        return;
    }
    
    // Check URL parameters first, then localStorage, then fallback to data-view attribute
    const urlParams = new URLSearchParams(window.location.search);
    const urlView = urlParams.get('view');
    const storedView = localStorage.getItem('shop-view-preference');
    const dataView = container.getAttribute('data-view');
    const view = urlView || storedView || dataView || 'grid';
    
    const list = document.getElementById('product-list');
    const gridBtn = document.getElementById('grid-btn');
    const listBtn = document.getElementById('list-btn');
    
    if (!list || !gridBtn || !listBtn) {
        console.log('Missing elements for view toggle');
        return;
    }
    
    console.log('Applying view:', view, 'url:', urlView, 'stored:', storedView, 'data:', dataView);
    
    // Update global state
    window.shopViewState.currentView = view;
    
    // Update container data-view attribute
    container.setAttribute('data-view', view);
    
    // Remove all view classes first
    list.classList.remove('product-grid', 'product-list', 'single-product');
    gridBtn.classList.remove('active');
    listBtn.classList.remove('active');
    
    if (view === 'list') {
        list.classList.add('product-list');
        listBtn.classList.add('active');
    } else {
        list.classList.add('product-grid');
        gridBtn.classList.add('active');
        
        // Check if there's only one product and add single-product class
        const productCards = list.querySelectorAll('.product-card');
        console.log('Product cards found:', productCards.length);
        
        if (productCards.length === 1) {
            list.classList.add('single-product');
            console.log('Single product detected, adding single-product class');
        }
    }
}

// Enhanced view toggle setup with event delegation
function setupViewToggle() {
    console.log('Setting up view toggle...');
    
    // Remove any existing event listeners to prevent duplicates
    const gridBtn = document.getElementById('grid-btn');
    const listBtn = document.getElementById('list-btn');
    
    console.log('View toggle buttons found:', {
        gridBtn: !!gridBtn,
        listBtn: !!listBtn,
        gridBtnClasses: gridBtn?.className,
        listBtnClasses: listBtn?.className
    });
    
    if (gridBtn) {
        // Remove existing listeners
        gridBtn.replaceWith(gridBtn.cloneNode(true));
        const newGridBtn = document.getElementById('grid-btn');
        
        // Add new listener
        newGridBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Grid button clicked');
            setView('grid');
        });
        console.log('Grid button listener added');
    }
    
    if (listBtn) {
        // Remove existing listeners
        listBtn.replaceWith(listBtn.cloneNode(true));
        const newListBtn = document.getElementById('list-btn');
        
        // Add new listener
        newListBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('List button clicked');
            setView('list');
        });
        console.log('List button listener added');
    }
    
    console.log('View toggle setup completed');
}

// htmx pagination (handled automatically by hx-boost)
function setupAjaxPagination() {
    // htmx handles this automatically with hx-boost
    // Just add htmx attributes to pagination links in template
}

function setupPaginationJump() {
    document.querySelectorAll('.pagination-jump-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const input = form.querySelector('.pagination-jump-input');
            const page = parseInt(input.value, 10);
            const min = parseInt(input.getAttribute('min'), 10);
            const max = parseInt(input.getAttribute('max'), 10);
            if (isNaN(page) || page < min || page > max) {
                input.focus();
                input.classList.add('error');
                setTimeout(() => input.classList.remove('error'), 1000);
                return;
            }
            const url = new URL(window.location);
            url.searchParams.set('page', page);
            fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.text())
                .then(html => {
                    const temp = document.createElement('div');
                    temp.innerHTML = html;
                    const newContainer = temp.querySelector('#product-list-container');
                    if (newContainer) {
                        document.getElementById('product-list-container').replaceWith(newContainer);
                        applyViewFromContainer();
                        setupAjaxPagination();
                        setupPaginationJump();
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    } else {
                        window.location = url;
                    }
                });
        });
    });
}

// Initialize shop functionality
function initializeShop() {
    console.log('initializeShop called');
    
    // Expose setView function globally for template use
    window.setView = setView;
    
    // Setup view toggle with event delegation
    setupViewToggle();
    
    // Only initialize once per page load
    if (!window.shopInitialized) {
        console.log('Shop not initialized yet, applying view state...');
        setTimeout(() => {
            applyViewFromContainer();
            window.shopInitialized = true;
            console.log('Shop functionality initialized');
        }, 100);
    } else {
        console.log('Shop already initialized, skipping...');
    }
}

// HTMX-aware reinitialization
function reinitializeShopAfterHtmx() {
    console.log('Reinitializing shop after HTMX swap');
    
    // Reset initialization flag
    window.shopInitialized = false;
    
    // Re-setup view toggle immediately
    setupViewToggle();
    
    // Preserve current view state before reinitializing
    const currentView = window.shopViewState?.currentView || localStorage.getItem('shop-view-preference') || 'grid';
    
    // Apply view state with a slight delay to ensure content is fully loaded
    setTimeout(() => {
        console.log('Applying view state after HTMX swap...');
        applyViewFromContainer();
        
        // Ensure the view state is properly applied
        if (currentView && currentView !== 'grid') {
            setView(currentView);
        }
        
        window.shopInitialized = true;
        console.log('Shop functionality reinitialized after HTMX with view:', currentView);
    }, 100); // Increased delay to ensure content is fully loaded
}

// Make initializeShop available globally for HTMX reinitialization
window.initializeShop = initializeShop;
window.reinitializeShopAfterHtmx = reinitializeShopAfterHtmx;

// Export for use in main.js
export { initializeShop, reinitializeShopAfterHtmx };