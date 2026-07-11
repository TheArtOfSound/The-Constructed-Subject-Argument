#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  evaluateAllClassificationRules,
  loadClassificationPolicy,
  loadProtocol,
  resolveCapacityAdjudication,
  scoreMechanismPreservation
} from './score-mechanism-preservation.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const capacityRulesPath = path.join(root, 'research', 'GENERIC_CAPACITY_CONFOUND_ADJUDICATION_RULES.json');
const outputPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_POLICY_FINITE_STATE_REPORT.json');
const NON_CAPACITY_HARD_FAIL = 'behavioral_theater_control_reproduces_all_primary_mechanistic_indicators';
const HARD_FAIL_MODES = ['none', 'triggered_nondecisive', 'triggered_decisive'];

function increment(object, key, amount = 1) {
  object[key] = (object[key] ?? 0) + amount;
}

function combinations(values, length, prefix = []) {
  if (prefix.length === length) return [prefix];
  return values.flatMap((value) => combinations(values, length, [...prefix, value]));
}

function capacityAdjudications(registry) {
  return registry.outcomes.map((entry) => ({
    adjudication_state: entry.state,
    maximum_generic_capacity_exclusion_score: entry.maximum_generic_capacity_exclusion_score,
    generic_capacity_hard_fail: entry.hard_fail
  }));
}

function matchingAdequate(state) {
  return state === 'no_detected_mismatch' || state === 'mismatch_nonexplanatory';
}

function makeRecord(protocol, dimensionIds, scores, adjudication, measurementAdequate, conflictingInterventions, hardFailMode, index) {
  const dimension_scores = Object.fromEntries(dimensionIds.map((id, position) => [id, scores[position]]));
  const hasCallerHardFail = hardFailMode !== 'none';
  return {
    protocol_id: protocol.protocol_id,
    run_id: `FINITE-STATE-${index}`,
    theory_family: 'synthetic-policy-enumeration',
    implementation_level: 'classifier-input-domain',
    dimension_scores,
    capacity_confound_adjudication: adjudication,
    triggered_hard_fails: hasCallerHardFail ? [NON_CAPACITY_HARD_FAIL] : [],
    decisive_hard_fail: hardFailMode === 'triggered_decisive',
    measurement_adequate: measurementAdequate,
    conflicting_interventions: conflictingInterventions
  };
}

