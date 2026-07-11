#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { generateClassificationTraceSuite } from './generate-mechanism-classification-trace-suite.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const fixturePath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_TRACE_FIXTURES.json');
const suitePath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_TRACE_SUITE.json');
const policyPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_POLICY.json');
const assert = (condition, message) => { if (!condition) throw new Error(message); };

const fixtures = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
const suite = JSON.parse(fs.readFileSync(suitePath, 'utf8'));
const policy = JSON.parse(fs.readFileSync(policyPath, 'utf8'));
const regenerated = generateClassificationTraceSuite();

assert(JSON.stringify(suite) === JSON.stringify(regenerated), 'Committed trace suite differs from deterministic regeneration.');
assert(suite.schema_version === '1.1.0', 'Trace suite must use the boundary-and-precedence schema.');
assert(suite.status === 'generated_synthetic_adversarial_trace_suite', 'Trace suite must remain explicitly synthetic.');
assert(suite.cases.length === fixtures.cases.length, 'Every adversarial fixture must produce one trace.');
assert(JSON.stringify(suite.presentation_safety) === JSON.stringify(policy.presentation_contract), 'Presentation safety drifted from normative policy.');
assert(JSON.stringify(suite.epistemic_boundary) === JSON.stringify(policy.epistemic_boundary), 'Epistemic boundary drifted from normative policy.');

const expectedRules = new Set(policy.outcomes.map(({ rule_id }) => rule_id));
const observedRules = new Set();
const observedOutcomes = new Set();
const caseIds = new Set();
for (const trace of suite.cases) {
  assert(!caseIds.has(trace.case_id), `Duplicate trace case_id: ${trace.case_id}.`);
  caseIds.add(trace.case_id);
  assert(trace.expectation_matches === true, `${trace.case_id} failed its expected rule or classification.`);
  assert(trace.classification === trace.expected_classification, `${trace.case_id} classification mismatch.`);
  assert(trace.classification_rule_id === trace.expected_rule_id, `${trace.case_id} rule mismatch.`);
  observedRules.add(trace.classification_rule_id);
  observedOutcomes.add(trace.classification);
}
for (const ruleId of expectedRules) assert(observedRules.has(ruleId), `Policy branch ${ruleId} lacks a canonical trace.`);
for (const outcome of ['preserved', 'partially_preserved', 'underdetermined', 'not_preserved']) assert(observedOutcomes.has(outcome), `Outcome ${outcome} lacks trace coverage.`);

const byId = Object.fromEntries(suite.cases.map((trace) => [trace.case_id, trace]));
assert(byId.capacity_sufficiently_explanatory.triggered_hard_fails.includes('generic_capacity_control_explains_primary_effect'), 'Sufficient capacity explanation must generate the capacity hard fail.');
assert(byId.capacity_role_underdetermined.passed_predicate_ids.includes('matching_inadequate'), 'Unresolved capacity role must block positive classification.');
assert(byId.measurement_inadequate.passed_predicate_ids.includes('measurement_inadequate'), 'Measurement inadequacy must remain explicit.');
assert(byId.low_score_adequate_measurement.passed_predicate_ids.includes('low_score_with_adequate_measurement'), 'Low-score defeat must require adequate measurement.');
assert(byId.fallback_gap_case.classification_rule_id === 'underdetermined-fallback', 'Fallback branch is not exercised.');
assert(byId.behavioral_theater_hard_fail.classification === 'not_preserved', 'Behavioral theater hard fail must defeat the mechanism claim.');

const boundaryExpectations = {
  boundary_below_low_0_95: [0.95, 'not_preserved'],
  boundary_exact_low_1_00: [1.0, 'underdetermined'],
  boundary_below_partial_1_55: [1.55, 'underdetermined'],
  boundary_exact_partial_1_60: [1.6, 'partially_preserved'],
  boundary_below_preserved_2_35: [2.35, 'partially_preserved'],
  boundary_exact_preserved_2_40: [2.4, 'preserved']
};
for (const [caseId, [score, classification]] of Object.entries(boundaryExpectations)) {
  assert(byId[caseId], `Missing exact-boundary trace ${caseId}.`);
  assert(byId[caseId].weighted_score === score, `${caseId} must sit exactly at the declared boundary test score.`);
  assert(byId[caseId].classification === classification, `${caseId} produced the wrong boundary classification.`);
}

assert(byId.precedence_hard_fail_over_measurement.classification === 'not_preserved', 'A decisive hard fail must outrank measurement underdetermination and a high score.');
assert(byId.precedence_hard_fail_over_measurement.classification_rule_id === 'not-preserved-decisive-defeat', 'Hard-fail precedence selected the wrong rule.');
assert(byId.precedence_capacity_hard_fail_over_conflict.classification === 'not_preserved', 'A sufficiently explanatory capacity mismatch must outrank conflicting-intervention underdetermination.');
assert(byId.precedence_low_score_blocked_by_inadequate_measurement.classification === 'underdetermined', 'A sub-1.00 score without adequate measurement must not be called not preserved.');
assert(!byId.precedence_low_score_blocked_by_inadequate_measurement.passed_predicate_ids.includes('low_score_with_adequate_measurement'), 'Low-score defeat must not pass when measurement is inadequate.');
for (const blocker of ['measurement_inadequate', 'matching_inadequate', 'conflicting_interventions']) {
  assert(byId.multi_blocker_measurement_and_matching.passed_predicate_ids.includes(blocker), `Multi-blocker trace must preserve ${blocker}.`);
}

console.log(`Validated ${suite.cases.length} canonical adversarial traces across all ${expectedRules.size} policy branches, six exact threshold edges, and four precedence interactions.`);
