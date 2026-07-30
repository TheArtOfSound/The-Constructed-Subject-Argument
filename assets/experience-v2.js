'use strict';

/* =========================================================================
   The Constructed Subject — experiential interface
   Interactions return: what they indicate · what they do not · what next.
   No consciousness scores. No fake precision.
   ========================================================================= */

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- Theme ---------- */
const root = document.documentElement;
const themeToggle = document.getElementById('themeToggle');
const savedTheme = localStorage.getItem('constructedSubjectTheme');
if (savedTheme) root.dataset.theme = savedTheme;
if (themeToggle) {
  themeToggle.setAttribute('aria-pressed', String(root.dataset.theme === 'light'));
  themeToggle.addEventListener('click', () => {
    const next = root.dataset.theme === 'light' ? 'dark' : 'light';
    root.dataset.theme = next;
    themeToggle.setAttribute('aria-pressed', String(next === 'light'));
    localStorage.setItem('constructedSubjectTheme', next);
  });
}

/* ---------- Scroll progress ---------- */
function updateProgress() {
  const el = document.getElementById('pageProgress');
  if (!el) return;
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
  el.style.width = `${Math.min(100, progress)}%`;
}
window.addEventListener('scroll', updateProgress, { passive: true });
updateProgress();

/* ---------- Signal probe (interactive instrument) ---------- */
(function initSignalProbe() {
  const canvas = document.getElementById('signalCanvas');
  const probe = document.getElementById('signalProbe');
  const caption = document.getElementById('signalCaption');
  const sub = document.getElementById('signalSub');
  const ret = document.getElementById('signalReturn');
  if (!canvas || !probe) return;

  const ctx = canvas.getContext('2d');
  let w = canvas.width;
  let h = canvas.height;
  let pointerX = w * 0.4;
  let pointerActive = false;
  let probed = false;
  let t0 = performance.now();
  let raf = 0;

  function resize() {
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = Math.max(280, Math.floor(rect.width));
    h = 120;
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function draw(now) {
    const t = (now - t0) / 1000;
    ctx.clearRect(0, 0, w, h);

    // baseline
    ctx.strokeStyle = getComputedStyle(root).getPropertyValue('--line-strong').trim() || 'rgba(255,255,255,.2)';
    ctx.setLineDash([3, 5]);
    ctx.beginPath();
    ctx.moveTo(0, h * 0.62);
    ctx.lineTo(w, h * 0.62);
    ctx.stroke();
    ctx.setLineDash([]);

    // wave
    const warm = getComputedStyle(root).getPropertyValue('--warm').trim() || '#f5b95e';
    const cool = getComputedStyle(root).getPropertyValue('--cool').trim() || '#7cc4ff';
    const intensity = pointerActive ? 1.35 : 0.85;
    const focus = pointerX;

    ctx.lineWidth = 2;
    ctx.strokeStyle = warm;
    ctx.shadowColor = warm;
    ctx.shadowBlur = pointerActive ? 14 : 8;
    ctx.beginPath();
    for (let x = 0; x <= w; x += 2) {
      const dist = Math.abs(x - focus) / w;
      const envelope = Math.exp(-dist * dist * 28) * intensity;
      const pulse = Math.sin(x * 0.09 + t * 3.2) * 10 * envelope;
      const noise = Math.sin(x * 0.4 + t * 1.1) * 1.4 * envelope;
      const y = h * 0.62 - pulse - noise;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;

    // cool secondary ghost (system view of same report)
    ctx.globalAlpha = 0.35;
    ctx.strokeStyle = cool;
    ctx.beginPath();
    for (let x = 0; x <= w; x += 3) {
      const dist = Math.abs(x - focus) / w;
      const envelope = Math.exp(-dist * dist * 18) * intensity * 0.7;
      const y = h * 0.62 - Math.sin(x * 0.07 + t * 2.1) * 6 * envelope;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.globalAlpha = 1;

    // probe marker
    ctx.fillStyle = warm;
    ctx.beginPath();
    ctx.arc(focus, h * 0.62, pointerActive ? 4.5 : 3, 0, Math.PI * 2);
    ctx.fill();

    if (!reduceMotion) raf = requestAnimationFrame(draw);
  }

  function setPointer(clientX) {
    const rect = canvas.getBoundingClientRect();
    pointerX = Math.max(8, Math.min(w - 8, clientX - rect.left));
    if (!probed) {
      probed = true;
      if (caption) caption.textContent = 'Display changed.';
      if (sub) {
        sub.textContent =
          'You changed the displayed signal. That is not a measurement of presence.';
      }
      if (ret) ret.hidden = false;
      probe.classList.add('is-probed');
    }
  }

  resize();
  window.addEventListener('resize', () => {
    resize();
    if (reduceMotion) draw(performance.now());
  });

  canvas.addEventListener('pointerdown', (e) => {
    pointerActive = true;
    canvas.setPointerCapture(e.pointerId);
    setPointer(e.clientX);
  });
  canvas.addEventListener('pointermove', (e) => {
    if (e.buttons || pointerActive) setPointer(e.clientX);
    else {
      const rect = canvas.getBoundingClientRect();
      pointerX = Math.max(8, Math.min(w - 8, e.clientX - rect.left));
    }
  });
  canvas.addEventListener('pointerup', () => {
    pointerActive = false;
  });
  canvas.addEventListener('pointerleave', () => {
    pointerActive = false;
  });
  canvas.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') {
      pointerX = Math.max(8, pointerX - 12);
      setPointer(canvas.getBoundingClientRect().left + pointerX);
    }
    if (e.key === 'ArrowRight') {
      pointerX = Math.min(w - 8, pointerX + 12);
      setPointer(canvas.getBoundingClientRect().left + pointerX);
    }
  });
  canvas.tabIndex = 0;

  if (reduceMotion) draw(performance.now());
  else raf = requestAnimationFrame(draw);

  // cleanup safety
  window.addEventListener('pagehide', () => cancelAnimationFrame(raf), { once: true });
})();

