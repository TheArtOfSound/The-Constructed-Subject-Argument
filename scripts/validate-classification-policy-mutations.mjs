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
const fixturesPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_TRACE_FIXTURES.json');
const mutationsPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_POLICY_MUTATIONS.json');

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function clone(value) {
  return structuredClone(value);
}

function findRule(policy, ruleId) {
  const matches = policy.outcomes.filter(({ rule_id: candidate }) => candidate === ruleId);
  assert(matches.length === 1, `Mutation target rule ${ruleId} must resolve exactly once.`);
  return matches[0];
}

function findPredicate(rule, predicateId) {
  const matches = (rule.requirements ?? []).filter(({ predicate_id: candidate }) => candidate === predicateId);
  assert(matches.length === 1, `Mutation target predicate ${predicateId} in ${rule.rule_id} must resolve exactly once.`);
  return matches[0];
}

function replaceChecked(target, field, from, to, mutationId) {
  assert(
    target[field] === from,
    `${mutationId} expected ${field}=${JSON.stringify(from)} but found ${JSON.stringify(target[field])}.`
  );
  target[field] = to;
}

function applyMutation(basePolicy, mutation) {
  const policy = clone(basePolicy);
  const rule = findRule(policy, mutation.rule_id);

  switch (mutation.operation) {
    case 'replace_priority':
      replaceChecked(rule, 'priority', mutation.from, mutation.to, mutation.mutation_id);
      break;
    case 'replace_rule_match':
      replaceChecked(rule, 'match', mutation.from, mutation.to, mutation.mutation_id);
      break;
    case 'replace_number': {
      const predicate = findPredicate(rule, mutation.predicate_id);
      replaceChecked(predicate, mutation.field_name, mutation.from, mutation.to, mutation.mutation_id);
      break;
    }
    case 'replace_operator': {
      const predicate = findPredicate(rule, mutation.predicate_id);
      const target = Number.isInteger(mutation.child_index)
        ? predicate.requirements?.[mutation.child_index]
        : predicate;
      assert(target, `${mutation.mutation_id} child_index does not resolve.`);
      replaceChecked(target, 'operator', mutation.from, mutation.to, mutation.mutation_id);
      break;
    }
    default:
      throw new Error(`Unsupported mutation operation: ${mutation.operation}.`);
  }

  return policy;
}

function classify(record, protocol, policy) {
  const result = scoreMechanismPreservation(clone(record), protocol, policy);
  return {
    classification: result.classification,
    rule_id: result.classification_rule_id,
    weighted_score: result.weighted_score
  };
}

function changedFromBaseline(baseline, mutant) {
  return baseline.classification !== mutant.classification || baseline.rule_id !== mutant.rule_id;
}

function main() {
  const protocol = loadProtocol();
  const policy = loadClassificationPolicy();
  const fixtures = readJson(fixturesPath);
  const mutationRegistry = readJson(mutationsPath);

  assert(fixtures.protocol_id === protocol.protocol_id, 'Fixture protocol_id must match the protocol.');
  assert(mutationRegistry.protocol_id === protocol.protocol_id, 'Mutation registry protocol_id must match the protocol.');
  assert(mutationRegistry.status === 'synthetic_adversarial_policy_mutations', 'Mutation registry must remain explicitly synthetic.');
  assert(/no observations about any actual AI system/i.test(mutationRegistry.purpose), 'Mutation registry must preserve the real-system non-entailment notice.');
  assert(/consciousness/i.test(mutationRegistry.epistemic_boundary), 'Mutation registry must preserve the consciousness non-entailment boundary.');

  const mutationIds = mutationRegistry.mutations.map(({ mutation_id }) => mutation_id);
  assert(new Set(mutationIds).size === mutationIds.length, 'Mutation IDs must be unique.');
  assert(mutationIds.length >= 10, 'Mutation suite must cover at least ten distinct policy corruptions.');

  const baselineByCase = new Map();
  for (const fixture of fixtures.cases) {
    const baseline = classify(fixture.record, protocol, policy);
    assert(
      baseline.classification === fixture.expected_classification,
      `${fixture.case_id} baseline classification drifted: expected ${fixture.expected_classification}, observed ${baseline.classification}.`
    );
    assert(
      baseline.rule_id === fixture.expected_rule_id,
      `${fixture.case_id} baseline rule drifted: expected ${fixture.expected_rule_id}, observed ${baseline.rule_id}.`
    );
    baselineByCase.set(fixture.case_id, baseline);
  }

  const results = [];
  for (const mutation of mutationRegistry.mutations) {
    const mutantPolicy = applyMutation(policy, mutation);
    const killedBy = [];
    const executionErrors = [];

    for (const fixture of fixtures.cases) {
      const baseline = baselineByCase.get(fixture.case_id);
      try {
        const mutant = classify(fixture.record, protocol, mutantPolicy);
        if (changedFromBaseline(baseline, mutant)) {
          killedBy.push({
            case_id: fixture.case_id,
            baseline_classification: baseline.classification,
            mutant_classification: mutant.classification,
            baseline_rule_id: baseline.rule_id,
            mutant_rule_id: mutant.rule_id
          });
        }
      } catch (error) {
        executionErrors.push({ case_id: fixture.case_id, error: error.message });
      }
    }

    const killed = killedBy.length > 0 || executionErrors.length > 0;
    results.push({
      mutation_id: mutation.mutation_id,
      killed,
      killed_by: killedBy,
      execution_errors: executionErrors
    });
  }

  const survivors = results.filter(({ killed }) => !killed);
  assert(
    survivors.length === 0,
    `Classification policy mutation survivors: ${survivors.map(({ mutation_id }) => mutation_id).join(', ')}.`
  );

  const killedWithoutExecutionError = results.filter(({ killed_by, execution_errors }) => killed_by.length > 0 && execution_errors.length === 0);
  assert(
    killedWithoutExecutionError.length === results.length,
    'Every registered mutation must be killed by a changed classification or matched rule, not merely by an execution error.'
  );

  console.log(`Classification policy mutation validation passed: ${results.length}/${results.length} mutations killed.`);
  for (const result of results) {
    const representative = result.killed_by[0];
    console.log(
      `- ${result.mutation_id}: killed by ${representative.case_id} ` +
      `(${representative.baseline_classification}/${representative.baseline_rule_id} -> ` +
      `${representative.mutant_classification}/${representative.mutant_rule_id})`
    );
  }
}

try {
  main();
} catch (error) {
  console.error(`Classification policy mutation validation failed: ${error.message}`);
  process.exit(1);
}
