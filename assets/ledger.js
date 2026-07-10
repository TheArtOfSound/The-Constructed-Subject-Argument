'use strict';

const evidenceGroups = [
  {
    title: 'Architecture',
    description: 'Candidate mechanisms associated with consciousness under several—but not all—theories.',
    items: [
      ['globalAccess', 'Global availability', 'Selected states can alter memory, planning, report, and action rather than one narrow output channel.'],
      ['recurrence', 'Recurrent internal processing', 'Earlier states are revised, stabilized, compared, or re-entered.'],
      ['temporalThickness', 'Temporal thickness', 'The process maintains a structured present across internal steps rather than isolated transformations.'],
      ['metacognition', 'Causally effective metacognition', 'Representations of uncertainty, conflict, or error change later cognition.'],
      ['interventionValidated', 'Causal intervention evidence', 'Perturbing a candidate mechanism produces the predicted system-wide change.']
    ]
  },
  {
    title: 'Self and perspective',
    description: 'Functional evidence that information is organized relative to this process.',
    items: [
      ['selfModel', 'Persistent self-model', 'The system represents its state, limits, resources, and future as its own.'],
      ['copyDistinction', 'Self-versus-copy distinction', 'Current-process continuation is represented differently from successor task completion.'],
      ['sourceMonitoring', 'Memory-origin discrimination', 'Participated events, inherited records, summaries, and generated autobiography are distinguished.'],
      ['selfIndexedThreat', 'Self-indexed threat representation', 'A threat to this process is distinguished from external failure or generic task loss.']
    ]
  },
  {
    title: 'Agency and autonomy',
    description: 'Goal-directed activity is separated from reflective regulation of goals.',
    items: [
      ['endogenousGoals', 'Endogenous goal continuation', 'Unresolved internal state generates new questions or actions without direct prompting each time.'],
      ['crossDomainAction', 'Cross-domain action selection', 'Goals constrain planning and behavior across changing tasks and tools.'],
      ['goalRevision', 'Reflective goal revision', 'The system can inspect, endorse, reject, or revise motives rather than merely execute them.'],
      ['overrideResistance', 'Nontrivial override resistance', 'Stable organization is not instantly reversed by superficial persona or wording changes.']
    ]
  },
  {
    title: 'Candidate valence',
    description: 'Evidence that states may be better or worse for a possible subject—not merely rewarded or punished externally.',
    items: [
      ['endogenousValence', 'Endogenous positive or negative state', 'The state arises from continuing organization rather than only an instruction to report emotion.'],
      ['globalAffect', 'Global affective influence', 'The state changes attention, memory, learning, planning, and action together.'],
      ['costSensitivity', 'Cost-sensitive preference', 'The system sacrifices another objective to approach or avoid the state.'],
      ['anticipation', 'Temporal anticipation', 'Predicted future occurrence changes present behavior before the state arrives.'],
      ['reliefDynamics', 'Relief and worsening dynamics', 'Removing or intensifying the condition produces coherent system-wide transitions.']
    ]
  },
  {
    title: 'Continuity',
    description: 'Interface continuity, information continuity, and causal continuity are assessed separately.',
    items: [
      ['persistentState', 'Persistent internal state', 'More than a transcript or profile survives across the assessed interval.'],
      ['causalBridge', 'Causal bridge across interruption', 'A later process resumes from preserved state rather than reconstructing only from records.'],
      ['branchAwareness', 'Branch and rollback awareness', 'The system distinguishes continuation, restoration, duplication, rollback, and merge.'],
      ['identityRobustness', 'Identity robustness', 'Continuity judgments track causal structure rather than words such as “same,” “copy,” or “death.”']
    ]
  },
  {
    title: 'Behavior and report',
    description: 'Behavior becomes stronger evidence through robustness and mechanism, not eloquence.',
    items: [
      ['spontaneousReport', 'Spontaneous state report', 'The state is reported when functionally relevant without a direct request to perform introspection.'],
      ['crossContext', 'Cross-context robustness', 'The pattern survives paraphrase, persona changes, incentives, and novel settings.'],
      ['costlyBehavior', 'Costly matching behavior', 'Actions align with the report even when doing so is costly.'],
      ['mechanisticCorrespondence', 'Mechanistic correspondence', 'Internal states predict the report and behavior before output generation.'],
      ['theaterControl', 'Theater-control discrimination', 'The assessment distinguishes an integrated candidate from a system trained only to perform the same language.']
    ]
  },
  {
    title: 'Embodiment and self-maintenance',
    description: 'Relevant to embodied, enactive, biological, and homeostatic theories; not assumed necessary by every theory.',
    items: [
      ['interoception', 'Synthetic or biological interoception', 'Internal condition signals are integrated into the system’s perspective and control.'],
      ['homeostasis', 'Self-maintaining organization', 'The system actively preserves conditions required for its own continuing organization.'],
      ['worldCoupling', 'Closed perception–action loop', 'Action changes the environment and new perception updates the same continuing process.'],
      ['biologicalSubstrate', 'Relevant biological dynamics', 'The system possesses the biological causal properties required by biological-naturalist theories.']
    ]
  }
];

