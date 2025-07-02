function setView(view) {
    const params = new URLSearchParams(window.location.search);
    params.set('view', view);
    
    // Use AJAX to load the new view without page reload
    const url = window.location.pathname + '?' + params.toString();
    
    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => response.text())
        .then(html => {
            // Extract the #product-list-container from the response
            const temp = document.createElement('div');
            temp.innerHTML = html;
            const newContainer = temp.querySelector('#product-list-container');
            if (newContainer) {
                document.getElementById('product-list-container').replaceWith(newContainer);
                applyViewFromContainer();
                setupAjaxPagination(); // Re-attach pagination listeners
                setupPaginationJump(); // Re-attach jump input listener
                
                // Update the URL without reloading the page
                window.history.pushState({}, '', url);
                
                // Smooth scroll to top
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else {
                window.location = url; // fallback to page reload
            }
        })
        .catch(error => {
            console.error('Error loading view:', error);
            // Fallback to page reload on error
            window.location.search = params.toString();
        });
}

function applyViewFromContainer() {
  const container = document.getElementById('product-list-container');
  if (!container) return;
  const view = container.getAttribute('data-view') || 'grid';
  const list = document.getElementById('product-list');
  const gridBtn = document.getElementById('grid-btn');
  const listBtn = document.getElementById('list-btn');
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
}

// AJAX pagination
function setupAjaxPagination() {
  document.querySelectorAll('.pagination-link').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      fetch(link.href, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => response.text())
        .then(html => {
          // Extract the #product-list-container from the response
          const temp = document.createElement('div');
          temp.innerHTML = html;
          const newContainer = temp.querySelector('#product-list-container');
          if (newContainer) {
            document.getElementById('product-list-container').replaceWith(newContainer);
            applyViewFromContainer();
            setupAjaxPagination(); // Re-attach listeners
            setupPaginationJump(); // Re-attach jump input listener
            window.scrollTo({ top: 0, behavior: 'smooth' });
          } else {
            window.location = link.href; // fallback
          }
        });
    });
  });
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

// On page load, set the view based on the query parameter (for initial render only)
window.addEventListener('DOMContentLoaded', function() {
  applyViewFromContainer();
  setupAjaxPagination();
  setupPaginationJump();
});

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}