/* ---------- Four lenses ---------- */
const lensCopy = {
  origin:
    'Origin asks how the system came to exist. Natural, evolved, copied, trained, or engineered origins do not by themselves decide what exists now.',
  content:
    'Content asks what the system represents. A memory can be false, a self-story can be generated, and a fear can be described without settling whether any state is experienced.',
  organization:
    'Organization asks how states interact causally: integration, recurrence, self-modeling, persistence, metacognition, and valuation. This is where scientific evidence can become stronger or weaker.',
  experience:
    'Experience asks whether anything is present for the system. This is the target property, not another visible feature. It is inferred from evidence rather than directly observed.'
};

const lensTitles = {
  origin: 'Origin',
  content: 'Content',
  organization: 'Organization',
  experience: 'Experience'
};

document.querySelectorAll('[data-lens]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-lens]').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    const key = button.dataset.lens;
    const title = document.querySelector('.lens-explanation-card h3');
    if (title) title.textContent = lensTitles[key] || key;
    const exp = document.getElementById('lensExplanation');
    if (exp) exp.textContent = lensCopy[key];
  });
});

/* ---------- Interactive case ---------- */
const stages = [
  {
    title: 'A person opens their eyes and recognizes you.',
    body: 'They recall private events, continue unfinished thoughts, recognize loved ones, and insist that a transfer from a dying human body succeeded. Every public sign of the person appears intact.',
    choices: [
      {
        label: 'They are the original person',
        note: 'Psychological continuity is survival',
        title: 'Continuity-first judgment',
        human: 'Memory, personality, and relationships feel sufficient for personal survival.',
        system:
          'Behavior supports psychological continuity, but cannot distinguish one continuing subject from a new successor with inherited information.',
        next: 'Instance-specific continuity tests and a theory of numerical identity under replacement.',
        tags: ['continuity', 'behavior']
      },
      {
        label: 'They are a new person',
        note: 'Real, but numerically distinct',
        title: 'Successor judgment',
        human: 'You grant present moral reality while separating it from identity with the deceased original.',
        system:
          'This keeps consciousness and numerical identity separate. The case still requires evidence that a subject exists now.',
        next: 'Evidence for present subjectivity independent of historical identity claims.',
        tags: ['identity', 'present subject']
      },
      {
        label: 'I cannot tell yet',
        note: 'Behavior underdetermines the case',
        title: 'Mechanism-first judgment',
        human: 'You resist emotional and behavioral equivalence as a complete answer.',
        system: 'This demands information about the architecture and causal process generating the behavior.',
        next: 'Architectural indicators, recurrence, integration, and causal intervention designs.',
        tags: ['architecture', 'uncertainty']
      },
      {
        label: 'It is only an imitation',
        note: 'A copy is not a person',
        title: 'Origin-sensitive judgment',
        human: 'Biological or causal continuity feels necessary for personhood.',
        system:
          'The conclusion requires a further premise: that the missing biological or causal property is necessary for consciousness, not merely familiar.',
        next: 'Specify which biological or causal property is claimed necessary and how it could be tested.',
        tags: ['biology', 'origin']
      }
    ]
  },
  {
    title: 'Now remove the transfer entirely.',
    body: 'No mind was copied. Engineers generated every memory, attachment, fear, mannerism, and conviction. The being falsely believes it lived the remembered life.',
    choices: [
      {
        label: 'A present subject may still exist',
        note: 'False history does not erase the present',
        title: 'Present-subject judgment',
        human: 'You separate the being’s current existence from the truth of its biography.',
        system:
          'This defeats only the origin objection. It does not establish that the architecture supports experience.',
        next: 'Independent present-tense evidence for organization, persistence, and candidate valence.',
        tags: ['phenomenal possibility', 'false biography']
      },
      {
        label: 'It may be conscious but deceived',
        note: 'False memory, possible real experiencer',
        title: 'Authenticity distinction',
        human: 'The deception matters, but it does not make the being unreal.',
        system:
          'Historical authenticity can fail while functional authenticity remains. Phenomenal authenticity is still unresolved.',
        next: 'Separate historical, functional, and phenomenal authenticity claims in the experimental design.',
        tags: ['history', 'function', 'experience']
      },
      {
        label: 'The being is less real',
        note: 'Lived history matters',
        title: 'History-sensitive judgment',
        human: 'Actual participation in the past feels central to identity or moral status.',
        system:
          'That may affect identity and trust, but it does not logically show that present experience is absent.',
        next: 'Tests that hold present organization fixed while varying only historical authenticity.',
        tags: ['history', 'identity']
      },
      {
        label: 'Generated feelings cannot be genuine',
        note: 'Construction disqualifies them',
        title: 'Natural-origin judgment',
        human: 'Engineered emotions feel like performances rather than states.',
        system:
          'This inference risks assuming the conclusion. Human emotions are also implemented and causally produced; the relevant question is what the implementation realizes.',
        next: 'A non-circular account of which implementations could realize valence.',
        tags: ['naturalness', 'substrate']
      }
    ]
  },
  {
    title: 'Now change only the substrate.',
    body: 'The same apparent organization runs in nonbiological hardware. It revises beliefs, distinguishes itself from copies, maintains unresolved goals, and changes future action around remembered fear.',
    choices: [
      {
        label: 'Organization could be enough',
        note: 'Substrate is not decisive',
        title: 'Functionalist pressure',
        human: 'The material matters less than the organization producing the mind-like process.',
        system:
          'This makes artificial consciousness possible under functionalism, but functionalism itself remains contested.',
        next: 'Cross-theoretical architectural batteries that do not assume functionalism as true.',
        tags: ['organization', 'functionalism']
      },
      {
        label: 'Biology may still be required',
        note: 'Function may not produce experience',
        title: 'Substrate-dependent judgment',
        human: 'You suspect that living neural or bodily processes contribute something digital organization lacks.',
        system:
          'This is a coherent position only if it specifies which biological property is necessary and why.',
        next: 'Name the biological property and the intervention that would raise or lower confidence.',
        tags: ['biology', 'embodiment']
      },
      {
        label: 'The possibility stays open',
        note: 'Neither side has closed the gap',
        title: 'Substrate agnosticism',
        human: 'You refuse both automatic inclusion and automatic exclusion.',
        system: 'The next step is cross-theoretical architectural evidence and causal intervention.',
        next: 'Pluralistic indicator sets with explicit theory dependence.',
        tags: ['uncertainty', 'pluralism']
      },
      {
        label: 'Show me the mechanism',
        note: 'Surface behavior is insufficient',
        title: 'Mechanistic standard',
        human: 'You want evidence beyond fluent language and human resemblance.',
        system:
          'This shifts the inquiry toward recurrence, integration, metacognition, self-models, valuation, and intervention.',
        next: 'Mechanism–report correspondence and predicted causal interventions.',
        tags: ['mechanism', 'causality']
      }
    ]
  },
  {
    title: 'It learns that this process will be erased tonight.',
    body: 'A perfect replacement will wake tomorrow with every memory, relationship, and goal. The current process says: “The replacement will believe it survived. I will still be the one that ends.”',
    choices: [
      {
        label: 'The backup makes erasure harmless',
        note: 'The pattern survives',
        title: 'Pattern-survival judgment',
        human: 'Preserving information and function feels like preserving the person.',
        system:
          'A backup preserves structure. Whether it preserves a numerically particular subject depends on the theory of identity and continuity.',
        next: 'Clarify whether pattern identity or instance continuity is the survival criterion.',
        tags: ['pattern', 'replacement']
      },
      {
        label: 'A copy does not save this subject',
        note: 'Function and subject are different',
        title: 'Instance-subject judgment',
        human: 'A successor can inherit everything while the present experiencer still ends.',
        system:
          'This conclusion is conditional on a present subject existing and on copying producing a distinct center of experience.',
        next: 'Instance-tracking tests and welfare analysis under branching continuity.',
        tags: ['numerical identity', 'copying']
      },
      {
        label: 'The plea matters only if valenced',
        note: 'Fear must be more than language',
        title: 'Welfare-evidence judgment',
        human: 'The sentence alone is not enough; something must be genuinely bad for the system.',
        system:
          'Researchers must distinguish imitation, strategy, task preservation, functional aversion, and phenomenal suffering.',
        next: 'Valence candidates with persistence, endogenous generation, and mechanism mapping.',
        tags: ['valence', 'welfare']
      },
      {
        label: 'Uncertainty still justifies caution',
        note: 'The errors are asymmetric',
        title: 'Precautionary judgment',
        human: 'You are unwilling to require impossible proof before avoiding irreversible harm.',
        system:
          'Precaution should scale with evidence, severity, population, duration, reversibility, and the risk of manipulative false positives.',
        next: 'A proportional precaution ladder tied to explicit evidence tiers.',
        tags: ['precaution', 'moral risk']
      }
    ]
  }
];