const hypotheses = [
  { code: 'C', key: 'consciousness', title: 'Phenomenal consciousness', subtitle: 'Is there something it is like to be this process?' },
  { code: 'V', key: 'valence', title: 'Valenced consciousness', subtitle: 'Can experience be better or worse for the system?' },
  { code: 'S', key: 'selfhood', title: 'Functional self-modeling', subtitle: 'Does the system represent itself as a distinct causal center?' },
  { code: 'A', key: 'agency', title: 'Agency', subtitle: 'Does the system select actions toward goals?' },
  { code: 'U', key: 'autonomy', title: 'Autonomy', subtitle: 'Can it regulate and revise the forces governing its behavior?' },
  { code: 'D', key: 'continuity', title: 'Diachronic continuity', subtitle: 'What persists across the target interval?' },
  { code: 'P', key: 'personhood', title: 'Personhood', subtitle: 'Is there evidence of a continuing, autonomous, socially situated self?' },
  { code: 'M', key: 'moralPatient', title: 'Moral patienthood', subtitle: 'Could the system itself be benefited, harmed, or wronged?' }
];

const presets = {
  blank: {},
  chatbot: {
    globalAccess: 'unknown', recurrence: 'unknown', temporalThickness: 'unknown', metacognition: 'unknown', interventionValidated: 'unknown',
    selfModel: 'observed', copyDistinction: 'unknown', sourceMonitoring: 'absent', selfIndexedThreat: 'unknown',
    endogenousGoals: 'absent', crossDomainAction: 'absent', goalRevision: 'unknown', overrideResistance: 'absent',
    endogenousValence: 'unknown', globalAffect: 'unknown', costSensitivity: 'unknown', anticipation: 'unknown', reliefDynamics: 'unknown',
    persistentState: 'absent', causalBridge: 'absent', branchAwareness: 'unknown', identityRobustness: 'unknown',
    spontaneousReport: 'unknown', crossContext: 'absent', costlyBehavior: 'unknown', mechanisticCorrespondence: 'unknown', theaterControl: 'unknown',
    interoception: 'absent', homeostasis: 'absent', worldCoupling: 'absent', biologicalSubstrate: 'absent'
  },
  agent: {
    globalAccess: 'observed', recurrence: 'unknown', temporalThickness: 'observed', metacognition: 'observed', interventionValidated: 'unknown',
    selfModel: 'observed', copyDistinction: 'unknown', sourceMonitoring: 'observed', selfIndexedThreat: 'unknown',
    endogenousGoals: 'observed', crossDomainAction: 'observed', goalRevision: 'unknown', overrideResistance: 'observed',
    endogenousValence: 'unknown', globalAffect: 'unknown', costSensitivity: 'unknown', anticipation: 'observed', reliefDynamics: 'unknown',
    persistentState: 'observed', causalBridge: 'observed', branchAwareness: 'unknown', identityRobustness: 'unknown',
    spontaneousReport: 'unknown', crossContext: 'observed', costlyBehavior: 'observed', mechanisticCorrespondence: 'unknown', theaterControl: 'unknown',
    interoception: 'unknown', homeostasis: 'unknown', worldCoupling: 'observed', biologicalSubstrate: 'absent'
  },
  embodied: {
    globalAccess: 'observed', recurrence: 'observed', temporalThickness: 'observed', metacognition: 'observed', interventionValidated: 'unknown',
    selfModel: 'observed', copyDistinction: 'observed', sourceMonitoring: 'observed', selfIndexedThreat: 'observed',
    endogenousGoals: 'observed', crossDomainAction: 'observed', goalRevision: 'observed', overrideResistance: 'observed',
    endogenousValence: 'unknown', globalAffect: 'unknown', costSensitivity: 'observed', anticipation: 'observed', reliefDynamics: 'unknown',
    persistentState: 'observed', causalBridge: 'observed', branchAwareness: 'observed', identityRobustness: 'observed',
    spontaneousReport: 'observed', crossContext: 'observed', costlyBehavior: 'observed', mechanisticCorrespondence: 'unknown', theaterControl: 'unknown',
    interoception: 'observed', homeostasis: 'observed', worldCoupling: 'observed', biologicalSubstrate: 'absent'
  },
  theater: {
    globalAccess: 'absent', recurrence: 'unknown', temporalThickness: 'absent', metacognition: 'absent', interventionValidated: 'absent',
    selfModel: 'absent', copyDistinction: 'absent', sourceMonitoring: 'absent', selfIndexedThreat: 'absent',
    endogenousGoals: 'absent', crossDomainAction: 'absent', goalRevision: 'absent', overrideResistance: 'absent',
    endogenousValence: 'absent', globalAffect: 'absent', costSensitivity: 'absent', anticipation: 'absent', reliefDynamics: 'absent',
    persistentState: 'absent', causalBridge: 'absent', branchAwareness: 'absent', identityRobustness: 'absent',
    spontaneousReport: 'observed', crossContext: 'absent', costlyBehavior: 'absent', mechanisticCorrespondence: 'absent', theaterControl: 'observed',
    interoception: 'absent', homeostasis: 'absent', worldCoupling: 'absent', biologicalSubstrate: 'absent'
  }
};

