#!/usr/bin/env node
import assert from 'node:assert/strict';
import {
  loadCapacityAdjudicationRules,
  loadClassificationPolicy,
  loadProtocol,
  resolveCapacityAdjudication,
  scoreMechanismPreservation
} from './score-mechanism-preservation.mjs';

try {
  const protocol = loadProtocol();
  const classificationPolicy = loadClassificationPolicy();
  const registry = loadCapacityAdjudicationRules();

  assert.equal(registry.schema_version, '1.1.0');
  assert.equal(registry.protocol_id, protocol.protocol_id);
  assert.equal(registry.outcomes.length, 5, 'Capacity registry must define exactly five adjudication states.');

  const states = new Map();
  for (const outcome of registry.outcomes) {
    assert.ok(outcome.state && !states.has(outcome.state), `Capacity state must be unique: ${outcome.state}.`);
    assert.equal(typeof outcome.matching_adequate, 'boolean', `${outcome.state} must declare matching_adequate.`);
    assert.equal(typeof outcome.hard_fail, 'boolean', `${outcome.state} must declare hard_fail.`);
    assert.ok(Number.isInteger(outcome.maximum_generic_capacity_exclusion_score));
    assert.ok(outcome.maximum_generic_capacity_exclusion_score >= 0 && outcome.maximum_generic_capacity_exclusion_score <= 3);
    states.set(outcome.state, outcome);
  }

  assert.equal(states.get('no_detected_mismatch').matching_adequate, true);
  assert.equal(states.get('mismatch_nonexplanatory').matching_adequate, true);
  assert.equal(states.get('mismatch_partially_explanatory').matching_adequate, false);
  assert.equal(states.get('mismatch_sufficiently_explanatory').hard_fail, true);
  assert.equal(states.get('explanatory_role_underdetermined').matching_adequate, false);

  const edgeIds = new Set();
  assert.ok(Array.isArray(registry.repair_edges) && registry.repair_edges.length > 0);
  for (const edge of registry.repair_edges) {
    assert.ok(edge.edge_id && !edgeIds.has(edge.edge_id), `Repair edge must be uniquely identified: ${edge.edge_id}.`);
    assert.ok(states.has(edge.from), `Repair edge ${edge.edge_id} has unknown source state.`);
    assert.ok(states.has(edge.to), `Repair edge ${edge.edge_id} has unknown target state.`);
    assert.notEqual(edge.from, edge.to, `Repair edge ${edge.edge_id} must change state.`);
    assert.ok(edge.epistemic_direction, `Repair edge ${edge.edge_id} must declare epistemic_direction.`);
    edgeIds.add(edge.edge_id);
  }

  const baseScores = {
    mapping_specificity: 3,
    selective_intervention_support: 3,
    counterfactual_dependency: 3,
    theater_resistance: 3,
    measurement_robustness: 3
  };

  for (const outcome of registry.outcomes) {
    const adjudication = {
      adjudication_state: outcome.state,
      maximum_generic_capacity_exclusion_score: outcome.maximum_generic_capacity_exclusion_score,
      generic_capacity_hard_fail: outcome.hard_fail
    };
    const record = {
      protocol_id: protocol.protocol_id,
      run_id: `REGISTRY-AUTHORITY-${outcome.state}`,
      theory_family: 'synthetic-registry-authority-test',
      implementation_level: 'classifier-contract',
      dimension_scores: baseScores,
      capacity_confound_adjudication: adjudication,
      triggered_hard_fails: [],
      decisive_hard_fail: false,
      measurement_adequate: true,
      conflicting_interventions: false
    };

    const resolved = resolveCapacityAdjudication(record, registry);
    assert.equal(resolved.policy, outcome, 'Scorer must resolve the exact registry outcome object.');
    const result = scoreMechanismPreservation(record, protocol, classificationPolicy, registry);
    assert.equal(result.dimension_scores.generic_capacity_exclusion, outcome.maximum_generic_capacity_exclusion_score);
    assert.equal(result.triggered_hard_fails.includes('generic_capacity_control_explains_primary_effect'), outcome.hard_fail);

    const corruptedScore = structuredClone(record);
    corruptedScore.capacity_confound_adjudication.maximum_generic_capacity_exclusion_score = (outcome.maximum_generic_capacity_exclusion_score + 1) % 4;
    assert.throws(() => scoreMechanismPreservation(corruptedScore, protocol, classificationPolicy, registry), /permits generic_capacity_exclusion score/);

    const corruptedHardFail = structuredClone(record);
    corruptedHardFail.capacity_confound_adjudication.generic_capacity_hard_fail = !outcome.hard_fail;
    assert.throws(() => scoreMechanismPreservation(corruptedHardFail, protocol, classificationPolicy, registry), /requires generic_capacity_hard_fail/);
  }

  assert.match(registry.epistemic_boundary, /do not establish mechanism preservation/i);
  assert.match(registry.epistemic_boundary, /consciousness, nonconsciousness/i);
  console.log(`Capacity adjudication registry authority passed: ${states.size} states and ${edgeIds.size} registry-owned repair edges.`);
} catch (error) {
  console.error(`Capacity adjudication registry authority validation failed: ${error.message}`);
  process.exit(1);
}