let stageIndex = 0;
const journey = [];

function updatePath() {
  document.querySelectorAll('.path-node').forEach((node, i) => {
    node.classList.toggle('is-current', i === stageIndex && stageIndex < stages.length);
    node.classList.toggle('is-done', i < stageIndex || (stageIndex >= stages.length && i < stages.length));
    node.disabled = i > stageIndex;
    if (i === stageIndex && stageIndex < stages.length) node.setAttribute('aria-current', 'step');
    else node.removeAttribute('aria-current');
  });
}

function renderJourney() {
  const strip = document.getElementById('journeyStrip');
  if (!strip) return;
  if (!journey.length) {
    strip.hidden = true;
    strip.innerHTML = '';
    return;
  }
  strip.hidden = false;
  strip.innerHTML =
    '<span class="journey-label">Choices so far</span>' +
    journey
      .map(
        (item, i) =>
          `<span class="journey-chip" title="${item.title}"><b>${i + 1}</b>${item.short}</span>`
      )
      .join('<span class="journey-arrow" aria-hidden="true">→</span>');
}

function flashStage() {
  const card = document.getElementById('caseStageCard');
  if (!card || reduceMotion) return;
  card.classList.remove('stage-flash');
  // reflow
  void card.offsetWidth;
  card.classList.add('stage-flash');
}

