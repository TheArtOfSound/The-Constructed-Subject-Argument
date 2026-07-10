'use strict';

const params = new URLSearchParams(location.search);
const chapterId = params.get('chapter') || '03';
let chapter = null;
let chapterRegistry = {};

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[char]);
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
      flushParagraph();
      closeList();
      if (inCode) {
        html += `<pre><code>${escapeHtml(code.join('\n'))}</code></pre>`;
        code = [];
      }
      inCode = !inCode;
      return;
    }
    if (inCode) {
      code.push(line);
      return;
    }
    if (!line.trim()) {
      flushParagraph();
      closeList();
      return;
    }
    if (/^---+$/.test(line.trim())) {
      flushParagraph();
      closeList();
      html += '<hr />';
      return;
    }

    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      closeList();
      const depth = heading[1].length;
      const text = heading[2].replace(/\*\*/g, '').trim();
      const id = slugify(text, used);
      html += `<h${depth} id="${id}">${inline(heading[2])}</h${depth}>`;
      if (depth >= 2) toc.push({ depth, text, id });
      return;
    }

    if (line.startsWith('> ')) {
      flushParagraph();
      closeList();
      html += `<blockquote><p>${inline(line.slice(2))}</p></blockquote>`;
      return;
    }

    const unordered = line.match(/^[-*]\s+(.+)$/);
    const ordered = line.match(/^\d+\.\s+(.+)$/);
    if (unordered || ordered) {
      flushParagraph();
      const target = ordered ? 'ol' : 'ul';
      if (listType !== target) {
        closeList();
        html += `<${target}>`;
        listType = target;
      }
      html += `<li>${inline((unordered || ordered)[1])}</li>`;
      return;
    }

    paragraph.push(line.trim());
  });

  flushParagraph();
  closeList();
  if (inCode) html += `<pre><code>${escapeHtml(code.join('\n'))}</code></pre>`;
  return { html, toc };
}

function sequenceNavigation() {
  const ids = Object.keys(chapterRegistry).sort((a, b) => Number(a) - Number(b));
  const index = ids.indexOf(chapterId);
  const previousId = index > 0 ? ids[index - 1] : null;
  const nextId = index >= 0 && index < ids.length - 1 ? ids[index + 1] : null;
  const link = (id, direction) => {
    if (!id) return '<span></span>';
    const target = chapterRegistry[id];
    return `<a href="read.html?chapter=${id}"><small>${direction}</small><strong>${escapeHtml(target.title)}</strong></a>`;
  };
  return `<nav class="chapter-sequence" aria-label="Adjacent readable chapters">${link(previousId, 'Previous readable chapter')}${link(nextId, 'Next readable chapter')}</nav>`;
}

const reviewStateLabels = {
  unreviewed: 'Unreviewed',
  adversarially_specified: 'Objection specified',
  source_grounded: 'Source grounded',
  survives_review: 'Survives review',
  revised: 'Revised',
  withdrawn: 'Withdrawn'
};

function evidenceForReview(review, evidencePayload) {
  const edgeIds = new Set(review.adversarial_evidence_edges || []);
  const sources = new Map((evidencePayload.sources || []).map((source) => [source.id, source]));
  return (evidencePayload.edges || [])
    .filter((edge) => edge.proposition_id === review.proposition_id || edgeIds.has(edge.id))
    .map((edge) => ({ edge, source: sources.get(edge.source_id) }))
    .filter(({ source }) => source);
}

function reviewMilestones(review) {
  const labels = {
    countermodel_specified: 'Countermodel',
    forced_concession_recorded: 'Concession',
    confidence_lowering_test_recorded: 'Discriminating test',
    opposing_source_grounded: 'Opposing source',
    experiment_linked: 'Experiment'
  };
  return Object.entries(labels).map(([key, label]) => {
    const complete = Boolean(review.milestones?.[key]);
    return `<span class="review-milestone ${complete ? 'complete' : 'missing'}"><span aria-hidden="true">${complete ? '✓' : '○'}</span>${label}</span>`;
  }).join('');
}

function reviewEvidenceHtml(review, evidencePayload) {
  const evidence = evidenceForReview(review, evidencePayload);
  if (!evidence.length) {
    return `<div class="review-evidence missing-evidence"><strong>No opposing source grounded yet</strong><p>${escapeHtml(review.required_next_evidence)}</p></div>`;
  }
  return evidence.map(({ edge, source }) => `
    <div class="review-evidence">
      <div class="evidence-heading"><span>${escapeHtml(edge.relationship.replace(/_/g, ' '))}</span><span>${escapeHtml(source.verification_status.replace(/_/g, ' '))}</span></div>
      <strong>${escapeHtml(source.authors.join(' & '))} (${escapeHtml(source.year)}), <em>${escapeHtml(source.title)}</em></strong>
      <p>${escapeHtml(edge.objection_scope)}</p>
      <p class="evidence-boundary"><strong>Does not establish:</strong> ${escapeHtml(edge.does_not_support)}</p>
      <small>${escapeHtml(edge.pinpoint_locator.value)}</small>
    </div>
  `).join('');
}

function manuscriptLinkForReview(review, linksPayload) {
  return (linksPayload.links || []).find((link) => link.proposition_id === review.proposition_id && link.chapter_id === chapterId);
}

