'use strict';

const root = document.documentElement;
const themeToggle = document.getElementById('themeToggle');
const savedTheme = localStorage.getItem('constructedSubjectTheme');
if (savedTheme) root.dataset.theme = savedTheme;

themeToggle.addEventListener('click', () => {
  const next = root.dataset.theme === 'light' ? 'dark' : 'light';
  root.dataset.theme = next;
  localStorage.setItem('constructedSubjectTheme', next);
});

function updateProgress() {
  const available = document.documentElement.scrollHeight - window.innerHeight;
  const progress = available > 0 ? (window.scrollY / available) * 100 : 0;
  document.getElementById('readingProgress').style.width = `${Math.min(progress, 100)}%`;
}
window.addEventListener('scroll', updateProgress, { passive: true });
updateProgress();

document.querySelectorAll('[data-reveal]').forEach((button) => {
  button.addEventListener('click', () => {
    const target = document.getElementById(button.dataset.reveal);
    const nextHidden = !target.hidden;
    target.hidden = nextHidden;
    button.textContent = nextHidden ? 'Reveal the decomposition' : 'Hide the decomposition';
  });
});

const navLinks = [...document.querySelectorAll('#chapterNav a')];
const sections = [...document.querySelectorAll('[data-section]')];
const observer = new IntersectionObserver((entries) => {
  const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
  if (!visible) return;
  navLinks.forEach((link) => link.classList.toggle('active', link.getAttribute('href') === `#${visible.target.id}`));
}, { rootMargin: '-20% 0px -65% 0px', threshold: [0.05, 0.2, 0.5] });
sections.forEach((section) => observer.observe(section));

const note = document.getElementById('chapterNote');
const status = document.getElementById('noteStatus');
const key = 'constructedSubjectChapter1Note';
note.value = localStorage.getItem(key) || '';
if (note.value) status.textContent = 'Saved in this browser';
note.addEventListener('input', () => { status.textContent = 'Unsaved changes'; });
document.getElementById('saveNote').addEventListener('click', () => {
  localStorage.setItem(key, note.value);
  status.textContent = 'Saved in this browser';
});