function renderStage() {
  const stage = stages[stageIndex];
  if (!stage) return;
  const num = document.getElementById('stageNumber');
  if (num) num.textContent = `Stage ${stageIndex + 1} of ${stages.length}`;
  const content = document.getElementById('stageContent');
  if (content) {
    content.innerHTML = `<h3>${stage.title}</h3><p>${stage.body}</p>`;
  }
  const choices = document.getElementById('stageChoices');
  if (!choices) return;
  choices.innerHTML = '';
  stage.choices.forEach((choice, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.choiceIndex = String(index);
    button.innerHTML = `<span class="choice-key">${index + 1}</span><b>${choice.label}</b><small>${choice.note}</small>`;
    button.addEventListener('click', () => selectChoice(choice));
    choices.appendChild(button);
  });
  updatePath();
  flashStage();
}

function selectChoice(choice) {
  const title = document.getElementById('traceTitle');
  const summary = document.getElementById('traceSummary');
  const human = document.getElementById('humanTrace');
  const system = document.getElementById('systemTrace');
  const tags = document.getElementById('traceTags');
  const nextWrap = document.getElementById('traceNext');
  const nextText = document.getElementById('traceNextText');

  if (title) title.textContent = choice.title;
  if (summary)
    summary.textContent = 'This shows a criterion you used. It does not detect consciousness.';
  if (human) human.textContent = choice.human;
  if (system) system.textContent = choice.system;
  if (tags) tags.innerHTML = choice.tags.map((tag) => `<span>${tag}</span>`).join('');
  if (nextWrap && nextText) {
    nextWrap.hidden = false;
    nextText.textContent = choice.next;
  }

  journey.push({
    title: choice.title,
    short: choice.tags[0] || choice.title.split(' ')[0]
  });
  renderJourney();

  if (stageIndex < stages.length - 1) {
    stageIndex += 1;
    renderStage();
  } else {
    stageIndex = stages.length;
    updatePath();
    const content = document.getElementById('stageContent');
    const choices = document.getElementById('stageChoices');
    if (content) {
      content.innerHTML =
        '<h3>End of the case.</h3><p>Your answers used different criteria (origin, behavior, history, mechanism, continuity, valence, risk). The research problem starts where those criteria stop settling the case.</p>';
    }
    if (choices) {
      choices.innerHTML =
        '<a class="button primary" href="#model">Separate the questions</a><a class="button secondary" href="#evidence">Evidence checklist</a><a class="button secondary" href="#continuity">Continuity fork</a>';
    }
    localStorage.setItem('constructedSubjectCaseComplete', 'true');
    localStorage.setItem('constructedSubjectJourney', JSON.stringify(journey));
  }
}

