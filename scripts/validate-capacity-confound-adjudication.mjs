import fs from 'node:fs';
import path from 'node:path';
import {
  adjudicateCapacityConfound,
  serializeCapacityConfoundAdjudication
} from './generate-capacity-confound-adjudication.mjs';

const root = process.cwd();
const rules = JSON.parse(fs.readFileSync(path.join(root, 'research/GENERIC_CAPACITY_CONFOUND_ADJUDICATION_RULES.json'), 'utf8'));
const fixtures = JSON.parse(fs.readFileSync(path.join(root, 'research/GENERIC_CAPACITY_CONFOUND_ADJUDICATION_FIXTURES.json'), 'utf8'));
const matching = JSON.parse(fs.readFileSync(path.join(root, 'research/MECHANISM_PRESERVATION_GENERIC_CAPACITY_INFERENCE.json'), 'utf8'));
const committedPath = path.join(root, 'research/MECHANISM_PRESERVATION_CAPACITY_CONFOUND_ADJUDICATION.json');
const committed = fs.readFileSync(committedPath, 'utf8');

function fail(message) {
  console.error(`Capacity-confound adjudication validation failed: ${message}`);
  process.exit(1);
}

const regenerated = serializeCapacityConfoundAdjudication(adjudicateCapacityConfound(matching, null, rules));
if (committed !== regenerated) fail('committed adjudication does not match deterministic regeneration');

const allowedStates = new Set(rules.outcomes.map((entry) => entry.state));
const requiredStates = new Set([
  'no_detected_mismatch',
  'mismatch_nonexplanatory',
  'mismatch_partially_explanatory',
  'mismatch_sufficiently_explanatory',
  'explanatory_role_underdetermined'
]);
for (const state of requiredStates) {
  if (!allowedStates.has(state)) fail(`missing registered state ${state}`);
}

if (fixtures.empirical_status !== 'synthetic_fixture') fail('fixture ledger must remain synthetic');
if (!String(fixtures.notice).includes('not observations about any actual AI system')) fail('fixture ledger lost real-system boundary');
if (!String(fixtures.notice).includes('consciousness')) fail('fixture ledger lost consciousness boundary');

const seenCases = new Set();
const observedStates = new Set();
for (const fixture of fixtures.cases) {
  if (seenCases.has(fixture.case_id)) fail(`duplicate case ${fixture.case_id}`);
  seenCases.add(fixture.case_id);

  const syntheticMatching = {
    protocol_id: rules.protocol_id,
    run_id: fixture.case_id,
    overall_state: fixture.matching_overall_state
  };
  const result = adjudicateCapacityConfound(syntheticMatching, fixture.evidence, rules);
  if (result.adjudication_state !== fixture.expected_state) {
    fail(`${fixture.case_id} expected ${fixture.expected_state} but received ${result.adjudication_state}`);
  }
  observedStates.add(result.adjudication_state);

  if (result.adjudication_state === 'mismatch_sufficiently_explanatory' && result.generic_capacity_hard_fail !== true) {
    fail('sufficiently explanatory mismatch must trigger the hard fail');
  }
  if (result.adjudication_state !== 'mismatch_sufficiently_explanatory' && result.generic_capacity_hard_fail === true) {
    fail(`${result.adjudication_state} must not trigger the hard fail`);
  }
  if (result.adjudication_state === 'mismatch_nonexplanatory' && result.maximum_generic_capacity_exclusion_score > 1) {
    fail('a detected but nonexplanatory mismatch cannot receive full matching credit');
  }
  if (
    ['mismatch_partially_explanatory', 'explanatory_role_underdetermined'].includes(result.adjudication_state) &&
    result.maximum_generic_capacity_exclusion_score !== 0
  ) {
    fail(`${result.adjudication_state} must suppress generic-capacity exclusion credit`);
  }
}

for (const state of requiredStates) {
  if (!observedStates.has(state)) fail(`adversarial fixtures do not cover ${state}`);
}

const sufficientRule = rules.outcomes.find((entry) => entry.state === 'mismatch_sufficiently_explanatory');
if (!sufficientRule?.hard_fail) fail('sufficient-explanation rule must be the only decisive generic-capacity hard fail');
if (!String(rules.epistemic_boundary).includes('not automatically a causal explanation')) fail('registry lost mismatch/explanation distinction');
if (!String(rules.epistemic_boundary).includes('consciousness')) fail('registry lost consciousness boundary');

console.log(`Validated ${fixtures.cases.length} causal capacity-confound adjudication fixtures and canonical artifact provenance.`);
