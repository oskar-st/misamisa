function setView(view) {
    const params = new URLSearchParams(window.location.search);
    params.set('view', view);
    // Reload the page with the new view parameter, preserving other params
    window.location.search = params.toString();
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
            window.scrollTo({ top: 0, behavior: 'smooth' });
          } else {
            window.location = link.href; // fallback
          }
        });
    });
  });
}

// On page load, set the view based on the query parameter (for initial render only)
window.addEventListener('DOMContentLoaded', function() {
  applyViewFromContainer();
  setupAjaxPagination();
});

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}