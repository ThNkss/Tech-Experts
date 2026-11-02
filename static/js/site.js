/* Small, optional enhancements. Django renders all page content and navigation. */
(() => {
  'use strict';
  const header = document.querySelector('.header');
  const toggle = document.querySelector('.menu-toggle');
  const navigation = document.getElementById('primary-nav');
  if (header && toggle && navigation) {
    const drawer = document.querySelector('.mobile-menu-drawer');
    const mobile = matchMedia('(max-width:960px)');
    const anchor = document.createComment('Primary navigation position');
    navigation.before(anchor);
    const closeMenu = () => {
      if (drawer?.open) drawer.close();
      toggle.setAttribute('aria-expanded','false');
      document.body.classList.remove('menu-open');
    };
    const layout = () => {
      closeMenu();
      if (mobile.matches && drawer && typeof drawer.showModal === 'function') {
        drawer.querySelector('.drawer-content').append(navigation);
      } else anchor.after(navigation);
    };
    toggle.hidden = false;
    header.classList.add('menu-enabled');
    layout();
    mobile.addEventListener?.('change',layout);
    toggle.addEventListener('click',() => {
      if (mobile.matches && drawer && typeof drawer.showModal === 'function') {
        if (drawer.open) closeMenu();
        else {
          drawer.showModal();
          toggle.setAttribute('aria-expanded','true');
          document.body.classList.add('menu-open');
        }
      } else toggle.setAttribute('aria-expanded',String(toggle.getAttribute('aria-expanded') !== 'true'));
    });
    drawer?.querySelector('[data-menu-close]').addEventListener('click',closeMenu);
    drawer?.addEventListener('close',() => {
      toggle.setAttribute('aria-expanded','false');
      document.body.classList.remove('menu-open');
      if (mobile.matches) toggle.focus({preventScroll:true});
    });
    drawer?.addEventListener('click',event => {
      const box=drawer.getBoundingClientRect();
      if (event.target===drawer && (event.clientX<box.left || event.clientX>box.right || event.clientY<box.top || event.clientY>box.bottom)) closeMenu();
    });
    header.addEventListener('keydown',event => {
      if (event.key==='Escape') closeMenu();
    });
    navigation.addEventListener('click',event => {
      if (event.target.closest('a')) closeMenu();
    });
  }

  document.querySelectorAll('.print-catalog').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => window.print());
  });

  let printStates = [];
  window.addEventListener('beforeprint', () => {
    printStates = Array.from(document.querySelectorAll('.catalog-faqs details'))
      .map(detail => [detail, detail.open]);
    printStates.forEach(([detail]) => { detail.open = true; });
  });
  window.addEventListener('afterprint', () => {
    printStates.forEach(([detail, wasOpen]) => { detail.open = wasOpen; });
    printStates = [];
  });

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (reducedMotion.matches || !('IntersectionObserver' in window)) return;
  const elements = Array.from(document.querySelectorAll('[data-reveal]'));
  if (!elements.length) return;
  const revealAll = () => elements.forEach(element => element.classList.remove('reveal-pending'));
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.remove('reveal-pending');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });
  elements.forEach(element => {
    element.classList.add('reveal-pending');
    observer.observe(element);
  });
  // Never leave content invisible if observation is interrupted or the user changes settings.
  window.setTimeout(() => { revealAll(); observer.disconnect(); }, 2200);
  window.addEventListener('pageshow', event => { if (event.persisted) revealAll(); });
  reducedMotion.addEventListener?.('change', revealAll);
})();
