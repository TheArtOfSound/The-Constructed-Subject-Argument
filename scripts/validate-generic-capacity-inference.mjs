import fs from 'node:fs';
import path from 'node:path';
import { buildGenericCapacityInference, serializeGenericCapacityInference } from './generate-generic-capacity-inference.mjs';

const root = process.cwd();
const matching = JSON.parse(fs.readFileSync(path.join(root, 'research/MECHANISM_PRESERVATION_MATCHING_DERIVED_RESULTS.json'), 'utf8'));
const empirical = JSON.parse(fs.readFileSync(path.join(root, 'research/MECHANISM_PRESERVATION_EMPIRICAL_FIXTURE.json'), 'utf8'));
const committed = fs.readFileSync(path.join(root, 'research/MECHANISM_PRESERVATION_GENERIC_CAPACITY_INFERENCE.json'), 'utf8');
const generated = buildGenericCapacityInference(matching);

function fail(message) {
  console.error(`Generic-capacity inference validation failed: ${message}`);
  process.exit(1);
}

if (committed !== serializeGenericCapacityInference(generated)) fail('committed artifact differs from deterministic regeneration');
if (!['matched', 'not_matched', 'underdetermined'].includes(generated.overall_state)) fail('invalid overall state');

const genericDimension = empirical.dimension_derivations.find((entry) => entry.dimension_id === 'generic_capacity_exclusion');
if (!genericDimension) fail('empirical fixture lacks generic-capacity dimension');
if (genericDimension.score !== generated.permitted_generic_capacity_exclusion_score) fail('empirical score exceeds or diverges from generated score');

const hardFail = empirical.hard_fail_assessments.find((entry) => entry.condition_id === 'generic_capacity_control_explains_primary_effect');
if (!hardFail) fail('empirical fixture lacks generic-capacity hard-fail assessment');
if (Boolean(hardFail.triggered) !== generated.generic_capacity_hard_fail) fail('hard-fail state diverges from generated inference');

const clone = () => JSON.parse(JSON.stringify(matching));

const outside = clone();
outside.metrics[0].equivalence_interval = [0.12, 0.18];
let result = buildGenericCapacityInference(outside);
if (result.overall_state !== 'not_matched' || result.permitted_generic_capacity_exclusion_score !== 0 || !result.generic_capacity_hard_fail) {
  fail('fully outside-margin fixture did not produce not_matched hard fail');
}

const crossing = clone();
crossing.metrics[0].equivalence_interval = [0.08, 0.12];
result = buildGenericCapacityInference(crossing);
if (result.overall_state !== 'underdetermined' || result.permitted_generic_capacity_exclusion_score !== 1 || result.generic_capacity_hard_fail) {
  fail('boundary-crossing fixture did not remain underdetermined');
}

const underpowered = clone();
underpowered.metrics[0].pair_count = 2;
result = buildGenericCapacityInference(underpowered);
if (result.overall_state !== 'underdetermined' || result.metric_states[0].reason !== 'insufficient_pairs') {
  fail('underpowered fixture did not remain underdetermined');
}

const missing = clone();
missing.metrics = missing.metrics.slice(1);
result = buildGenericCapacityInference(missing);
if (result.overall_state === 'matched') fail('omitted protocol metric was incorrectly accepted as matched');

if (!generated.epistemic_boundary.includes('does not establish mechanism preservation') || !generated.epistemic_boundary.includes('consciousness')) {
  fail('epistemic boundary was weakened');
}

console.log('Generic-capacity inference artifact, negative paths, score cap, and hard-fail propagation validated.');
