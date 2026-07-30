'use strict';

/**
 * Minimal live status for the walkthrough page.
 * Loads public-safe readiness JSON and shows one plain sentence.
 * Does not invent readiness if the fetch fails.
 */

const readinessUrl = 'research/egc2/expert_reviewer_dry_run_execution_readiness.v0.1.json';

function setStatus(message, tone) {
  const el = document.getElementById('liveStatusLine');
  if (!el) return;
  el.textContent = message;
  el.classList.remove('is-blocked', 'is-good', 'is-error');
  if (tone) el.classList.add(tone);
}

async function loadSimpleStatus() {
  const el = document.getElementById('liveStatusLine');
  if (!el) return;

  try {
    const response = await fetch(readinessUrl, { cache: 'no-store' });
    if (!response.ok) {
      throw new Error(`status ${response.status}`);
    }
    const readiness = await response.json();
    const allowed = readiness.execution_allowed === true;
    const gates = Array.isArray(readiness.preflight_gates) ? readiness.preflight_gates : [];
    const verified = gates.filter((g) => g.status === 'verified').length;

    if (allowed) {
      setStatus(
        `Current status: synthetic cloud run is marked allowed in the public record (${verified}/${gates.length} preflight gates verified). Still verify evidence before treating this as operational clearance.`,
        'is-good'
      );
    } else {
      setStatus(
        `Current status: synthetic cloud dry run is blocked (${verified}/${gates.length} preflight gates verified). That is the accurate public state—not a website placeholder.`,
        'is-blocked'
      );
    }
  } catch (error) {
    setStatus(
      'Current status: public readiness record could not be loaded in this browser. No readiness is inferred from the missing fetch.',
      'is-error'
    );
  }
}

const programRoot = document.documentElement;
const programThemeToggle = document.getElementById('programThemeToggle');
const storedTheme = localStorage.getItem('constructedSubjectTheme');
if (storedTheme) programRoot.dataset.theme = storedTheme;

if (programThemeToggle) {
  programThemeToggle.setAttribute(
    'aria-pressed',
    String(programRoot.dataset.theme === 'light')
  );
  programThemeToggle.addEventListener('click', () => {
    const next = programRoot.dataset.theme === 'light' ? 'dark' : 'light';
    programRoot.dataset.theme = next;
    programThemeToggle.setAttribute('aria-pressed', String(next === 'light'));
    localStorage.setItem('constructedSubjectTheme', next);
  });
}

loadSimpleStatus();