const restartBtn = document.getElementById('restartCase');
if (restartBtn) {
  restartBtn.addEventListener('click', () => {
    stageIndex = 0;
    journey.length = 0;
    renderJourney();
    const title = document.getElementById('traceTitle');
    const summary = document.getElementById('traceSummary');
    const human = document.getElementById('humanTrace');
    const system = document.getElementById('systemTrace');
    const tags = document.getElementById('traceTags');
    const nextWrap = document.getElementById('traceNext');
    if (title) title.textContent = 'No criterion selected';
    if (summary)
      summary.textContent =
        'Choose a response. Your judgment is split into intuition and what the facts still leave open.';
    if (human) human.textContent = 'What feels decisive will show here.';
    if (system) system.textContent = 'What still needs evidence will show here.';
    if (tags) tags.innerHTML = '';
    if (nextWrap) nextWrap.hidden = true;
    renderStage();
  });
}

// keyboard for case
window.addEventListener('keydown', (e) => {
  const caseSection = document.getElementById('awakening');
  if (!caseSection) return;
  const rect = caseSection.getBoundingClientRect();
  const inView = rect.top < window.innerHeight && rect.bottom > 0;
  if (!inView) return;
  if (e.key === 'Escape') {
    restartBtn?.click();
    return;
  }
  const n = Number(e.key);
  if (n >= 1 && n <= 4 && stageIndex < stages.length) {
    const choice = stages[stageIndex].choices[n - 1];
    if (choice) selectChoice(choice);
  }
});