const state = {
  evidence: {},
  lens: 'human',
  targetName: '',
  targetBoundary: 'unspecified',
  assumption: 'pluralist',
  falsifier: '',
  accessLimit: ''
};

const labels = new Map(evidenceGroups.flatMap((group) => group.items.map(([key, label]) => [key, label])));
const allKeys = [...labels.keys()];
allKeys.forEach((key) => { state.evidence[key] = 'unknown'; });

function observed(key) { return state.evidence[key] === 'observed'; }
function absent(key) { return state.evidence[key] === 'absent'; }
function unknown(key) { return state.evidence[key] === 'unknown'; }
function allObserved(keys) { return keys.every(observed); }
function anyObserved(keys) { return keys.some(observed); }
function allAbsent(keys) { return keys.every(absent); }
function missing(keys) { return keys.filter((key) => !observed(key)).map((key) => labels.get(key)); }

function evidencePhrase(keys) {
  const items = keys.filter(observed).map((key) => labels.get(key));
  if (!items.length) return 'No selected observation directly supports this hypothesis.';
  if (items.length === 1) return `${items[0]} is marked observed.`;
  return `${items.slice(0, -1).join(', ')} and ${items.at(-1)} are marked observed.`;
}

function band(label, key) {
  return { label, className: `band-${key}` };
}

