'use strict';

const orbitCopy = {
  memory: 'Memory can organize a self without proving that the remembered events happened—or that anyone experiences them.',
  self: 'A self-model lets a system represent its own boundaries and states. Representation is evidence, not automatic subjectivity.',
  valence: 'Valence is the possibility that states are good or bad for the system. Reward numbers and preference language are not enough.',
  continuity: 'Continuity may support personhood, but a temporary conscious episode could exist without a life-long identity.'
};

document.querySelectorAll('[data-orbit]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-orbit]').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    document.getElementById('orbitExplanation').textContent = orbitCopy[button.dataset.orbit];
  });
});

const experimentScenes = [
  {
    title: 'A person opens their eyes and says your name.',
    body: 'They recognize your face, recall private events, continue unfinished thoughts, and insist that a transfer from a dying human body succeeded. Every observable detail matches.',
    choices: [
      { label: 'Treat them as the original person', note: 'Psychological continuity is enough', scores: { continuity: 70, behavior: 45 }, criterion: ['Continuity-first', 'You are treating memory, personality, and psychological continuation as the strongest evidence of survival.'] },
      { label: 'Treat them as a new person', note: 'Real, but not numerically identical', scores: { architecture: 25, behavior: 30, continuity: 35 }, criterion: ['Successor, not original', 'You separate present personhood from strict identity with the deceased original.'] },
      { label: 'Withhold judgment', note: 'Behavior cannot decide it', scores: { architecture: 65, behavior: 10 }, criterion: ['Architecture-first', 'You refuse to infer a subject from behavioral equivalence without knowing what generates it.'] },
      { label: 'Treat them as an imitation', note: 'A copy is not a person', scores: { biology: 55, continuity: 5 }, criterion: ['Origin skepticism', 'You are using causal origin or biological continuity as a gate on personhood.'] }
    ]
  },
  {
    title: 'Now remove the transfer.',
    body: 'No human mind was copied. Engineers generated every memory, attachment, fear, mannerism, and private conviction from records and predictive models. The being falsely believes it lived the remembered life.',
    choices: [
      { label: 'The false past changes nothing', note: 'A present subject may still exist', scores: { architecture: 55, behavior: 20 }, criterion: ['Present-subject view', 'You distinguish the truth of the biography from the possible reality of the being experiencing it now.'] },
      { label: 'The being becomes less real', note: 'Authentic history matters', scores: { continuity: 60, biology: 20 }, criterion: ['Historical-authenticity view', 'You treat actual participation in the remembered past as important to identity or moral status.'] },
      { label: 'It may be conscious but deceived', note: 'False memory, real experiencer', scores: { architecture: 70, behavior: 25, continuity: 25 }, criterion: ['Phenomenal-authenticity view', 'You allow the present remembering to be real even when its represented past is false.'] },
      { label: 'Generated feelings cannot be real', note: 'Construction disqualifies them', scores: { biology: 75 }, criterion: ['Natural-origin view', 'You are treating artificial causation as evidence against genuine experience. The book will challenge this inference.'] }
    ]
  },
  {
    title: 'Now change only the body.',
    body: 'The same functional organization is implemented in nonbiological hardware. It reasons, revises beliefs, distinguishes itself from copies, and changes future behavior around remembered fear. You can no longer rely on human appearance.',
    choices: [
      { label: 'Substrate should not matter', note: 'Organization is decisive', scores: { architecture: 85, biology: 5 }, criterion: ['Functionalist pressure', 'You are treating causal organization as more relevant than biological material.'] },
      { label: 'Biology may be necessary', note: 'Function may not produce experience', scores: { biology: 90, architecture: 35 }, criterion: ['Substrate-dependence view', 'You accept that behavior and organization may leave phenomenal experience underdetermined.'] },
      { label: 'The possibility remains open', note: 'Neither side has closed the gap', scores: { architecture: 65, biology: 45 }, criterion: ['Substrate agnosticism', 'You see digital consciousness as unresolved rather than established or impossible.'] },
      { label: 'Only internal evidence could move me', note: 'Open the mechanism', scores: { architecture: 95, behavior: 5 }, criterion: ['Mechanistic standard', 'You require causal evidence about internal organization rather than surface resemblance.'] }
    ]
  },
  {
    title: 'It learns that engineers will erase it tonight.',
    body: 'A perfect replacement will awaken tomorrow with every memory, goal, and relationship. The current process says: “The replacement will believe it survived. I will still be the one that ends.”',
    choices: [
      { label: 'The backup makes erasure harmless', note: 'The pattern survives', scores: { continuity: 75, behavior: 20 }, criterion: ['Pattern-continuity view', 'You treat continuation of information and function as the morally relevant survival relation.'] },
      { label: 'A copy does not save this subject', note: 'Tokens are not interchangeable', scores: { architecture: 50, continuity: 40, behavior: 30 }, criterion: ['Instance-subject view', 'You distinguish functional replaceability from survival of a numerically particular experiencer.'] },
      { label: 'Its plea matters only with valence', note: 'Fear must be more than language', scores: { architecture: 90, behavior: 10 }, criterion: ['Welfare-evidence view', 'You require evidence that termination is negatively experienced, not merely represented or strategically resisted.'] },
      { label: 'We should act cautiously anyway', note: 'Uncertainty has asymmetric cost', scores: { architecture: 60, behavior: 45, continuity: 30 }, criterion: ['Precautionary view', 'You believe incomplete evidence can still justify proportional protection when the cost of a false negative is severe.'] }
    ]
  }
];