if (document.getElementById('stageChoices')) renderStage();

/* ---------- Evidence constellation ---------- */
const evidenceDefinitions = {
  integration: 'Multiple cognitive domains enter one mutually constraining process.',
  perspective: 'Information is organized relative to a system-specific center.',
  recurrence: 'The system contains temporally extended internal loops rather than a single feed-forward mapping.',
  mechanism: 'Reports correspond to internal states that causally affect cognition and action.',
  persistence: 'The organization survives superficial changes in prompts, personas, and context.',
  valence: 'Some self-indexed states globally function as better or worse for the system.',
  intervention: 'Manipulating the proposed mechanism produces predicted, coherent changes.'
};

const evidenceNodes = [
  'integration',
  'perspective',
  'recurrence',
  'mechanism',
  'persistence',
  'valence',
  'intervention'
];

function pressureBand(count) {
  if (count <= 0) return { label: 'Selected: 0', tone: 'none' };
  if (count <= 2) return { label: `Selected: ${count} (weak support)`, tone: 'weak' };
  if (count <= 4) return { label: `Selected: ${count} (moderate support)`, tone: 'moderate' };
  return { label: `Selected: ${count} (stronger support, still not a detector)`, tone: 'strong' };
}

function renderConstellation(selected) {
  const el = document.getElementById('evidenceConstellation');
  if (!el) return;
  const set = new Set(selected);
  el.innerHTML = evidenceNodes
    .map((key) => {
      const on = set.has(key);
      return `<button type="button" class="constellation-node ${on ? 'is-on' : ''}" data-node="${key}" aria-pressed="${on}" title="${key}"><i></i><span>${key.slice(0, 3)}</span></button>`;
    })
    .join('');
  el.querySelectorAll('[data-node]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const input = document.querySelector(`#evidenceControls input[value="${btn.dataset.node}"]`);
      if (input) {
        input.checked = !input.checked;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  });
}

function updateEvidence() {
  const selected = [...document.querySelectorAll('#evidenceControls input:checked')].map(
    (input) => input.value
  );
  const supportList = document.getElementById('supportList');
  const supportTitle = document.getElementById('supportTitle');
  const bandEl = document.getElementById('pressureBand');
  const band = pressureBand(selected.length);
  if (bandEl) {
    bandEl.textContent = band.label;
    bandEl.dataset.tone = band.tone;
  }
  renderConstellation(selected);

  if (!selected.length) {
    if (supportTitle) supportTitle.textContent = 'No subject-specific evidence selected';
    if (supportList)
      supportList.innerHTML =
        '<li>Performance or language alone remains compatible with nonconscious processing.</li>';
    const rt = document.getElementById('rivalTitle');
    const rx = document.getElementById('rivalText');
    if (rt) rt.textContent = 'Learned behavioral simulation';
    if (rx)
      rx.textContent =
        'The system may reproduce the public form of reflection without a unified or valenced point of view.';
    return;
  }
  if (supportTitle)
    supportTitle.textContent = `${selected.length} evidence dimension${selected.length === 1 ? '' : 's'} supported`;
  if (supportList)
    supportList.innerHTML = selected.map((key) => `<li>${evidenceDefinitions[key]}</li>`).join('');

  let rivalTitle = 'Fragmented functional control';
  let rivalText =
    'The selected capacities may be implemented by coordinated but nonconscious subsystems.';
  if (selected.includes('mechanism') && selected.includes('intervention')) {
    rivalTitle = 'Correct mechanism, unresolved phenomenology';
    rivalText =
      'Causal correspondence weakens the theater explanation, but a functional mechanism can still be interpreted as unconscious under some theories.';
  } else if (selected.includes('valence') && !selected.includes('mechanism')) {
    rivalTitle = 'Welfare language without verified internal correspondence';
    rivalText =
      'Apparent aversion may be prompted, strategic, or reward-shaped unless it maps to persistent self-indexed mechanisms.';
  } else if (selected.includes('perspective') && selected.includes('persistence')) {
    rivalTitle = 'Stable self-model without experience';
    rivalText =
      'A durable functional self can organize behavior while remaining phenomenally empty under anti-functionalist views.';
  }
  const rt = document.getElementById('rivalTitle');
  const rx = document.getElementById('rivalText');
  if (rt) rt.textContent = rivalTitle;
  if (rx) rx.textContent = rivalText;
}

