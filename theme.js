(() => {
  const root = document.documentElement;
  const button = document.querySelector('[data-theme-toggle]');
  const favicon = document.querySelector('#theme-favicon');

  function setTheme(theme) {
    root.dataset.theme = theme;
    localStorage.setItem('netch-theme', theme);
    if (button) {
      const isDark = theme === 'dark';
      button.textContent = isDark ? 'Light mode' : 'Dark mode';
      button.setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'} mode`);
    }
    if (favicon) favicon.href = `assets/logo-${theme === 'dark' ? 'dark' : 'light'}.png`;
  }

  setTheme(root.dataset.theme || 'dark');
  button?.addEventListener('click', () => setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark'));
})();