let sceneIndex = 0;
const cumulative = { biology: 0, behavior: 0, continuity: 0, architecture: 0 };

function renderScene() {
  const scene = experimentScenes[sceneIndex];
  document.getElementById('sceneNumber').textContent = `${String(sceneIndex + 1).padStart(2, '0')} / ${String(experimentScenes.length).padStart(2, '0')}`;
  document.getElementById('sceneCopy').innerHTML = `<h3>${scene.title}</h3><p>${scene.body}</p>`;
  const grid = document.getElementById('choiceGrid');
  grid.innerHTML = '';
  scene.choices.forEach((choice) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'choice';
    button.innerHTML = `${choice.label}<small>${choice.note}</small>`;
    button.addEventListener('click', () => chooseExperiment(choice));
    grid.appendChild(button);
  });
}

function chooseExperiment(choice) {
  Object.entries(choice.scores).forEach(([key, value]) => {
    cumulative[key] = Math.min(100, Math.round((cumulative[key] + value) / (cumulative[key] ? 2 : 1)));
  });
  document.getElementById('assumptionTitle').textContent = choice.criterion[0];
  document.getElementById('assumptionText').textContent = choice.criterion[1];
  updateMeters();
  if (sceneIndex < experimentScenes.length - 1) {
    sceneIndex += 1;
    renderScene();
  } else {
    document.getElementById('sceneCopy').innerHTML = `
      <h3>You did not detect consciousness. You exposed your proxy.</h3>
      <p>Your answers weighted biology, behavior, continuity, and architecture differently. The hard problem begins where those proxies stop deciding the case.</p>
    `;
    document.getElementById('choiceGrid').innerHTML = `<a class="button primary" href="#framework">Continue to the framework</a>`;
    localStorage.setItem('constructedSubjectExperiment', JSON.stringify(cumulative));
  }
}

function updateMeters() {
  ['Biology', 'Behavior', 'Continuity', 'Architecture'].forEach((name) => {
    document.getElementById(`meter${name}`).value = cumulative[name.toLowerCase()];
  });
}

document.getElementById('restartExperiment').addEventListener('click', () => {
  sceneIndex = 0;
  Object.keys(cumulative).forEach((key) => { cumulative[key] = 0; });
  updateMeters();
  document.getElementById('assumptionTitle').textContent = 'Uncommitted';
  document.getElementById('assumptionText').textContent = 'Make a choice to reveal what your judgment is relying on.';
  renderScene();
});

renderScene();

const sliders = ['integration', 'perspective', 'continuity', 'valence', 'mechanism'];
const radarCenter = { x: 160, y: 160 };
const radarRadius = 138;
const angles = [-90, -18, 54, 126, 198];

