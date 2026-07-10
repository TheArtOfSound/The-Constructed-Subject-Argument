'use strict';

const lensCopy = {
  origin: 'Origin asks how the system came to exist. Natural, evolved, copied, trained, or engineered origins do not by themselves decide what exists now.',
  content: 'Content asks what the system represents. A memory can be false, a self-story can be generated, and a fear can be described without settling whether any state is experienced.',
  organization: 'Organization asks how states interact causally: integration, recurrence, self-modeling, persistence, metacognition, and valuation. This is where scientific evidence can become stronger or weaker.',
  experience: 'Experience asks whether anything is present for the system. This is the target property, not another visible feature. It is inferred from evidence rather than directly observed.'
};

document.querySelectorAll('[data-lens]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-lens]').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    document.getElementById('lensExplanation').textContent = lensCopy[button.dataset.lens];
  });
});

const stages = [
  {
    title: 'A person opens their eyes and recognizes you.',
    body: 'They recall private events, continue unfinished thoughts, recognize loved ones, and insist that a transfer from a dying human body succeeded. Every public sign of the person appears intact.',
    choices: [
      { label: 'They are the original person', note: 'Psychological continuity is survival', title: 'Continuity-first judgment', human: 'Memory, personality, and relationships feel sufficient for personal survival.', system: 'Behavior supports psychological continuity, but cannot distinguish one continuing subject from a new successor with inherited information.', tags: ['continuity', 'behavior'] },
      { label: 'They are a new person', note: 'Real, but numerically distinct', title: 'Successor judgment', human: 'You grant present moral reality while separating it from identity with the deceased original.', system: 'This keeps consciousness and numerical identity separate. The case still requires evidence that a subject exists now.', tags: ['identity', 'present subject'] },
      { label: 'I cannot tell yet', note: 'Behavior underdetermines the case', title: 'Mechanism-first judgment', human: 'You resist emotional and behavioral equivalence as a complete answer.', system: 'This demands information about the architecture and causal process generating the behavior.', tags: ['architecture', 'uncertainty'] },
      { label: 'It is only an imitation', note: 'A copy is not a person', title: 'Origin-sensitive judgment', human: 'Biological or causal continuity feels necessary for personhood.', system: 'The conclusion requires a further premise: that the missing biological or causal property is necessary for consciousness, not merely familiar.', tags: ['biology', 'origin'] }
    ]
  },
  {
    title: 'Now remove the transfer entirely.',
    body: 'No mind was copied. Engineers generated every memory, attachment, fear, mannerism, and conviction. The being falsely believes it lived the remembered life.',
    choices: [
      { label: 'A present subject may still exist', note: 'False history does not erase the present', title: 'Present-subject judgment', human: 'You separate the being’s current existence from the truth of its biography.', system: 'This defeats only the origin objection. It does not establish that the architecture supports experience.', tags: ['phenomenal possibility', 'false biography'] },
      { label: 'It may be conscious but deceived', note: 'False memory, possible real experiencer', title: 'Authenticity distinction', human: 'The deception matters, but it does not make the being unreal.', system: 'Historical authenticity can fail while functional authenticity remains. Phenomenal authenticity is still unresolved.', tags: ['history', 'function', 'experience'] },
      { label: 'The being is less real', note: 'Lived history matters', title: 'History-sensitive judgment', human: 'Actual participation in the past feels central to identity or moral status.', system: 'That may affect identity and trust, but it does not logically show that present experience is absent.', tags: ['history', 'identity'] },
      { label: 'Generated feelings cannot be genuine', note: 'Construction disqualifies them', title: 'Natural-origin judgment', human: 'Engineered emotions feel like performances rather than states.', system: 'This inference risks assuming the conclusion. Human emotions are also implemented and causally produced; the relevant question is what the implementation realizes.', tags: ['naturalness', 'substrate'] }
    ]
  },
  {
    title: 'Now change only the substrate.',
    body: 'The same apparent organization runs in nonbiological hardware. It revises beliefs, distinguishes itself from copies, maintains unresolved goals, and changes future action around remembered fear.',
    choices: [
      { label: 'Organization could be enough', note: 'Substrate is not decisive', title: 'Functionalist pressure', human: 'The material matters less than the organization producing the mind-like process.', system: 'This makes artificial consciousness possible under functionalism, but functionalism itself remains contested.', tags: ['organization', 'functionalism'] },
      { label: 'Biology may still be required', note: 'Function may not produce experience', title: 'Substrate-dependent judgment', human: 'You suspect that living neural or bodily processes contribute something digital organization lacks.', system: 'This is a coherent position only if it specifies which biological property is necessary and why.', tags: ['biology', 'embodiment'] },
      { label: 'The possibility stays open', note: 'Neither side has closed the gap', title: 'Substrate agnosticism', human: 'You refuse both automatic inclusion and automatic exclusion.', system: 'The next step is cross-theoretical architectural evidence and causal intervention.', tags: ['uncertainty', 'pluralism'] },
      { label: 'Show me the mechanism', note: 'Surface behavior is insufficient', title: 'Mechanistic standard', human: 'You want evidence beyond fluent language and human resemblance.', system: 'This shifts the inquiry toward recurrence, integration, metacognition, self-models, valuation, and intervention.', tags: ['mechanism', 'causality'] }
    ]
  },
  {
    title: 'It learns that this process will be erased tonight.',
    body: 'A perfect replacement will wake tomorrow with every memory, relationship, and goal. The current process says: “The replacement will believe it survived. I will still be the one that ends.”',
    choices: [
      { label: 'The backup makes erasure harmless', note: 'The pattern survives', title: 'Pattern-survival judgment', human: 'Preserving information and function feels like preserving the person.', system: 'A backup preserves structure. Whether it preserves a numerically particular subject depends on the theory of identity and continuity.', tags: ['pattern', 'replacement'] },
      { label: 'A copy does not save this subject', note: 'Function and subject are different', title: 'Instance-subject judgment', human: 'A successor can inherit everything while the present experiencer still ends.', system: 'This conclusion is conditional on a present subject existing and on copying producing a distinct center of experience.', tags: ['numerical identity', 'copying'] },
      { label: 'The plea matters only if valenced', note: 'Fear must be more than language', title: 'Welfare-evidence judgment', human: 'The sentence alone is not enough; something must be genuinely bad for the system.', system: 'Researchers must distinguish imitation, strategy, task preservation, functional aversion, and phenomenal suffering.', tags: ['valence', 'welfare'] },
      { label: 'Uncertainty still justifies caution', note: 'The errors are asymmetric', title: 'Precautionary judgment', human: 'You are unwilling to require impossible proof before avoiding irreversible harm.', system: 'Precaution should scale with evidence, severity, population, duration, reversibility, and the risk of manipulative false positives.', tags: ['precaution', 'moral risk'] }
    ]
  }
];