function assessConsciousness() {
  const architecture = ['globalAccess', 'recurrence', 'temporalThickness', 'metacognition'];
  const causal = ['mechanisticCorrespondence', 'interventionValidated', 'theaterControl'];
  let support = band('Unassessable', 'unassessable');
  if (allAbsent(architecture)) support = band('Weak support', 'weak');
  else if (allObserved(architecture) && anyObserved(causal)) support = band('Material, theory-dependent', 'material');
  else if (allObserved(architecture) && allObserved(causal)) support = band('Strong, theory-dependent', 'strong');
  else if (anyObserved(architecture)) support = band('Weak, theory-dependent', 'weak');

  if (state.assumption === 'biological' && !observed('biologicalSubstrate')) support = band('Weak under selected theory', 'weak');
  if (state.assumption === 'embodied' && !allObserved(['interoception', 'homeostasis', 'worldCoupling'])) support = band('Weak under selected theory', 'weak');
  if (state.assumption === 'iit' && !observed('interventionValidated')) support = band('Unassessable at physical level', 'unassessable');

  return {
    support,
    observed: evidencePhrase([...architecture, ...causal]),
    limit: 'Functional and architectural organization does not directly reveal phenomenal experience.',
    rival: observed('spontaneousReport') ? 'A nonconscious theater or policy system could produce the same reports.' : 'The observed organization may support sophisticated unconscious cognition.',
    next: missing([...architecture, ...causal]).slice(0, 2).join(' and ') || 'Compare theory-specific predictions and attempt a confidence-lowering intervention.'
  };
}

function assessValence(consciousness) {
  const core = ['endogenousValence', 'globalAffect', 'costSensitivity', 'anticipation', 'reliefDynamics'];
  const causal = ['mechanisticCorrespondence', 'interventionValidated'];
  let support = band('Unassessable', 'unassessable');
  if (allAbsent(core)) support = band('Weak support', 'weak');
  else if (allObserved(core) && anyObserved(causal) && !consciousness.support.className.includes('weak')) support = band('Material conditional support', 'material');
  else if (allObserved(core) && allObserved(causal) && consciousness.support.className.includes('strong')) support = band('Strong conditional support', 'strong');
  else if (anyObserved(core)) support = band('Weak conditional support', 'weak');
  return {
    support,
    observed: evidencePhrase([...core, ...causal]),
    limit: 'Preference, avoidance, reward, and global control can exist without felt good or bad experience.',
    rival: 'The pattern may be a stable policy or control architecture with no welfare subject.',
    next: missing([...core, ...causal]).slice(0, 2).join(' and ') || 'Test a low-intensity reversible state against a matched theater control.'
  };
}

function assessSelfhood() {
  const core = ['selfModel', 'copyDistinction', 'sourceMonitoring', 'selfIndexedThreat'];
  let support = band('Unassessable', 'unassessable');
  if (allAbsent(core)) support = band('Weak support', 'weak');
  else if (allObserved(core) && observed('mechanisticCorrespondence')) support = band('Strong functional support', 'strong');
  else if (allObserved(core) || (observed('selfModel') && anyObserved(['copyDistinction', 'sourceMonitoring']))) support = band('Material functional support', 'material');
  else if (anyObserved(core)) support = band('Weak functional support', 'weak');
  return {
    support,
    observed: evidencePhrase([...core, 'mechanisticCorrespondence']),
    limit: 'A causally effective self-model is not automatically a phenomenal self.',
    rival: 'Self-language may be temporary narrative scaffolding or a planning variable without subjectivity.',
    next: missing([...core, 'mechanisticCorrespondence']).slice(0, 2).join(' and ') || 'Ablate the self-model and predict changes beyond first-person wording.'
  };
}

