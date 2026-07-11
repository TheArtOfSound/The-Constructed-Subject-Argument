#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { generateTransitionReport } from './generate-classification-policy-transition-report.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const reportPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_POLICY_TRANSITION_REPORT.json');

try {
  const committed = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
  const regenerated = generateTransitionReport();
  assert.deepStrictEqual(committed, regenerated, 'Committed transition report must equal deterministic semantic regeneration.');
  assert.equal(committed.status, 'generated_exhaustive_synthetic_transition_analysis');
  assert.equal(committed.enumerated_domain.valid_source_state_count, 61440);
  assert.equal(committed.summary.total_one_step_transitions, committed.enumerated_domain.total_one_step_transitions);
  const partition = committed.summary.improved_transition_count
    + committed.summary.unchanged_transition_count
    + committed.summary.resolved_negative_transition_count
    + committed.summary.worsened_transition_count;
  assert.equal(partition, committed.summary.total_one_step_transitions, 'Transition categories must partition the enumerated transition set.');
  assert.equal(committed.summary.worsened_transition_count, 0, 'No declared one-step evidential improvement may worsen the ordered classification.');
  assert.equal(committed.summary.monotonicity_defect_candidate_count, 0);
  assert.equal(committed.summary.exhaustive_transition_pass, true);
  assert.equal(committed.findings.dimension_increase_worsening_count, 0);
  assert.equal(committed.findings.hard_fail_repair_worsening_count, 0);
  assert.equal(committed.findings.capacity_repair_worsening_count, 0);
  assert.ok(committed.summary.resolved_negative_transition_count > 0, 'The audit must retain legitimate uncertainty-to-negative resolution cases.');
  assert.equal(committed.findings.measurement_repairs_resolving_negative, committed.summary.resolved_negative_transition_count);
  assert.match(committed.transition_contract.resolved_negative_definition, /resolution, not monotonicity failure/i);
  assert.ok(committed.interpretation_boundary.does_not_support.some((entry) => /scientific optimality/i.test(entry)));
  assert.ok(committed.interpretation_boundary.does_not_support.some((entry) => /actual AI system.*conscious/i.test(entry)));
  console.log(`Classification policy transition report passed: ${committed.summary.total_one_step_transitions} adjacent transitions, ${committed.summary.worsened_transition_count} defect candidates, ${committed.summary.resolved_negative_transition_count} legitimate uncertainty-to-negative resolutions.`);
} catch (error) {
  console.error(`Classification policy transition validation failed: ${error.message}`);
  process.exit(1);
}
