/* Native dialog enhancement; source image and PDF links also work without JS. */
(() => {
  'use strict';
  const dialog = document.querySelector('.figure-dialog');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const image = dialog.querySelector('img');
  const title = dialog.querySelector('.figure-dialog-title');
  const close = () => dialog.close();
  document.querySelectorAll('[data-figure-src]').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      image.src = link.dataset.figureSrc;
      image.alt = link.querySelector('img').alt;
      title.textContent = link.dataset.figureTitle;
      dialog.showModal();
      document.documentElement.classList.add('figure-is-open');
    });
  });
  dialog.querySelector('button').addEventListener('click', close);
  dialog.addEventListener('click', event => { if (event.target === dialog) close(); });
  dialog.addEventListener('close', () => document.documentElement.classList.remove('figure-is-open'));
})();
