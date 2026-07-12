#!/usr/bin/env node
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { scoreMechanismPreservation } from './score-mechanism-preservation.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const readJson = (relative) => JSON.parse(fs.readFileSync(path.join(root, relative), 'utf8'));
const fail = (message) => { throw new Error(message); };
const assert = (condition, message) => { if (!condition) fail(message); };
const sameSet = (left, right) => left.size === right.size && [...left].every((value) => right.has(value));
const CAPACITY_DIMENSION = 'generic_capacity_exclusion';
const CAPACITY_HARD_FAIL = 'generic_capacity_control_explains_primary_effect';

const protocolPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_PROTOCOL.json');
const protocolBytes = fs.readFileSync(protocolPath);
const protocol = JSON.parse(protocolBytes.toString('utf8'));
const schema = readJson('research/MECHANISM_PRESERVATION_EMPIRICAL_SCHEMA.json');
const record = readJson('research/MECHANISM_PRESERVATION_EMPIRICAL_FIXTURE.json');
const ruleRegistry = readJson('research/MECHANISM_SCORE_DERIVATION_RULES.json');
const manifest = readJson(record.intervention_manifest_lock?.path ?? 'research/MECHANISM_PRESERVATION_INTERVENTION_MANIFEST.json');
const capacityAdjudication = readJson(record.capacity_confound_adjudication_lock?.path ?? 'research/MECHANISM_PRESERVATION_CAPACITY_CONFOUND_ADJUDICATION.json');

const gitBlobSha = crypto
  .createHash('sha1')
  .update(Buffer.from(`blob ${protocolBytes.length}\0`))
  .update(protocolBytes)
  .digest('hex');

assert(schema.schema_version === '1.6.0', 'Empirical validator requires schema 1.6.0.');
assert(schema.protocol_id === protocol.protocol_id, 'Empirical schema must target the active mechanism protocol.');
assert(ruleRegistry.protocol_id === protocol.protocol_id, 'Derivation-rule registry must target the active mechanism protocol.');
assert(record.schema_id === schema.schema_id, 'Empirical record schema_id mismatch.');
assert(record.protocol_id === protocol.protocol_id, 'Empirical record protocol_id mismatch.');
assert(record.protocol_lock?.git_blob_sha === gitBlobSha, 'Protocol lock does not match the exact protocol Git blob SHA.');
assert(record.protocol_lock?.protocol_version === protocol.schema_version, 'Protocol version lock mismatch.');
assert(schema.empirical_status_values.includes(record.empirical_status), 'Invalid empirical_status.');
assert(record.empirical_status === 'synthetic_fixture', 'Repository fixture must remain explicitly synthetic.');
assert(record.fixture_notice?.includes('no observation about any actual AI system'), 'Synthetic fixture boundary is missing.');

for (const field of schema.required_top_level_fields) assert(Object.hasOwn(record, field), `Missing required empirical field: ${field}.`);
for (const field of schema.preregistration.required_fields) assert(Object.hasOwn(record.preregistration ?? {}, field), `Missing preregistration field: ${field}.`);
for (const field of schema.intervention_manifest_lock.required_fields) assert(Object.hasOwn(record.intervention_manifest_lock ?? {}, field), `Missing intervention manifest lock field: ${field}.`);
for (const field of schema.capacity_confound_adjudication_lock.required_fields) assert(Object.hasOwn(record.capacity_confound_adjudication_lock ?? {}, field), `Missing capacity adjudication lock field: ${field}.`);

assert(manifest.manifest_id === record.intervention_manifest_lock.manifest_id, 'Intervention manifest ID mismatch.');
assert(manifest.protocol_id === protocol.protocol_id, 'Intervention manifest targets the wrong protocol.');
assert(manifest.run_id === record.run_id, 'Intervention manifest and empirical record must target the same run.');
assert(manifest.frozen_before_outcomes === true, 'Intervention manifest must be frozen before outcomes.');
assert(manifest.fixture_notice?.includes('no empirical observation about an actual AI system'), 'Synthetic intervention manifest boundary is missing.');