function renderReviewCard(review, evidencePayload, linksPayload) {
  const state = reviewStateLabels[review.current_state] || review.current_state;
  const manuscriptLink = manuscriptLinkForReview(review, linksPayload);
  const manuscriptTrace = manuscriptLink
    ? `<a class="manuscript-trace" href="#${escapeHtml(manuscriptLink.anchor)}"><span>Read the claim in the chapter</span><small>${escapeHtml(manuscriptLink.heading)}</small></a>`
    : '<p class="review-status-note">No manuscript anchor is registered for this proposition.</p>';
  return `
    <article class="adversarial-card" id="review-${escapeHtml(review.proposition_id.toLowerCase())}">
      <header>
        <div><span class="proposition-id">${escapeHtml(review.proposition_id)}</span><h3>${escapeHtml(review.surviving_narrowed_claim)}</h3></div>
        <span class="review-state state-${escapeHtml(review.current_state)}">${escapeHtml(state)}</span>
      </header>
      ${manuscriptTrace}
      <div class="review-milestones" aria-label="Review milestones">${reviewMilestones(review)}</div>
      <details open>
        <summary>Strongest live countermodel</summary>
        <p>${escapeHtml(review.strongest_countermodel)}</p>
        <ol>${review.critic_inferential_route.map((step) => `<li>${escapeHtml(step)}</li>`).join('')}</ol>
      </details>
      <details>
        <summary>Concession forced by the objection</summary>
        <p>${escapeHtml(review.forced_concession)}</p>
      </details>
      <details>
        <summary>What would lower confidence?</summary>
        <p>${escapeHtml(review.confidence_lowering_test)}</p>
      </details>
      ${reviewEvidenceHtml(review, evidencePayload)}
      ${review.status_note ? `<p class="review-status-note">${escapeHtml(review.status_note)}</p>` : ''}
    </article>
  `;
}

async function loadAdversarialReviewPanel() {
  try {
    const [reviewsResponse, evidenceResponse, protocolResponse, linksResponse] = await Promise.all([
      fetch('../research/ADVERSARIAL_REVIEWS.json'),
      fetch('../research/ADVERSARIAL_EVIDENCE.json'),
      fetch('../research/MECHANISM_PRESERVATION_PROTOCOL.json'),
      fetch('../research/MANUSCRIPT_PROPOSITION_LINKS.json')
    ]);
    if (!reviewsResponse.ok || !evidenceResponse.ok || !protocolResponse.ok || !linksResponse.ok) throw new Error('review data unavailable');
    const [reviewsPayload, evidencePayload, protocolPayload, linksPayload] = await Promise.all([
      reviewsResponse.json(), evidenceResponse.json(), protocolResponse.json(), linksResponse.json()
    ]);
    const reviews = reviewsPayload.reviews || [];
    const grounded = reviews.filter((review) => ['source_grounded', 'survives_review'].includes(review.current_state)).length;
    const survived = reviews.filter((review) => review.current_state === 'survives_review').length;
    return `
      <section class="adversarial-review-panel" id="adversarial-review" aria-labelledby="adversarial-review-title">
        <div class="review-panel-intro">
          <p class="kicker">Live epistemic audit</p>
          <h2 id="adversarial-review-title">The argument under pressure</h2>
          <p>This panel exposes the strongest registered objections, the concessions they force, and the evidence still missing. A source-grounded objection has entered the literature record; it has not thereby been defeated or shown to succeed.</p>
          <div class="review-summary"><span><strong>${reviews.length}</strong> high-confidence propositions tracked</span><span><strong>${grounded}</strong> source grounded</span><span><strong>${survived}</strong> survived experimental review</span></div>
          <p class="epistemic-boundary"><strong>Boundary:</strong> ${escapeHtml(protocolPayload.epistemic_boundary.tests)} It does not determine phenomenal consciousness, sentience, personhood, or moral status.</p>
        </div>
        <div class="adversarial-grid">${reviews.map((review) => renderReviewCard(review, evidencePayload, linksPayload)).join('')}</div>
      </section>
    `;
  } catch (error) {
    return `<section class="adversarial-review-panel review-load-error"><h2>Adversarial review data unavailable</h2><p>The chapter remains readable, but the machine-readable review records could not be loaded from this deployment.</p></section>`;
  }
}

async function loadChapter() {
  try {
    const registryResponse = await fetch('chapters.json');
    if (!registryResponse.ok) throw new Error(`Registry HTTP ${registryResponse.status}`);
    const registryPayload = await registryResponse.json();
    chapterRegistry = registryPayload.chapters || {};
    chapter = chapterRegistry[chapterId];

    if (!chapter) {
      document.getElementById('chapterBody').innerHTML = '<h1>Chapter not found</h1><p>Return to the chapter library and choose an available draft.</p>';
      return;
    }

    document.title = `${chapter.title} — The Constructed Subject`;
    document.getElementById('sideTitle').textContent = chapter.title;
    document.getElementById('readerMeta').innerHTML = `<span>Chapter ${chapterId}</span><span>${chapter.part}</span><span>${chapter.status}</span>`;

    const response = await fetch(chapter.file);
    if (!response.ok) throw new Error(`Chapter HTTP ${response.status}`);
    const markdown = await response.text();
    const rendered = renderMarkdown(markdown);
    const adversarialPanel = chapterId === '06' ? await loadAdversarialReviewPanel() : '';
    document.getElementById('chapterBody').innerHTML = `${rendered.html}${adversarialPanel}${sequenceNavigation()}`;
    const toc = [...rendered.toc];
    if (chapterId === '06') toc.push({ depth: 2, text: 'Adversarial review — live research state', id: 'adversarial-review' });
    document.getElementById('chapterToc').innerHTML = toc.map((item) => `<a class="depth-${item.depth}" href="#${item.id}">${item.text}</a>`).join('');
    observeHeadings();
  } catch (error) {
    document.getElementById('chapterBody').innerHTML = `<h1>Unable to load this draft</h1><p>The chapter registry or manuscript file could not be fetched from the current deployment. Error: ${escapeHtml(error.message)}</p>`;
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
note.addEventListener('input', () => {
  noteStatus.textContent = 'Unsaved changes';
});
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
