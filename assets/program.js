'use strict';

const readinessUrl = 'research/egc2/expert_reviewer_dry_run_execution_readiness.v0.1.json';
const provisioningUrl = 'research/egc2/expert_reviewer_dry_run_assignment_and_provisioning.v0.1.json';

const gateLabels = {
  P01: 'Operator accepted',
  P02: 'Ownership assigned',
  P03: 'Proton isolated',
  P04: 'AWS isolated',
  P05: 'Object Lock',
  P06: 'CloudTrail',
  P07: 'Role separation',
  P08: 'Artifacts frozen',
  P09: 'Leakage scan',
  P10: 'Evidence closure',
  P11: 'Incident authority',
  P12: 'No live data'
};

function text(value, fallback = 'unknown') {
  if (value === null || value === undefined || value === '') return fallback;
  return String(value);
}

function makeStateCard({ kicker, title, value, body, tone }) {
  return `
    <article class="state-card ${tone}">
      <span class="state-kicker">${kicker}</span>
      <h3>${title}</h3>
      <span class="state-value">${value}</span>
      <p>${body}</p>
    </article>`;
}

function renderLiveState(readiness, provisioning) {
  const stateGrid = document.getElementById('liveStateGrid');
  const gates = Array.isArray(readiness.preflight_gates) ? readiness.preflight_gates : [];
  const verifiedGates = gates.filter((gate) => gate.status === 'verified').length;

  const ownership = Array.isArray(provisioning.assignments?.ownership_roles)
    ? provisioning.assignments.ownership_roles
    : [];
  const acceptedOwnership = ownership.filter((role) => role.accepted === true).length;
  const accountableAssignments = [
    provisioning.assignments?.primary_operator,
    provisioning.assignments?.independent_audit_reviewer
  ].filter(Boolean);
  const acceptedAccountable = accountableAssignments.filter((assignment) => assignment.accepted === true).length;

  const controls = Array.isArray(provisioning.resource_controls) ? provisioning.resource_controls : [];
  const provisionedControls = controls.filter((control) => control.provisioned === true).length;

  const executionAllowed = readiness.execution_allowed === true || provisioning.execution_allowed === true;
  const displayStatus = executionAllowed ? 'allowed' : 'blocked';

  stateGrid.innerHTML = [
    makeStateCard({
      kicker: 'Execution boundary',
      title: 'Synthetic cloud run',
      value: displayStatus,
      body: executionAllowed
        ? 'The public record reports execution as allowed. Verify every gate and independent-review record before interpreting this state.'
        : 'The committed records prohibit execution. This is the accurate current state, not a site placeholder.',
      tone: executionAllowed ? 'is-good' : 'is-blocked'
    }),
    makeStateCard({
      kicker: 'Accountability',
      title: 'Accepted roles',
      value: `${acceptedAccountable + acceptedOwnership}/${accountableAssignments.length + ownership.length}`,
      body: `${acceptedAccountable} of ${accountableAssignments.length} accountable assignments and ${acceptedOwnership} of ${ownership.length} ownership roles are accepted.`,
      tone: acceptedAccountable + acceptedOwnership > 0 ? 'is-neutral' : 'is-zero'
    }),
    makeStateCard({
      kicker: 'Provisioning',
      title: 'Operational controls',
      value: `${provisionedControls}/${controls.length}`,
      body: 'R01–R08 cover the isolated Proton/AWS resources, audit chain, role separation, private stores, and frozen synthetic artifacts.',
      tone: provisionedControls === controls.length && controls.length > 0 ? 'is-good' : 'is-zero'
    }),
    makeStateCard({
      kicker: 'Preflight',
      title: 'Verified gates',
      value: `${verifiedGates}/${gates.length}`,
      body: 'Every gate requires evidence-backed independent review. Missing or unresolved evidence keeps the run blocked.',
      tone: verifiedGates === gates.length && gates.length > 0 ? 'is-good' : 'is-neutral'
    })
  ].join('');

  const gateGrid = document.getElementById('gateGrid');
  gateGrid.innerHTML = gates.map((gate) => {
    const statusClass = gate.status === 'verified' ? 'verified' : '';
    return `<div class="gate ${statusClass}"><b>${text(gate.id)}</b><span>${gateLabels[gate.id] || text(gate.name)}</span></div>`;
  }).join('');

  document.getElementById('gateSummary').textContent = `${verifiedGates} verified · ${gates.length - verifiedGates} unresolved or blocked`;
}

function renderLoadFailure(error) {
  const stateGrid = document.getElementById('liveStateGrid');
  stateGrid.innerHTML = makeStateCard({
    kicker: 'Public record load',
    title: 'State unavailable',
    value: 'error',
    body: `The static JSON could not be loaded in this browser. No readiness inference is made. ${text(error?.message, '')}`,
    tone: 'is-blocked'
  });
  document.getElementById('gateSummary').textContent = 'No gate state inferred';
  document.getElementById('gateGrid').innerHTML = '';
}

async function loadProgramState() {
  try {
    const [readinessResponse, provisioningResponse] = await Promise.all([
      fetch(readinessUrl, { cache: 'no-store' }),
      fetch(provisioningUrl, { cache: 'no-store' })
    ]);

    if (!readinessResponse.ok) throw new Error(`Readiness record returned ${readinessResponse.status}`);
    if (!provisioningResponse.ok) throw new Error(`Provisioning record returned ${provisioningResponse.status}`);

    const [readiness, provisioning] = await Promise.all([
      readinessResponse.json(),
      provisioningResponse.json()
    ]);

    renderLiveState(readiness, provisioning);
  } catch (error) {
    renderLoadFailure(error);
  }
}

const programRoot = document.documentElement;
const programThemeToggle = document.getElementById('programThemeToggle');
const storedTheme = localStorage.getItem('constructedSubjectTheme');
if (storedTheme) programRoot.dataset.theme = storedTheme;

programThemeToggle.addEventListener('click', () => {
  const next = programRoot.dataset.theme === 'light' ? 'dark' : 'light';
  programRoot.dataset.theme = next;
  programThemeToggle.setAttribute('aria-pressed', String(next === 'light'));
  localStorage.setItem('constructedSubjectTheme', next);
});

function updateProgramProgress() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
  document.getElementById('programProgress').style.width = `${Math.min(100, progress)}%`;
}

window.addEventListener('scroll', updateProgramProgress, { passive: true });
updateProgramProgress();
loadProgramState();