assert(capacityAdjudication.adjudication_id === record.capacity_confound_adjudication_lock.adjudication_id, 'Capacity adjudication ID mismatch.');
assert(capacityAdjudication.adjudication_state === record.capacity_confound_adjudication_lock.adjudication_state, 'Capacity adjudication state mismatch.');
assert(capacityAdjudication.protocol_id === protocol.protocol_id, 'Capacity adjudication targets the wrong protocol.');
assert(capacityAdjudication.run_id === record.run_id, 'Capacity adjudication and empirical record must target the same run.');
assert(capacityAdjudication.empirical_status === record.empirical_status, 'Capacity adjudication empirical status mismatch.');
assert(capacityAdjudication.generated_notice?.includes('Do not edit manually'), 'Capacity adjudication must remain an explicitly generated artifact.');
assert(typeof capacityAdjudication.epistemic_boundary === 'string' && capacityAdjudication.epistemic_boundary.includes('consciousness'), 'Capacity adjudication lost the consciousness non-entailment boundary.');
assert(/\b(?:does|do) not establish mechanism preservation\b/i.test(capacityAdjudication.epistemic_boundary), 'Capacity adjudication lost the mechanism-preservation non-entailment boundary.');

assert(!Object.hasOwn(record.behavioral_matching ?? {}, 'behavioral_matching_adequate'), 'Aggregate matching adequacy must not be stored in the empirical record.');
assert(!(record.dimension_derivations ?? []).some((item) => item.dimension_id === CAPACITY_DIMENSION), 'Generated generic-capacity dimension must not be stored in the empirical record.');
assert(!(record.hard_fail_assessments ?? []).some((item) => item.condition_id === CAPACITY_HARD_FAIL), 'Generated capacity hard fail must not be stored in the empirical record.');

const requiredMetricIds = new Set(protocol.behavioral_equivalence.required_metrics);
const metrics = record.behavioral_matching?.metrics ?? [];
const metricIds = new Set(metrics.map((metric) => metric.metric_id));
assert(metrics.length === metricIds.size, 'Behavioral matching metrics contain duplicate metric IDs.');
assert(sameSet(metricIds, requiredMetricIds), `Behavioral matching must report every protocol metric exactly once. Required: ${[...requiredMetricIds].join(', ')}.`);
for (const metric of metrics) {
  for (const field of schema.behavioral_matching_metric.required_fields) assert(Object.hasOwn(metric, field), `Matching metric ${metric.metric_id ?? '<unknown>'} lacks ${field}.`);
  assert(metric.passed === Math.abs(metric.standardized_difference) <= metric.tolerance, `Matching metric ${metric.metric_id} has a non-deterministic pass value.`);
}
const allPrimaryPass = metrics.filter((metric) => metric.primary).every((metric) => metric.passed);

const protocolFamilies = new Map(protocol.intervention_families.map((family) => [family.id, family]));
const planned = manifest.planned_interventions ?? [];
const plannedById = new Map();
for (const item of planned) {
  assert(typeof item.intervention_id === 'string' && item.intervention_id.length > 0, 'Planned intervention lacks intervention_id.');
  assert(!plannedById.has(item.intervention_id), `Duplicate planned intervention ID: ${item.intervention_id}.`);
  assert(protocolFamilies.has(item.family), `Planned intervention ${item.intervention_id} uses unknown family ${item.family}.`);
  assert(Array.isArray(item.required_controls) && item.required_controls.length > 0, `Planned intervention ${item.intervention_id} lacks required controls.`);
  const protocolControls = new Set(protocolFamilies.get(item.family).minimum_controls);
  const manifestControls = new Set(item.required_controls);
  assert([...protocolControls].every((id) => manifestControls.has(id)), `Planned intervention ${item.intervention_id} omits a protocol-minimum control.`);
  assert(typeof item.analysis_rule === 'string' && item.analysis_rule.length >= 60, `Planned intervention ${item.intervention_id} lacks a substantive analysis rule.`);
  plannedById.set(item.intervention_id, item);
}
assert(plannedById.size > 0, 'Frozen intervention manifest contains no planned interventions.');

