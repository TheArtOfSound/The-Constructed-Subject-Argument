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

console.log(`Validated ${suite.cases.length} canonical adversarial traces across all ${expectedRules.size} classification-policy branches.`);