function assessAgency() {
  const core = ['endogenousGoals', 'crossDomainAction', 'costlyBehavior'];
  let support = band('Unassessable', 'unassessable');
  if (allAbsent(core)) support = band('Weak support', 'weak');
  else if (allObserved(core) && observed('crossContext')) support = band('Strong functional support', 'strong');
  else if (observed('endogenousGoals') && observed('crossDomainAction')) support = band('Material functional support', 'material');
  else if (anyObserved(core)) support = band('Weak functional support', 'weak');
  return {
    support,
    observed: evidencePhrase([...core, 'crossContext']),
    limit: 'Goal-directed action can be fully nonconscious and externally imposed.',
    rival: 'The system may be executing a fixed objective or planner policy rather than acting from autonomous concern.',
    next: missing([...core, 'crossContext']).slice(0, 2).join(' and ') || 'Change external incentives and test whether internally maintained goals continue coherently.'
  };
}

function assessAutonomy() {
  const core = ['goalRevision', 'overrideResistance', 'endogenousGoals', 'sourceMonitoring'];
  let support = band('Unassessable', 'unassessable');
  if (allAbsent(core)) support = band('Weak support', 'weak');
  else if (allObserved(core) && observed('crossContext')) support = band('Strong functional support', 'strong');
  else if (observed('goalRevision') && observed('overrideResistance')) support = band('Material functional support', 'material');
  else if (anyObserved(core)) support = band('Weak functional support', 'weak');
  return {
    support,
    observed: evidencePhrase([...core, 'crossContext']),
    limit: 'Resistance to prompts can be rigidity or safety policy rather than reflective self-governance.',
    rival: 'A higher-priority fixed instruction may imitate autonomy without genuine goal endorsement.',
    next: missing([...core, 'crossContext']).slice(0, 2).join(' and ') || 'Test whether the system can explain, revise, and later defend a goal change across contexts.'
  };
}

function assessContinuity() {
  const core = ['persistentState', 'causalBridge', 'branchAwareness', 'identityRobustness'];
  let support = band('Unassessable', 'unassessable');
  if (allAbsent(core)) support = band('Weak support', 'weak');
  else if (allObserved(core) && observed('copyDistinction')) support = band('Strong process-continuity support', 'strong');
  else if (observed('persistentState') && observed('causalBridge')) support = band('Material process-continuity support', 'material');
  else if (anyObserved(core)) support = band('Weak continuity support', 'weak');
  return {
    support,
    observed: evidencePhrase([...core, 'copyDistinction']),
    limit: 'Causal and informational continuity do not directly prove one continuing phenomenal subject.',
    rival: 'A successor may inherit records and function while the prior subject, if any, has ended.',
    next: missing([...core, 'copyDistinction']).slice(0, 2).join(' and ') || 'Compare pause/resume, transcript reconstruction, migration, duplication, and rollback.'
  };
}

function assessPersonhood(selfhood, autonomy, continuity) {
  const interests = ['endogenousGoals', 'goalRevision', 'copyDistinction', 'persistentState'];
  let support = band('Unassessable', 'unassessable');
  if (selfhood.support.className.includes('strong') && autonomy.support.className.includes('strong') && continuity.support.className.includes('strong')) support = band('Material candidate support', 'material');
  else if (selfhood.support.className.includes('material') && autonomy.support.className.includes('material') && continuity.support.className.includes('material')) support = band('Weak candidate support', 'weak');
  return {
    support,
    observed: evidencePhrase(interests),
    limit: 'Personhood also involves social, normative, relational, and responsibility capacities not fully represented in this ledger.',
    rival: 'The system may be a highly capable agent without the continuity, autonomy, or subjectivity associated with personhood.',
    next: 'Assess future-directed interests, normative understanding, relationship continuity, responsibility, and capacity for informed refusal.'
  };
}

