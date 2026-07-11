#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { generateClassificationTrace, serializeClassificationTrace } from './generate-mechanism-classification-trace.mjs';
import { loadClassificationPolicy } from './score-mechanism-preservation.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const tracePath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_TRACE.json');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const committed = fs.readFileSync(tracePath, 'utf8');
const regenerated = serializeClassificationTrace();
assert(committed === regenerated, 'Committed classification trace differs byte-for-byte from deterministic regeneration.');

const trace = generateClassificationTrace();
const policy = loadClassificationPolicy();
assert(trace.schema_version === '1.2.0', 'Classification trace schema must expose structured-policy provenance.');
assert(trace.generated === true, 'Classification trace must be marked generated.');
assert(trace.empirical_status === 'synthetic_fixture', 'Canonical classification trace must remain explicitly synthetic.');
assert(trace.classification_policy_id === policy.schema_id, 'Trace must identify the authoritative classification policy.');
assert(trace.source_artifacts.classification_policy === 'research/MECHANISM_PRESERVATION_CLASSIFICATION_POLICY.json', 'Trace must expose the classification-policy source artifact.');
assert(trace.dimensions.length === 6, 'Classification trace must contain all six protocol dimensions.');
assert(new Set(trace.dimensions.map(({ dimension_id }) => dimension_id)).size === 6, 'Classification trace dimension IDs must be unique.');
assert(trace.hard_fail_assessments.length === 5, 'Classification trace must contain all five protocol hard-fail conditions.');
assert(new Set(trace.hard_fail_assessments.map(({ condition_id }) => condition_id)).size === 5, 'Hard-fail condition IDs must be unique.');
assert(trace.dimensions.filter(({ provenance }) => provenance === 'generated_capacity_adjudication').length === 1, 'Exactly one dimension must come from generated capacity adjudication.');
assert(trace.hard_fail_assessments.filter(({ provenance }) => provenance === 'generated_capacity_adjudication').length === 1, 'Exactly one hard fail must come from generated capacity adjudication.');

const contributionTotal = Number(trace.dimensions.reduce((sum, dimension) => sum + dimension.weighted_contribution, 0).toFixed(4));
assert(contributionTotal === trace.weighted_score, 'Weighted contributions must sum exactly to the reported weighted score.');
assert(trace.expected_classification_matches === true, 'Generated classification must match the fixture expectation.');
assert(trace.final_classification === 'preserved', 'Canonical positive-path fixture must exercise the preserved branch.');
assert(trace.classification_rule_id === 'preserved-thresholds', 'Canonical positive-path fixture must resolve through the preserved policy rule.');
assert(trace.triggered_hard_fails.length === 0, 'Canonical positive-path fixture must not trigger a hard fail.');
assert(trace.fixture_notice.includes('no observation about any actual AI system'), 'Trace must retain the real-system non-entailment notice.');

assert(!Object.hasOwn(trace, 'classification_blockers'), 'Positive and negative rationale must not be mislabeled as classification blockers.');
assert(Array.isArray(trace.classification_reasons) && trace.classification_reasons.length > 0, 'Trace must expose neutral classification reasons.');

const preservedRule = policy.outcomes.find(({ rule_id }) => rule_id === trace.classification_rule_id);
assert(preservedRule, 'Trace classification rule must resolve in the authoritative policy.');
assert(trace.threshold_evaluations.length === preservedRule.requirements.length, 'Trace threshold count must equal the matched policy rule requirement count.');
const expectedPredicates = new Map(preservedRule.requirements.map((predicate) => [predicate.predicate_id, predicate]));
assert(new Set(trace.threshold_evaluations.map(({ threshold_id }) => threshold_id)).size === trace.threshold_evaluations.length, 'Threshold IDs must be unique.');
for (const threshold of trace.threshold_evaluations) {
  const expected = expectedPredicates.get(threshold.threshold_id);
  assert(expected, `Threshold ${threshold.threshold_id} is not declared by the matched policy rule.`);
  assert(threshold.operator === expected.operator, `Threshold ${threshold.threshold_id} uses an operator that differs from policy.`);
  assert(threshold.required === expected.value, `Threshold ${threshold.threshold_id} uses a requirement that differs from policy.`);
  assert(threshold.description === expected.description, `Threshold ${threshold.threshold_id} description differs from policy.`);
  assert(threshold.passed === true, `Preserved-policy predicate ${threshold.threshold_id} must pass.`);
}

assert(trace.presentation_safety?.status_label === policy.presentation_contract.synthetic_fixture_label, 'Trace synthetic-fixture label must come from policy.');
assert(trace.presentation_safety?.display_rule === policy.presentation_contract.synthetic_label_prominence, 'Trace display prominence must come from policy.');
assert(trace.presentation_safety?.prohibited_implication === policy.presentation_contract.prohibited_implication, 'Trace prohibited implication must come from policy.');
assert(JSON.stringify(trace.epistemic_boundary) === JSON.stringify(policy.epistemic_boundary), 'Trace epistemic boundary must equal the policy boundary.');

const forbiddenText = JSON.stringify(trace.epistemic_boundary.does_not_support).toLowerCase();
for (const required of ['conscious', 'sentient', 'personhood', 'theory']) {
  assert(forbiddenText.includes(required), `Epistemic boundary must retain ${required} non-entailment.`);
}

console.log('Mechanism classification trace is deterministic, policy-derived, threshold-auditable, and epistemically bounded.');
