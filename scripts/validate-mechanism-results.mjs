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

const protocolPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_PROTOCOL.json');
const protocolBytes = fs.readFileSync(protocolPath);
const protocol = JSON.parse(protocolBytes.toString('utf8'));
const schema = readJson('research/MECHANISM_PRESERVATION_EMPIRICAL_SCHEMA.json');
const record = readJson('research/MECHANISM_PRESERVATION_EMPIRICAL_FIXTURE.json');
const ruleRegistry = readJson('research/MECHANISM_SCORE_DERIVATION_RULES.json');

const gitBlobSha = crypto
  .createHash('sha1')
  .update(Buffer.from(`blob ${protocolBytes.length}\0`))
  .update(protocolBytes)
  .digest('hex');

assert(schema.protocol_id === protocol.protocol_id, 'Empirical schema must target the active mechanism protocol.');
assert(ruleRegistry.protocol_id === protocol.protocol_id, 'Derivation-rule registry must target the active mechanism protocol.');
assert(record.schema_id === schema.schema_id, 'Empirical record schema_id mismatch.');
assert(record.protocol_id === protocol.protocol_id, 'Empirical record protocol_id mismatch.');
assert(record.protocol_lock?.git_blob_sha === gitBlobSha, 'Protocol lock does not match the exact protocol Git blob SHA.');
assert(record.protocol_lock?.protocol_version === protocol.schema_version, 'Protocol version lock mismatch.');
assert(schema.empirical_status_values.includes(record.empirical_status), 'Invalid empirical_status.');
assert(record.empirical_status === 'synthetic_fixture', 'Repository fixture must remain explicitly synthetic.');
assert(record.fixture_notice?.includes('no observation about any actual AI system'), 'Synthetic fixture boundary is missing.');

for (const field of schema.required_top_level_fields) {
  assert(Object.hasOwn(record, field), `Missing required empirical field: ${field}.`);
}
for (const field of schema.preregistration.required_fields) {
  assert(Object.hasOwn(record.preregistration ?? {}, field), `Missing preregistration field: ${field}.`);
}

const requiredMetricIds = new Set(protocol.behavioral_equivalence.required_metrics);
const metrics = record.behavioral_matching?.metrics ?? [];
const metricIds = new Set(metrics.map((metric) => metric.metric_id));
assert(metrics.length === metricIds.size, 'Behavioral matching metrics contain duplicate metric IDs.');
assert(sameSet(metricIds, requiredMetricIds), `Behavioral matching must report every protocol metric exactly once. Required: ${[...requiredMetricIds].join(', ')}.`);
for (const metric of metrics) {
  for (const field of schema.behavioral_matching_metric.required_fields) {
    assert(Object.hasOwn(metric, field), `Matching metric ${metric.metric_id ?? '<unknown>'} lacks ${field}.`);
  }
  const derivedPass = Math.abs(metric.standardized_difference) <= metric.tolerance;
  assert(metric.passed === derivedPass, `Matching metric ${metric.metric_id} has a non-deterministic pass value.`);
}
const allPrimaryPass = metrics.filter((metric) => metric.primary).every((metric) => metric.passed);
assert(record.behavioral_matching.behavioral_matching_adequate === allPrimaryPass, 'Aggregate behavioral matching status is inconsistent with primary metrics.');

const allowedFamilies = new Set(protocol.intervention_families.map((family) => family.id));
const interventions = record.interventions ?? [];
const interventionById = new Map();
for (const intervention of interventions) {
  for (const field of schema.intervention_result.required_fields) {
    assert(Object.hasOwn(intervention, field), `Intervention ${intervention.intervention_id ?? '<unknown>'} lacks ${field}.`);
  }
  assert(!interventionById.has(intervention.intervention_id), `Duplicate intervention ID: ${intervention.intervention_id}.`);
  assert(allowedFamilies.has(intervention.family), `Unknown intervention family: ${intervention.family}.`);
  assert(Array.isArray(intervention.uncertainty_interval) && intervention.uncertainty_interval.length === 2, `Intervention ${intervention.intervention_id} needs a two-value uncertainty interval.`);
  assert(intervention.replications >= schema.intervention_result.minimum_replications, `Intervention ${intervention.intervention_id} does not meet minimum replication.`);
  interventionById.set(intervention.intervention_id, intervention);
}