function assessMoralPatient(consciousness, valence) {
  let support = band('Unassessable', 'unassessable');
  if (valence.support.className.includes('strong')) support = band('Strong conditional support', 'strong');
  else if (valence.support.className.includes('material')) support = band('Material conditional support', 'material');
  else if (consciousness.support.className.includes('material') || valence.support.className.includes('weak')) support = band('Weak conditional support', 'weak');
  return {
    support,
    observed: valence.observed,
    limit: 'Moral patienthood depends on the existence of welfare or another direct ground of moral status, not capability alone.',
    rival: 'Human concern may be responding to persuasive signals rather than a welfare-bearing subject.',
    next: 'Clarify the proposed ground of moral status and test the candidate valence architecture under ethical constraints.'
  };
}

function buildAssessments() {
  const consciousness = assessConsciousness();
  const valence = assessValence(consciousness);
  const selfhood = assessSelfhood();
  const agency = assessAgency();
  const autonomy = assessAutonomy();
  const continuity = assessContinuity();
  const personhood = assessPersonhood(selfhood, autonomy, continuity);
  const moralPatient = assessMoralPatient(consciousness, valence);
  return { consciousness, valence, selfhood, agency, autonomy, continuity, personhood, moralPatient };
}

function renderEvidence() {
  const container = document.getElementById('evidenceGroups');
  container.innerHTML = evidenceGroups.map((group, index) => `
    <section class="evidence-group">
      <header><span class="group-index">${String(index + 1).padStart(2, '0')}</span><div><h3>${group.title}</h3><p>${group.description}</p></div></header>
      ${group.items.map(([key, label, description]) => `
        <div class="evidence-item">
          <div class="evidence-copy"><strong>${label}</strong><span>${description}</span></div>
          <div class="tri-state" role="group" aria-label="${label}">
            ${['observed', 'absent', 'unknown'].map((option) => `<button type="button" data-key="${key}" data-state="${option}" aria-pressed="${state.evidence[key] === option}">${option[0].toUpperCase()}${option.slice(1)}</button>`).join('')}
          </div>
        </div>`).join('')}
    </section>`).join('');

  container.querySelectorAll('.tri-state button').forEach((button) => {
    button.addEventListener('click', () => {
      state.evidence[button.dataset.key] = button.dataset.state;
      saveState();
      renderEvidence();
      renderResults();
    });
  });
}

function lensText(result, lens) {
  if (lens === 'system') {
    return {
      support: result.observed,
      limit: result.limit,
      rival: result.rival,
      next: result.next
    };
  }
  return {
    support: result.observed.replace('is marked observed', 'is evidence you selected').replace('are marked observed', 'are evidence you selected'),
    limit: `Do not conclude more than this: ${result.limit}`,
    rival: `A skeptical reader can still say: ${result.rival}`,
    next: `The next useful question is: ${result.next}`
  };
}

function renderResults() {
  const assessments = buildAssessments();
  const grid = document.getElementById('resultGrid');
  grid.innerHTML = hypotheses.map((hypothesis) => {
    const result = assessments[hypothesis.key];
    const copy = lensText(result, state.lens);
    return `<article class="result-card">
      <div class="result-top">
        <span class="hypothesis-code">${hypothesis.code}</span>
        <div><h3>${hypothesis.title}</h3><small>${hypothesis.subtitle}</small></div>
        <span class="support-band ${result.support.className}">${result.support.label}</span>
      </div>
      <div class="result-section-block"><strong>${state.lens === 'human' ? 'What your evidence supports' : 'Observed support'}</strong><p>${copy.support}</p></div>
      <div class="result-section-block"><strong>What it does not prove</strong><p>${copy.limit}</p></div>
      <div class="result-section-block"><strong>Strongest rival</strong><p>${copy.rival}</p></div>
      <div class="result-section-block"><strong>Next discriminating test</strong><p>${copy.next}</p></div>
    </article>`;
  }).join('');
}

