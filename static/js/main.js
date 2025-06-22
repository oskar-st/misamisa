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
  themeToggle.textContent = currentTheme === 'dark' ? '☀️' : '🌙';

  themeToggle.addEventListener('click', () => {
    let newTheme = docElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    docElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    themeToggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
  });
});
