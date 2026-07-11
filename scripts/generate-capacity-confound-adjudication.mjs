import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = process.cwd();
const rulesPath = path.join(root, 'research/GENERIC_CAPACITY_CONFOUND_ADJUDICATION_RULES.json');
const matchingPath = path.join(root, 'research/MECHANISM_PRESERVATION_GENERIC_CAPACITY_INFERENCE.json');
const evidencePath = path.join(root, 'research/MECHANISM_PRESERVATION_CAPACITY_CONFOUND_EVIDENCE.json');
const outputPath = path.join(root, 'research/MECHANISM_PRESERVATION_CAPACITY_CONFOUND_ADJUDICATION.json');

function isFiniteInterval(value) {
  return Array.isArray(value) && value.length === 2 && value.every((entry) => Number.isFinite(Number(entry)));
}

function intervalInside(interval, region) {
  return Number(interval[0]) >= Number(region[0]) && Number(interval[1]) <= Number(region[1]);
}

export function adjudicateCapacityConfound(matching, evidence, rules) {
  const thresholds = rules.thresholds;
  const matchingState = matching.overall_state;

  if (matchingState === 'matched') {
    return buildResult('no_detected_mismatch', matching, null, rules,
      'All represented primary matching metrics satisfied their preregistered equivalence criteria.');
  }

  if (matchingState !== 'not_matched') {
    return buildResult('explanatory_role_underdetermined', matching, evidence ?? null, rules,
      'Matching itself is underdetermined, so causal-confound relevance cannot be adjudicated.');
  }

  if (!evidence || evidence.analysis_status !== 'complete' || evidence.matching_state !== 'not_matched') {
    return buildResult('explanatory_role_underdetermined', matching, evidence ?? null, rules,
      'A detected mismatch lacks a complete causal-confound adjudication record.');
  }

  const numericFields = ['unadjusted_primary_effect', 'adjusted_primary_effect', 'mediation_fraction'];
  const invalidNumeric = numericFields.some((field) => !Number.isFinite(Number(evidence[field])));
  if (
    invalidNumeric ||
    !isFiniteInterval(evidence.adjusted_interval) ||
    evidence.causal_pathway_preregistered !== true ||
    evidence.model_diagnostics_pass !== true
  ) {
    return buildResult('explanatory_role_underdetermined', matching, evidence, rules,
      'The causal pathway, numerical evidence, interval, or model diagnostics are insufficient for a directional adjudication.');
  }

  const mediation = Number(evidence.mediation_fraction);
  const adjustedEffect = Math.abs(Number(evidence.adjusted_primary_effect));
  const adjustedInsideNull = intervalInside(evidence.adjusted_interval, thresholds.registered_null_region);

  if (
    mediation >= Number(thresholds.sufficiency_mediation_fraction_threshold) &&
    adjustedInsideNull
  ) {
    return buildResult('mismatch_sufficiently_explanatory', matching, evidence, rules,
      'The preregistered adjustment places the residual effect inside the null region and attributes at least the registered sufficiency fraction to the mismatch.');
  }

  if (
    mediation < Number(thresholds.nonexplanatory_mediation_fraction_ceiling) &&
    adjustedEffect >= Number(thresholds.minimum_residual_primary_effect)
  ) {
    return buildResult('mismatch_nonexplanatory', matching, evidence, rules,
      'The mismatch explains less than the registered nonexplanatory ceiling while a material residual primary effect remains.');
  }

  if (
    mediation >= Number(thresholds.partial_mediation_fraction_lower_bound) &&
    mediation < Number(thresholds.partial_mediation_fraction_upper_bound) &&
    adjustedEffect >= Number(thresholds.minimum_residual_primary_effect)
  ) {
    return buildResult('mismatch_partially_explanatory', matching, evidence, rules,
      'The mismatch explains a preregistered intermediate fraction of the primary effect while a material residual remains.');
  }

  return buildResult('explanatory_role_underdetermined', matching, evidence, rules,
    'The evidence does not satisfy any registered directional adjudication rule.');
}

function buildResult(state, matching, evidence, rules, rationale) {
  const rule = rules.outcomes.find((entry) => entry.state === state);
  if (!rule) throw new Error(`No adjudication rule registered for state ${state}.`);
  return {
    schema_version: '1.0.0',
    adjudication_id: 'EXP11-CAPACITY-CONFOUND-ADJUDICATION-001',
    protocol_id: rules.protocol_id,
    run_id: matching.run_id,
    empirical_status: 'synthetic_fixture',
    generated_notice: 'Generated deterministically from matching state, registered adjudication rules, and any supplied synthetic confound evidence. Do not edit manually.',
    matching_overall_state: matching.overall_state,
    metric_id: evidence?.metric_id ?? null,
    primary_outcome_id: evidence?.primary_outcome_id ?? null,
    adjudication_state: state,
    generic_capacity_hard_fail: rule.hard_fail,
    maximum_generic_capacity_exclusion_score: rule.maximum_generic_capacity_exclusion_score,
    rationale,
    classification_effect: rule.interpretation,
    epistemic_boundary: rules.epistemic_boundary
  };
}

export function serializeCapacityConfoundAdjudication(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function runCli() {
  const rules = JSON.parse(fs.readFileSync(rulesPath, 'utf8'));
  const matching = JSON.parse(fs.readFileSync(matchingPath, 'utf8'));
  const evidence = fs.existsSync(evidencePath) ? JSON.parse(fs.readFileSync(evidencePath, 'utf8')) : null;
  const serialized = serializeCapacityConfoundAdjudication(adjudicateCapacityConfound(matching, evidence, rules));

  if (process.argv.includes('--stdout')) {
    process.stdout.write(serialized);
    return;
  }
  if (process.argv.includes('--check')) {
    const committed = fs.existsSync(outputPath) ? fs.readFileSync(outputPath, 'utf8') : '';
    if (committed !== serialized) {
      console.error('Capacity-confound adjudication artifact is stale or manually edited.');
      process.exit(1);
    }
    console.log('Capacity-confound adjudication artifact matches deterministic regeneration.');
    return;
  }
  fs.writeFileSync(outputPath, serialized);
  console.log(`Wrote ${path.relative(root, outputPath)}`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) runCli();
