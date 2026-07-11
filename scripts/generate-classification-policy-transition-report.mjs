#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  loadClassificationPolicy,
  loadProtocol,
  scoreMechanismPreservation
} from './score-mechanism-preservation.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const capacityRulesPath = path.join(root, 'research', 'GENERIC_CAPACITY_CONFOUND_ADJUDICATION_RULES.json');
const outputPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_POLICY_TRANSITION_REPORT.json');
const NON_CAPACITY_HARD_FAIL = 'behavioral_theater_control_reproduces_all_primary_mechanistic_indicators';
const HARD_FAIL_MODES = ['none', 'triggered_nondecisive', 'triggered_decisive'];
const OUTCOME_RANK = Object.freeze({ not_preserved: 0, underdetermined: 1, partially_preserved: 2, preserved: 3 });
const CAPACITY_REPAIRS = [
  ['mismatch_sufficiently_explanatory', 'mismatch_partially_explanatory', 'remove_sufficient_explanation'],
  ['explanatory_role_underdetermined', 'mismatch_partially_explanatory', 'resolve_role_partial'],
  ['explanatory_role_underdetermined', 'mismatch_nonexplanatory', 'resolve_role_nonexplanatory'],
  ['mismatch_partially_explanatory', 'mismatch_nonexplanatory', 'reduce_explanatory_strength'],
  ['mismatch_nonexplanatory', 'no_detected_mismatch', 'remove_detected_mismatch']
];

function combinations(values, length, prefix = []) {
  if (prefix.length === length) return [prefix];
  return values.flatMap((value) => combinations(values, length, [...prefix, value]));
}

function increment(object, key, amount = 1) {
  object[key] = (object[key] ?? 0) + amount;
}

function capacityAdjudications(registry) {
  return Object.fromEntries(registry.outcomes.map((entry) => [entry.state, {
    adjudication_state: entry.state,
    maximum_generic_capacity_exclusion_score: entry.maximum_generic_capacity_exclusion_score,
    generic_capacity_hard_fail: entry.hard_fail
  }]));
}

function makeRecord(protocol, dimensionIds, scores, adjudication, measurementAdequate, conflictingInterventions, hardFailMode, runId) {
  return {
    protocol_id: protocol.protocol_id,
    run_id: runId,
    theory_family: 'synthetic-policy-transition-enumeration',
    implementation_level: 'classifier-input-domain',
    dimension_scores: Object.fromEntries(dimensionIds.map((id, index) => [id, scores[index]])),
    capacity_confound_adjudication: adjudication,
    triggered_hard_fails: hardFailMode === 'none' ? [] : [NON_CAPACITY_HARD_FAIL],
    decisive_hard_fail: hardFailMode === 'triggered_decisive',
    measurement_adequate: measurementAdequate,
    conflicting_interventions: conflictingInterventions
  };
}

function stateKey(state) {
  return JSON.stringify(state);
}

function classifyTransition(sourceResult, targetResult, transitionType) {
  const sourceRank = OUTCOME_RANK[sourceResult.classification];
  const targetRank = OUTCOME_RANK[targetResult.classification];
  const epistemicRepair = transitionType === 'measurement_repair'
    || transitionType === 'intervention_conflict_repair'
    || transitionType.startsWith('capacity_repair:');
  if (sourceResult.classification === 'underdetermined'
      && targetResult.classification === 'not_preserved'
      && epistemicRepair) return 'resolved_negative';
  if (targetRank > sourceRank) return 'improved';
  if (targetRank === sourceRank) return 'unchanged';
  return 'worsened';
}

function transitionFamily(type) {
  return type.split(':')[0];
}

