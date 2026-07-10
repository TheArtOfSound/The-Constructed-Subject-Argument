import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const protocolFile = path.join(root, 'research/MECHANISM_PRESERVATION_PROTOCOL.json');
const reviewFile = path.join(root, 'research/ADVERSARIAL_REVIEWS.json');
let failures = 0;

function fail(message) {
  failures += 1;
  console.error(`Mechanism protocol validation failed: ${message}`);
}

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (error) {
    fail(`${path.relative(root, file)} is not valid JSON: ${error.message}`);
    return null;
  }
}

const protocol = readJson(protocolFile);
const reviewData = readJson(reviewFile);
if (!protocol || !reviewData) process.exit(1);

const required = [
  'schema_version', 'protocol_id', 'status', 'epistemic_boundary',
  'required_preregistration_fields', 'system_roles', 'behavioral_equivalence',
  'mechanism_graph_schema', 'candidate_mapping_schema', 'intervention_families',
  'scoring', 'analysis_requirements', 'interpretation_contract', 'review_link'
];
for (const key of required) if (!(key in protocol)) fail(`missing ${key}`);

if (protocol.protocol_id !== 'EXP-11-MECHANISM-PRESERVATION') fail('unexpected protocol_id');
if (['completed', 'validated'].includes(protocol.status)) fail('unexecuted protocol has a completion status');

const prereg = new Set(protocol.required_preregistration_fields || []);
for (const key of ['theory_family', 'implementation_level', 'mechanism_graph', 'candidate_mapping', 'behavioral_matching_plan', 'intervention_plan', 'strongest_nonconscious_rival', 'confidence_lowering_result', 'forbidden_conclusions']) {
  if (!prereg.has(key)) fail(`missing preregistration field ${key}`);
}

const roles = new Map((protocol.system_roles || []).map((item) => [item.id, item.role]));
const expectedRoles = {
  A: 'claimed_mechanism',
  B: 'behavioral_theater_control',
  C: 'generic_capacity_control',
  D: 'lesioned_mechanism'
};
for (const [id, role] of Object.entries(expectedRoles)) {
  if (roles.get(id) !== role) fail(`system ${id} must have role ${role}`);
}

const matching = protocol.behavioral_equivalence || {};
if (!Array.isArray(matching.required_metrics) || matching.required_metrics.length < 8) fail('matching battery is too narrow');
if (!(matching.default_standardized_difference_limit > 0 && matching.default_standardized_difference_limit <= 0.25)) fail('matching tolerance is outside the allowed range');

const interventionIds = new Set((protocol.intervention_families || []).map((item) => item.id));
for (const id of ['selective_lesion', 'component_substitution', 'causal_mediation', 'state_patching', 'dependency_reversal', 'out_of_distribution_transfer']) {
  if (!interventionIds.has(id)) fail(`missing intervention ${id}`);
}
for (const item of protocol.intervention_families || []) {
  if (!Array.isArray(item.minimum_controls) || item.minimum_controls.length < 2) fail(`${item.id} needs at least two controls`);
}

const dimensions = protocol.scoring?.dimensions || [];
const dimensionIds = new Set(dimensions.map((item) => item.id));
for (const id of ['mapping_specificity', 'selective_intervention_support', 'counterfactual_dependency', 'theater_resistance', 'generic_capacity_exclusion', 'measurement_robustness']) {
  if (!dimensionIds.has(id)) fail(`missing scoring dimension ${id}`);
}
const weight = dimensions.reduce((sum, item) => sum + Number(item.weight || 0), 0);
if (Math.abs(weight - 1) > 1e-9) fail(`weights sum to ${weight}, not 1`);
for (const item of dimensions) {
  for (const level of ['0', '1', '2', '3']) {
    if (typeof item.score_definition?.[level] !== 'string' || item.score_definition[level].length < 12) fail(`${item.id} has an incomplete level ${level}`);
  }
}

if ((protocol.scoring?.hard_fail_conditions || []).length < 5) fail('too few hard-fail conditions');
const outcomes = new Set((protocol.scoring?.classification_rules || []).map((item) => item.outcome));
for (const outcome of ['preserved', 'partially_preserved', 'not_preserved', 'underdetermined']) {
  if (!outcomes.has(outcome)) fail(`missing outcome ${outcome}`);
}

if (protocol.review_link?.proposition_id !== 'C6-P03') fail('protocol must link to C6-P03');
if (protocol.review_link?.experiment_result_required_for_survives_review !== true) fail('review survival must require experimental results');

const reviews = Array.isArray(reviewData) ? reviewData : reviewData.reviews;
if (!Array.isArray(reviews)) {
  fail('review data has no review array');
} else {
  const review = reviews.find((item) => item.proposition_id === 'C6-P03');
  if (!review) fail('C6-P03 review is missing');
  else {
    const links = JSON.stringify(review.experiment_links || review.linked_experiments || []);
    if (!links.includes('EXPERIMENT_11_MECHANISM_PRESERVATION.md')) fail('C6-P03 does not link to Experiment 11');
    const state = review.state || review.review_state;
    if (state === 'survives_review') fail('C6-P03 is marked as surviving before results exist');
  }
}

if (failures) process.exit(1);
console.log(`Mechanism protocol valid: ${dimensions.length} dimensions, ${outcomes.size} outcomes, ${interventionIds.size} interventions.`);
