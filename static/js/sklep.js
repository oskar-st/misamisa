function setView(view) {
    const list = document.getElementById('product-list');
    if (view === 'list') {
      list.classList.remove('product-grid');
      list.classList.add('product-list');
    } else {
      list.classList.remove('product-list');
      list.classList.add('product-grid');
    }
  }
  
  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }