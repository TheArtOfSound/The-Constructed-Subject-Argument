import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const rawPath = path.join(root, 'research/MECHANISM_PRESERVATION_MATCHING_RAW_FIXTURE.json');
const outputPath = path.join(root, 'research/MECHANISM_PRESERVATION_MATCHING_DERIVED_RESULTS.json');
const raw = JSON.parse(fs.readFileSync(rawPath, 'utf8'));
const contract = raw.derivation_contract;

const round = value => Number(value.toFixed(contract.rounding_decimals));
const mean = values => values.reduce((sum, value) => sum + value, 0) / values.length;
const sampleSd = values => {
  if (values.length < 2) return 0;
  const average = mean(values);
  return Math.sqrt(values.reduce((sum, value) => sum + ((value - average) ** 2), 0) / (values.length - 1));
};

function deriveMetric(metric) {
  if (metric.pairs.length < contract.minimum_pairs) {
    throw new Error(`${metric.metric_id} has fewer than ${contract.minimum_pairs} pairs.`);
  }
  const differences = metric.pairs.map(pair => (pair.candidate - pair.reference) / metric.preregistered_scale);
  const standardizedDifference = mean(differences);
  const standardError = sampleSd(differences) / Math.sqrt(differences.length);
  const interval = [
    standardizedDifference - contract.interval_multiplier * standardError,
    standardizedDifference + contract.interval_multiplier * standardError
  ];
  const passed = interval[0] >= -metric.equivalence_margin && interval[1] <= metric.equivalence_margin;
  return {
    metric_id: metric.metric_id,
    primary: metric.primary,
    estimator: contract.estimator,
    standardizer: contract.standardizer,
    pair_count: differences.length,
    standardized_difference: round(standardizedDifference),
    equivalence_interval: interval.map(round),
    equivalence_margin: metric.equivalence_margin,
    interval_level: contract.interval_level,
    passed
  };
}

export function buildMatchingResults() {
  const metrics = raw.metrics.map(deriveMetric);
  const primaryMetrics = metrics.filter(metric => metric.primary);
  return {
    schema_id: 'EXP-11-MATCHING-DERIVED-RESULTS',
    artifact_id: 'EXP11-SYNTHETIC-MATCHING-DERIVED-001',
    source_artifact_id: raw.artifact_id,
    run_id: raw.run_id,
    empirical_status: raw.empirical_status,
    generated_notice: 'Generated deterministically from the synthetic raw behavioral-matching artifact. Do not edit manually.',
    derivation_contract: contract,
    metrics,
    behavioral_matching_adequate: primaryMetrics.length > 0 && primaryMetrics.every(metric => metric.passed),
    epistemic_boundary: 'Behavioral equivalence is a control against generic-capacity confounding. It does not establish mechanism preservation, consciousness, nonconsciousness, sentience, personhood, identity, or moral status.'
  };
}

const serialized = `${JSON.stringify(buildMatchingResults(), null, 2)}\n`;
const args = new Set(process.argv.slice(2));

if (args.has('--stdout')) {
  process.stdout.write(serialized);
} else if (args.has('--check')) {
  const committed = fs.readFileSync(outputPath, 'utf8');
  if (committed !== serialized) {
    console.error('Committed behavioral-matching results differ from deterministic regeneration.');
    process.exit(1);
  }
  console.log('Behavioral-matching derived results are byte-identical to regeneration.');
} else {
  fs.writeFileSync(outputPath, serialized);
  console.log(`Wrote ${path.relative(root, outputPath)}.`);
}