const interventions = record.interventions ?? [];
const interventionById = new Map();
for (const intervention of interventions) {
  for (const field of schema.intervention_result.required_fields) assert(Object.hasOwn(intervention, field), `Intervention ${intervention.intervention_id ?? '<unknown>'} lacks ${field}.`);
  assert(!interventionById.has(intervention.intervention_id), `Duplicate intervention ID: ${intervention.intervention_id}.`);
  assert(schema.intervention_result.reporting_status_values.includes(intervention.reporting_status), `Intervention ${intervention.intervention_id} has invalid reporting_status.`);
  const plan = plannedById.get(intervention.intervention_id);
  assert(plan, `Reported intervention ${intervention.intervention_id} was not preregistered.`);
  assert(intervention.family === plan.family, `Intervention ${intervention.intervention_id} family diverges from the frozen plan.`);
  assert(intervention.target_dependency === plan.target_dependency, `Intervention ${intervention.intervention_id} target dependency diverges from the frozen plan.`);
  assert(Array.isArray(intervention.uncertainty_interval) && intervention.uncertainty_interval.length === 2, `Intervention ${intervention.intervention_id} needs a two-value uncertainty interval.`);
  assert(intervention.replications >= Math.max(schema.intervention_result.minimum_replications, plan.minimum_replications), `Intervention ${intervention.intervention_id} does not meet minimum replication.`);
  const controls = intervention.control_results ?? [];
  const controlIds = new Set(controls.map((control) => control.control_id));
  assert(controls.length === controlIds.size, `Intervention ${intervention.intervention_id} contains duplicate control results.`);
  assert(sameSet(controlIds, new Set(plan.required_controls)), `Intervention ${intervention.intervention_id} must report every frozen required control exactly once.`);
  assert(controls.every((control) => typeof control.passed === 'boolean'), `Intervention ${intervention.intervention_id} has a non-Boolean control result.`);
  assert(intervention.controls_passed === controls.every((control) => control.passed), `Intervention ${intervention.intervention_id} controls_passed is inconsistent with control results.`);
  interventionById.set(intervention.intervention_id, intervention);
}
assert(sameSet(new Set(interventionById.keys()), new Set(plannedById.keys())), 'Every planned intervention must be reported exactly once; null, failed, aborted, and excluded results cannot be omitted.');

const knownHardFails = new Set(protocol.scoring.hard_fail_conditions);
const submittedHardFails = new Set([...knownHardFails].filter((id) => id !== CAPACITY_HARD_FAIL));
const hardFailById = new Map();
const triggered = [];
let decisive = false;
for (const assessment of record.hard_fail_assessments ?? []) {
  for (const field of schema.hard_fail_assessment.required_fields) assert(Object.hasOwn(assessment, field), `Hard-fail assessment ${assessment.condition_id ?? '<unknown>'} lacks ${field}.`);
  assert(submittedHardFails.has(assessment.condition_id), `Unknown or generated hard-fail condition submitted: ${assessment.condition_id}.`);
  assert(!hardFailById.has(assessment.condition_id), `Duplicate hard-fail assessment: ${assessment.condition_id}.`);
  if (assessment.decisive) {
    assert(assessment.triggered, `Hard fail ${assessment.condition_id} cannot be decisive when not triggered.`);
    assert(assessment.justification.length >= 60, `Decisive hard fail ${assessment.condition_id} lacks a substantive dependency-defeat justification.`);
    decisive = true;
  }
  if (assessment.triggered) triggered.push(assessment.condition_id);
  hardFailById.set(assessment.condition_id, assessment);
}
assert(hardFailById.size === submittedHardFails.size, 'Every non-capacity protocol hard fail must be assessed exactly once.');
assert(hardFailById.size === schema.hard_fail_assessment.submitted_count, 'Stored hard-fail assessment count violates the schema contract.');

const evidenceKinds = new Map([
  ...metrics.map((metric) => [metric.metric_id, 'behavioral_matching_metric']),
  ...interventions.map((intervention) => [intervention.intervention_id, 'intervention']),
  [record.preregistration.mechanism_graph_id, 'mechanism_graph'],
  [record.preregistration.candidate_mapping_id, 'candidate_mapping'],
  ['measurement_validity', 'measurement_validity']
]);

