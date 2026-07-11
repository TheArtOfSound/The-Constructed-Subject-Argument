#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const reportPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_MUTATION_REPORT.json');
const registryPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_POLICY_MUTATIONS.json');
const generatorPath = path.join(root, 'scripts', 'generate-classification-policy-mutation-report.mjs');

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function main() {
  execFileSync(process.execPath, [generatorPath, '--check'], { cwd: root, stdio: 'inherit' });

  const report = readJson(reportPath);
  const registry = readJson(registryPath);

  assert(report.schema_id === 'EXP-11-CLASSIFICATION-MUTATION-REPORT', 'Unexpected mutation-report schema_id.');
  assert(report.status === 'generated_synthetic_mutation_analysis', 'Mutation report must remain explicitly generated and synthetic.');
  assert(report.protocol_id === registry.protocol_id, 'Mutation report protocol_id must match the mutation registry.');
  assert(report.summary.mutation_count === registry.mutations.length, 'Mutation count must equal the registry length.');
  assert(report.results.length === registry.mutations.length, 'Exactly one result is required per registered mutation.');
  assert(report.summary.killed_count === report.results.filter(({ killed }) => killed).length, 'Killed-count summary drifted.');
  assert(report.summary.survived_count === report.results.filter(({ killed }) => !killed).length, 'Survivor-count summary drifted.');
  assert(report.summary.mutation_score === report.summary.killed_count / report.summary.mutation_count, 'Mutation score must be derived from killed/total.');
  assert(report.summary.survived_count === 0, 'No registered classification-policy mutation may survive.');
  assert(report.summary.mutation_score === 1, 'Canonical registered mutation score must remain 1.0.');

  const registeredIds = registry.mutations.map(({ mutation_id }) => mutation_id);
  const reportedIds = report.results.map(({ mutation_id }) => mutation_id);
  assert(JSON.stringify(reportedIds) === JSON.stringify(registeredIds), 'Mutation report order and IDs must match the registry exactly.');
  assert(new Set(reportedIds).size === reportedIds.length, 'Mutation report IDs must be unique.');

  for (const result of report.results) {
    assert(result.killed === true, `${result.mutation_id} survived.`);
    assert(result.execution_error_count === 0, `${result.mutation_id} was detected through execution failure rather than changed inference.`);
    assert(result.representative_kill?.case_id, `${result.mutation_id} lacks representative killing evidence.`);
    const { baseline, mutant } = result.representative_kill;
    assert(
      baseline.classification !== mutant.classification || baseline.rule_id !== mutant.rule_id,
      `${result.mutation_id} representative evidence does not change classification or matched rule.`
    );
    assert(baseline.weighted_score === mutant.weighted_score, `${result.mutation_id} must mutate policy semantics, not empirical scores.`);
  }

  assert(/not evidence about any actual AI system/i.test(report.purpose), 'Mutation report must preserve the real-system non-entailment notice.');
  assert(/does not prove the normative policy is scientifically correct/i.test(report.limitations.join(' ')), 'Mutation report must distinguish test sensitivity from normative truth.');
  assert(/consciousness/i.test(report.epistemic_boundary), 'Mutation report must preserve the consciousness non-entailment boundary.');

  console.log(`Classification policy mutation report validation passed: ${report.summary.killed_count}/${report.summary.mutation_count} registered mutations killed.`);
}

try {
  main();
} catch (error) {
  console.error(`Classification policy mutation report validation failed: ${error.message}`);
  process.exit(1);
}
