#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const policyPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_POLICY.json');
const traceSuitePath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_TRACE_SUITE.json');
const outputPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_POLICY_STRUCTURE_REPORT.json');

const allowedFields = new Set([
  'decisive_hard_fail',
  'weighted_score',
  'measurement_adequate',
  'matching_adequate',
  'conflicting_interventions',
  'triggered_hard_fail_count',
  'dimension_scores.selective_intervention_support',
  'dimension_scores.counterfactual_dependency',
  'dimension_scores.theater_resistance'
]);

function walkPredicates(requirements = [], result = []) {
  for (const predicate of requirements) {
    result.push(predicate);
    if (Array.isArray(predicate.requirements)) walkPredicates(predicate.requirements, result);
  }
  return result;
}

export function generateStructureReport() {
  const policy = JSON.parse(fs.readFileSync(policyPath, 'utf8'));
  const traceSuite = JSON.parse(fs.readFileSync(traceSuitePath, 'utf8'));
  const rulesByPriority = [...policy.outcomes].sort((a, b) => a.priority - b.priority);
  const ruleIds = rulesByPriority.map((rule) => rule.rule_id);
  const priorities = rulesByPriority.map((rule) => rule.priority);
  const fallback = rulesByPriority.at(-1);
  const predicates = rulesByPriority.flatMap((rule) => walkPredicates(rule.requirements));
  const fields = [...new Set(predicates.map((predicate) => predicate.field).filter(Boolean))].sort();
  const operators = [...new Set(predicates.map((predicate) => predicate.operator).filter(Boolean))].sort();
  const reachedRuleIds = [...new Set(traceSuite.cases.map((entry) => entry.classification_rule_id))];
  const unreachableRuleIds = ruleIds.filter((ruleId) => !reachedRuleIds.includes(ruleId));
  const duplicateRuleIds = ruleIds.filter((ruleId, index) => ruleIds.indexOf(ruleId) !== index);
  const duplicatePriorities = priorities.filter((priority, index) => priorities.indexOf(priority) !== index);
  const invalidFields = fields.filter((field) => !allowedFields.has(field));
  const invalidOperators = operators.filter((operator) => !policy.operators.includes(operator));
  const signatures = rulesByPriority.map((rule) => ({
    rule_id: rule.rule_id,
    signature: JSON.stringify({ match: rule.match, requirements: rule.requirements })
  }));
  const duplicateSignatures = signatures.filter((entry, index) => signatures.findIndex((other) => other.signature === entry.signature) !== index).map((entry) => entry.rule_id);
  const checks = {
    unique_rule_ids: duplicateRuleIds.length === 0,
    unique_priorities: duplicatePriorities.length === 0,
    evaluation_order_matches_priority_order: JSON.stringify(policy.evaluation_order) === JSON.stringify(ruleIds),
    priorities_strictly_increase: priorities.every((priority, index) => index === 0 || priority > priorities[index - 1]),
    fallback_is_last: fallback?.rule_id === 'underdetermined-fallback',
    fallback_is_unconditional: fallback?.match === 'all' && (fallback.requirements ?? []).length === 0,
    all_predicate_fields_allowed: invalidFields.length === 0,
    all_operators_declared: invalidOperators.length === 0,
    every_rule_reached_by_canonical_suite: unreachableRuleIds.length === 0,
    no_duplicate_rule_signatures: duplicateSignatures.length === 0
  };
  const passed = Object.values(checks).every(Boolean);
  return {
    schema_id: 'EXP-11-CLASSIFICATION-POLICY-STRUCTURE-REPORT',
    schema_version: '1.0.0',
    protocol_id: policy.protocol_id,
    status: 'generated_synthetic_policy_structure_analysis',
    policy_id: policy.schema_id,
    source_artifacts: {
      policy: 'research/MECHANISM_PRESERVATION_CLASSIFICATION_POLICY.json',
      trace_suite: 'research/MECHANISM_PRESERVATION_CLASSIFICATION_TRACE_SUITE.json'
    },
    summary: {
      rule_count: ruleIds.length,
      predicate_count: predicates.length,
      reached_rule_count: reachedRuleIds.length,
      structural_checks_passed: Object.values(checks).filter(Boolean).length,
      structural_check_count: Object.keys(checks).length,
      overall_pass: passed
    },
    ordered_rules: rulesByPriority.map((rule) => ({ rule_id: rule.rule_id, outcome: rule.outcome, priority: rule.priority, match: rule.match })),
    checks,
    findings: {
      duplicate_rule_ids: duplicateRuleIds,
      duplicate_priorities: duplicatePriorities,
      invalid_predicate_fields: invalidFields,
      invalid_operators: invalidOperators,
      unreachable_rule_ids: unreachableRuleIds,
      duplicate_rule_signatures: duplicateSignatures
    },
    interpretation_boundary: {
      supports: 'Structural consistency of the encoded classification policy and demonstrated reachability under the canonical synthetic trace suite.',
      does_not_support: [
        'That the policy thresholds are scientifically optimal',
        'That the policy ontology is uniquely correct',
        'That all possible semantic shadowing has been mathematically excluded',
        'Any claim about whether an actual AI system is conscious, nonconscious, sentient, a person, or morally considerable'
      ]
    }
  };
}

function main() {
  const report = generateStructureReport();
  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  if (process.argv.includes('--stdout')) process.stdout.write(serialized);
  else if (process.argv.includes('--check')) {
    const current = fs.readFileSync(outputPath, 'utf8');
    if (current !== serialized) throw new Error('Committed structure report differs from deterministic regeneration.');
    console.log('Classification policy structure report is current.');
  } else {
    fs.writeFileSync(outputPath, serialized);
    console.log(`Wrote ${path.relative(root, outputPath)}.`);
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { main(); } catch (error) { console.error(`Structure report generation failed: ${error.message}`); process.exit(1); }
}