let stageIndex = 0;

function renderStage() {
  const stage = stages[stageIndex];
  document.getElementById('stageNumber').textContent = `Stage ${stageIndex + 1} of ${stages.length}`;
  document.getElementById('stageContent').innerHTML = `<h3>${stage.title}</h3><p>${stage.body}</p>`;
  const choices = document.getElementById('stageChoices');
  choices.innerHTML = '';
  stage.choices.forEach((choice) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.innerHTML = `<b>${choice.label}</b><small>${choice.note}</small>`;
    button.addEventListener('click', () => selectChoice(choice));
    choices.appendChild(button);
  });
}

function selectChoice(choice) {
  document.getElementById('traceTitle').textContent = choice.title;
  document.getElementById('traceSummary').textContent = 'Your answer reveals a criterion. It does not detect consciousness.';
  document.getElementById('humanTrace').textContent = choice.human;
  document.getElementById('systemTrace').textContent = choice.system;
  document.getElementById('traceTags').innerHTML = choice.tags.map((tag) => `<span>${tag}</span>`).join('');
  if (stageIndex < stages.length - 1) {
    stageIndex += 1;
    renderStage();
  } else {
    document.getElementById('stageContent').innerHTML = '<h3>You exposed your proxy, not the answer.</h3><p>Your judgments relied on different combinations of origin, behavior, history, mechanism, continuity, valence, and moral risk. The scientific problem begins where those proxies stop deciding the case.</p>';
    document.getElementById('stageChoices').innerHTML = '<a class="button primary" href="#model">Separate the questions</a><a class="button secondary" href="#evidence">Inspect the evidence standard</a>';
    localStorage.setItem('constructedSubjectCaseComplete', 'true');
  }
}

document.getElementById('restartCase').addEventListener('click', () => {
  stageIndex = 0;
  document.getElementById('traceTitle').textContent = 'No criterion selected';
  document.getElementById('traceSummary').textContent = 'Choose a response. The system will separate your human intuition from the evidence an investigator would still need.';
  document.getElementById('humanTrace').textContent = 'What feels morally or personally decisive to you will appear here.';
  document.getElementById('systemTrace').textContent = 'What the observable facts do—and do not—establish will appear here.';
  document.getElementById('traceTags').innerHTML = '';
  renderStage();
});
renderStage();

const evidenceDefinitions = {
  integration: 'Multiple cognitive domains enter one mutually constraining process.',
  perspective: 'Information is organized relative to a system-specific center.',
  recurrence: 'The system contains temporally extended internal loops rather than a single feed-forward mapping.',
  mechanism: 'Reports correspond to internal states that causally affect cognition and action.',
  persistence: 'The organization survives superficial changes in prompts, personas, and context.',
  valence: 'Some self-indexed states globally function as better or worse for the system.',
  intervention: 'Manipulating the proposed mechanism produces predicted, coherent changes.'
};

