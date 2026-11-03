/* Progressive enhancement: every paper and language remains accessible without JavaScript. */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const papers = [...document.querySelectorAll('[data-category]')];
  const count = document.querySelector('[data-result-count]');
  const menuToggle = document.querySelector('[data-menu-toggle]');
  const navigation = document.querySelector('#site-navigation');
  const languageLinks = [...document.querySelectorAll('[data-language-link]')];
  const validFilters = new Set(buttons.map(button => button.dataset.filter));
  const setFilter = (filter, updateAddress = true) => {
    const selected = validFilters.has(filter) ? filter : 'all';
    let visible = 0;
    papers.forEach(paper => {
      const show = selected === 'all' || paper.dataset.category === selected;
      paper.hidden = !show;
      if (show) visible += 1;
    });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === selected)));
    if (count) count.textContent = count.dataset.template.replace('{count}', String(visible));
    languageLinks.forEach(link => {
      const destination = new URL(link.dataset.languageLink, location.origin);
      if (selected !== 'all') destination.searchParams.set('topic', selected);
      link.href = destination.pathname + destination.search;
    });
    if (updateAddress) {
      const address = new URL(location.href);
      if (selected === 'all') address.searchParams.delete('topic');
      else address.searchParams.set('topic', selected);
      history.replaceState(null, '', address.pathname + address.search + address.hash);
    }
  };
  buttons.forEach(button => button.addEventListener('click', () => setFilter(button.dataset.filter)));
  setFilter(new URLSearchParams(location.search).get('topic') || 'all', false);
  addEventListener('popstate', () => setFilter(new URLSearchParams(location.search).get('topic') || 'all', false));
  if (menuToggle && navigation) {
    const closeMenu = () => {
      menuToggle.setAttribute('aria-expanded', 'false');
      navigation.classList.remove('is-open');
    };
    menuToggle.addEventListener('click', () => {
      const expanded = menuToggle.getAttribute('aria-expanded') !== 'true';
      menuToggle.setAttribute('aria-expanded', String(expanded));
      navigation.classList.toggle('is-open', expanded);
    });
    navigation.addEventListener('click', event => {
      if (event.target.closest('a')) closeMenu();
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && navigation.classList.contains('is-open')) {
        closeMenu();
        menuToggle.focus();
      }
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('.site-header')) closeMenu();
    });
  }
})();
