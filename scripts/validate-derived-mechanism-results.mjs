#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { generateDerivedResults, serializeDerivedResults } from './generate-mechanism-derived-results.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DERIVED_PATH = path.join(ROOT, 'research/MECHANISM_PRESERVATION_DERIVED_RESULTS.json');
const EMPIRICAL_PATH = path.join(ROOT, 'research/MECHANISM_PRESERVATION_EMPIRICAL_FIXTURE.json');

const committedBytes = fs.readFileSync(DERIVED_PATH, 'utf8');
const regeneratedBytes = serializeDerivedResults();
if (committedBytes !== regeneratedBytes) {
  throw new Error('Committed derived results are stale or differ from deterministic regeneration.');
}

const derived = generateDerivedResults();
const empirical = JSON.parse(fs.readFileSync(EMPIRICAL_PATH, 'utf8'));

if (derived.empirical_status !== 'synthetic_fixture' || empirical.empirical_status !== 'synthetic_fixture') {
  throw new Error('Repository fixture must remain explicitly synthetic.');
}
if (derived.run_id !== empirical.run_id) {
  throw new Error('Derived and empirical run identifiers diverge.');
}

const empiricalById = new Map(empirical.interventions.map((entry) => [entry.intervention_id, entry]));
if (empiricalById.size !== derived.interventions.length) {
  throw new Error('Derived and empirical intervention inventories diverge.');
}

for (const generated of derived.interventions) {
  const reported = empiricalById.get(generated.intervention_id);
  if (!reported) throw new Error(`Missing empirical intervention ${generated.intervention_id}.`);

  const comparisons = [
    ['effect_size', reported.effect_size, generated.effect_size],
    ['replications', reported.replications, generated.replications],
    ['controls_passed', reported.controls_passed, generated.controls_passed]
  ];
  for (const [field, actual, expected] of comparisons) {
    if (actual !== expected) {
      throw new Error(`${generated.intervention_id} ${field} is not generated from raw evidence.`);
    }
  }

  if (JSON.stringify(reported.uncertainty_interval) !== JSON.stringify(generated.uncertainty_interval)) {
    throw new Error(`${generated.intervention_id} uncertainty interval is not generated from raw evidence.`);
  }

  const reportedControls = new Map(reported.control_results.map((control) => [control.control_id, control.passed]));
  for (const control of generated.controls) {
    if (reportedControls.get(control.control_id) !== control.passed) {
      throw new Error(`${generated.intervention_id}/${control.control_id} pass state diverges from raw evidence.`);
    }
  }
}

const forbiddenBoundary = derived.epistemic_boundary.toLowerCase();
if (!forbiddenBoundary.includes('not evidence') || !forbiddenBoundary.includes('conscious')) {
  throw new Error('Generated artifact lost its consciousness non-entailment boundary.');
}

console.log(`Validated ${derived.interventions.length} byte-reproducible synthetic intervention summaries.`);
