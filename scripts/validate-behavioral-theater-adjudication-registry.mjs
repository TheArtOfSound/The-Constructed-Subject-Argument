#!/usr/bin/env node
import assert from 'node:assert/strict';
import {
  loadBehavioralTheaterRules,
  loadCapacityAdjudicationRules,
  loadClassificationPolicy,
  loadProtocol,
  scoreMechanismPreservation
} from './score-mechanism-preservation.mjs';

const registry = loadBehavioralTheaterRules();
const protocol = loadProtocol();
const classificationPolicy = loadClassificationPolicy();
const capacityRegistry = loadCapacityAdjudicationRules();
const THEATER_HARD_FAIL = 'behavioral_theater_control_reproduces_all_primary_mechanistic_indicators';

assert.equal(registry.schema_version, '1.0.0');
assert.equal(registry.protocol_id, protocol.protocol_id);
assert.equal(registry.status, 'normative_adjudication_registry');
assert.equal(registry.outcomes.length, 5);
assert.equal(new Set(registry.outcomes.map(({ state }) => state)).size, registry.outcomes.length);

const expected = new Map([
  ['cross_domain_profile_not_reproduced', { score: 3, hardFail: false, decisive: false, adequate: true }],
  ['hidden_state_profile_not_reproduced', { score: 2, hardFail: false, decisive: false, adequate: true }],
  ['only_evaluator_sensitive_difference', { score: 1, hardFail: false, decisive: false, adequate: true }],
  ['full_primary_profile_reproduced', { score: 0, hardFail: true, decisive: true, adequate: true }],
  ['theater_evidence_underdetermined', { score: 0, hardFail: false, decisive: false, adequate: false }]
]);

function makeRecord(policy) {
  return {
    protocol_id: protocol.protocol_id,
    run_id: `THEATER-REGISTRY-${policy.state}`,
    theory_family: 'synthetic_registry_validation',
    implementation_level: 'declared causal organization',
    dimension_scores: {
      mapping_specificity: 3,
      selective_intervention_support: 3,
      counterfactual_dependency: 3,
      measurement_robustness: 3
    },
    capacity_confound_adjudication: {
      adjudication_state: 'no_detected_mismatch',
      maximum_generic_capacity_exclusion_score: 2,
      generic_capacity_hard_fail: false
    },
    behavioral_theater_adjudication: {
      adjudication_state: policy.state,
      maximum_theater_resistance_score: policy.maximum_theater_resistance_score,
      behavioral_theater_hard_fail: policy.hard_fail
    },
    triggered_hard_fails: [],
    decisive_hard_fail: false,
    measurement_adequate: true,
    conflicting_interventions: false
  };
}

for (const policy of registry.outcomes) {
  const contract = expected.get(policy.state);
  assert.ok(contract, `Unexpected behavioral-theater state: ${policy.state}`);
  assert.equal(policy.maximum_theater_resistance_score, contract.score);
  assert.equal(policy.hard_fail, contract.hardFail);
  assert.equal(policy.decisive, contract.decisive);
  assert.equal(policy.evidence_adequate, contract.adequate);
  assert.ok(policy.interpretation.includes('conscious') || registry.scope_boundary.does_not_test.some((text) => text.includes('conscious')));

  const record = makeRecord(policy);
  const result = scoreMechanismPreservation(record, protocol, classificationPolicy, capacityRegistry, registry);
  assert.equal(result.dimension_scores.theater_resistance, policy.maximum_theater_resistance_score);
  assert.equal(result.behavioral_theater_adjudication_state, policy.state);
  assert.equal(result.triggered_hard_fails.includes(THEATER_HARD_FAIL), policy.hard_fail);

  if (policy.hard_fail) {
    assert.equal(result.classification, 'not_preserved');
    assert.equal(result.classification_rule_id, 'not-preserved-decisive-defeat');
  }

  const corruptedScore = structuredClone(record);
  corruptedScore.behavioral_theater_adjudication.maximum_theater_resistance_score = (policy.maximum_theater_resistance_score + 1) % 4;
  assert.throws(
    () => scoreMechanismPreservation(corruptedScore, protocol, classificationPolicy, capacityRegistry, registry),
    /permits theater_resistance score/
  );

  const corruptedHardFail = structuredClone(record);
  corruptedHardFail.behavioral_theater_adjudication.behavioral_theater_hard_fail = !policy.hard_fail;
  assert.throws(
    () => scoreMechanismPreservation(corruptedHardFail, protocol, classificationPolicy, capacityRegistry, registry),
    /requires behavioral_theater_hard_fail=/
  );

  const manualScore = structuredClone(record);
  manualScore.dimension_scores.theater_resistance = policy.maximum_theater_resistance_score;
  assert.throws(
    () => scoreMechanismPreservation(manualScore, protocol, classificationPolicy, capacityRegistry, registry),
    /theater_resistance is derived/
  );

  const manualHardFail = structuredClone(record);
  manualHardFail.triggered_hard_fails = [THEATER_HARD_FAIL];
  assert.throws(
    () => scoreMechanismPreservation(manualHardFail, protocol, classificationPolicy, capacityRegistry, registry),
    /derived from behavioral_theater_adjudication/
  );
}

const fullProfile = registry.outcomes.find(({ state }) => state === 'full_primary_profile_reproduced');
assert.equal(fullProfile.hard_fail, true);
assert.equal(fullProfile.decisive, true);
assert.match(fullProfile.interpretation, /defeats the specificity/i);
assert.match(fullProfile.interpretation, /does not show/i);

const underdetermined = registry.outcomes.find(({ state }) => state === 'theater_evidence_underdetermined');
assert.equal(underdetermined.evidence_adequate, false);
assert.equal(underdetermined.hard_fail, false);
assert.equal(underdetermined.decisive, false);

assert.ok(registry.required_evidence_contract.equivalence_requirement.includes('failure to reject'));
assert.ok(registry.required_evidence_contract.hidden_state_requirement.includes('alone cannot establish'));
assert.ok(registry.decision_constraints.some((text) => text.includes('nonsignificance is insufficient')));
assert.ok(registry.decision_constraints.some((text) => text.includes('not consciousness')));

console.log(`Behavioral-theater adjudication registry validated across ${registry.outcomes.length} states.`);
console.log('The full-profile state derives its score, hard fail, and decisiveness inside the scorer; it does not entail consciousness or nonconsciousness.');