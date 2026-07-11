'use strict';

const REPORT_PATH = 'research/MECHANISM_PRESERVATION_CLASSIFICATION_MUTATION_REPORT.json';

const categoryFor = (result) => {
  const operation = result.target.operation;
  if (operation === 'replace_priority') return result.mutation_id.includes('fallback') ? 'fallback' : 'priority';
  if (operation === 'replace_rule_match' || result.target.to === 'all_true' || result.target.to === 'any_true') return 'connective';
  return 'threshold';
};

const readable = (value) => {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'string') return value.replaceAll('_', ' ');
  return String(value);
};

const changeLabel = (result) => {
  const target = result.target;
  if (target.operation === 'replace_priority') return `priority ${target.from} → ${target.to}`;
  if (target.operation === 'replace_rule_match') return `${target.from} → ${target.to}`;
  if (target.field_name) return `${target.field_name}: ${target.from} → ${target.to}`;
  return `${target.from} → ${target.to}`;
};

let report;
let activeFilter = 'all';
let selectedId;

function renderSummary() {
  document.getElementById('mutationCount').textContent = report.summary.mutation_count;
  document.getElementById('killedCount').textContent = report.summary.killed_count;
  document.getElementById('survivedCount').textContent = report.summary.survived_count;
  document.getElementById('mutationScore').textContent = `${report.summary.killed_count}/${report.summary.mutation_count} registered`;
}

function renderList() {
  const container = document.getElementById('mutationList');
  const visible = report.results.filter((result) => activeFilter === 'all' || categoryFor(result) === activeFilter);
  container.innerHTML = '';

  visible.forEach((result) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `mutation-button${selectedId === result.mutation_id ? ' active' : ''}`;
    button.dataset.mutationId = result.mutation_id;
    button.innerHTML = `<span class="row"><b>${result.mutation_id.replaceAll('-', ' ')}</b><span class="mutation-badge">${result.killed ? 'detected' : 'survived'}</span></span><small>${result.description}</small>`;
    button.addEventListener('click', () => {
      selectedId = result.mutation_id;
      renderList();
      renderDetail(result);
    });
    container.appendChild(button);
  });

  if (!visible.length) container.innerHTML = '<p class="audit-error">No registered mutations match this filter.</p>';
  if (visible.length && !visible.some((result) => result.mutation_id === selectedId)) {
    selectedId = visible[0].mutation_id;
    renderDetail(visible[0]);
    container.querySelector('[data-mutation-id]')?.classList.add('active');
  }
}

function renderDetail(result) {
  const kill = result.representative_kill;
  const target = result.target;
  const targetPath = [target.rule_id, target.predicate_id, target.field_name].filter(Boolean).join(' · ');
  const detail = document.getElementById('mutationDetail');
  detail.innerHTML = `
    <p class="micro-label">${categoryFor(result)} mutation · ${result.killed ? 'detected' : 'survived'}</p>
    <h3>${result.description}</h3>
    <p class="description">Target: <code>${targetPath}</code>. The same synthetic evidence is evaluated under the normative rule and the deliberately corrupted rule.</p>
    <div class="rule-change" aria-label="Original and mutated rule values">
      <div class="rule-box"><span>Normative value</span><code>${readable(target.from)}</code></div>
      <div class="rule-arrow" aria-hidden="true">→</div>
      <div class="rule-box"><span>Corrupted value</span><code>${readable(target.to)}</code></div>
    </div>
    <div class="scenario">
      <span class="scenario-id">Detecting fixture · ${kill.case_id}</span>
      <div class="comparison">
        <div class="outcome baseline"><span>Baseline conclusion</span><strong>${readable(kill.baseline.classification)}</strong><p>${readable(kill.baseline.rule_id)}</p></div>
        <div class="outcome mutant"><span>Mutant conclusion</span><strong>${readable(kill.mutant.classification)}</strong><p>${readable(kill.mutant.rule_id)}</p></div>
      </div>
      <p class="score-invariant"><strong>Evidence held fixed:</strong> weighted score ${kill.baseline.weighted_score}. The conclusion changed because policy interpretation changed, not because the evidence changed.</p>
    </div>
    <p class="description"><strong>What this demonstrates:</strong> the registered fixture suite is sensitive to this specific corruption. It does not establish that the unmutated policy is scientifically optimal.</p>`;
}

function bindFilters() {
  document.querySelectorAll('[data-filter]').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('[data-filter]').forEach((item) => item.classList.remove('active'));
      button.classList.add('active');
      activeFilter = button.dataset.filter;
      renderList();
    });
  });
}

async function init() {
  try {
    const response = await fetch(REPORT_PATH, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Report request failed with ${response.status}`);
    report = await response.json();
    if (!report?.summary || !Array.isArray(report.results)) throw new Error('Report structure is invalid');
    renderSummary();
    bindFilters();
    selectedId = report.results[0]?.mutation_id;
    renderList();
    if (report.results[0]) renderDetail(report.results[0]);
  } catch (error) {
    document.getElementById('mutationList').innerHTML = `<p class="audit-error">The canonical mutation report could not be loaded. ${error.message}</p>`;
    document.getElementById('mutationDetail').innerHTML = '<p class="audit-error">Audit data unavailable. Inspect the raw report and repository validation status before drawing any conclusion.</p>';
  }
}

init();
