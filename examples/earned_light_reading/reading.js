'use strict';
const root = document.documentElement;
let size = 21;
document.getElementById('smaller')?.addEventListener('click', () => {
  size = Math.max(17, size - 1);
  root.style.setProperty('--story-size', `${size}px`);
});
document.getElementById('larger')?.addEventListener('click', () => {
  size = Math.min(29, size + 1);
  root.style.setProperty('--story-size', `${size}px`);
});
document.getElementById('theme')?.addEventListener('click', event => {
  const night = document.body.classList.toggle('night');
  event.currentTarget.setAttribute('aria-pressed', String(night));
  event.currentTarget.textContent = night ? 'Day reading' : 'Night reading';
});
