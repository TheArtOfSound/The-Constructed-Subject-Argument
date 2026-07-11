#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { generateStructureReport } from './generate-classification-policy-structure-report.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const reportPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_POLICY_STRUCTURE_REPORT.json');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

try {
  const committed = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
  const regenerated = generateStructureReport();
  assert(JSON.stringify(committed) === JSON.stringify(regenerated), 'Committed structure report differs from deterministic semantic regeneration.');
  assert(committed.status === 'generated_synthetic_policy_structure_analysis', 'Structure report must remain explicitly synthetic policy analysis.');
  assert(committed.summary.overall_pass === true, 'Classification policy structural analysis must pass.');
  assert(committed.summary.structural_checks_passed === committed.summary.structural_check_count, 'Every declared structural check must pass.');
  for (const [check, passed] of Object.entries(committed.checks)) assert(passed === true, `Structural check failed: ${check}.`);
  for (const [finding, entries] of Object.entries(committed.findings)) assert(Array.isArray(entries) && entries.length === 0, `Structural finding must be empty: ${finding}.`);
  assert(committed.ordered_rules.at(-1)?.rule_id === 'underdetermined-fallback', 'Fallback must be the final ordered rule.');
  assert(committed.interpretation_boundary.does_not_support.some((entry) => entry.includes('scientifically optimal')), 'Report must deny that structural validity proves threshold optimality.');
  assert(committed.interpretation_boundary.does_not_support.some((entry) => entry.includes('actual AI system') && entry.includes('conscious')), 'Report must preserve the actual-system consciousness non-entailment boundary.');
  console.log(`Classification policy structure report validated: ${committed.summary.structural_checks_passed}/${committed.summary.structural_check_count} checks passed.`);
} catch (error) {
  console.error(`Classification policy structure validation failed: ${error.message}`);
  process.exit(1);
}