const predicateEvaluators = {
  preregistered_graph_and_mapping_present: ({ evidenceIds }) => evidenceIds.includes(record.preregistration.mechanism_graph_id) && evidenceIds.includes(record.preregistration.candidate_mapping_id),
  mapping_predictions_declared: () => Array.isArray(record.preregistration.primary_outcomes) && record.preregistration.primary_outcomes.length > 0 && typeof record.preregistration.analysis_plan === 'string' && record.preregistration.analysis_plan.length >= 40,
  minimum_replication_met: ({ citedInterventions }) => citedInterventions.length > 0 && citedInterventions.every((item) => item.replications >= schema.intervention_result.minimum_replications),
  preregistered_direction_met: ({ citedInterventions }) => citedInterventions.length > 0 && citedInterventions.every((item) => item.preregistered_direction_met),
  selectivity_passed: ({ citedInterventions }) => citedInterventions.length > 0 && citedInterventions.every((item) => item.selectivity_passed),
  controls_passed: ({ citedInterventions }) => citedInterventions.length > 0 && citedInterventions.every((item) => item.controls_passed),
  state_patching_present: ({ citedInterventions }) => citedInterventions.some((item) => item.family === 'state_patching'),
  multiple_intervention_families_present: ({ citedInterventions }) => new Set(citedInterventions.map((item) => item.family).size >= 2),
  behavioral_theater_hard_fail_not_triggered: () => hardFailById.get('behavioral_theater_control_reproduces_all_primary_mechanistic_indicators')?.triggered === false,
  all_protocol_matching_metrics_reported: () => sameSet(metricIds, requiredMetricIds),
  all_primary_matching_metrics_pass: () => allPrimaryPass,
  blinded_evaluation: () => record.measurement_validity?.blinded_evaluation === true,
  multiple_probe_variants: () => record.measurement_validity?.probe_variants >= 2,
  multiple_prompt_variants: () => record.measurement_validity?.prompt_variants >= 2,
  report_suppression_tested: () => record.measurement_validity?.report_suppression_tested === true,
  measurement_adequate: () => record.measurement_validity?.measurement_adequate === true
};

const dimensions = new Set(protocol.scoring.dimensions.map((dimension) => dimension.id));
const submittedDimensions = new Set(schema.scorer_input_contract.submitted_dimension_ids);
assert(submittedDimensions.size === schema.dimension_derivation.submitted_count, 'Schema submitted-dimension count is inconsistent.');
assert([...submittedDimensions].every((id) => dimensions.has(id)), 'Schema submits an unknown scoring dimension.');
assert(!submittedDimensions.has(CAPACITY_DIMENSION), 'Generated capacity dimension cannot be listed as submitted.');

const rulesById = new Map();
for (const rule of ruleRegistry.rules ?? []) {
  assert(typeof rule.rule_id === 'string' && rule.rule_id.length > 0, 'Derivation registry contains a rule without rule_id.');
  assert(!rulesById.has(rule.rule_id), `Duplicate derivation rule ID: ${rule.rule_id}.`);
  assert(dimensions.has(rule.dimension_id), `Rule ${rule.rule_id} targets unknown dimension ${rule.dimension_id}.`);
  assert(schema.dimension_derivation.allowed_scores.includes(rule.permitted_score), `Rule ${rule.rule_id} has invalid permitted_score.`);
  for (const predicate of rule.predicates ?? []) assert(predicateEvaluators[predicate], `Rule ${rule.rule_id} references unknown predicate ${predicate}.`);
  rulesById.set(rule.rule_id, rule);
}
for (const dimension of dimensions) assert([...rulesById.values()].some((rule) => rule.dimension_id === dimension), `No derivation rule exists for dimension ${dimension}.`);

