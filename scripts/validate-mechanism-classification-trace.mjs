#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { generateClassificationTrace, serializeClassificationTrace } from './generate-mechanism-classification-trace.mjs';

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
assert(trace.generated === true, 'Classification trace must be marked generated.');
assert(trace.empirical_status === 'synthetic_fixture', 'Canonical classification trace must remain explicitly synthetic.');
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
assert(trace.triggered_hard_fails.length === 0, 'Canonical positive-path fixture must not trigger a hard fail.');
assert(trace.fixture_notice.includes('no observation about any actual AI system'), 'Trace must retain the real-system non-entailment notice.');

const forbiddenText = JSON.stringify(trace.epistemic_boundary.does_not_support).toLowerCase();
for (const required of ['conscious', 'sentient', 'personhood', 'theory']) {
  assert(forbiddenText.includes(required), `Epistemic boundary must retain ${required} non-entailment.`);
}

console.log('Mechanism classification trace is deterministic, complete, and epistemically bounded.');
