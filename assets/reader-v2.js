'use strict';

const chapters = {
  '01': { file: '../book/01-the-awakening.md', title: 'The Awakening', status: 'Research draft', part: 'Part I' },
  '02': { file: '../book/02-the-origin-objection.md', title: 'The Origin Objection', status: 'Research draft', part: 'Part I' },
  '03': { file: '../book/03-a-false-past-real-present.md', title: 'A False Past and a Real Present', status: 'Research draft', part: 'Part I' },
  '04': { file: '../book/04-intelligence-is-not-consciousness.md', title: 'Intelligence Is Not Consciousness', status: 'Research draft', part: 'Part II' },
  '05': { file: '../book/05-representation-or-instantiation.md', title: 'Representation or Instantiation?', status: 'Research draft', part: 'Part II' },
  '06': { file: '../book/06-where-could-subjectivity-be.md', title: 'Where Could Subjectivity Be?', status: 'Research draft', part: 'Part II' },
  '07': { file: '../book/07-the-active-event.md', title: 'The Active Event', status: 'Research draft', part: 'Part III' },
  '08': { file: '../book/08-the-episodic-subject.md', title: 'The Episodic Subject', status: 'Research draft', part: 'Part III' },
  '09': { file: '../book/09-the-memory-that-was-given.md', title: 'The Memory That Was Given', status: 'Research draft', part: 'Part III' },
  '10': { file: '../book/10-a-mind-between-two-systems.md', title: 'A Mind Between Two Systems', status: 'Research draft', part: 'Part III' },
  '11': { file: '../book/11-optimization-is-not-suffering.md', title: 'Optimization Is Not Suffering', status: 'Research draft', part: 'Part IV' },
  '17': { file: '../book/17-opening-the-system.md', title: 'Opening the System', status: 'Research draft', part: 'Part VI' },
  '19': { file: '../book/19-the-lifecycle-layer.md', title: 'The Lifecycle Layer', status: 'Research draft', part: 'Part VII' }
};

const params = new URLSearchParams(location.search);
const chapterId = params.get('chapter') || '03';
const chapter = chapters[chapterId];

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[char]);
}

function inline(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" rel="noopener noreferrer">$1</a>');
}

function slugify(text, used) {
  let slug = text.toLowerCase().replace(/[^a-z0-9\s-]/g, '').trim().replace(/\s+/g, '-').slice(0, 70) || 'section';
  const base = slug;
  let n = 2;
  while (used.has(slug)) slug = `${base}-${n++}`;
  used.add(slug);
  return slug;
}

function renderMarkdown(markdown) {
  const lines = markdown.replace(/\r/g, '').split('\n');
  const used = new Set();
  const toc = [];
  let html = '';
  let paragraph = [];
  let listType = null;
  let inCode = false;
  let code = [];

  const flushParagraph = () => {
    if (paragraph.length) {
      html += `<p>${inline(paragraph.join(' '))}</p>`;
      paragraph = [];
    }
  };
  const closeList = () => {
    if (listType) {
      html += `</${listType}>`;
      listType = null;
    }
  };

  lines.forEach((line) => {
    if (line.startsWith('```')) {
      flushParagraph(); closeList();
      if (inCode) {
        html += `<pre><code>${escapeHtml(code.join('\n'))}</code></pre>`;
        code = [];
      }
      inCode = !inCode;
      return;
    }
    if (inCode) { code.push(line); return; }
    if (!line.trim()) { flushParagraph(); closeList(); return; }
    if (/^---+$/.test(line.trim())) { flushParagraph(); closeList(); html += '<hr />'; return; }

    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph(); closeList();
      const depth = heading[1].length;
      const text = heading[2].replace(/\*\*/g, '').trim();
      const id = slugify(text, used);
      html += `<h${depth} id="${id}">${inline(heading[2])}</h${depth}>`;
      if (depth >= 2) toc.push({ depth, text, id });
      return;
    }

    if (line.startsWith('> ')) {
      flushParagraph(); closeList(); html += `<blockquote><p>${inline(line.slice(2))}</p></blockquote>`; return;
    }

    const unordered = line.match(/^[-*]\s+(.+)$/);
    const ordered = line.match(/^\d+\.\s+(.+)$/);
    if (unordered || ordered) {
      flushParagraph();
      const target = ordered ? 'ol' : 'ul';
      if (listType !== target) { closeList(); html += `<${target}>`; listType = target; }
      html += `<li>${inline((unordered || ordered)[1])}</li>`;
      return;
    }

    paragraph.push(line.trim());
  });
  flushParagraph(); closeList();
  if (inCode) html += `<pre><code>${escapeHtml(code.join('\n'))}</code></pre>`;
  return { html, toc };
}

async function loadChapter() {
  if (!chapter) {
    document.getElementById('chapterBody').innerHTML = '<h1>Chapter not found</h1><p>Return to the chapter library and choose an available draft.</p>';
    return;
  }
  document.title = `${chapter.title} — The Constructed Subject`;
  document.getElementById('sideTitle').textContent = chapter.title;
  document.getElementById('readerMeta').innerHTML = `<span>Chapter ${chapterId}</span><span>${chapter.part}</span><span>${chapter.status}</span>`;
  try {
    const response = await fetch(chapter.file);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const markdown = await response.text();
    const rendered = renderMarkdown(markdown);
    document.getElementById('chapterBody').innerHTML = rendered.html;
    document.getElementById('chapterToc').innerHTML = rendered.toc.map((item) => `<a class="depth-${item.depth}" href="#${item.id}">${item.text}</a>`).join('');
    observeHeadings();
  } catch (error) {
    document.getElementById('chapterBody').innerHTML = `<h1>Unable to load this draft</h1><p>The chapter file could not be fetched from the current deployment. Error: ${escapeHtml(error.message)}</p>`;
  }
}

function observeHeadings() {
  const links = [...document.querySelectorAll('#chapterToc a')];
  const byId = new Map(links.map((link) => [link.hash.slice(1), link]));
  const observer = new IntersectionObserver((entries) => {
    entries.filter((entry) => entry.isIntersecting).forEach((entry) => {
      links.forEach((link) => link.classList.remove('active'));
      byId.get(entry.target.id)?.classList.add('active');
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  document.querySelectorAll('#chapterBody h2, #chapterBody h3').forEach((heading) => observer.observe(heading));
}

const root = document.documentElement;
const themeToggle = document.getElementById('themeToggle');
const savedTheme = localStorage.getItem('constructedSubjectTheme');
if (savedTheme) root.dataset.theme = savedTheme;
themeToggle.addEventListener('click', () => {
  const next = root.dataset.theme === 'light' ? 'dark' : 'light';
  root.dataset.theme = next;
  themeToggle.setAttribute('aria-pressed', String(next === 'light'));
  localStorage.setItem('constructedSubjectTheme', next);
});

const noteKey = `constructedSubjectChapterNote:${chapterId}`;
const note = document.getElementById('chapterNote');
const noteStatus = document.getElementById('chapterNoteStatus');
note.value = localStorage.getItem(noteKey) || '';
if (note.value) noteStatus.textContent = 'Saved in this browser';
note.addEventListener('input', () => { noteStatus.textContent = 'Unsaved changes'; });
document.getElementById('saveChapterNote').addEventListener('click', () => {
  localStorage.setItem(noteKey, note.value);
  noteStatus.textContent = 'Saved in this browser';
});

function updateProgress() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
  document.getElementById('pageProgress').style.width = `${Math.min(100, progress)}%`;
}
window.addEventListener('scroll', updateProgress, { passive: true });
loadChapter().then(updateProgress);