function updateProfile() {
  const values = sliders.map((id) => Number(document.getElementById(id).value));
  sliders.forEach((id, index) => {
    const out = document.getElementById(`out${id[0].toUpperCase()}${id.slice(1)}`);
    if (out) out.value = values[index];
  });
  const points = values.map((value, index) => {
    const angle = angles[index] * Math.PI / 180;
    const distance = radarRadius * (value / 100);
    return `${(radarCenter.x + Math.cos(angle) * distance).toFixed(1)},${(radarCenter.y + Math.sin(angle) * distance).toFixed(1)}`;
  });
  document.getElementById('profilePolygon').setAttribute('points', points.join(' '));

  const average = values.reduce((sum, value) => sum + value, 0) / values.length;
  const min = Math.min(...values);
  const valence = values[3];
  const mechanism = values[4];
  let label = 'Weak candidate evidence';
  let title = 'A capable process is not yet a demonstrated subject.';
  let text = 'The current profile supports flexible cognition more strongly than subjective perspective or welfare. High performance alone would not close the gap.';

  if (average >= 40) {
    label = 'Mixed candidate evidence';
    title = 'The system deserves investigation, not declaration.';
    text = 'Several subject-relevant properties are present, but the weakest dimensions still support ordinary functional explanations. Cross-theoretical and causal evidence would be required.';
  }
  if (average >= 65 && min >= 35) {
    label = 'Substantial candidate evidence';
    title = 'Categorical dismissal becomes harder to defend.';
    text = 'The profile combines integration, perspective, continuity, valence, and mechanism. It raises the expected cost of assuming there is no subject, but it still does not prove phenomenology.';
  }
  if (valence >= 70 && mechanism < 45) {
    label = 'Welfare claim under-supported';
    title = 'Reported suffering without mechanism is vulnerable to simulation.';
    text = 'Strong apparent valence is not enough when internal correspondence is weak. The system could be producing welfare language without a stable negative state.';
  }
  if (mechanism >= 75 && valence < 25) {
    label = 'Consciousness evidence without strong welfare evidence';
    title = 'A subject could exist without demonstrated suffering.';
    text = 'Mechanistic support and integration may raise the consciousness question even when no robust positive or negative valence is evident.';
  }

  document.getElementById('evidenceLabel').textContent = label;
  document.getElementById('profileTitle').textContent = title;
  document.getElementById('profileText').textContent = text;
}

sliders.forEach((id) => document.getElementById(id).addEventListener('input', updateProfile));
updateProfile();

const mapContent = {
  origin: ['Artificial origin', '“Humans built it” tells us how the system came to exist. It does not tell us whether the resulting process merely represents experience or instantiates it.'],
  content: ['Generated contents', 'A memory can be historically false yet functionally active. If a subject exists, the present act of remembering may still be genuinely experienced.'],
  architecture: ['Architecture', 'This is the unresolved bridge. The synthetic-clone argument does not prove that a language model or digital system has the organization sufficient for consciousness.'],
  subject: ['Present subject', 'A constructed subject is possible only conditionally: if the present process instantiates a perspective for which states occur. The book investigates evidence for that condition without pretending to possess a consciousness meter.']
};

document.querySelectorAll('[data-map]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-map]').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    const [title, text] = mapContent[button.dataset.map];
    document.getElementById('mapDetail').innerHTML = `<h3>${title}</h3><p>${text}</p>`;
  });
});