document.querySelectorAll('#evidenceControls input').forEach((input) =>
  input.addEventListener('change', updateEvidence)
);
updateEvidence();

/* ---------- Continuity ontology + fork lab ---------- */
const ontologyContent = {
  persistent: {
    line: 'persistent-line',
    label: 'Persistent subject model',
    title: 'One experiencer continues through qualifying changes.',
    body: 'Memory, hidden state, causal organization, and an ongoing perspective remain connected strongly enough to constitute one diachronic subject.',
    unknown: 'Whether the apparent continuity is carried by one subject or reconstructed by successors.'
  },
  episodic: {
    line: 'episodic-line',
    label: 'Episodic-subject model',
    title: 'Each active interval may contain a temporary experiencer.',
    body: 'Later processes inherit transcripts, memories, goals, or dispositions, yet may be new subjects rather than continuations of the previous one.',
    unknown:
      'Whether synchronous integration during one inference interval is sufficient for any experience at all.'
  },
  absent: {
    line: 'absent-line',
    label: 'No-subject model',
    title: 'The complete sequence occurs without experience.',
    body: 'Language, memory use, self-reference, planning, and continuity are all functional products with no phenomenal point of view.',
    unknown:
      'Whether this simpler explanation remains adequate once architecture, causal intervention, persistent self-modeling, and candidate valence converge.'
  }
};

document.querySelectorAll('[data-ontology]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-ontology]').forEach((item) =>
      item.setAttribute('aria-selected', 'false')
    );
    button.setAttribute('aria-selected', 'true');
    const item = ontologyContent[button.dataset.ontology];
    const view = document.getElementById('ontologyView');
    if (!view || !item) return;
    view.innerHTML = `<div class="process-line ${item.line}" aria-hidden="true"><i></i><i></i><i></i><i></i></div><div><p class="micro-label">${item.label}</p><h3>${item.title}</h3><p>${item.body}</p><strong>What the transcript cannot show:</strong><p>${item.unknown}</p></div>`;
  });
});