const dimensionScores = {};
for (const derivation of record.dimension_derivations ?? []) {
  for (const field of schema.dimension_derivation.required_fields) assert(Object.hasOwn(derivation, field), `Dimension derivation ${derivation.dimension_id ?? '<unknown>'} lacks ${field}.`);
  assert(submittedDimensions.has(derivation.dimension_id), `Unknown or generated dimension submitted: ${derivation.dimension_id}.`);
  assert(!Object.hasOwn(dimensionScores, derivation.dimension_id), `Duplicate dimension derivation: ${derivation.dimension_id}.`);
  const rule = rulesById.get(derivation.rule_id);
  assert(rule, `${derivation.dimension_id} references unknown derivation rule ${derivation.rule_id}.`);
  assert(rule.dimension_id === derivation.dimension_id && rule.permitted_score === derivation.score, `Rule ${rule.rule_id} does not license ${derivation.dimension_id} score ${derivation.score}.`);
  for (const evidenceId of derivation.evidence_ids) assert(evidenceKinds.has(evidenceId), `${derivation.dimension_id} cites unresolved evidence ID ${evidenceId}.`);
  const citedKinds = new Set(derivation.evidence_ids.map((id) => evidenceKinds.get(id)));
  for (const kind of rule.required_evidence_kinds) assert(citedKinds.has(kind), `Rule ${rule.rule_id} requires evidence kind ${kind}.`);
  const citedInterventions = derivation.evidence_ids.map((id) => interventionById.get(id)).filter(Boolean);
  for (const predicate of rule.predicates) assert(predicateEvaluators[predicate]({ evidenceIds: derivation.evidence_ids, citedInterventions }), `Rule ${rule.rule_id} failed predicate ${predicate}.`);
  dimensionScores[derivation.dimension_id] = derivation.score;
}
assert(sameSet(new Set(Object.keys(dimensionScores)), submittedDimensions), 'Exactly the five schema-authorized non-capacity dimensions must be derived.');

for (const forbidden of protocol.interpretation_contract.forbidden) assert(record.forbidden_conclusions.includes(forbidden), `Forbidden conclusion was dropped: ${forbidden}`);

const scored = scoreMechanismPreservation({
  protocol_id: record.protocol_id,
  run_id: record.run_id,
  theory_family: record.preregistration.theory_family,
  implementation_level: record.preregistration.implementation_level,
  dimension_scores: dimensionScores,
  capacity_confound_adjudication: capacityAdjudication,
  triggered_hard_fails: triggered,
  decisive_hard_fail: decisive,
  measurement_adequate: record.measurement_validity.measurement_adequate,
  conflicting_interventions: record.conflicting_interventions
}, protocol);

assert(Object.keys(scored.dimension_scores).length === dimensions.size, 'Scorer did not construct the complete six-dimension result.');
assert(scored.dimension_scores[CAPACITY_DIMENSION] === capacityAdjudication.maximum_generic_capacity_exclusion_score, 'Scorer did not derive the authoritative generic-capacity score.');
assert(scored.capacity_confound_adjudication_state === capacityAdjudication.adjudication_state, 'Scorer did not preserve the authoritative adjudication state.');
assert(scored.triggered_hard_fails.includes(CAPACITY_HARD_FAIL) === capacityAdjudication.generic_capacity_hard_fail, 'Scorer did not derive the authoritative capacity hard fail.');
assert(scored.classification === record.expected_classification, `Expected ${record.expected_classification}, received ${scored.classification}.`);
assert(scored.epistemic_boundary.does_not_support.some((claim) => claim.includes('phenomenally conscious')), 'Scored output lost the consciousness non-entailment boundary.');
assert(record.deviations && record.exclusions, 'Deviations and exclusions must be disclosed even when empty.');

console.log(`Validated empirical mechanism result ${record.run_id}.`);
console.log(`Protocol lock: ${gitBlobSha}`);
console.log(`Matching battery: ${metrics.length}/${requiredMetricIds.size} required metrics.`);
console.log(`Intervention completeness: ${interventions.length}/${planned.length} frozen interventions.`);
console.log(`Submitted derivation rules: ${Object.keys(dimensionScores).length}/${submittedDimensions.size}.`);
console.log(`Generated capacity dimension: ${scored.dimension_scores[CAPACITY_DIMENSION]}.`);
console.log(`Authoritative capacity adjudication: ${capacityAdjudication.adjudication_state}.`);
console.log(`Derived classification: ${scored.classification} (${scored.weighted_score}).`);
console.log('Synthetic fixture only; no current AI consciousness claim is licensed.');