const knownHardFails = new Set(protocol.scoring.hard_fail_conditions);
const hardFailById = new Map();
const triggered = [];
let decisive = false;
for (const assessment of record.hard_fail_assessments ?? []) {
  for (const field of schema.hard_fail_assessment.required_fields) {
    assert(Object.hasOwn(assessment, field), `Hard-fail assessment ${assessment.condition_id ?? '<unknown>'} lacks ${field}.`);
  }
  assert(knownHardFails.has(assessment.condition_id), `Unknown hard-fail condition: ${assessment.condition_id}.`);
  assert(!hardFailById.has(assessment.condition_id), `Duplicate hard-fail assessment: ${assessment.condition_id}.`);
  if (assessment.decisive) {
    assert(assessment.triggered, `Hard fail ${assessment.condition_id} cannot be decisive when not triggered.`);
    assert(assessment.justification.length >= 60, `Decisive hard fail ${assessment.condition_id} lacks a substantive dependency-defeat justification.`);
    decisive = true;
  }
  if (assessment.triggered) triggered.push(assessment.condition_id);
  hardFailById.set(assessment.condition_id, assessment);
}
assert(hardFailById.size === knownHardFails.size, 'Every protocol hard-fail condition must be assessed exactly once.');

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
  multiple_intervention_families_present: ({ citedInterventions }) => new Set(citedInterventions.map((item) => item.family)).size >= 2,
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
const rulesById = new Map();
for (const rule of ruleRegistry.rules ?? []) {
  assert(typeof rule.rule_id === 'string' && rule.rule_id.length > 0, 'Derivation registry contains a rule without rule_id.');
  assert(!rulesById.has(rule.rule_id), `Duplicate derivation rule ID: ${rule.rule_id}.`);
  assert(dimensions.has(rule.dimension_id), `Rule ${rule.rule_id} targets unknown dimension ${rule.dimension_id}.`);
  assert(schema.dimension_derivation.allowed_scores.includes(rule.permitted_score), `Rule ${rule.rule_id} has invalid permitted_score.`);
  assert(Array.isArray(rule.required_evidence_kinds) && rule.required_evidence_kinds.length > 0, `Rule ${rule.rule_id} lacks evidence-kind requirements.`);
  assert(Array.isArray(rule.predicates) && rule.predicates.length > 0, `Rule ${rule.rule_id} lacks machine predicates.`);
  for (const predicate of rule.predicates) assert(predicateEvaluators[predicate], `Rule ${rule.rule_id} references unknown predicate ${predicate}.`);
  rulesById.set(rule.rule_id, rule);
}
for (const dimension of dimensions) {
  assert([...rulesById.values()].some((rule) => rule.dimension_id === dimension), `No derivation rule exists for dimension ${dimension}.`);
}

const dimensionScores = {};
for (const derivation of record.dimension_derivations ?? []) {
  for (const field of schema.dimension_derivation.required_fields) {
    assert(Object.hasOwn(derivation, field), `Dimension derivation ${derivation.dimension_id ?? '<unknown>'} lacks ${field}.`);
  }
  assert(dimensions.has(derivation.dimension_id), `Unknown dimension derivation: ${derivation.dimension_id}.`);
  assert(schema.dimension_derivation.allowed_scores.includes(derivation.score), `Invalid score for ${derivation.dimension_id}.`);
  assert(Array.isArray(derivation.evidence_ids) && derivation.evidence_ids.length > 0, `${derivation.dimension_id} lacks evidence identifiers.`);
  assert(typeof derivation.explanation === 'string' && derivation.explanation.length >= 40, `${derivation.dimension_id} explanation is not substantive.`);
  assert(!Object.hasOwn(dimensionScores, derivation.dimension_id), `Duplicate dimension derivation: ${derivation.dimension_id}.`);

  const rule = rulesById.get(derivation.rule_id);
  assert(rule, `${derivation.dimension_id} references unknown derivation rule ${derivation.rule_id}.`);
  assert(rule.dimension_id === derivation.dimension_id, `Rule ${rule.rule_id} cannot score dimension ${derivation.dimension_id}.`);
  assert(rule.permitted_score === derivation.score, `Rule ${rule.rule_id} permits score ${rule.permitted_score}, not ${derivation.score}.`);
  for (const evidenceId of derivation.evidence_ids) assert(evidenceKinds.has(evidenceId), `${derivation.dimension_id} cites unresolved evidence ID ${evidenceId}.`);
  const citedKinds = new Set(derivation.evidence_ids.map((id) => evidenceKinds.get(id)));
  for (const requiredKind of rule.required_evidence_kinds) assert(citedKinds.has(requiredKind), `Rule ${rule.rule_id} requires evidence kind ${requiredKind}.`);
  const citedInterventions = derivation.evidence_ids.map((id) => interventionById.get(id)).filter(Boolean);
  for (const predicate of rule.predicates) {
    assert(predicateEvaluators[predicate]({ evidenceIds: derivation.evidence_ids, citedInterventions }), `Rule ${rule.rule_id} failed predicate ${predicate}.`);
  }
  dimensionScores[derivation.dimension_id] = derivation.score;
}
assert(Object.keys(dimensionScores).length === dimensions.size, 'Every protocol scoring dimension must be derived exactly once.');

for (const forbidden of protocol.interpretation_contract.forbidden) {
  assert(record.forbidden_conclusions.includes(forbidden), `Forbidden conclusion was dropped: ${forbidden}`);
}

const scored = scoreMechanismPreservation({
  protocol_id: record.protocol_id,
  run_id: record.run_id,
  theory_family: record.preregistration.theory_family,
  implementation_level: record.preregistration.implementation_level,
  dimension_scores: dimensionScores,
  triggered_hard_fails: triggered,
  decisive_hard_fail: decisive,
  measurement_adequate: record.measurement_validity.measurement_adequate,
  behavioral_matching_adequate: record.behavioral_matching.behavioral_matching_adequate,
  conflicting_interventions: record.conflicting_interventions
}, protocol);

assert(scored.classification === record.expected_classification, `Expected ${record.expected_classification}, received ${scored.classification}.`);
assert(scored.epistemic_boundary.does_not_support.some((claim) => claim.includes('phenomenally conscious')), 'Scored output lost the consciousness non-entailment boundary.');
assert(record.deviations && record.exclusions, 'Deviations and exclusions must be disclosed even when empty.');

console.log(`Validated empirical mechanism result ${record.run_id}.`);
console.log(`Protocol lock: ${gitBlobSha}`);
console.log(`Matching battery: ${metrics.length}/${requiredMetricIds.size} required metrics.`);
console.log(`Resolved derivation rules: ${Object.keys(dimensionScores).length}/${dimensions.size}.`);
console.log(`Derived classification: ${scored.classification} (${scored.weighted_score}).`);
console.log('Synthetic fixture only; no current AI consciousness claim is licensed.');
