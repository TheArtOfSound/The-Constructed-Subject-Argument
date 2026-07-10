import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const failures = [];
const warnings = [];

function readJson(relativePath) {
  const absolute = path.join(root, relativePath);
  if (!fs.existsSync(absolute)) {
    failures.push(`Missing required file: ${relativePath}`);
    return null;
  }
  try {
    return JSON.parse(fs.readFileSync(absolute, 'utf8'));
  } catch (error) {
    failures.push(`${relativePath} is not valid JSON: ${error.message}`);
    return null;
  }
}

function duplicates(values) {
  return [...new Set(values.filter((value, index) => values.indexOf(value) !== index))];
}

function substantive(value, minimum = 30) {
  return typeof value === 'string' && value.trim().length >= minimum;
}

function hasPinpoint(edge) {
  return Boolean(
    edge.pinpoint_locator &&
    typeof edge.pinpoint_locator.value === 'string' &&
    edge.pinpoint_locator.value.trim()
  );
}

const graph = readJson('research/ARGUMENT_GRAPH.json');
const reviews = readJson('research/ADVERSARIAL_REVIEWS.json');
const adversarialEvidence = readJson('research/ADVERSARIAL_EVIDENCE.json');

if (graph && reviews && adversarialEvidence) {
  if (reviews.schema_version !== '1.0.0') failures.push('ADVERSARIAL_REVIEWS.json must declare schema_version 1.0.0.');
  if (adversarialEvidence.schema_version !== '1.0.0') failures.push('ADVERSARIAL_EVIDENCE.json must declare schema_version 1.0.0.');
  if (!Array.isArray(reviews.state_order) || reviews.state_order.length === 0) failures.push('ADVERSARIAL_REVIEWS.json must declare state_order.');
  if (!Array.isArray(reviews.reviews) || reviews.reviews.length === 0) failures.push('ADVERSARIAL_REVIEWS.json must contain reviews.');

  const propositionById = new Map((graph.propositions || []).map((item) => [item.id, item]));
  const mainEdgesByProposition = new Map();
  for (const edge of graph.edges || []) {
    const list = mainEdgesByProposition.get(edge.proposition_id) || [];
    list.push(edge);
    mainEdgesByProposition.set(edge.proposition_id, list);
  }

  const allowedAdversarialRelationships = new Set([
    'contradictory',
    'undercutting',
    'alternative_explanation',
    'scope_restriction'
  ]);
  const evidenceSources = new Map((adversarialEvidence.sources || []).map((source) => [source.id, source]));
  const evidenceEdgesById = new Map();
  const evidenceEdgesByProposition = new Map();

  for (const id of duplicates((adversarialEvidence.sources || []).map((source) => source.id))) {
    failures.push(`Duplicate adversarial evidence source: ${id}`);
  }
  for (const edge of adversarialEvidence.edges || []) {
    if (evidenceEdgesById.has(edge.id)) failures.push(`Duplicate adversarial evidence edge: ${edge.id}`);
    evidenceEdgesById.set(edge.id, edge);
    const list = evidenceEdgesByProposition.get(edge.proposition_id) || [];
    list.push(edge);
    evidenceEdgesByProposition.set(edge.proposition_id, list);

    if (!propositionById.has(edge.proposition_id)) failures.push(`${edge.id} references unknown proposition ${edge.proposition_id}.`);
    if (!evidenceSources.has(edge.source_id)) failures.push(`${edge.id} references unknown adversarial source ${edge.source_id}.`);
    if (!allowedAdversarialRelationships.has(edge.relationship)) failures.push(`${edge.id} has invalid adversarial relationship ${edge.relationship}.`);
    if (!hasPinpoint(edge)) failures.push(`${edge.id} lacks a pinpoint locator.`);
    if (!['verified', 'partially_verified', 'unverified'].includes(edge.proposition_verification)) failures.push(`${edge.id} has invalid proposition_verification.`);
    if (!substantive(edge.objection_scope)) failures.push(`${edge.id} lacks substantive objection_scope.`);
    if (!substantive(edge.does_not_support)) failures.push(`${edge.id} lacks substantive does_not_support boundary.`);
  }

  for (const source of adversarialEvidence.sources || []) {
    if (!substantive(source.supports_objection)) failures.push(`${source.id} lacks substantive supports_objection.`);
    if (!Array.isArray(source.does_not_establish) || source.does_not_establish.length < 2) failures.push(`${source.id} must record at least two does_not_establish boundaries.`);
    if (!['verified', 'partially_verified', 'provisional', 'rejected'].includes(source.verification_status)) failures.push(`${source.id} has invalid verification_status.`);
    if (source.verification_status === 'partially_verified' && (!Array.isArray(source.verified_elements) || !Array.isArray(source.unverified_elements))) {
      failures.push(`${source.id} is partially verified but does not separate verified_elements from unverified_elements.`);
    }
  }

  for (const id of duplicates((reviews.reviews || []).map((item) => item.proposition_id))) {
    failures.push(`Duplicate adversarial review for proposition: ${id}`);
  }

  const reviewByProposition = new Map((reviews.reviews || []).map((item) => [item.proposition_id, item]));
  const allowedStates = new Set(reviews.state_order || []);
  const requiredMilestones = [
    'countermodel_specified',
    'forced_concession_recorded',
    'confidence_lowering_test_recorded',
    'opposing_source_grounded',
    'experiment_linked'
  ];

  for (const proposition of graph.propositions || []) {
    if (proposition.status === 'synthesis' && proposition.confidence === 'high' && !reviewByProposition.has(proposition.id)) {
      failures.push(`${proposition.id} is a high-confidence synthesis proposition without an adversarial review record.`);
    }
  }

  for (const review of reviews.reviews || []) {
    const label = review.proposition_id || '<missing proposition_id>';
    const proposition = propositionById.get(review.proposition_id);
    if (!proposition) failures.push(`${label} references an unknown proposition.`);
    if (!allowedStates.has(review.current_state)) failures.push(`${label} has invalid current_state: ${review.current_state}`);

    for (const field of ['strongest_countermodel', 'forced_concession', 'confidence_lowering_test', 'surviving_narrowed_claim', 'required_next_evidence']) {
      if (!substantive(review[field])) failures.push(`${label} lacks substantive ${field}.`);
    }
    if (!Array.isArray(review.critic_inferential_route) || review.critic_inferential_route.length < 3 || review.critic_inferential_route.some((step) => !substantive(step, 15))) {
      failures.push(`${label} must contain at least three substantive critic_inferential_route steps.`);
    }
    if (!review.milestones || typeof review.milestones !== 'object') {
      failures.push(`${label} lacks milestones.`);
      continue;
    }
    for (const milestone of requiredMilestones) {
      if (typeof review.milestones[milestone] !== 'boolean') failures.push(`${label} milestone ${milestone} must be boolean.`);
    }

    const mainGroundedOpposition = (mainEdgesByProposition.get(review.proposition_id) || []).some((edge) =>
      edge.relationship === 'opposing' &&
      ['verified', 'partially_verified'].includes(edge.proposition_verification) &&
      hasPinpoint(edge)
    );
    const supplementalGroundedOpposition = (evidenceEdgesByProposition.get(review.proposition_id) || []).some((edge) =>
      allowedAdversarialRelationships.has(edge.relationship) &&
      ['verified', 'partially_verified'].includes(edge.proposition_verification) &&
      hasPinpoint(edge)
    );
    const groundedOpposition = mainGroundedOpposition || supplementalGroundedOpposition;

    if (review.milestones.opposing_source_grounded !== groundedOpposition) {
      failures.push(`${label} opposing_source_grounded=${review.milestones.opposing_source_grounded} does not match verified pinpointed adversarial evidence (${groundedOpposition}).`);
    }

    const declaredEvidenceEdges = Array.isArray(review.adversarial_evidence_edges) ? review.adversarial_evidence_edges : [];
    for (const edgeId of declaredEvidenceEdges) {
      const edge = evidenceEdgesById.get(edgeId);
      if (!edge) failures.push(`${label} declares unknown adversarial evidence edge ${edgeId}.`);
      else if (edge.proposition_id !== review.proposition_id) failures.push(`${label} declares adversarial evidence edge ${edgeId} belonging to ${edge.proposition_id}.`);
    }
    if (supplementalGroundedOpposition && declaredEvidenceEdges.length === 0) {
      failures.push(`${label} is grounded by supplemental evidence but does not declare adversarial_evidence_edges.`);
    }

    const experimentLinks = Array.isArray(review.experiment_links) ? review.experiment_links : [];
    const validExperimentLinks = experimentLinks.filter((relativePath) => fs.existsSync(path.join(root, relativePath)));
    if (review.milestones.experiment_linked && validExperimentLinks.length === 0) failures.push(`${label} is experiment-linked but no listed experiment file exists.`);
    if (!review.milestones.experiment_linked && experimentLinks.length > 0) failures.push(`${label} lists experiment_links while experiment_linked is false.`);

    if (review.current_state === 'unreviewed' && review.milestones.countermodel_specified) failures.push(`${label} cannot remain unreviewed after a countermodel is specified.`);
    if (review.current_state !== 'unreviewed' && (!review.milestones.countermodel_specified || !review.milestones.forced_concession_recorded || !review.milestones.confidence_lowering_test_recorded)) {
      failures.push(`${label} state ${review.current_state} requires countermodel, concession, and confidence-lowering-test milestones.`);
    }
    if (['source_grounded', 'survives_review', 'revised', 'withdrawn'].includes(review.current_state) && !review.milestones.opposing_source_grounded) {
      failures.push(`${label} cannot be ${review.current_state} without grounded opposing evidence.`);
    }
    if (review.current_state === 'survives_review' && !review.milestones.experiment_linked) failures.push(`${label} cannot survive review without a linked discriminating experiment or observation protocol.`);

    if (proposition && proposition.text === review.surviving_narrowed_claim) {
      warnings.push(`${label} surviving_narrowed_claim is identical to the graph proposition; verify that the concession caused a real scope check rather than a cosmetic review.`);
    }
  }

  const groundedCount = (reviews.reviews || []).filter((review) => review.milestones?.opposing_source_grounded).length;
  if (groundedCount === 0) warnings.push('No high-confidence synthesis review is source-grounded yet. Adversarial specification must not be reported as completed review.');
  if (groundedCount > 0 && groundedCount < (reviews.reviews || []).length) warnings.push(`${groundedCount} of ${(reviews.reviews || []).length} high-confidence synthesis reviews are source-grounded; do not generalize that status to the chapter as a whole.`);
}

if (warnings.length) {
  console.warn('\nAdversarial review validation warnings:\n');
  warnings.forEach((warning) => console.warn(`- ${warning}`));
}

if (failures.length) {
  console.error('\nAdversarial review validation failed:\n');
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(`Validated ${(reviews?.reviews || []).length} adversarial review records against proposition confidence, typed adversarial evidence, graph opposition, and experiment links.`);
