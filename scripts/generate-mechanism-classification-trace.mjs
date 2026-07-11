#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { scoreMechanismPreservation, loadProtocol, loadClassificationPolicy } from './score-mechanism-preservation.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const empiricalPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_EMPIRICAL_FIXTURE.json');
const outputPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_TRACE.json');

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function buildScorerInput(empirical, adjudication) {
  const dimensionScores = Object.fromEntries(empirical.dimension_derivations.map(({ dimension_id, score }) => [dimension_id, score]));
  const nonCapacityHardFails = empirical.hard_fail_assessments.filter(({ triggered }) => triggered).map(({ condition_id }) => condition_id);
  return {
    protocol_id: empirical.protocol_id,
    run_id: empirical.run_id,
    theory_family: empirical.preregistration.theory_family,
    implementation_level: empirical.preregistration.implementation_level,
    dimension_scores: dimensionScores,
    capacity_confound_adjudication: adjudication,
    triggered_hard_fails: nonCapacityHardFails,
    decisive_hard_fail: empirical.hard_fail_assessments.some(({ triggered, decisive }) => triggered && decisive),
    measurement_adequate: empirical.measurement_validity.measurement_adequate,
    conflicting_interventions: empirical.conflicting_interventions
  };
}

function policyEvaluationToTrace(evaluation) {
  const required = evaluation.value ?? (
    evaluation.operator === 'between_inclusive_lower_exclusive_upper'
      ? { lower: evaluation.lower, upper_exclusive: evaluation.upper }
      : evaluation.operator === 'is_true'
        ? true
        : evaluation.operator === 'is_false'
          ? false
          : undefined
  );
  return {
    threshold_id: evaluation.predicate_id,
    description: evaluation.description,
    observed: evaluation.observed,
    operator: evaluation.operator,
    required,
    passed: evaluation.passed
  };
}

export function generateClassificationTrace() {
  const empirical = readJson(empiricalPath);
  const adjudication = readJson(path.join(root, empirical.capacity_confound_adjudication_lock.path));
  const protocol = loadProtocol();
  const classificationPolicy = loadClassificationPolicy();
  const result = scoreMechanismPreservation(buildScorerInput(empirical, adjudication), protocol, classificationPolicy);
  const submittedById = new Map(empirical.dimension_derivations.map((entry) => [entry.dimension_id, entry]));
  const dimensions = protocol.scoring.dimensions.map((dimension) => {
    const submitted = submittedById.get(dimension.id);
    const generated = dimension.id === 'generic_capacity_exclusion';
    return {
      dimension_id: dimension.id,
      provenance: generated ? 'generated_capacity_adjudication' : 'submitted_rule_derivation',
      score: result.dimension_scores[dimension.id],
      weight: dimension.weight,
      weighted_contribution: Number((result.dimension_scores[dimension.id] * dimension.weight).toFixed(4)),
      rule_id: generated ? null : submitted.rule_id,
      evidence_ids: generated ? [adjudication.adjudication_id] : submitted.evidence_ids,
      explanation: generated ? `Capacity-confound adjudication state ${adjudication.adjudication_state} permits score ${adjudication.maximum_generic_capacity_exclusion_score}.` : submitted.explanation
    };
  });
  const submittedHardFails = empirical.hard_fail_assessments.map((assessment) => ({
    condition_id: assessment.condition_id,
    provenance: 'submitted_structured_assessment',
    triggered: assessment.triggered,
    decisive: assessment.decisive,
    evidence_ids: assessment.evidence_ids,
    justification: assessment.justification
  }));
  const capacityHardFail = {
    condition_id: 'generic_capacity_control_explains_primary_effect',
    provenance: 'generated_capacity_adjudication',
    triggered: adjudication.generic_capacity_hard_fail,
    decisive: adjudication.generic_capacity_hard_fail,
    evidence_ids: [adjudication.adjudication_id],
    justification: adjudication.classification_effect
  };
  return {
    schema_id: 'EXP-11-CLASSIFICATION-TRACE',
    schema_version: '1.2.0',
    generated: true,
    generated_warning: 'Generated deterministically from the empirical fixture, protocol, structured classification policy, and capacity-confound adjudication. Do not edit manually.',
    presentation_safety: {
      status_label: classificationPolicy.presentation_contract.synthetic_fixture_label,
      display_rule: classificationPolicy.presentation_contract.synthetic_label_prominence,
      prohibited_implication: classificationPolicy.presentation_contract.prohibited_implication
    },
    protocol_id: result.protocol_id,
    classification_policy_id: result.classification_policy_id,
    classification_rule_id: result.classification_rule_id,
    run_id: result.run_id,
    empirical_status: empirical.empirical_status,
    source_artifacts: {
      empirical_record: 'research/MECHANISM_PRESERVATION_EMPIRICAL_FIXTURE.json',
      protocol: 'research/MECHANISM_PRESERVATION_PROTOCOL.json',
      classification_policy: 'research/MECHANISM_PRESERVATION_CLASSIFICATION_POLICY.json',
      capacity_confound_adjudication: empirical.capacity_confound_adjudication_lock.path
    },
    declared_scope: {
      theory_family: result.theory_family,
      target_property: empirical.preregistration.target_property,
      implementation_level: result.implementation_level,
      system_boundary: empirical.preregistration.system_boundary
    },
    capacity_confound_adjudication_state: result.capacity_confound_adjudication_state,
    dimensions,
    weighted_score: result.weighted_score,
    hard_fail_assessments: [...submittedHardFails, capacityHardFail],
    triggered_hard_fails: result.triggered_hard_fails,
    threshold_evaluations: result.classification_predicate_evaluations.map(policyEvaluationToTrace),
    classification_reasons: result.reasons,
    final_classification: result.classification,
    expected_classification_matches: result.classification === empirical.expected_classification,
    epistemic_boundary: result.epistemic_boundary,
    fixture_notice: empirical.fixture_notice
  };
}

export function serializeClassificationTrace(trace = generateClassificationTrace()) {
  return `${JSON.stringify(trace, null, 2)}\n`;
}

function main() {
  const serialized = serializeClassificationTrace();
  if (process.argv.includes('--stdout')) return void process.stdout.write(serialized);
  if (process.argv.includes('--check')) {
    const committed = fs.existsSync(outputPath) ? fs.readFileSync(outputPath, 'utf8') : '';
    if (committed !== serialized) {
      console.error('Committed mechanism classification trace differs from deterministic regeneration.');
      process.exit(1);
    }
    console.log('Mechanism classification trace matches deterministic regeneration.');
    return;
  }
  fs.writeFileSync(outputPath, serialized);
  console.log(`Wrote ${path.relative(root, outputPath)}.`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
