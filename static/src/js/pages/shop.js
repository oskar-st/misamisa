// Expose setView function globally
window.setView = function(view) {
    const list = document.getElementById('product-list');
    const gridBtn = document.getElementById('grid-btn');
    const listBtn = document.getElementById('list-btn');
    
    if (!list || !gridBtn || !listBtn) {
        console.log('Missing elements for view toggle');
        return;
    }
    
    console.log('Switching to view:', view);
    
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
    } else {
        list.classList.remove('product-list');
        list.classList.add('product-grid');
        gridBtn.classList.add('active');
        listBtn.classList.remove('active');
    }
    
    console.log('View switched successfully to:', view);
}

function applyViewFromContainer() {
  const container = document.getElementById('product-list-container');
  if (!container) {
    console.log('No product-list-container found');
    return;
  }
  
  const view = container.getAttribute('data-view') || 'grid';
  const list = document.getElementById('product-list');
  const gridBtn = document.getElementById('grid-btn');
  const listBtn = document.getElementById('list-btn');
  
  console.log('Applying view:', view);
  console.log('Elements found:', { list: !!list, gridBtn: !!gridBtn, listBtn: !!listBtn });
  
  if (!list || !gridBtn || !listBtn) {
    console.log('Missing elements for view toggle');
    return;
  }
  
  if (view === 'list') {
    list.classList.remove('product-grid');
    list.classList.add('product-list');
    listBtn.classList.add('active');
    gridBtn.classList.remove('active');
    console.log('Applied list view');
  } else {
    list.classList.remove('product-list');
    list.classList.add('product-grid');
    gridBtn.classList.add('active');
    listBtn.classList.remove('active');
    console.log('Applied grid view');
  }
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

// Initialize view functionality
function initializeProductView() {
  applyViewFromContainer();
  setupAjaxPagination();
  setupPaginationJump();
}

// Export for use in base template
window.initializeShopFunctionality = initializeProductView;

// On page load, set the view based on the query parameter (for initial render only)
window.addEventListener('DOMContentLoaded', initializeProductView);

// Reinitialize after htmx content swaps
document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'main-content') {
        initializeProductView();
    }
});

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}