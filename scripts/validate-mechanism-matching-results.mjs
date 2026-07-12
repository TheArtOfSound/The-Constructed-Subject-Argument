import fs from 'node:fs';
import path from 'node:path';
import { buildMatchingResults } from './generate-mechanism-matching-results.mjs';

const root = process.cwd();
const derivedPath = path.join(root, 'research/MECHANISM_PRESERVATION_MATCHING_DERIVED_RESULTS.json');
const empiricalPath = path.join(root, 'research/MECHANISM_PRESERVATION_EMPIRICAL_FIXTURE.json');
const rawPath = path.join(root, 'research/MECHANISM_PRESERVATION_MATCHING_RAW_FIXTURE.json');

const committedText = fs.readFileSync(derivedPath, 'utf8');
const regenerated = buildMatchingResults();
const regeneratedText = `${JSON.stringify(regenerated, null, 2)}\n`;
const committed = JSON.parse(committedText);
const empirical = JSON.parse(fs.readFileSync(empiricalPath, 'utf8'));
const raw = JSON.parse(fs.readFileSync(rawPath, 'utf8'));
const fail = message => { console.error(message); process.exit(1); };

if (committedText !== regeneratedText) fail('Committed matching artifact is not byte-identical to deterministic regeneration.');
if (raw.empirical_status !== 'synthetic_fixture' || committed.empirical_status !== 'synthetic_fixture') fail('Matching fixture must remain explicitly synthetic.');
if (!raw.fixture_notice.includes('not measurements of an actual AI system')) fail('Raw matching fixture lost its real-system boundary.');
if (!committed.epistemic_boundary.includes('does not establish mechanism preservation')) fail('Derived matching artifact overstates what behavioral equivalence supports.');
if (!committed.epistemic_boundary.includes('consciousness')) fail('Derived matching artifact lost the consciousness non-entailment boundary.');

const expectedIds = [
  'task_accuracy',
  'calibration_error',
  'response_latency',
  'action_or_token_budget',
  'working_memory_capacity',
  'tool_access',
  'training_distribution',
  'total_compute',
  'evaluator_visible_language_quality'
];
const actualIds = committed.metrics.map(metric => metric.metric_id);
if (JSON.stringify(actualIds) !== JSON.stringify(expectedIds)) fail('Generated matching artifact does not contain the complete ordered nine-metric battery.');

const empiricalMetrics = new Map(empirical.behavioral_matching.metrics.map(metric => [metric.metric_id, metric]));
for (const metric of committed.metrics) {
  const reported = empiricalMetrics.get(metric.metric_id);
  if (!reported) fail(`Empirical fixture omits generated matching metric ${metric.metric_id}.`);
  if (reported.standardized_difference !== metric.standardized_difference) fail(`${metric.metric_id} standardized difference is stale or manually altered.`);
  if (reported.tolerance !== metric.equivalence_margin) fail(`${metric.metric_id} tolerance differs from the frozen equivalence margin.`);
  if (reported.passed !== metric.passed) fail(`${metric.metric_id} pass state differs from the generated equivalence decision.`);
  if (metric.pair_count < raw.derivation_contract.minimum_pairs) fail(`${metric.metric_id} lacks the preregistered minimum pair count.`);
}

const derivedAdequate = committed.metrics.filter(metric => metric.primary).every(metric => metric.passed);
if (committed.behavioral_matching_adequate !== derivedAdequate) fail('Generated aggregate matching state is inconsistent with primary metric decisions.');
if (Object.hasOwn(empirical.behavioral_matching, 'behavioral_matching_adequate')) fail('Empirical fixture must not store derived aggregate matching authority.');

console.log('Behavioral-matching results are complete, equivalence-based, synthetic-bounded, byte-identical to regeneration, and authoritative only in the generated artifact.');
