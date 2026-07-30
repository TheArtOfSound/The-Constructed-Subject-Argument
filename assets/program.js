'use strict';

/**
 * Program walkthrough — live status + experiential lab.
 * Every forced conclusion returns what it does and does not establish.
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
  if (!document.getElementById('liveStatusLine')) return;
  try {
    const response = await fetch(readinessUrl, { cache: 'no-store' });
    if (!response.ok) throw new Error(`status ${response.status}`);
    const readiness = await response.json();
    const allowed = readiness.execution_allowed === true;
    const gates = Array.isArray(readiness.preflight_gates) ? readiness.preflight_gates : [];
    const verified = gates.filter((g) => g.status === 'verified').length;
    if (allowed) {
      setStatus(
        `Current status: synthetic cloud run is marked allowed (${verified}/${gates.length} gates verified). Still verify evidence before treating this as clearance.`,
        'is-good'
      );
    } else {
      setStatus(
        `Current status: synthetic cloud dry run is blocked (${verified}/${gates.length} gates verified). That is the accurate public state.`,
        'is-blocked'
      );
    }
  } catch {
    setStatus(
      'Current status: public readiness record could not be loaded. No readiness is inferred from the missing fetch.',
      'is-error'
    );
  }
}

/* Theme */
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

/* Scroll progress */
function updateProgramProgress() {
  const bar = document.getElementById('programProgress');
  if (!bar) return;
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
  bar.style.width = `${Math.min(100, progress)}%`;
}
window.addEventListener('scroll', updateProgramProgress, { passive: true });
updateProgramProgress();

/* Settle slider */
const settleBands = [
  {
    max: 20,
    title: 'Strong “only a report” lean',
    body: 'You treat first-person language as cheap. That may be right—but it still needs architectural and causal reasons, not style alone.'
  },
  {
    max: 40,
    title: 'Skeptical lean',
    body: 'Reports are underweighted. Keep open the possibility that organization still supports a subject under some theories.'
  },
  {
    max: 60,
    title: 'Undecided',
    body: 'A mid-range guess is honest. The report still underdetermines the mechanism and the subject attribution.'
  },
  {
    max: 80,
    title: 'Subject lean',
    body: 'You feel a subject is present. That feeling is a human-lens signal; it is not a detection result.'
  },
  {
    max: 100,
    title: 'Strong “real subject” lean',
    body: 'You treat the report as nearly decisive. The program refuses that shortcut: content is not identity, and report is not experience.'
  }
];

function updateSettle(value) {
  const readout = document.getElementById('settleReadout');
  if (!readout) return;
  const band = settleBands.find((b) => value <= b.max) || settleBands[settleBands.length - 1];
  readout.innerHTML = `<strong>${band.title}</strong><p>${band.body}</p>`;
}

const settleSlider = document.getElementById('settleSlider');
if (settleSlider) {
  updateSettle(Number(settleSlider.value));
  settleSlider.addEventListener('input', () => updateSettle(Number(settleSlider.value)));
}

/* Dual lens mix */
function updateLensMix(value) {
  const copy = document.getElementById('lensMixCopy');
  if (!copy) return;
  if (value < 30) {
    copy.textContent =
      'Human lens dominant: intuition, moral weight, and narrative recognition are loud. Still ask what observations would survive a hostile reviewer.';
  } else if (value > 70) {
    copy.textContent =
      'System lens dominant: architecture, controls, and underdetermination are loud. Still ask what would count as harm if a subject were present.';
  } else {
    copy.textContent =
      'Both lenses stay visible. Feeling and evidence are not the same kind of claim—and neither is a consciousness meter.';
  }
}

const lensMix = document.getElementById('lensMix');
if (lensMix) {
  updateLensMix(Number(lensMix.value));
  lensMix.addEventListener('input', () => updateLensMix(Number(lensMix.value)));
}

/* Force conclusion */
const forceCopy = {
  empty: {
    indicates: 'You treat construction, imitation risk, or report cheapness as decisive against a subject.',
    not:
      'That current systems are nonconscious, or that every first-person report is empty. You still need a non-circular criterion.',
    next: 'Specify the property that would have to be present for you to reverse the judgment, and how it could be measured without private holdouts as public proof.'
  },
  real: {
    indicates: 'You treat fluent first-person language or continuity of story as nearly sufficient for a subject.',
    not:
      'That a subject has been detected. Report production is not report reference, and neither is phenomenal presence.',
    next: 'Demand mechanism–report correspondence, persistence across context shifts, and rivals that remain open under the same transcript.'
  },
  reset: null
};

function showForce(kind) {
  const el = document.getElementById('forceReturn');
  if (!el) return;
  if (kind === 'reset' || !forceCopy[kind]) {
    el.hidden = true;
    el.innerHTML = '';
    if (settleSlider) {
      settleSlider.value = '50';
      updateSettle(50);
    }
    return;
  }
  const item = forceCopy[kind];
  el.hidden = false;
  el.innerHTML = `
    <span class="label">What forcing this indicates</span>
    <p>${item.indicates}</p>
    <span class="label">What it does not establish</span>
    <p>${item.not}</p>
    <span class="label">Next evidence</span>
    <p>${item.next}</p>`;
  if (settleSlider) {
    settleSlider.value = kind === 'empty' ? '8' : '92';
    updateSettle(Number(settleSlider.value));
  }
}

document.querySelectorAll('[data-force]').forEach((btn) => {
  btn.addEventListener('click', () => showForce(btn.dataset.force));
});

/* Layer stack */
const layerCopy = {
  origin: {
    title: 'Origin',
    body: 'How the system was produced matters historically. It does not, by itself, settle whether anything is present now.'
  },
  content: {
    title: 'Content',
    body: 'What is represented—memories, fear, a self-story—can be generated, false, or role-played without settling experience.'
  },
  organization: {
    title: 'Organization',
    body: 'How states interact causally is where scientific evidence can strengthen or weaken. Still not a direct look at presence.'
  },
  experience: {
    title: 'Experience',
    body: 'Whether anything is present for the system is the target property. It is inferred, not read off the screen.'
  }
};

document.querySelectorAll('[data-layer]').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('[data-layer]').forEach((b) => {
      b.classList.remove('is-active');
      b.setAttribute('aria-selected', 'false');
    });
    btn.classList.add('is-active');
    btn.setAttribute('aria-selected', 'true');
    const item = layerCopy[btn.dataset.layer];
    const ret = document.getElementById('layerReturn');
    if (ret && item) {
      ret.innerHTML = `<strong>${item.title}</strong><p>${item.body}</p>`;
    }
  });
});

loadSimpleStatus();
