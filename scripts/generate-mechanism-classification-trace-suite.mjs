#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { scoreMechanismPreservation, loadClassificationPolicy } from './score-mechanism-preservation.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const fixturePath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_TRACE_FIXTURES.json');
const outputPath = path.join(root, 'research', 'MECHANISM_PRESERVATION_CLASSIFICATION_TRACE_SUITE.json');

export function generateClassificationTraceSuite() {
  const fixtures = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
  const policy = loadClassificationPolicy();
  const cases = fixtures.cases.map((fixture) => {
    const result = scoreMechanismPreservation(fixture.record);
    return {
      case_id: fixture.case_id,
      run_id: fixture.record.run_id,
      expected_classification: fixture.expected_classification,
      expected_rule_id: fixture.expected_rule_id,
      classification: result.classification,
      classification_rule_id: result.classification_rule_id,
      weighted_score: result.weighted_score,
      dimension_scores: result.dimension_scores,
      capacity_confound_adjudication_state: result.capacity_confound_adjudication_state,
      triggered_hard_fails: result.triggered_hard_fails,
      classification_reasons: result.reasons,
      classification_predicate_evaluations: result.classification_predicate_evaluations,
      expectation_matches:
        result.classification === fixture.expected_classification &&
        result.classification_rule_id === fixture.expected_rule_id
    };
  });

  return {
    schema_id: 'EXP-11-CLASSIFICATION-TRACE-SUITE',
    schema_version: '1.0.0',
    protocol_id: fixtures.protocol_id,
    status: 'generated_synthetic_adversarial_trace_suite',
    purpose:
      'Exercise every classification-policy branch and precedence interaction with synthetic records. This suite is a logic audit, not evidence about any actual AI system.',
    presentation_safety: policy.presentation_contract,
    cases,
    epistemic_boundary: policy.epistemic_boundary
  };
}

export function serializeClassificationTraceSuite() {
  return `${JSON.stringify(generateClassificationTraceSuite(), null, 2)}\n`;
}

function main() {
  const serialized = serializeClassificationTraceSuite();
  if (process.argv.includes('--stdout')) {
    process.stdout.write(serialized);
    return;
  }
  if (process.argv.includes('--check')) {
    const committed = fs.readFileSync(outputPath, 'utf8');
    if (committed !== serialized) {
      throw new Error('Committed classification trace suite differs from deterministic regeneration.');
    }
    console.log('Classification trace suite matches deterministic regeneration.');
    return;
  }
  fs.writeFileSync(outputPath, serialized);
  console.log(`Wrote ${path.relative(root, outputPath)}.`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    main();
  } catch (error) {
    console.error(`Classification trace suite generation failed: ${error.message}`);
    process.exit(1);
  }
}
