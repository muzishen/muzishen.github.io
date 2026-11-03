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
  const aliases = { application: 'applied', understanding: 'fundamental', reliability: 'fundamental', capabilities: 'fundamental' };
  const setFilter = (filter, updateAddress = true) => {
    const normalized = aliases[filter] || filter;
    const selected = validFilters.has(normalized) ? normalized : 'fundamental';
    let visible = 0;
    papers.forEach(paper => {
      const show = paper.dataset.category === selected;
      paper.hidden = !show;
      if (show) visible += 1;
    });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === selected)));
    if (count) count.textContent = count.dataset.template.replace('{count}', String(visible));
    languageLinks.forEach(link => {
      const destination = new URL(link.dataset.languageLink, location.origin);
      if (selected !== 'fundamental') destination.searchParams.set('topic', selected);
      link.href = destination.pathname + destination.search;
    });
    if (updateAddress) {
      const address = new URL(location.href);
      if (selected === 'fundamental') address.searchParams.delete('topic');
      else address.searchParams.set('topic', selected);
      history.replaceState(null, '', address.pathname + address.search + address.hash);
    }
  };
  buttons.forEach(button => button.addEventListener('click', () => setFilter(button.dataset.filter)));
  const initialTopic = () => {
    const query = new URLSearchParams(location.search).get('topic');
    const anchoredPaper = papers.find(paper => '#' + paper.id === location.hash);
    return query || anchoredPaper?.dataset.category || 'fundamental';
  };
  setFilter(initialTopic(), false);
  addEventListener('popstate', () => setFilter(initialTopic(), false));
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
