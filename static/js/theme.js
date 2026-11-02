/* Apply the saved/system theme before styles paint, then enhance the switch. */
(() => {
  'use strict';
  const root = document.documentElement;
  const key = 'dte-theme';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let button;
  const preference = () => {
    try {
      const value = window.localStorage.getItem(key);
      return value === 'light' || value === 'dark' ? value : null;
    } catch (_) { return null; }
  };
  const systemTheme = () => system.matches ? 'dark' : 'light';
  const apply = theme => {
    root.dataset.theme = theme;
    if (!button) return;
    const dark = theme === 'dark';
    const label = dark ? button.dataset.lightLabel : button.dataset.darkLabel;
    button.setAttribute('aria-pressed', String(dark));
    button.setAttribute('aria-label', label);
    button.title = label;
  };
  apply(preference() || systemTheme());
  document.addEventListener('DOMContentLoaded', () => {
    button = document.querySelector('.theme-toggle');
    if (!button) return;
    apply(root.dataset.theme);
    button.hidden = false;
    button.addEventListener('click', () => {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      apply(next);
      try { window.localStorage.setItem(key, next); } catch (_) { /* Switching still works without storage. */ }
    });
  }, { once: true });
  system.addEventListener?.('change', () => { if (!preference()) apply(systemTheme()); });
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) apply(preference() || systemTheme());
  });
})();
