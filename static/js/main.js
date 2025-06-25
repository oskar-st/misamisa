document.addEventListener('DOMContentLoaded', function () {
  const logoLink = document.querySelector('.logo-link');
  if (logoLink && window.location.pathname === '/') {
    logoLink.addEventListener('click', function (e) {
      e.preventDefault(); // Already on home — don't reload
    });
  }

  // Theme switcher
  const themeToggle = document.getElementById('theme-toggle');
  const docElement = document.documentElement;

  const currentTheme = localStorage.getItem('theme') || 'light';
  docElement.setAttribute('data-theme', currentTheme);
  if (currentTheme === 'dark') {
    themeToggle.classList.add('active');
  } else {
    themeToggle.classList.remove('active');
  }
  // Prevent animation on page load, remove after theme is set
  themeToggle.classList.add('no-animate');
  setTimeout(() => {
    themeToggle.classList.remove('no-animate');
  }, 300);

  themeToggle.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent bubbling to document or other handlers
    let newTheme = docElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    docElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    if (newTheme === 'dark') {
      themeToggle.classList.add('active');
    } else {
      themeToggle.classList.remove('active');
    }
  });
});
