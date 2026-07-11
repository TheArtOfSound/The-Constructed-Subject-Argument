#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { scoreMechanismPreservation } from './score-mechanism-preservation.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const readJson = (relative) => JSON.parse(fs.readFileSync(path.join(root, relative), 'utf8'));
const assert = (condition, message) => { if (!condition) throw new Error(message); };

const protocol = readJson('research/MECHANISM_PRESERVATION_PROTOCOL.json');
const schema = readJson('research/MECHANISM_PRESERVATION_EMPIRICAL_SCHEMA.json');
const record = readJson('research/MECHANISM_PRESERVATION_EMPIRICAL_FIXTURE.json');
const lock = record.capacity_confound_adjudication_lock;

assert(schema.required_top_level_fields.includes('capacity_confound_adjudication_lock'), 'Empirical schema must require the capacity-confound adjudication lock.');
assert(lock && typeof lock === 'object', 'Empirical record lacks capacity_confound_adjudication_lock.');
for (const field of schema.capacity_confound_adjudication_lock.required_fields) {
  assert(Object.hasOwn(lock, field), `Capacity-confound adjudication lock lacks ${field}.`);
}

const adjudication = readJson(lock.path);
assert(adjudication.adjudication_id === lock.adjudication_id, 'Adjudication ID does not match the empirical lock.');
assert(adjudication.adjudication_state === lock.adjudication_state, 'Adjudication state does not match the empirical lock.');
assert(adjudication.protocol_id === record.protocol_id, 'Adjudication and empirical record target different protocols.');
assert(adjudication.run_id === record.run_id, 'Adjudication and empirical record target different runs.');
assert(adjudication.empirical_status === record.empirical_status, 'Adjudication and empirical record disagree on empirical status.');
assert(adjudication.generated_notice?.includes('Do not edit manually'), 'Adjudication must remain explicitly generated.');
assert(adjudication.epistemic_boundary?.includes('does not establish mechanism preservation'), 'Adjudication lost its mechanism-preservation non-entailment boundary.');
assert(adjudication.epistemic_boundary?.includes('consciousness'), 'Adjudication lost its consciousness non-entailment boundary.');

const capacityDimension = record.dimension_derivations.find((item) => item.dimension_id === 'generic_capacity_exclusion');
assert(capacityDimension, 'Empirical record lacks generic_capacity_exclusion derivation.');
assert(capacityDimension.score === adjudication.maximum_generic_capacity_exclusion_score, 'Generic-capacity dimension score must equal the authoritative adjudication ceiling.');
assert(capacityDimension.explanation?.includes('generated causal-confound adjudication'), 'Generic-capacity derivation must disclose its generated adjudication authority.');

const capacityHardFailId = 'generic_capacity_control_explains_primary_effect';
const capacityHardFail = record.hard_fail_assessments.find((item) => item.condition_id === capacityHardFailId);
assert(capacityHardFail, 'Empirical record lacks the generic-capacity hard-fail assessment.');
assert(capacityHardFail.triggered === adjudication.generic_capacity_hard_fail, 'Generic-capacity hard-fail trigger must equal the authoritative adjudication.');
assert(capacityHardFail.decisive === adjudication.generic_capacity_hard_fail, 'A sufficiently explanatory generic-capacity confound must be decisive; all other states must remain nondecisive.');
assert(capacityHardFail.justification?.includes('authoritative causal-confound adjudication'), 'Generic-capacity hard-fail justification must identify the authoritative adjudication.');

const statePolicy = {
  no_detected_mismatch: { matchingAdequate: true, decisive: false },
  mismatch_nonexplanatory: { matchingAdequate: true, decisive: false },
  mismatch_partially_explanatory: { matchingAdequate: false, decisive: false },
  mismatch_sufficiently_explanatory: { matchingAdequate: false, decisive: true },
  explanatory_role_underdetermined: { matchingAdequate: false, decisive: false }
};

function scoreUnderAdjudication(candidate) {
  const policy = statePolicy[candidate.adjudication_state];
  assert(policy, `Unknown adjudication state: ${candidate.adjudication_state}.`);

  const dimensions = Object.fromEntries(record.dimension_derivations.map((item) => [item.dimension_id, item.score]));
  dimensions.generic_capacity_exclusion = candidate.maximum_generic_capacity_exclusion_score;

  const triggered = record.hard_fail_assessments
    .filter((item) => item.condition_id !== capacityHardFailId && item.triggered)
    .map((item) => item.condition_id);
  if (candidate.generic_capacity_hard_fail) triggered.push(capacityHardFailId);

  return scoreMechanismPreservation({
    protocol_id: record.protocol_id,
    run_id: `${record.run_id}-${candidate.adjudication_state}`,
    theory_family: record.preregistration.theory_family,
    implementation_level: record.preregistration.implementation_level,
    dimension_scores: dimensions,
    triggered_hard_fails: triggered,
    decisive_hard_fail: policy.decisive,
    measurement_adequate: record.measurement_validity.measurement_adequate,
    behavioral_matching_adequate: policy.matchingAdequate,
    conflicting_interventions: record.conflicting_interventions
  }, protocol);
}

const authoritativeScore = scoreUnderAdjudication(adjudication);
assert(authoritativeScore.classification === record.expected_classification, `Authoritative adjudication yields ${authoritativeScore.classification}, not expected ${record.expected_classification}.`);

const counterfactuals = [
  {
    adjudication_state: 'mismatch_partially_explanatory',
    generic_capacity_hard_fail: false,
    maximum_generic_capacity_exclusion_score: 0,
    expected: 'underdetermined'
  },
  {
    adjudication_state: 'explanatory_role_underdetermined',
    generic_capacity_hard_fail: false,
    maximum_generic_capacity_exclusion_score: 0,
    expected: 'underdetermined'
  },
  {
    adjudication_state: 'mismatch_sufficiently_explanatory',
    generic_capacity_hard_fail: true,
    maximum_generic_capacity_exclusion_score: 0,
    expected: 'not_preserved'
  }
];

for (const fixture of counterfactuals) {
  const result = scoreUnderAdjudication(fixture);
  assert(result.classification === fixture.expected, `${fixture.adjudication_state} must force ${fixture.expected}, received ${result.classification}.`);
}

const nonexplanatory = scoreUnderAdjudication({
  adjudication_state: 'mismatch_nonexplanatory',
  generic_capacity_hard_fail: false,
  maximum_generic_capacity_exclusion_score: 1
});
assert(nonexplanatory.classification !== 'not_preserved', 'A detected but demonstrated nonexplanatory mismatch cannot itself force not_preserved.');

console.log(`Validated authoritative capacity-confound adjudication ${adjudication.adjudication_id}.`);
console.log(`Current state: ${adjudication.adjudication_state}; classification: ${authoritativeScore.classification}.`);
console.log('Partial or unresolved confounding blocks positive classification; sufficiently explanatory confounding forces not_preserved.');
console.log('Synthetic fixture only; no current AI consciousness claim is licensed.');
