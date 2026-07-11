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
const outputPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_MUTATION_REPORT.json');

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

export function generateMutationReport() {
  const protocol = loadProtocol();
  const policy = loadClassificationPolicy();
  const fixtures = readJson(fixturesPath);
  const mutationRegistry = readJson(mutationsPath);

  assert(fixtures.protocol_id === protocol.protocol_id, 'Fixture protocol_id must match the protocol.');
  assert(mutationRegistry.protocol_id === protocol.protocol_id, 'Mutation registry protocol_id must match the protocol.');

  const baselineByCase = new Map();
  for (const fixture of fixtures.cases) {
    const baseline = classify(fixture.record, protocol, policy);
    assert(baseline.classification === fixture.expected_classification, `${fixture.case_id} baseline classification drifted.`);
    assert(baseline.rule_id === fixture.expected_rule_id, `${fixture.case_id} baseline rule drifted.`);
    baselineByCase.set(fixture.case_id, baseline);
  }

  const results = mutationRegistry.mutations.map((mutation) => {
    const mutantPolicy = applyMutation(policy, mutation);
    let representativeKill = null;
    let executionErrorCount = 0;

    for (const fixture of fixtures.cases) {
      const baseline = baselineByCase.get(fixture.case_id);
      try {
        const mutant = classify(fixture.record, protocol, mutantPolicy);
        if (!representativeKill && changedFromBaseline(baseline, mutant)) {
          representativeKill = {
            case_id: fixture.case_id,
            baseline,
            mutant
          };
        }
      } catch {
        executionErrorCount += 1;
      }
    }

    return {
      mutation_id: mutation.mutation_id,
      description: mutation.description,
      target: {
        operation: mutation.operation,
        rule_id: mutation.rule_id,
        predicate_id: mutation.predicate_id ?? null,
        field_name: mutation.field_name ?? null,
        child_index: mutation.child_index ?? null,
        from: mutation.from,
        to: mutation.to
      },
      killed: representativeKill !== null,
      representative_kill: representativeKill,
      execution_error_count: executionErrorCount
    };
  });

  const killedCount = results.filter(({ killed }) => killed).length;
  const survivedCount = results.length - killedCount;

  return {
    schema_id: 'EXP-11-CLASSIFICATION-MUTATION-REPORT',
    schema_version: '1.0.0',
    protocol_id: protocol.protocol_id,
    classification_policy_id: policy.schema_id,
    status: 'generated_synthetic_mutation_analysis',
    generated_notice: 'Generated deterministically from the normative classification policy, registered policy mutations, and canonical synthetic classification fixtures. Do not edit manually.',
    purpose: 'Demonstrate that representative adversarial fixtures detect deliberate corruptions of classification thresholds, connectives, and rule priority. This is an audit of inference software, not evidence about any actual AI system.',
    source_artifacts: {
      classification_policy: 'research/MECHANISM_PRESERVATION_CLASSIFICATION_POLICY.json',
      mutation_registry: 'research/MECHANISM_PRESERVATION_CLASSIFICATION_POLICY_MUTATIONS.json',
      fixture_registry: 'research/MECHANISM_PRESERVATION_CLASSIFICATION_TRACE_FIXTURES.json',
      scorer: 'scripts/score-mechanism-preservation.mjs'
    },
    summary: {
      mutation_count: results.length,
      killed_count: killedCount,
      survived_count: survivedCount,
      mutation_score: results.length === 0 ? 0 : killedCount / results.length,
      interpretation: survivedCount === 0
        ? 'Every registered semantic corruption changed at least one canonical classification or matched rule.'
        : 'One or more registered corruptions survived; the fixture suite does not protect every declared policy property.'
    },
    results,
    limitations: [
      'The registry samples high-value policy faults rather than exhaustively generating every possible mutation.',
      'A killed mutant shows fixture sensitivity to that corruption; it does not prove the normative policy is scientifically correct.',
      'Representative kills are reported for compact public auditability; additional fixtures may also kill the same mutant.',
      'Mutation analysis does not validate the empirical truth of any mechanism-preservation result.'
    ],
    epistemic_boundary: mutationRegistry.epistemic_boundary
  };
}

export function serializeMutationReport(report = generateMutationReport()) {
  return `${JSON.stringify(report, null, 2)}\n`;
}

function main() {
  const serialized = serializeMutationReport();
  if (process.argv.includes('--stdout')) {
    process.stdout.write(serialized);
    return;
  }
  if (process.argv.includes('--check')) {
    assert(fs.existsSync(outputPath), `Missing generated mutation report: ${path.relative(root, outputPath)}.`);
    assert(fs.readFileSync(outputPath, 'utf8') === serialized, 'Committed classification mutation report differs from deterministic regeneration.');
    console.log('Classification policy mutation report is current.');
    return;
  }
  fs.writeFileSync(outputPath, serialized);
  console.log(`Wrote ${path.relative(root, outputPath)}.`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    main();
  } catch (error) {
    console.error(`Classification policy mutation report generation failed: ${error.message}`);
    process.exit(1);
  }
}