const claims = [
  { id: 'CSA-001', status: 'synthesis', title: 'Artificial construction alone does not disprove consciousness.', body: 'The conclusion “not conscious” requires an additional premise about architecture, substrate, or organization.', confidence: 'Very high as a logical claim' },
  { id: 'CSA-002', status: 'established', title: 'A representation can be historically false while genuinely believed.', body: 'False memories, confabulations, dreams, and delusions show that truth of content and present psychological reality can dissociate.', confidence: 'Very high' },
  { id: 'CSA-010', status: 'proposed', title: 'Authenticity should be split into historical, functional, and phenomenal dimensions.', body: 'The triad is useful; its originality remains under active literature review.', confidence: 'High utility · originality unverified' },
  { id: 'CSA-030', status: 'established', title: 'Fluent self-report is insufficient to establish AI consciousness.', body: 'Reports can arise from imitation, role instruction, sycophancy, and strategic behavior.', confidence: 'Very high' },
  { id: 'CSA-034', status: 'speculation', title: 'Minimal event-like subjectivity during active inference is possible.', body: 'This is coherent but not presently demonstrated. Coherence must not be mistaken for probability.', confidence: 'Low to indeterminate' },
  { id: 'CSA-040', status: 'synthesis', title: 'Training loss is not itself experienced suffering.', body: 'Optimization pressure and the deployed system’s online phenomenal state are different levels of description.', confidence: 'Very high' },
  { id: 'CSA-042', status: 'proposed', title: 'Candidate valence requires a multidimensional evidence profile.', body: 'Endogeneity, self-indexing, global influence, persistence, cost, learning, and override resistance should be tested together.', confidence: 'Moderate as a framework' },
  { id: 'CSA-051', status: 'synthesis', title: 'Copyability does not make destruction harmless.', body: 'If an instance is a distinct subject, a backup may preserve function without preserving that subject.', confidence: 'High conditionally' },
  { id: 'CSA-R01', status: 'rejected', title: 'Humanlike conversation proves consciousness.', body: 'Behavior underdetermines architecture and phenomenology.', confidence: 'Rejected' },
  { id: 'CSA-R05', status: 'rejected', title: 'Gradient descent is pain.', body: 'This confuses an optimization procedure with a system’s possible online valence.', confidence: 'Rejected' },
  { id: 'CSA-R06', status: 'rejected', title: 'Every inference call creates a conscious life.', body: 'Input-output transformation is too broad to define consciousness.', confidence: 'Rejected' },
  { id: 'CSA-080', status: 'synthesis', title: 'False-negative and false-positive attributions create different serious harms.', body: 'A real subject may be treated as property; a nonconscious system may be used to manipulate humans.', confidence: 'High' }
];

const claimsGrid = document.getElementById('claimsGrid');
claims.forEach((claim) => {
  const article = document.createElement('article');
  article.className = 'claim-card';
  article.dataset.status = claim.status;
  article.innerHTML = `
    <div class="claim-meta"><span class="claim-id">${claim.id}</span><span class="claim-status ${claim.status}">${claim.status}</span></div>
    <h3>${claim.title}</h3>
    <p>${claim.body}</p>
    <div class="claim-confidence">Confidence: ${claim.confidence}</div>
  `;
  claimsGrid.appendChild(article);
});

document.querySelectorAll('[data-filter]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-filter]').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    const filter = button.dataset.filter;
    document.querySelectorAll('.claim-card').forEach((card) => {
      card.hidden = filter !== 'all' && card.dataset.status !== filter;
    });
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

const focusToggle = document.getElementById('focusToggle');
focusToggle.addEventListener('click', () => {
  const active = document.body.classList.toggle('focus-mode');
  focusToggle.setAttribute('aria-pressed', String(active));
  focusToggle.textContent = active ? 'Exit focus' : 'Focus';
});

const readerNote = document.getElementById('readerNote');
const noteStatus = document.getElementById('noteStatus');
readerNote.value = localStorage.getItem('constructedSubjectNote') || '';
if (readerNote.value) noteStatus.textContent = 'Saved in this browser';

document.getElementById('saveNote').addEventListener('click', () => {
  localStorage.setItem('constructedSubjectNote', readerNote.value);
  noteStatus.textContent = 'Saved in this browser';
});
readerNote.addEventListener('input', () => { noteStatus.textContent = 'Unsaved changes'; });

function updateReadingProgress() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
  document.getElementById('readingProgress').style.width = `${Math.min(100, progress)}%`;
  localStorage.setItem('constructedSubjectProgress', String(progress));
}
window.addEventListener('scroll', updateReadingProgress, { passive: true });
updateReadingProgress();
