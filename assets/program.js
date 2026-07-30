'use strict';

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
        `Status: execution allowed in the public record (${verified}/${gates.length} gates verified). Check the evidence before treating this as clearance.`,
        'is-good'
      );
    } else {
      setStatus(
        `Status: synthetic cloud dry run blocked (${verified}/${gates.length} gates verified).`,
        'is-blocked'
      );
    }
  } catch {
    setStatus(
      'Status: readiness record could not be loaded. No status is inferred from that failure.',
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

function updateProgramProgress() {
  const bar = document.getElementById('programProgress');
  if (!bar) return;
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
  bar.style.width = `${Math.min(100, progress)}%`;
}
window.addEventListener('scroll', updateProgramProgress, { passive: true });
updateProgramProgress();

const settleBands = [
  {
    max: 20,
    title: 'Lean: only a report',
    body: 'First-person language is treated as weak evidence. You still need a stated criterion, not just style.'
  },
  {
    max: 40,
    title: 'Skeptical',
    body: 'Reports are underweighted. Organization could still matter under some theories.'
  },
  {
    max: 60,
    title: 'Open',
    body: 'A report alone does not fix whether a subject exists or which process it is.'
  },
  {
    max: 80,
    title: 'Lean: subject present',
    body: 'You are treating presence as likely. That is a judgment, not a detection result.'
  },
  {
    max: 100,
    title: 'Lean: real subject',
    body: 'Report content is not the same as subject identity, and neither is experience.'
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

function updateLensMix(value) {
  const copy = document.getElementById('lensMixCopy');
  if (!copy) return;
  if (value < 30) {
    copy.textContent =
      'Judgment is weighted higher. Still ask what a critic would accept as observation.';
  } else if (value > 70) {
    copy.textContent =
      'Evidence is weighted higher. Still ask what harm would mean if a subject were present.';
  } else {
    copy.textContent = 'Judgment and evidence answer different questions. Keep them separate.';
  }
}

const lensMix = document.getElementById('lensMix');
if (lensMix) {
  updateLensMix(Number(lensMix.value));
  lensMix.addEventListener('input', () => updateLensMix(Number(lensMix.value)));
}

const forceCopy = {
  empty: {
    indicates: 'You treat construction or cheap reports as enough to deny a subject.',
    not: 'That current systems are nonconscious. You still need a non-circular criterion.',
    next: 'State what evidence would reverse the judgment, without using private holdouts as public proof.'
  },
  real: {
    indicates: 'You treat first-person language or story continuity as nearly enough for a subject.',
    not: 'That a subject was detected. Producing a report is not the same as referring to, or being, a subject.',
    next: 'Ask for mechanism–report mapping, stability across context changes, and open rival explanations.'
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
    <span class="label">What this choice shows</span>
    <p>${item.indicates}</p>
    <span class="label">What it does not show</span>
    <p>${item.not}</p>
    <span class="label">What would help next</span>
    <p>${item.next}</p>`;
  if (settleSlider) {
    settleSlider.value = kind === 'empty' ? '8' : '92';
    updateSettle(Number(settleSlider.value));
  }
}

document.querySelectorAll('[data-force]').forEach((btn) => {
  btn.addEventListener('click', () => showForce(btn.dataset.force));
});

const layerCopy = {
  origin: {
    title: 'Origin',
    body: 'How the system was produced is a historical question. It does not settle whether anything is present now.'
  },
  content: {
    title: 'Content',
    body: 'What is represented can be generated or false without settling experience.'
  },
  organization: {
    title: 'Organization',
    body: 'How states interact is where measurements can help. It is still not direct access to presence.'
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
