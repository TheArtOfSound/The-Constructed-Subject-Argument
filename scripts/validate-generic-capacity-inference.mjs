import fs from 'node:fs';
import path from 'node:path';
import { buildGenericCapacityInference, serializeGenericCapacityInference } from './generate-generic-capacity-inference.mjs';

const root = process.cwd();
const matching = JSON.parse(fs.readFileSync(path.join(root, 'research/MECHANISM_PRESERVATION_MATCHING_DERIVED_RESULTS.json'), 'utf8'));
const empirical = JSON.parse(fs.readFileSync(path.join(root, 'research/MECHANISM_PRESERVATION_EMPIRICAL_FIXTURE.json'), 'utf8'));
const adjudication = JSON.parse(fs.readFileSync(path.join(root, 'research/MECHANISM_PRESERVATION_CAPACITY_CONFOUND_ADJUDICATION.json'), 'utf8'));
const committed = fs.readFileSync(path.join(root, 'research/MECHANISM_PRESERVATION_GENERIC_CAPACITY_INFERENCE.json'), 'utf8');
const generated = buildGenericCapacityInference(matching);

function fail(message) {
  console.error(`Generic-capacity inference validation failed: ${message}`);
  process.exit(1);
}

if (committed !== serializeGenericCapacityInference(generated)) fail('committed artifact differs from deterministic regeneration');
if (!['matched', 'not_matched', 'underdetermined'].includes(generated.overall_state)) fail('invalid overall state');

if (Object.hasOwn(empirical.behavioral_matching ?? {}, 'behavioral_matching_adequate')) fail('empirical fixture stores deprecated aggregate matching authority');
if ((empirical.dimension_derivations ?? []).some((entry) => entry.dimension_id === 'generic_capacity_exclusion')) fail('empirical fixture stores deprecated generated generic-capacity dimension');
if ((empirical.hard_fail_assessments ?? []).some((entry) => entry.condition_id === 'generic_capacity_control_explains_primary_effect')) fail('empirical fixture stores deprecated generated capacity hard fail');

if (adjudication.protocol_id !== generated.protocol_id || adjudication.run_id !== generated.run_id) fail('authoritative adjudication targets a different protocol or run');
if (adjudication.matching_overall_state !== generated.overall_state) fail('authoritative adjudication disagrees with generated matching state');
if (adjudication.maximum_generic_capacity_exclusion_score !== generated.permitted_generic_capacity_exclusion_score) fail('authoritative adjudication score ceiling diverges from generated inference');
if (adjudication.generic_capacity_hard_fail !== generated.generic_capacity_hard_fail) fail('authoritative adjudication hard-fail state diverges from generated inference');

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

console.log('Generic-capacity inference artifact, negative paths, authoritative-adjudication agreement, and non-duplication contract validated.');
