import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = process.cwd();
const readBytes = relative => fs.readFileSync(path.join(root, relative));
const readJson = relative => JSON.parse(readBytes(relative).toString('utf8'));
const gitBlobSha = bytes => crypto.createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex');
const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const fail = message => { console.error(`Preregistration bundle validation failed: ${message}`); process.exit(1); };
const sameSet = (a, b) => a.length === b.length && [...a].sort().every((value, index) => value === [...b].sort()[index]);
const unique = values => new Set(values).size === values.length;

const lock = readJson('research/MECHANISM_PRESERVATION_PREREGISTRATION_LOCK.json');
const bundleBytes = readBytes(lock.bundle_path);
const bundle = JSON.parse(bundleBytes.toString('utf8'));
const result = readJson(lock.empirical_record_path);
const manifest = readJson('research/MECHANISM_PRESERVATION_INTERVENTION_MANIFEST.json');

if (lock.bundle_id !== bundle.bundle_id) fail('lock bundle_id does not match bundle.');
if (lock.run_id !== bundle.run_id || lock.run_id !== result.run_id) fail('run_id mismatch across lock, bundle, and empirical record.');
if (gitBlobSha(bundleBytes) !== lock.bundle_git_blob_sha) fail('bundle Git blob SHA does not match exact bytes.');
if (sha256(bundleBytes) !== lock.bundle_sha256) fail('bundle SHA-256 does not match exact bytes.');
if (!bundle.frozen_before_outcomes) fail('bundle must declare frozen_before_outcomes=true.');
if (!String(bundle.fixture_notice).includes('synthetic')) fail('synthetic fixture boundary is missing.');
if (!String(bundle.epistemic_boundary).includes('cannot establish consciousness')) fail('consciousness non-entailment boundary is missing.');
if (!String(lock.chronology_claim).includes('no external timestamp authority')) fail('lock overstates chronology.');

const dependencyRoles = bundle.dependency_locks.map(item => item.role);
for (const required of ['governing_protocol', 'frozen_intervention_inventory', 'normative_score_derivation']) {
  if (!dependencyRoles.includes(required)) fail(`missing dependency role ${required}.`);
}
if (!unique(bundle.dependency_locks.map(item => item.path))) fail('dependency paths must be unique.');
for (const dependency of bundle.dependency_locks) {
  const bytes = readBytes(dependency.path);
  if (gitBlobSha(bytes) !== dependency.git_blob_sha) fail(`dependency Git blob SHA mismatch for ${dependency.path}.`);
  if (dependency.sha256 && sha256(bytes) !== dependency.sha256) fail(`dependency SHA-256 mismatch for ${dependency.path}.`);
}

if (bundle.protocol_id !== result.protocol_id || bundle.protocol_id !== manifest.protocol_id) fail('protocol mismatch.');
if (bundle.mechanism_graph.graph_id !== result.preregistration.mechanism_graph_id) fail('mechanism graph ID drifted from empirical record.');
if (bundle.candidate_mapping.mapping_id !== result.preregistration.candidate_mapping_id) fail('candidate mapping ID drifted from empirical record.');

const nodeIds = bundle.mechanism_graph.nodes.map(node => node.node_id);
if (!unique(nodeIds)) fail('mechanism graph node IDs must be unique.');
for (const dependency of bundle.mechanism_graph.dependencies) {
  if (!nodeIds.includes(dependency.source) || !nodeIds.includes(dependency.target)) fail(`graph dependency ${dependency.dependency_id} references an unknown node.`);
}

const plannedIds = manifest.planned_interventions.map(item => item.intervention_id);
const mappingInterventionIds = bundle.candidate_mapping.mappings.map(item => item.predicted_intervention_id);
if (!sameSet(mappingInterventionIds, plannedIds)) fail('candidate mapping predictions must cover exactly the frozen intervention inventory.');
for (const mapping of bundle.candidate_mapping.mappings) {
  if (!nodeIds.includes(mapping.graph_node_id)) fail(`candidate mapping references unknown graph node ${mapping.graph_node_id}.`);
}

const bundleOutcomes = bundle.outcome_inventory.filter(item => item.priority === 'primary').map(item => item.outcome_id);
if (!sameSet(bundleOutcomes, result.preregistration.primary_outcomes)) fail('primary outcome inventory drifted from empirical record.');
if (!sameSet(bundleOutcomes, manifest.planned_interventions.map(item => item.primary_outcome))) fail('primary outcome inventory drifted from intervention manifest.');
for (const outcome of bundle.outcome_inventory) {
  if (!outcome.estimand || !outcome.expected_direction || !outcome.decision_rule) fail(`outcome ${outcome.outcome_id} lacks estimand, direction, or decision rule.`);
}

const bundleMetrics = bundle.matching_plan.required_metric_ids;
const reportedMetrics = result.behavioral_matching.metrics.map(metric => metric.metric_id);
if (!sameSet(bundleMetrics, reportedMetrics)) fail('matching metric inventory drifted from empirical record.');
if (!unique(bundleMetrics)) fail('matching metric IDs must be unique.');
for (const metric of result.behavioral_matching.metrics) {
  if (metric.tolerance !== bundle.matching_plan.default_standardized_difference_tolerance) fail(`metric ${metric.metric_id} tolerance differs from frozen bundle.`);
}

if (bundle.analysis_policy.score_rule_registry_id !== 'EXP-11-SCORE-DERIVATION-RULES') fail('score registry binding is missing or changed.');
if (bundle.analysis_policy.minimum_replications !== 3) fail('minimum replication policy drifted.');
if (bundle.analysis_policy.interval_level !== 0.95) fail('interval level must remain explicit and frozen at 0.95 for the fixture.');
if (!Array.isArray(bundle.analysis_policy.null_region) || bundle.analysis_policy.null_region.length !== 2) fail('null region must contain exactly two bounds.');

const forbidden = new Set(bundle.forbidden_conclusions);
for (const statement of result.forbidden_conclusions) {
  if (!forbidden.has(statement)) fail(`empirical forbidden conclusion missing from bundle: ${statement}`);
}
if (!bundle.exclusion_codes.some(item => item.code === 'OUTCOME_DEPENDENT_EXCLUSION' && item.allowed === false)) fail('outcome-dependent exclusion prohibition is missing.');
if (!String(bundle.completeness_rule).includes('reconcile exactly')) fail('exact cross-file reconciliation rule is missing.');

console.log('Preregistration bundle validation passed.');
console.log(`Bundle: ${bundle.bundle_id}`);
console.log(`Dependencies locked: ${bundle.dependency_locks.length}`);
console.log(`Graph nodes: ${nodeIds.length}; mappings: ${bundle.candidate_mapping.mappings.length}; primary outcomes: ${bundleOutcomes.length}; matching metrics: ${bundleMetrics.length}`);
console.log('Boundary preserved: repository-internal consistency does not establish external chronology, real mechanism preservation, or consciousness.');
