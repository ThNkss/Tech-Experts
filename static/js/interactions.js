/* Progressive interaction layer; content, links and forms work without it. */
(() => {
  'use strict';
  const root = document.documentElement;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let motion = !reduced.matches;
  const updateMotion = () => { motion = !reduced.matches; root.dataset.motion = motion ? 'on' : 'off'; };
  updateMotion();
  reduced.addEventListener?.('change', updateMotion);
  const pageVisibility = () => { root.dataset.pageVisible = document.hidden ? 'false' : 'true'; };
  pageVisibility(); document.addEventListener('visibilitychange', pageVisibility);

  let syncCatalogSection = () => {};
  const bar = document.querySelector('.reading-progress span');
  const topButton = document.querySelector('.back-top');
  let scrollFrame = 0;
  const updateScroll = () => {
    const max = root.scrollHeight - window.innerHeight;
    if (bar) bar.style.transform = `scaleX(${max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0})`;
    if (topButton) topButton.hidden = window.scrollY < 650;
    syncCatalogSection();
    scrollFrame = 0;
  };
  const scheduleScroll = () => { if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScroll); };
  window.addEventListener('scroll', scheduleScroll, { passive:true });
  window.addEventListener('resize', scheduleScroll, { passive:true });
  updateScroll();
  topButton?.addEventListener('click', () => {
    window.scrollTo({ top:0, behavior:motion ? 'smooth' : 'instant' });
    const first = document.querySelector('.header .brand');
    first?.focus({ preventScroll:true });
  });

  const sectionLinks = Array.from(document.querySelectorAll('.catalog-nav a[href^="#"]'));
  const sectionSelect = document.getElementById('catalog-section-select');
  if (sectionSelect && sectionLinks.length) {
    sectionLinks.forEach(link => {
      const option = document.createElement('option');
      option.value = link.hash;
      option.textContent = link.textContent.trim();
      sectionSelect.append(option);
    });
    sectionSelect.closest('.catalog-jump').hidden = false;
    document.querySelector('.catalog-nav').classList.add('catalog-nav-enhanced');
    if (sectionLinks.some(link => link.hash === location.hash)) sectionSelect.value = location.hash;
    sectionSelect.addEventListener('change', () => {
      const target = document.getElementById(sectionSelect.value.slice(1));
      if (!target) return;
      target.scrollIntoView({ behavior:motion ? 'smooth' : 'instant', block:'start' });
      history.replaceState(null,'',sectionSelect.value);
    });
  }
  if (sectionLinks.length) {
    const sections = sectionLinks.map(link => document.getElementById(link.hash.slice(1))).filter(Boolean);
    syncCatalogSection = () => {
      const mobile = matchMedia('(max-width:700px)').matches;
      const controls = document.querySelector(mobile ? '.catalog-jump' : '.catalog-nav');
      const offset = (controls?.getBoundingClientRect().height || 60)
        + (parseFloat(getComputedStyle(root).scrollPaddingTop) || 0) + 32;
      const active = sections.filter(section => section.getBoundingClientRect().top <= offset).pop() || sections[0];
      if (!active) return;
      if (sectionSelect && document.activeElement !== sectionSelect) sectionSelect.value = `#${active.id}`;
      sectionLinks.forEach(link => {
        if (link.hash === `#${active.id}`) link.setAttribute('aria-current','location');
        else link.removeAttribute('aria-current');
      });
    };
    syncCatalogSection();
    window.addEventListener('hashchange',syncCatalogSection);
  }

  const viewer = document.querySelector('.image-viewer');
  const galleryLinks = Array.from(document.querySelectorAll('.gallery figure>a, .catalog-screenshot>a'));
  if (viewer && typeof viewer.showModal === 'function' && galleryLinks.length) {
    let current = 0;
    let opener = null;
    const image = viewer.querySelector('img');
    const caption = viewer.querySelector('.viewer-caption');
    const showImage = index => {
      current = (index + galleryLinks.length) % galleryLinks.length;
      const link = galleryLinks[current];
      image.src = link.href;
      image.alt = link.querySelector('img')?.alt || '';
      caption.textContent = link.closest('figure')?.querySelector('figcaption')?.textContent || image.alt;
      viewer.querySelector('.viewer-count').textContent = `${current + 1} / ${galleryLinks.length}`;
    };
    galleryLinks.forEach((link,index) => link.addEventListener('click',event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault(); opener = link; showImage(index); viewer.showModal();
      document.body.classList.add('viewer-open');
    }));
    const close = () => viewer.close();
    viewer.querySelector('[data-viewer-close]').addEventListener('click',close);
    viewer.querySelector('[data-viewer-prev]').addEventListener('click',() => showImage(current-1));
    viewer.querySelector('[data-viewer-next]').addEventListener('click',() => showImage(current+1));
    viewer.querySelector('.viewer-controls').hidden = galleryLinks.length < 2;
    viewer.addEventListener('click', event => { if (event.target === viewer) close(); });
    viewer.addEventListener('keydown', event => {
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
        event.preventDefault();
        const increment = (event.key === 'ArrowRight') !== (root.dir === 'rtl') ? 1 : -1;
        showImage(current + increment);
      }
    });
    viewer.addEventListener('close', () => { document.body.classList.remove('viewer-open'); opener?.focus(); });
  }
})();
