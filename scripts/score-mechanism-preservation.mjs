#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const protocolPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_PROTOCOL.json');
const classificationPolicyPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_POLICY.json');
const capacityAdjudicationRulesPath = path.join(root, 'research', 'GENERIC_CAPACITY_CONFOUND_ADJUDICATION_RULES.json');

const CAPACITY_HARD_FAIL = 'generic_capacity_control_explains_primary_effect';

export function loadProtocol() {
  return JSON.parse(fs.readFileSync(protocolPath, 'utf8'));
}

export function loadClassificationPolicy() {
  return JSON.parse(fs.readFileSync(classificationPolicyPath, 'utf8'));
}

export function loadCapacityAdjudicationRules() {
  return JSON.parse(fs.readFileSync(capacityAdjudicationRulesPath, 'utf8'));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function round(value, places = 4) {
  const factor = 10 ** places;
  return Math.round((value + Number.EPSILON) * factor) / factor;
}

function getField(context, field) {
  return field.split('.').reduce((value, key) => value?.[key], context);
}

export function evaluatePredicate(predicate, context) {
  if (predicate.operator === 'all_true' || predicate.operator === 'any_true') {
    const evaluations = (predicate.requirements ?? []).map((child) => evaluatePredicate(child, context));
    const passed = predicate.operator === 'all_true'
      ? evaluations.every(({ passed: childPassed }) => childPassed)
      : evaluations.some(({ passed: childPassed }) => childPassed);
    return { ...predicate, observed: evaluations.map(({ observed }) => observed), passed, evaluations };
  }

  const observed = getField(context, predicate.field);
  let passed;
  switch (predicate.operator) {
    case '==': passed = observed === predicate.value; break;
    case '<': passed = observed < predicate.value; break;
    case '<=': passed = observed <= predicate.value; break;
    case '>=': passed = observed >= predicate.value; break;
    case 'is_false': passed = observed === false; break;
    case 'is_true': passed = observed === true; break;
    case 'between_inclusive_lower_exclusive_upper':
      passed = observed >= predicate.lower && observed < predicate.upper;
      break;
    default:
      throw new Error(`Unsupported classification-policy operator: ${predicate.operator}.`);
  }
  return { ...predicate, observed, passed };
}

export function evaluateAllClassificationRules(policy, context) {
  assert(policy.protocol_id === context.protocol_id, `Classification policy protocol_id must equal ${context.protocol_id}.`);
  return [...policy.outcomes]
    .sort((a, b) => a.priority - b.priority)
    .map((rule) => {
      const evaluations = (rule.requirements ?? []).map((predicate) => evaluatePredicate(predicate, context));
      const matched = rule.match === 'any'
        ? evaluations.some(({ passed }) => passed)
        : evaluations.every(({ passed }) => passed);
      return { rule, evaluations, matched };
    });
}

export function evaluateClassificationPolicy(policy, context) {
  const matched = evaluateAllClassificationRules(policy, context).find((entry) => entry.matched);
  if (matched) return { rule: matched.rule, evaluations: matched.evaluations };
  throw new Error('Classification policy has no matching rule or fallback.');
}

export function resolveCapacityAdjudication(record, registry = loadCapacityAdjudicationRules()) {
  assert(!Object.hasOwn(record, 'behavioral_matching_adequate'), 'behavioral_matching_adequate is deprecated; supply capacity_confound_adjudication.');
  assert(registry.protocol_id === record.protocol_id, `Capacity adjudication registry protocol_id must equal ${record.protocol_id}.`);
  const adjudication = record.capacity_confound_adjudication;
  assert(adjudication && typeof adjudication === 'object', 'capacity_confound_adjudication is required.');
  const policy = registry.outcomes.find(({ state }) => state === adjudication.adjudication_state);
  assert(policy, `Unknown capacity-confound adjudication state: ${adjudication.adjudication_state}.`);
  assert(typeof policy.matching_adequate === 'boolean', `Capacity adjudication state ${policy.state} must declare matching_adequate.`);
  assert(Number.isInteger(policy.maximum_generic_capacity_exclusion_score), `Capacity adjudication state ${policy.state} must declare an integer score ceiling.`);
  assert(typeof policy.hard_fail === 'boolean', `Capacity adjudication state ${policy.state} must declare hard_fail.`);
  assert(
    adjudication.maximum_generic_capacity_exclusion_score === policy.maximum_generic_capacity_exclusion_score,
    `Adjudication state ${adjudication.adjudication_state} permits generic_capacity_exclusion score ${policy.maximum_generic_capacity_exclusion_score}.`
  );
  assert(
    adjudication.generic_capacity_hard_fail === policy.hard_fail,
    `Adjudication state ${adjudication.adjudication_state} requires generic_capacity_hard_fail=${policy.hard_fail}.`
  );
  return { adjudication, policy };
}

export function scoreMechanismPreservation(record, protocol = loadProtocol(), classificationPolicy = loadClassificationPolicy(), capacityRegistry = loadCapacityAdjudicationRules()) {
  assert(record && typeof record === 'object', 'Result record must be an object.');
  assert(record.protocol_id === protocol.protocol_id, `protocol_id must equal ${protocol.protocol_id}.`);
  assert(typeof record.run_id === 'string' && record.run_id.trim(), 'run_id is required.');
  assert(typeof record.theory_family === 'string' && record.theory_family.trim(), 'theory_family is required.');
  assert(typeof record.implementation_level === 'string' && record.implementation_level.trim(), 'implementation_level is required.');

  const { adjudication, policy: capacityPolicy } = resolveCapacityAdjudication(record, capacityRegistry);
  const dimensions = protocol.scoring.dimensions;
  const allowedDimensionIds = new Set(dimensions.map((dimension) => dimension.id));
  const submittedScores = { ...(record.dimension_scores ?? {}) };
  assert(!Object.hasOwn(submittedScores, 'generic_capacity_exclusion'), 'generic_capacity_exclusion is derived from capacity_confound_adjudication and must not be supplied manually.');
  submittedScores.generic_capacity_exclusion = capacityPolicy.maximum_generic_capacity_exclusion_score;
  const submittedIds = Object.keys(submittedScores);

  assert(submittedIds.length === dimensions.length, 'Every non-derived scoring dimension must be supplied exactly once.');
  for (const id of submittedIds) assert(allowedDimensionIds.has(id), `Unknown scoring dimension: ${id}.`);

  let weightedScore = 0;
  const normalizedScores = {};
  for (const dimension of dimensions) {
    const score = submittedScores[dimension.id];
    assert(Number.isInteger(score) && score >= 0 && score <= 3, `${dimension.id} must be an integer from 0 to 3.`);
    normalizedScores[dimension.id] = score;
    weightedScore += score * dimension.weight;
  }
  weightedScore = round(weightedScore);

  const knownHardFails = new Set(protocol.scoring.hard_fail_conditions);
  const callerHardFails = [...new Set(record.triggered_hard_fails ?? [])];
  assert(!callerHardFails.includes(CAPACITY_HARD_FAIL), `${CAPACITY_HARD_FAIL} is derived from capacity_confound_adjudication and must not be supplied manually.`);
  for (const hardFail of callerHardFails) assert(knownHardFails.has(hardFail), `Unknown hard-fail condition: ${hardFail}.`);
  const triggeredHardFails = [...callerHardFails];
  if (capacityPolicy.hard_fail) triggeredHardFails.push(CAPACITY_HARD_FAIL);

  const measurementAdequate = record.measurement_adequate === true;
  const matchingAdequate = capacityPolicy.matching_adequate;
  const conflictingInterventions = record.conflicting_interventions === true;
  const otherDecisiveHardFail = record.decisive_hard_fail === true && callerHardFails.length > 0;
  const decisiveHardFail = capacityPolicy.hard_fail || otherDecisiveHardFail;
  const context = {
    protocol_id: protocol.protocol_id,
    weighted_score: weightedScore,
    dimension_scores: normalizedScores,
    triggered_hard_fail_count: triggeredHardFails.length,
    decisive_hard_fail: decisiveHardFail,
    measurement_adequate: measurementAdequate,
    matching_adequate: matchingAdequate,
    conflicting_interventions: conflictingInterventions
  };
  const { rule, evaluations } = evaluateClassificationPolicy(classificationPolicy, context);
  const reasons = evaluations
    .filter(({ passed }) => passed)
    .map(({ description, predicate_id }) => description ?? predicate_id)
    .filter(Boolean);
  if (reasons.length === 0) reasons.push(rule.description ?? 'The record did not satisfy a more decisive protocol classification.');
  if (capacityPolicy.hard_fail) reasons.unshift('A sufficiently explanatory generic-capacity mismatch defeated the primary mechanism inference.');

  return {
    protocol_id: protocol.protocol_id,
    classification_policy_id: classificationPolicy.schema_id,
    classification_rule_id: rule.rule_id,
    run_id: record.run_id,
    theory_family: record.theory_family,
    implementation_level: record.implementation_level,
    weighted_score: weightedScore,
    dimension_scores: normalizedScores,
    capacity_confound_adjudication_state: adjudication.adjudication_state,
    triggered_hard_fails: triggeredHardFails,
    classification: rule.outcome,
    reasons,
    classification_predicate_evaluations: evaluations,
    epistemic_boundary: classificationPolicy.epistemic_boundary
  };
}

function main() {
  const inputPath = process.argv[2];
  if (!inputPath) {
    console.error('Usage: node scripts/score-mechanism-preservation.mjs <result-record.json>');
    process.exit(2);
  }

  try {
    const absolute = path.resolve(process.cwd(), inputPath);
    const record = JSON.parse(fs.readFileSync(absolute, 'utf8'));
    console.log(JSON.stringify(scoreMechanismPreservation(record), null, 2));
  } catch (error) {
    console.error(`Mechanism-preservation scoring failed: ${error.message}`);
    process.exit(1);
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
