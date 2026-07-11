#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const RAW_PATH = path.join(ROOT, 'research/MECHANISM_PRESERVATION_RAW_FIXTURE.json');
const MANIFEST_PATH = path.join(ROOT, 'research/MECHANISM_PRESERVATION_RAW_ARTIFACT_MANIFEST.json');
const OUTPUT_PATH = path.join(ROOT, 'research/MECHANISM_PRESERVATION_DERIVED_RESULTS.json');

const raw = JSON.parse(fs.readFileSync(RAW_PATH, 'utf8'));
const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
const contract = manifest.derivation_contract;

function round(value) {
  return Number(value.toFixed(contract.rounding_decimals));
}

function mean(values) {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function sampleStandardDeviation(values) {
  if (values.length < 2) throw new Error('At least two replicates are required for an interval.');
  const average = mean(values);
  const variance = values.reduce((sum, value) => sum + (value - average) ** 2, 0) / (values.length - 1);
  return Math.sqrt(variance);
}

function directionFor(interventionId) {
  if (interventionId.includes('LESION')) return contract.lesion_direction;
  if (interventionId.includes('PATCH')) return contract.patch_direction;
  throw new Error(`No preregistered direction for ${interventionId}`);
}

function pairedDifference(row, direction) {
  if (direction === 'reference_minus_candidate') return row.reference - row.candidate;
  if (direction === 'candidate_minus_reference') return row.candidate - row.reference;
  throw new Error(`Unsupported direction: ${direction}`);
}

function deriveIntervention(intervention) {
  if (intervention.estimator !== contract.estimator) {
    throw new Error(`${intervention.intervention_id} estimator diverges from the locked contract.`);
  }
  if (intervention.interval_method !== contract.interval_method) {
    throw new Error(`${intervention.intervention_id} interval method diverges from the locked contract.`);
  }

  const direction = directionFor(intervention.intervention_id);
  const effects = intervention.replicates.map((row) => pairedDifference(row, direction));
  const effectSize = mean(effects);
  const standardError = sampleStandardDeviation(effects) / Math.sqrt(effects.length);
  const margin = contract.interval_multiplier * standardError;

  const controls = Object.entries(intervention.controls)
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([controlId, rows]) => {
      const controlEffect = mean(rows.map((row) => pairedDifference(row, direction)));
      return {
        control_id: controlId,
        mean_paired_difference: round(controlEffect),
        passed: Math.abs(controlEffect) <= 0.05
      };
    });

  return {
    intervention_id: intervention.intervention_id,
    estimator: intervention.estimator,
    direction,
    replications: intervention.replicates.length,
    effect_size: round(effectSize),
    uncertainty_interval: [round(effectSize - margin), round(effectSize + margin)],
    controls,
    controls_passed: controls.every((control) => control.passed)
  };
}

export function generateDerivedResults() {
  return {
    generator_id: 'EXP11-DERIVED-RESULTS-V1',
    run_id: raw.run_id,
    empirical_status: raw.empirical_status,
    source_manifest_id: manifest.manifest_id,
    source_artifact_id: raw.artifact_id,
    generated_notice: 'Generated deterministically from the locked synthetic raw artifact. Do not edit manually.',
    interventions: raw.interventions.map(deriveIntervention),
    epistemic_boundary: 'This generated synthetic artifact tests numerical provenance only. It is not evidence that any actual AI system preserves a consciousness-relevant mechanism or is conscious.'
  };
}

export function serializeDerivedResults() {
  return `${JSON.stringify(generateDerivedResults(), null, 2)}\n`;
}

const requestedCheck = process.argv.includes('--check');
const requestedStdout = process.argv.includes('--stdout');

if (requestedStdout) {
  process.stdout.write(serializeDerivedResults());
} else if (requestedCheck) {
  const generated = serializeDerivedResults();
  const committed = fs.readFileSync(OUTPUT_PATH, 'utf8');
  if (generated !== committed) {
    console.error('Derived mechanism result artifact is stale or manually edited.');
    process.exit(1);
  }
  console.log('Derived mechanism result artifact matches locked raw observations.');
} else {
  fs.writeFileSync(OUTPUT_PATH, serializeDerivedResults());
  console.log(`Wrote ${path.relative(ROOT, OUTPUT_PATH)}.`);
}
