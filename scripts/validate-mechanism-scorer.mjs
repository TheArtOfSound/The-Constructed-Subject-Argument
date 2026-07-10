#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadProtocol, scoreMechanismPreservation } from './score-mechanism-preservation.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const fixturePath = path.join(root, 'research', 'MECHANISM_PRESERVATION_TEST_CASES.json');

function fail(message) {
  console.error(`Mechanism scorer validation failed: ${message}`);
  process.exit(1);
}

function assert(condition, message) {
  if (!condition) fail(message);
}

const protocol = loadProtocol();
const fixtures = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));

assert(fixtures.protocol_id === protocol.protocol_id, 'Fixture protocol_id does not match the protocol.');
assert(Array.isArray(fixtures.cases) && fixtures.cases.length >= 5, 'At least five adversarial fixtures are required.');
assert(/not empirical findings/i.test(fixtures.purpose), 'Fixtures must state that they are not empirical findings.');
assert(/never establishes consciousness/i.test(fixtures.governing_boundary), 'Fixtures must preserve the consciousness boundary.');

const requiredOutcomes = new Set(['preserved', 'partially_preserved', 'not_preserved', 'underdetermined']);
const observedOutcomes = new Set();
const runIds = new Set();

for (const testCase of fixtures.cases) {
  assert(typeof testCase.name === 'string' && testCase.name.trim(), 'Each fixture requires a name.');
  assert(requiredOutcomes.has(testCase.expected_classification), `${testCase.name} has an invalid expected classification.`);
  assert(!runIds.has(testCase.record.run_id), `Duplicate run_id: ${testCase.record.run_id}.`);
  runIds.add(testCase.record.run_id);

  let result;
  try {
    result = scoreMechanismPreservation(testCase.record, protocol);
  } catch (error) {
    fail(`${testCase.name} threw: ${error.message}`);
  }

  assert(
    result.classification === testCase.expected_classification,
    `${testCase.name} expected ${testCase.expected_classification} but received ${result.classification}.`
  );
  assert(result.weighted_score >= 0 && result.weighted_score <= 3, `${testCase.name} produced an invalid weighted score.`);
  assert(
    result.epistemic_boundary.does_not_support.some((statement) => /conscious/i.test(statement)),
    `${testCase.name} lost the consciousness non-entailment boundary.`
  );
  observedOutcomes.add(result.classification);
}

for (const outcome of requiredOutcomes) {
  assert(observedOutcomes.has(outcome), `No fixture exercises the ${outcome} classification.`);
}

const failedMatchingFixture = fixtures.cases.find((testCase) => testCase.name === 'failed_matching_blocks_inference');
assert(failedMatchingFixture, 'Missing failed-matching fixture.');
const failedMatchingResult = scoreMechanismPreservation(failedMatchingFixture.record, protocol);
assert(
  failedMatchingResult.classification === 'underdetermined',
  'Failed behavioral matching must block a positive preservation classification.'
);

const theaterFixture = fixtures.cases.find((testCase) => testCase.name === 'behavioral_theater_defeats_mechanism_claim');
assert(theaterFixture, 'Missing behavioral-theater fixture.');
const theaterResult = scoreMechanismPreservation(theaterFixture.record, protocol);
assert(
  theaterResult.classification === 'not_preserved',
  'A decisive behavioral-theater hard fail must defeat the declared mechanism claim.'
);

console.log(`Mechanism scorer validation passed: ${fixtures.cases.length} fixtures, all four outcomes exercised.`);
