import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = process.cwd();
const matchingPath = path.join(root, 'research/MECHANISM_PRESERVATION_MATCHING_DERIVED_RESULTS.json');
const outputPath = path.join(root, 'research/MECHANISM_PRESERVATION_GENERIC_CAPACITY_INFERENCE.json');

function classifyMetric(metric) {
  const pairCount = Number(metric.pair_count ?? metric.n_pairs ?? 0);
  const minimumPairs = Number(metric.minimum_pair_count ?? 4);
  const interval = metric.equivalence_interval ?? metric.uncertainty_interval;
  const margin = Number(metric.equivalence_margin ?? metric.tolerance ?? 0.10);

  if (!Array.isArray(interval) || interval.length !== 2 || pairCount < minimumPairs) {
    return { state: 'underdetermined', reason: pairCount < minimumPairs ? 'insufficient_pairs' : 'missing_interval' };
  }

  const [lower, upper] = interval.map(Number);
  if (!Number.isFinite(lower) || !Number.isFinite(upper) || !Number.isFinite(margin)) {
    return { state: 'underdetermined', reason: 'invalid_numeric_evidence' };
  }

  if (lower >= -margin && upper <= margin) {
    return { state: 'matched', reason: 'equivalence_interval_within_margin' };
  }

  if (upper < -margin || lower > margin) {
    return { state: 'not_matched', reason: 'equivalence_interval_outside_margin' };
  }

  return { state: 'underdetermined', reason: 'interval_crosses_equivalence_boundary' };
}

export function buildGenericCapacityInference(matching) {
  const metrics = matching.metrics ?? matching.results ?? [];
  if (!Array.isArray(metrics) || metrics.length === 0) throw new Error('Matching artifact contains no metrics.');

  const metricStates = metrics.map((metric) => {
    const classified = classifyMetric(metric);
    return {
      metric_id: metric.metric_id,
      primary: metric.primary !== false,
      state: classified.state,
      reason: classified.reason
    };
  });

  const primary = metricStates.filter((metric) => metric.primary);
  const hasNotMatched = primary.some((metric) => metric.state === 'not_matched');
  const hasUnderdetermined = primary.some((metric) => metric.state === 'underdetermined');
  const overallState = hasNotMatched ? 'not_matched' : hasUnderdetermined ? 'underdetermined' : 'matched';

  return {
    schema_version: '1.0.0',
    inference_id: 'EXP11-GENERIC-CAPACITY-INFERENCE-001',
    protocol_id: matching.protocol_id ?? 'EXP-11-MECHANISM-PRESERVATION',
    run_id: matching.run_id,
    empirical_status: 'synthetic_fixture',
    generated_notice: 'Generated deterministically from the synthetic behavioral-matching artifact. Do not edit manually.',
    metric_states: metricStates,
    overall_state: overallState,
    permitted_generic_capacity_exclusion_score: overallState === 'matched' ? 2 : overallState === 'underdetermined' ? 1 : 0,
    generic_capacity_hard_fail: overallState === 'not_matched',
    classification_effect: overallState === 'matched'
      ? 'Matching supports bounded exclusion of the represented generic-capacity differences.'
      : overallState === 'underdetermined'
        ? 'Mechanism-preservation classification must remain underdetermined until matching equivalence is established.'
        : 'A detected generic-capacity mismatch defeats a positive mechanism-preservation classification for this comparison.',
    epistemic_boundary: 'Behavioral matching controls represented generic-capacity confounds only. It does not establish mechanism preservation, consciousness, nonconsciousness, sentience, personhood, identity, or moral status.'
  };
}

export function serializeGenericCapacityInference(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function runCli() {
  const matching = JSON.parse(fs.readFileSync(matchingPath, 'utf8'));
  const serialized = serializeGenericCapacityInference(buildGenericCapacityInference(matching));
  if (process.argv.includes('--stdout')) {
    process.stdout.write(serialized);
    return;
  }
  if (process.argv.includes('--check')) {
    const committed = fs.existsSync(outputPath) ? fs.readFileSync(outputPath, 'utf8') : '';
    if (committed !== serialized) {
      console.error('Generic-capacity inference artifact is stale or manually edited.');
      process.exit(1);
    }
    console.log('Generic-capacity inference artifact matches deterministic regeneration.');
    return;
  }
  fs.writeFileSync(outputPath, serialized);
  console.log(`Wrote ${path.relative(root, outputPath)}`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) runCli();