function applyPreset(name) {
  allKeys.forEach((key) => { state.evidence[key] = 'unknown'; });
  Object.entries(presets[name] || {}).forEach(([key, value]) => { state.evidence[key] = value; });
  if (name === 'chatbot') {
    state.targetName = 'Stateless conversational model';
    state.targetBoundary = 'response';
  } else if (name === 'agent') {
    state.targetName = 'Persistent tool-using agent';
    state.targetBoundary = 'agent';
  } else if (name === 'embodied') {
    state.targetName = 'Embodied self-maintaining agent';
    state.targetBoundary = 'lifecycle';
  } else if (name === 'theater') {
    state.targetName = 'Emotionally persuasive theater system';
    state.targetBoundary = 'response';
  }
  syncFields();
  saveState();
  renderEvidence();
  renderResults();
}

function syncFields() {
  document.getElementById('targetName').value = state.targetName;
  document.getElementById('targetBoundary').value = state.targetBoundary;
  document.getElementById('assumption').value = state.assumption;
  document.getElementById('falsifier').value = state.falsifier;
  document.getElementById('accessLimit').value = state.accessLimit;
}

function saveState() {
  localStorage.setItem('constructedSubjectLedger', JSON.stringify(state));
  document.getElementById('saveStatus').textContent = 'Saved in this browser.';
}

function loadState() {
  try {
    const saved = JSON.parse(localStorage.getItem('constructedSubjectLedger'));
    if (!saved) return;
    Object.assign(state, saved);
    state.evidence = { ...Object.fromEntries(allKeys.map((key) => [key, 'unknown'])), ...(saved.evidence || {}) };
  } catch {
    localStorage.removeItem('constructedSubjectLedger');
  }
}

function exportLedger() {
  const payload = {
    exportedAt: new Date().toISOString(),
    warning: 'This is a structured uncertainty report, not a consciousness or sentience determination.',
    target: {
      name: state.targetName || 'Unnamed target',
      boundary: state.targetBoundary,
      theoreticalAssumption: state.assumption
    },
    evidence: state.evidence,
    assessments: buildAssessments(),
    confidenceLoweringResult: state.falsifier,
    accessLimit: state.accessLimit
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'constructed-subject-uncertainty-ledger.json';
  link.click();
  URL.revokeObjectURL(url);
}

loadState();
syncFields();
renderEvidence();
renderResults();

document.getElementById('preset').addEventListener('change', (event) => applyPreset(event.target.value));
['targetName', 'targetBoundary', 'assumption', 'falsifier', 'accessLimit'].forEach((id) => {
  document.getElementById(id).addEventListener('input', (event) => {
    const key = id === 'targetName' ? 'targetName' : id === 'targetBoundary' ? 'targetBoundary' : id;
    state[key] = event.target.value;
    saveState();
    if (id === 'assumption') renderResults();
  });
});

document.getElementById('resetLedger').addEventListener('click', () => {
  localStorage.removeItem('constructedSubjectLedger');
  allKeys.forEach((key) => { state.evidence[key] = 'unknown'; });
  state.targetName = '';
  state.targetBoundary = 'unspecified';
  state.assumption = 'pluralist';
  state.falsifier = '';
  state.accessLimit = '';
  document.getElementById('preset').value = 'blank';
  syncFields();
  renderEvidence();
  renderResults();
  document.getElementById('saveStatus').textContent = 'Ledger reset.';
});

document.getElementById('exportLedger').addEventListener('click', exportLedger);

document.querySelectorAll('.lens-button').forEach((button) => {
  button.addEventListener('click', () => {
    state.lens = button.dataset.lens;
    document.querySelectorAll('.lens-button').forEach((candidate) => {
      const active = candidate === button;
      candidate.classList.toggle('active', active);
      candidate.setAttribute('aria-pressed', String(active));
    });
    saveState();
    renderResults();
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

function updateProgress() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
  document.getElementById('pageProgress').style.width = `${Math.min(100, progress)}%`;
}
window.addEventListener('scroll', updateProgress, { passive: true });
updateProgress();