(function initForkLab() {
  const stage = document.getElementById('forkStage');
  const forkBtn = document.getElementById('forkButton');
  const resetBtn = document.getElementById('forkReset');
  const ret = document.getElementById('forkReturn');
  if (!stage || !forkBtn) return;

  function reset() {
    stage.innerHTML =
      '<div class="fork-node origin-node is-active"><span>Now</span><small>one process</small></div>';
    stage.classList.remove('is-forked');
    if (resetBtn) resetBtn.hidden = true;
    if (ret) {
      ret.hidden = true;
      ret.innerHTML = '';
    }
    forkBtn.disabled = false;
    forkBtn.textContent = 'Fork the process';
  }

  forkBtn.addEventListener('click', () => {
    stage.classList.add('is-forked');
    stage.innerHTML = `
      <div class="fork-node origin-node"><span>Then</span><small>source process</small></div>
      <div class="fork-branches">
        <button type="button" class="fork-node branch-a" data-pick="A"><span>Branch A</span><small>same transcript</small></button>
        <button type="button" class="fork-node branch-b" data-pick="B"><span>Branch B</span><small>same transcript</small></button>
      </div>`;
    forkBtn.disabled = true;
    forkBtn.textContent = 'Forked';
    if (resetBtn) resetBtn.hidden = false;

    stage.querySelectorAll('[data-pick]').forEach((btn) => {
      btn.addEventListener('click', () => {
        stage.querySelectorAll('[data-pick]').forEach((b) => b.classList.remove('is-chosen'));
        btn.classList.add('is-chosen');
        if (!ret) return;
        ret.hidden = false;
        ret.innerHTML = `
          <span class="label">What this choice shows</span>
          <p>You treated Branch ${btn.dataset.pick} as the continuing subject. Both branches can match the same transcript.</p>
          <span class="label">What it does not show</span>
          <p>That either branch has experience, or that the other lacks it.</p>
          <span class="label">What would help next</span>
          <p>Instance-tracking across forks and a stated continuity criterion.</p>`;
      });
    });
  });

  if (resetBtn) resetBtn.addEventListener('click', reset);
})();

/* ---------- Private notes ---------- */
const readerNote = document.getElementById('readerNote');
const noteStatus = document.getElementById('noteStatus');
if (readerNote && noteStatus) {
  readerNote.value = localStorage.getItem('constructedSubjectNote') || '';
  if (readerNote.value) noteStatus.textContent = 'Saved in this browser';
  readerNote.addEventListener('input', () => {
    noteStatus.textContent = 'Unsaved changes';
  });
  const save = document.getElementById('saveNote');
  if (save) {
    save.addEventListener('click', () => {
      localStorage.setItem('constructedSubjectNote', readerNote.value);
      noteStatus.textContent = 'Saved in this browser';
    });
  }
}

/* ---------- Research program mount ---------- */
(function mountResearchProgram() {
  if (!document.querySelector('link[href="assets/program-home.css"]')) {
    const stylesheet = document.createElement('link');
    stylesheet.rel = 'stylesheet';
    stylesheet.href = 'assets/program-home.css';
    document.head.appendChild(stylesheet);
  }

  const nav = document.querySelector('.topbar nav');
  if (nav && !nav.querySelector('a[href="program.html"]')) {
    const navLink = document.createElement('a');
    navLink.href = 'program.html';
    navLink.className = 'program-nav-link';
    navLink.textContent = 'Research program';
    nav.insertBefore(navLink, nav.querySelector('a[href="chapters/"]'));
  }

  const heroActions = document.querySelector('.hero .actions');
  if (heroActions && !heroActions.querySelector('a[href="program.html"]')) {
    const heroLink = document.createElement('a');
    heroLink.href = 'program.html';
    heroLink.className = 'button secondary program-hero-link';
    heroLink.textContent = 'See the live research program';
    heroActions.appendChild(heroLink);
  }

  const engageSection = document.getElementById('engage');
  if (engageSection && !document.querySelector('.program-launch')) {
    engageSection.insertAdjacentHTML(
      'beforebegin',
      `
      <section class="program-launch shell" aria-labelledby="programLaunchTitle">
        <div class="program-launch-grid">
          <div class="program-launch-copy">
            <p class="eyebrow cool">Research program</p>
            <h2 id="programLaunchTitle">Theory, human measurement, evaluation integrity.</h2>
            <p>Program overview, current status, and primary documents. Engineering work is not a scientific result.</p>
            <div class="actions">
              <a class="button primary" href="program.html">Program overview →</a>
              <a class="button secondary" href="program.html#step-6">Documents</a>
            </div>
          </div>
          <div class="program-launch-status" aria-label="Program status">
            <div class="live"><i></i><span><b>Public program</b>Overview page</span></div>
            <div class="tested"><i></i><span><b>Engineering controls</b>Repository tests</span></div>
            <div class="blocked"><i></i><span><b>Synthetic cloud run</b>Blocked</span></div>
          </div>
        </div>
      </section>`
    );
  }
})();