export function generateFiniteStateReport() {
  const protocol = loadProtocol();
  const policy = loadClassificationPolicy();
  const capacityRegistry = JSON.parse(fs.readFileSync(capacityRulesPath, 'utf8'));
  const adjudications = capacityAdjudications(capacityRegistry);
  const dimensionIds = protocol.scoring.dimensions
    .map(({ id }) => id)
    .filter((id) => id !== 'generic_capacity_exclusion');
  const scoreVectors = combinations([0, 1, 2, 3], dimensionIds.length);
  const orderedRuleIds = [...policy.outcomes].sort((a, b) => a.priority - b.priority).map(({ rule_id }) => rule_id);
  const selectedRuleCounts = Object.fromEntries(orderedRuleIds.map((id) => [id, 0]));
  const rawRuleMatchCounts = Object.fromEntries(orderedRuleIds.map((id) => [id, 0]));
  const suppressedRuleMatchCounts = Object.fromEntries(orderedRuleIds.map((id) => [id, 0]));
  const outcomeCounts = {};
  const overlapCounts = {};
  const matchSignatureCounts = {};
  let totalStates = 0;
  let noRuleStates = 0;

  for (const scores of scoreVectors) {
    for (const adjudication of adjudications) {
      for (const measurementAdequateValue of [false, true]) {
        for (const conflictingInterventions of [false, true]) {
          for (const hardFailMode of HARD_FAIL_MODES) {
            const record = makeRecord(
              protocol,
              dimensionIds,
              scores,
              adjudication,
              measurementAdequateValue,
              conflictingInterventions,
              hardFailMode,
              totalStates
            );
            const result = scoreMechanismPreservation(record, protocol, policy);
            const { policy: capacityPolicy } = resolveCapacityAdjudication(record);
            const context = {
              protocol_id: protocol.protocol_id,
              weighted_score: result.weighted_score,
              dimension_scores: result.dimension_scores,
              triggered_hard_fail_count: result.triggered_hard_fails.length,
              decisive_hard_fail: capacityPolicy.hardFail || hardFailMode === 'triggered_decisive',
              measurement_adequate: measurementAdequateValue,
              matching_adequate: matchingAdequate(adjudication.adjudication_state),
              conflicting_interventions: conflictingInterventions
            };
            const evaluations = evaluateAllClassificationRules(policy, context);
            const matchedRuleIds = evaluations.filter(({ matched }) => matched).map(({ rule }) => rule.rule_id);
            if (matchedRuleIds.length === 0) noRuleStates += 1;
            increment(selectedRuleCounts, result.classification_rule_id);
            increment(outcomeCounts, result.classification);
            increment(matchSignatureCounts, matchedRuleIds.join(' | '));
            for (const ruleId of matchedRuleIds) {
              increment(rawRuleMatchCounts, ruleId);
              if (ruleId !== result.classification_rule_id) increment(suppressedRuleMatchCounts, ruleId);
            }
            for (let left = 0; left < matchedRuleIds.length; left += 1) {
              for (let right = left + 1; right < matchedRuleIds.length; right += 1) {
                increment(overlapCounts, `${matchedRuleIds[left]} | ${matchedRuleIds[right]}`);
              }
            }
            totalStates += 1;
          }
        }
      }
    }
  }

  const selectedRuleCoverage = orderedRuleIds.map((rule_id) => ({ rule_id, selected_state_count: selectedRuleCounts[rule_id] }));
  const fullyShadowedRules = selectedRuleCoverage.filter(({ selected_state_count }) => selected_state_count === 0).map(({ rule_id }) => rule_id);
  const partiallyShadowedRules = orderedRuleIds.filter((ruleId) => selectedRuleCounts[ruleId] > 0 && suppressedRuleMatchCounts[ruleId] > 0);
  const report = {
    schema_id: 'EXP-11-CLASSIFICATION-POLICY-FINITE-STATE-REPORT',
    schema_version: '1.0.0',
    protocol_id: protocol.protocol_id,
    status: 'generated_exhaustive_synthetic_policy_analysis',
    policy_id: policy.schema_id,
    source_artifacts: {
      policy: 'research/MECHANISM_PRESERVATION_CLASSIFICATION_POLICY.json',
      protocol: 'research/MECHANISM_PRESERVATION_PROTOCOL.json',
      capacity_adjudication_rules: 'research/GENERIC_CAPACITY_CONFOUND_ADJUDICATION_RULES.json',
      scorer: 'scripts/score-mechanism-preservation.mjs'
    },
    enumerated_domain: {
      submitted_dimension_ids: dimensionIds,
      submitted_dimension_values: [0, 1, 2, 3],
      submitted_score_vector_count: scoreVectors.length,
      capacity_adjudication_states: adjudications.map(({ adjudication_state }) => adjudication_state),
      measurement_adequate_values: [false, true],
      conflicting_interventions_values: [false, true],
      non_capacity_hard_fail_modes: HARD_FAIL_MODES,
      total_valid_states: totalStates
    },
    summary: {
      total_valid_states: totalStates,
      states_without_matching_rule: noRuleStates,
      selected_rule_count: selectedRuleCoverage.filter(({ selected_state_count }) => selected_state_count > 0).length,
      policy_rule_count: orderedRuleIds.length,
      fully_shadowed_rule_count: fullyShadowedRules.length,
      partially_shadowed_rule_count: partiallyShadowedRules.length,
      distinct_match_signature_count: Object.keys(matchSignatureCounts).length,
      exhaustive_coverage_pass: noRuleStates === 0 && fullyShadowedRules.length === 0
    },
    selected_rule_coverage: selectedRuleCoverage,
    outcome_counts: Object.entries(outcomeCounts).sort(([left], [right]) => left.localeCompare(right)).map(([outcome, state_count]) => ({ outcome, state_count })),
    raw_rule_match_counts: orderedRuleIds.map((rule_id) => ({ rule_id, matched_state_count: rawRuleMatchCounts[rule_id] })),
    suppressed_rule_match_counts: orderedRuleIds.map((rule_id) => ({ rule_id, suppressed_state_count: suppressedRuleMatchCounts[rule_id] })),
    rule_overlap_counts: Object.entries(overlapCounts).sort(([left], [right]) => left.localeCompare(right)).map(([rule_pair, state_count]) => ({ rule_pair: rule_pair.split(' | '), state_count })),
    match_signatures: Object.entries(matchSignatureCounts).sort(([left], [right]) => left.localeCompare(right)).map(([signature, state_count]) => ({ matched_rule_ids: signature ? signature.split(' | ') : [], state_count })),
    findings: {
      fully_shadowed_rule_ids: fullyShadowedRules,
      partially_shadowed_rule_ids: partiallyShadowedRules,
      no_rule_state_count: noRuleStates,
      fallback_selected_state_count: selectedRuleCounts['underdetermined-fallback'] ?? 0
    },
    interpretation_boundary: {
      supports: 'Exhaustive behavioral analysis over the declared finite scorer-input domain, including rule reachability, overlap, suppression, and fallback use.',
      does_not_support: [
        'That the classification thresholds are scientifically optimal',
        'That the enumerated input schema captures every scientifically relevant uncertainty',
        'That overlap between policy rules is itself an error when priority resolves it explicitly',
        'Any claim that an actual AI system is conscious, nonconscious, sentient, a person, or morally considerable'
      ]
    }
  };
  return report;
}

function main() {
  const report = generateFiniteStateReport();
  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  if (process.argv.includes('--stdout')) process.stdout.write(serialized);
  else if (process.argv.includes('--check')) {
    const current = fs.readFileSync(outputPath, 'utf8');
    if (current !== serialized) throw new Error('Committed finite-state report differs from deterministic regeneration.');
    console.log('Classification policy finite-state report is current.');
  } else {
    fs.writeFileSync(outputPath, serialized);
    console.log(`Wrote ${path.relative(root, outputPath)}.`);
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { main(); } catch (error) { console.error(`Finite-state report generation failed: ${error.message}`); process.exit(1); }
}
