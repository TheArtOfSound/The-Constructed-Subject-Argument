#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { generateFiniteStateReport } from './generate-classification-policy-finite-state-report.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const reportPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_POLICY_FINITE_STATE_REPORT.json');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function sum(entries, field) {
  return entries.reduce((total, entry) => total + entry[field], 0);
}

try {
  const committed = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
  const regenerated = generateFiniteStateReport();
  assert(
    JSON.stringify(committed) === JSON.stringify(regenerated),
    'Committed finite-state report differs from deterministic semantic regeneration.'
  );
  assert(committed.status === 'generated_exhaustive_synthetic_policy_analysis', 'Finite-state report must retain generated synthetic-analysis status.');
  assert(committed.enumerated_domain.total_valid_states === 61440, 'Finite-state domain must contain exactly 61,440 declared valid scorer inputs.');
  assert(committed.enumerated_domain.submitted_score_vector_count === 1024, 'Five integer dimensions scored 0–3 must yield 1,024 score vectors.');
  assert(committed.summary.total_valid_states === committed.enumerated_domain.total_valid_states, 'Summary and domain state totals must agree.');
  assert(committed.summary.states_without_matching_rule === 0, 'Every valid state must match at least the fallback rule.');
  assert(committed.summary.fully_shadowed_rule_count === 0, 'No policy rule may be fully shadowed over the declared finite domain.');
  assert(committed.summary.selected_rule_count === committed.summary.policy_rule_count, 'Every policy rule must control at least one valid state.');
  assert(committed.summary.exhaustive_coverage_pass === true, 'Exhaustive finite-state coverage must pass.');
  assert(sum(committed.selected_rule_coverage, 'selected_state_count') === committed.summary.total_valid_states, 'Selected-rule state counts must partition the valid domain.');
  assert(sum(committed.outcome_counts, 'state_count') === committed.summary.total_valid_states, 'Outcome state counts must partition the valid domain.');
  assert(committed.findings.fallback_selected_state_count > 0, 'Fallback must be genuinely reachable rather than decorative.');
  assert(committed.findings.partially_shadowed_rule_ids.includes('preserved-thresholds'), 'Report must disclose that preserved thresholds can be suppressed by higher-priority blockers.');
  assert(committed.findings.partially_shadowed_rule_ids.includes('partially-preserved-thresholds'), 'Report must disclose that partial-preservation thresholds can be suppressed by higher-priority blockers.');
  const preserved = committed.selected_rule_coverage.find(({ rule_id }) => rule_id === 'preserved-thresholds');
  assert(preserved?.selected_state_count > 0, 'Preserved classification must remain reachable.');
  const noRule = committed.findings.no_rule_state_count;
  assert(noRule === 0, 'No valid enumerated state may escape classification.');
  const boundaryText = JSON.stringify(committed.interpretation_boundary);
  assert(boundaryText.includes('scientifically optimal'), 'Report must deny that finite-state consistency proves scientific optimality.');
  assert(boundaryText.includes('actual AI system') && boundaryText.includes('conscious'), 'Report must preserve actual-system and consciousness non-entailment language.');
  console.log(`Classification policy finite-state report validated across ${committed.summary.total_valid_states.toLocaleString('en-US')} valid states.`);
} catch (error) {
  console.error(`Classification policy finite-state validation failed: ${error.message}`);
  process.exit(1);
}
