(() => {
  const root = document.documentElement;
  const system = matchMedia('(prefers-color-scheme: dark)');
  const key = 'od-theme';
  const preference = value => value === 'light' || value === 'dark' ? value : null;
  const systemTheme = () => system.matches ? 'dark' : 'light';
  let override = null;
  let button;

  try { override = preference(localStorage.getItem(key)); } catch {}

  function apply() {
    const theme = override || systemTheme();
    root.dataset.theme = theme;
    if (!button) return;

    const dark = theme === 'dark';
    const label = dark ? '라이트 모드로 전환' : '다크 모드로 전환';
    const icon = dark
      ? '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4 4l2 2m12 12 2 2M2 12h2m16 0h2M4 20l2-2M18 6l2-2"/>'
      : '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>';
    button.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true">' + icon + '</svg>';
    button.setAttribute('aria-label', label);
    button.title = label;
  }

  apply();
  system.addEventListener('change', apply);
  window.addEventListener('storage', event => {
    if (event.key !== key && event.key !== null) return;
    override = preference(event.newValue);
    apply();
  });
  document.addEventListener('DOMContentLoaded', () => {
    button = document.querySelector('[data-action="theme"]');
    button.addEventListener('click', event => {
      // Archived players still delegate this button's click at the app root.
      event.stopPropagation();
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      override = next === systemTheme() ? null : next;
      try {
        if (override) localStorage.setItem(key, override);
        else localStorage.removeItem(key);
      } catch {}
      apply();
    });
    apply();
  }, {once: true});
})();