export function generateTransitionReport() {
  const protocol = loadProtocol();
  const policy = loadClassificationPolicy();
  const capacityRegistry = JSON.parse(fs.readFileSync(capacityRulesPath, 'utf8'));
  const adjudications = capacityAdjudications(capacityRegistry);
  const dimensionIds = protocol.scoring.dimensions.map(({ id }) => id).filter((id) => id !== 'generic_capacity_exclusion');
  const scoreVectors = combinations([0, 1, 2, 3], dimensionIds.length);
  const states = [];
  const results = new Map();

  for (const scores of scoreVectors) {
    for (const capacityState of Object.keys(adjudications)) {
      for (const measurementAdequate of [false, true]) {
        for (const conflictingInterventions of [false, true]) {
          for (const hardFailMode of HARD_FAIL_MODES) {
            const state = { scores, capacityState, measurementAdequate, conflictingInterventions, hardFailMode };
            const key = stateKey(state);
            const record = makeRecord(protocol, dimensionIds, scores, adjudications[capacityState], measurementAdequate, conflictingInterventions, hardFailMode, `TRANSITION-${states.length}`);
            states.push(state);
            results.set(key, scoreMechanismPreservation(record, protocol, policy));
          }
        }
      }
    }
  }

  const categoryCounts = {};
  const typeCounts = {};
  const familyCounts = {};
  const examples = {};
  let totalTransitions = 0;

  function observe(source, target, type) {
    const sourceResult = results.get(stateKey(source));
    const targetRecord = makeRecord(protocol, dimensionIds, target.scores, adjudications[target.capacityState], target.measurementAdequate, target.conflictingInterventions, target.hardFailMode, `TARGET-${totalTransitions}`);
    const targetResult = scoreMechanismPreservation(targetRecord, protocol, policy);
    const category = classifyTransition(sourceResult, targetResult, type);
    increment(categoryCounts, category);
    typeCounts[type] ??= {};
    increment(typeCounts[type], category);
    const family = transitionFamily(type);
    familyCounts[family] ??= {};
    increment(familyCounts[family], category);
    examples[`${type}|${category}`] ??= {
      transition_type: type,
      category,
      source: { classification: sourceResult.classification, rule_id: sourceResult.classification_rule_id, weighted_score: sourceResult.weighted_score },
      target: { classification: targetResult.classification, rule_id: targetResult.classification_rule_id, weighted_score: targetResult.weighted_score }
    };
    totalTransitions += 1;
  }

  for (const state of states) {
    for (let index = 0; index < dimensionIds.length; index += 1) {
      if (state.scores[index] < 3) {
        const scores = [...state.scores];
        scores[index] += 1;
        observe(state, { ...state, scores }, `dimension_increase:${dimensionIds[index]}`);
      }
    }
    if (!state.measurementAdequate) observe(state, { ...state, measurementAdequate: true }, 'measurement_repair');
    if (state.conflictingInterventions) observe(state, { ...state, conflictingInterventions: false }, 'intervention_conflict_repair');
    for (const [from, to, label] of CAPACITY_REPAIRS) {
      if (state.capacityState === from) observe(state, { ...state, capacityState: to }, `capacity_repair:${label}`);
    }
    if (state.hardFailMode === 'triggered_decisive') observe(state, { ...state, hardFailMode: 'triggered_nondecisive' }, 'hard_fail_demotion');
    else if (state.hardFailMode === 'triggered_nondecisive') observe(state, { ...state, hardFailMode: 'none' }, 'hard_fail_removal');
  }

  const orderedCounts = (counts) => Object.entries(counts)
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([id, categories]) => ({ id, ...categories }));
  const worsenedCount = categoryCounts.worsened ?? 0;
  const resolvedNegativeCount = categoryCounts.resolved_negative ?? 0;

  return {
    schema_id: 'EXP-11-CLASSIFICATION-POLICY-TRANSITION-REPORT',
    schema_version: '1.0.0',
    protocol_id: protocol.protocol_id,
    policy_id: policy.schema_id,
    status: 'generated_exhaustive_synthetic_transition_analysis',
    source_artifacts: {
      policy: 'research/MECHANISM_PRESERVATION_CLASSIFICATION_POLICY.json',
      protocol: 'research/MECHANISM_PRESERVATION_PROTOCOL.json',
      capacity_adjudication_rules: 'research/GENERIC_CAPACITY_CONFOUND_ADJUDICATION_RULES.json',
      scorer: 'scripts/score-mechanism-preservation.mjs',
      finite_state_report: 'research/MECHANISM_PRESERVATION_CLASSIFICATION_POLICY_FINITE_STATE_REPORT.json'
    },
    transition_contract: {
      outcome_order_for_audit: ['not_preserved', 'underdetermined', 'partially_preserved', 'preserved'],
      one_step_changes: [
        'increase one submitted scoring dimension by one point',
        'repair measurement adequacy',
        'remove intervention conflict',
        'move along a declared capacity-confound repair edge',
        'demote or remove a non-capacity hard fail'
      ],
      resolved_negative_definition: 'An epistemic repair can legitimately move underdetermined evidence to not_preserved when adequate evidence reveals a low-score or defeat condition. This is resolution, not monotonicity failure.',
      defect_candidate_definition: 'A worsened transition is any other one-step evidential improvement that lowers the ordered classification.'
    },
    enumerated_domain: {
      valid_source_state_count: states.length,
      submitted_dimension_ids: dimensionIds,
      submitted_dimension_values: [0, 1, 2, 3],
      capacity_repair_edges: CAPACITY_REPAIRS.map(([from, to, id]) => ({ id, from, to })),
      total_one_step_transitions: totalTransitions
    },
    summary: {
      total_one_step_transitions: totalTransitions,
      improved_transition_count: categoryCounts.improved ?? 0,
      unchanged_transition_count: categoryCounts.unchanged ?? 0,
      resolved_negative_transition_count: resolvedNegativeCount,
      worsened_transition_count: worsenedCount,
      monotonicity_defect_candidate_count: worsenedCount,
      exhaustive_transition_pass: worsenedCount === 0
    },
    transition_family_counts: orderedCounts(familyCounts),
    transition_type_counts: orderedCounts(typeCounts),
    representative_examples: Object.values(examples).sort((left, right) => `${left.transition_type}|${left.category}`.localeCompare(`${right.transition_type}|${right.category}`)),
    findings: {
      dimension_increase_worsening_count: familyCounts.dimension_increase?.worsened ?? 0,
      hard_fail_repair_worsening_count: (familyCounts.hard_fail_demotion?.worsened ?? 0) + (familyCounts.hard_fail_removal?.worsened ?? 0),
      capacity_repair_worsening_count: familyCounts.capacity_repair?.worsened ?? 0,
      measurement_repairs_resolving_negative: typeCounts.measurement_repair?.resolved_negative ?? 0,
      explanation: 'No declared one-step evidential improvement worsened the ordered outcome. Measurement repair sometimes converts underdetermination into not_preserved because better measurement can reveal genuinely negative evidence.'
    },
    interpretation_boundary: {
      supports: 'Exhaustive transition analysis over adjacent states in the declared finite scorer domain, distinguishing monotonic improvements from legitimate uncertainty-to-negative resolution.',
      does_not_support: [
        'That the outcome ordering is the only philosophically defensible ordering',
        'That every scientifically relevant evidence transition is represented',
        'That absence of transition defects establishes scientific optimality of the policy',
        'Any claim that an actual AI system is conscious, nonconscious, sentient, a person, or morally considerable'
      ]
    }
  };
}

function main() {
  const report = generateTransitionReport();
  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  if (process.argv.includes('--stdout')) process.stdout.write(serialized);
  else if (process.argv.includes('--check')) {
    const current = fs.readFileSync(outputPath, 'utf8');
    if (current !== serialized) throw new Error('Committed transition report differs from deterministic regeneration.');
    console.log('Classification policy transition report is current.');
  } else {
    fs.writeFileSync(outputPath, serialized);
    console.log(`Wrote ${path.relative(root, outputPath)}.`);
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { main(); } catch (error) { console.error(`Transition report generation failed: ${error.message}`); process.exit(1); }
}