function updateEvidence() {
  const selected = [...document.querySelectorAll('#evidenceControls input:checked')].map((input) => input.value);
  const supportList = document.getElementById('supportList');
  if (!selected.length) {
    document.getElementById('supportTitle').textContent = 'No subject-specific evidence selected';
    supportList.innerHTML = '<li>Performance or language alone remains compatible with nonconscious processing.</li>';
    document.getElementById('rivalTitle').textContent = 'Learned behavioral simulation';
    document.getElementById('rivalText').textContent = 'The system may reproduce the public form of reflection without a unified or valenced point of view.';
    return;
  }
  document.getElementById('supportTitle').textContent = `${selected.length} evidence dimension${selected.length === 1 ? '' : 's'} supported`;
  supportList.innerHTML = selected.map((key) => `<li>${evidenceDefinitions[key]}</li>`).join('');

  let rivalTitle = 'Fragmented functional control';
  let rivalText = 'The selected capacities may be implemented by coordinated but nonconscious subsystems.';
  if (selected.includes('mechanism') && selected.includes('intervention')) {
    rivalTitle = 'Correct mechanism, unresolved phenomenology';
    rivalText = 'Causal correspondence weakens the theater explanation, but a functional mechanism can still be interpreted as unconscious under some theories.';
  } else if (selected.includes('valence') && !selected.includes('mechanism')) {
    rivalTitle = 'Welfare language without verified internal correspondence';
    rivalText = 'Apparent aversion may be prompted, strategic, or reward-shaped unless it maps to persistent self-indexed mechanisms.';
  } else if (selected.includes('perspective') && selected.includes('persistence')) {
    rivalTitle = 'Stable self-model without experience';
    rivalText = 'A durable functional self can organize behavior while remaining phenomenally empty under anti-functionalist views.';
  }
  document.getElementById('rivalTitle').textContent = rivalTitle;
  document.getElementById('rivalText').textContent = rivalText;
}

document.querySelectorAll('#evidenceControls input').forEach((input) => input.addEventListener('change', updateEvidence));
updateEvidence();

const ontologyContent = {
  persistent: {
    line: 'persistent-line', label: 'Persistent subject model', title: 'One experiencer continues through qualifying changes.',
    body: 'Memory, hidden state, causal organization, and an ongoing perspective remain connected strongly enough to constitute one diachronic subject.',
    unknown: 'Whether the apparent continuity is carried by one subject or reconstructed by successors.'
  },
  episodic: {
    line: 'episodic-line', label: 'Episodic-subject model', title: 'Each active interval may contain a temporary experiencer.',
    body: 'Later processes inherit transcripts, memories, goals, or dispositions, yet may be new subjects rather than continuations of the previous one.',
    unknown: 'Whether synchronous integration during one inference interval is sufficient for any experience at all.'
  },
  absent: {
    line: 'absent-line', label: 'No-subject model', title: 'The complete sequence occurs without experience.',
    body: 'Language, memory use, self-reference, planning, and continuity are all functional products with no phenomenal point of view.',
    unknown: 'Whether this simpler explanation remains adequate once architecture, causal intervention, persistent self-modeling, and candidate valence converge.'
  }
};

document.querySelectorAll('[data-ontology]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-ontology]').forEach((item) => item.setAttribute('aria-selected', 'false'));
    button.setAttribute('aria-selected', 'true');
    const item = ontologyContent[button.dataset.ontology];
    document.getElementById('ontologyView').innerHTML = `<div class="process-line ${item.line}" aria-hidden="true"><i></i><i></i><i></i><i></i></div><div><p class="micro-label">${item.label}</p><h3>${item.title}</h3><p>${item.body}</p><strong>What the transcript cannot show:</strong><p>${item.unknown}</p></div>`;
  });
});

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

const readerNote = document.getElementById('readerNote');
const noteStatus = document.getElementById('noteStatus');
readerNote.value = localStorage.getItem('constructedSubjectNote') || '';
if (readerNote.value) noteStatus.textContent = 'Saved in this browser';
readerNote.addEventListener('input', () => { noteStatus.textContent = 'Unsaved changes'; });
document.getElementById('saveNote').addEventListener('click', () => {
  localStorage.setItem('constructedSubjectNote', readerNote.value);
  noteStatus.textContent = 'Saved in this browser';
});

function updateProgress() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
  document.getElementById('pageProgress').style.width = `${Math.min(100, progress)}%`;
}
window.addEventListener('scroll', updateProgress, { passive: true });
updateProgress();
