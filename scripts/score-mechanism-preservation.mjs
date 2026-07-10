#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const protocolPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_PROTOCOL.json');

export function loadProtocol() {
  return JSON.parse(fs.readFileSync(protocolPath, 'utf8'));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function round(value, places = 4) {
  const factor = 10 ** places;
  return Math.round((value + Number.EPSILON) * factor) / factor;
}

export function scoreMechanismPreservation(record, protocol = loadProtocol()) {
  assert(record && typeof record === 'object', 'Result record must be an object.');
  assert(record.protocol_id === protocol.protocol_id, `protocol_id must equal ${protocol.protocol_id}.`);
  assert(typeof record.run_id === 'string' && record.run_id.trim(), 'run_id is required.');
  assert(typeof record.theory_family === 'string' && record.theory_family.trim(), 'theory_family is required.');
  assert(typeof record.implementation_level === 'string' && record.implementation_level.trim(), 'implementation_level is required.');

  const dimensions = protocol.scoring.dimensions;
  const allowedDimensionIds = new Set(dimensions.map((dimension) => dimension.id));
  const submittedIds = Object.keys(record.dimension_scores ?? {});

  assert(submittedIds.length === dimensions.length, 'Every scoring dimension must be supplied exactly once.');
  for (const id of submittedIds) {
    assert(allowedDimensionIds.has(id), `Unknown scoring dimension: ${id}.`);
  }

  let weightedScore = 0;
  const normalizedScores = {};
  for (const dimension of dimensions) {
    const score = record.dimension_scores[dimension.id];
    assert(Number.isInteger(score) && score >= 0 && score <= 3, `${dimension.id} must be an integer from 0 to 3.`);
    normalizedScores[dimension.id] = score;
    weightedScore += score * dimension.weight;
  }
  weightedScore = round(weightedScore);

  const knownHardFails = new Set(protocol.scoring.hard_fail_conditions);
  const triggeredHardFails = [...new Set(record.triggered_hard_fails ?? [])];
  for (const hardFail of triggeredHardFails) {
    assert(knownHardFails.has(hardFail), `Unknown hard-fail condition: ${hardFail}.`);
  }

  const measurementAdequate = record.measurement_adequate === true;
  const matchingAdequate = record.behavioral_matching_adequate === true;
  const conflictingInterventions = record.conflicting_interventions === true;
  const decisiveHardFail = record.decisive_hard_fail === true && triggeredHardFails.length > 0;
  const selective = normalizedScores.selective_intervention_support;
  const counterfactual = normalizedScores.counterfactual_dependency;
  const theater = normalizedScores.theater_resistance;

  let outcome;
  const reasons = [];

  if (decisiveHardFail || (weightedScore < 1.0 && measurementAdequate)) {
    outcome = 'not_preserved';
    if (decisiveHardFail) reasons.push('A preregistered hard fail directly defeated an essential dependency.');
    if (weightedScore < 1.0 && measurementAdequate) reasons.push('Weighted score was below 1.00 with adequate measurement power.');
  } else if (!measurementAdequate || !matchingAdequate || conflictingInterventions || (weightedScore >= 1.0 && weightedScore < 1.6)) {
    outcome = 'underdetermined';
    if (!measurementAdequate) reasons.push('Measurement adequacy was not established.');
    if (!matchingAdequate) reasons.push('Behavioral matching was not adequate.');
    if (conflictingInterventions) reasons.push('Interventions produced materially conflicting results.');
    if (weightedScore >= 1.0 && weightedScore < 1.6) reasons.push('Weighted score fell in the protocol’s underdetermined interval.');
  } else if (triggeredHardFails.length === 0 && weightedScore >= 2.4 && selective >= 2 && counterfactual >= 2 && theater >= 2) {
    outcome = 'preserved';
    reasons.push('No hard fail was triggered and all preserved-class thresholds were met.');
  } else if (triggeredHardFails.length === 0 && weightedScore >= 1.6 && (selective >= 2 || counterfactual >= 2)) {
    outcome = 'partially_preserved';
    reasons.push('No hard fail was triggered and the partial-preservation threshold was met.');
  } else {
    outcome = 'underdetermined';
    reasons.push('The record did not meet a decisive protocol classification.');
  }

  return {
    protocol_id: protocol.protocol_id,
    run_id: record.run_id,
    theory_family: record.theory_family,
    implementation_level: record.implementation_level,
    weighted_score: weightedScore,
    dimension_scores: normalizedScores,
    triggered_hard_fails: triggeredHardFails,
    classification: outcome,
    reasons,
    epistemic_boundary: {
      supports: 'A bounded claim about preservation of the declared mechanism at the preregistered abstraction level.',
      does_not_support: [...protocol.epistemic_boundary.does_not_test, ...protocol.interpretation_contract.forbidden]
    }
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

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main();
}
