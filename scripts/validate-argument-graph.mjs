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

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function duplicates(values) {
  return [...new Set(values.filter((value, index) => values.indexOf(value) !== index))];
}

const graph = readJson('research/ARGUMENT_GRAPH.json');
const registry = readJson('research/SOURCE_REGISTRY.json');
const claimsPath = 'research/CLAIMS_LEDGER.md';
const claimsSource = fs.existsSync(path.join(root, claimsPath)) ? read(claimsPath) : '';
if (!claimsSource) failures.push(`Missing required file: ${claimsPath}`);

if (graph && registry && claimsSource) {
  if (graph.schema_version !== '1.0.0') failures.push('ARGUMENT_GRAPH.json must declare schema_version 1.0.0.');
  if (!Array.isArray(graph.propositions) || graph.propositions.length === 0) failures.push('ARGUMENT_GRAPH.json must contain propositions.');
  if (!Array.isArray(graph.edges) || graph.edges.length === 0) failures.push('ARGUMENT_GRAPH.json must contain typed edges.');
  if (!Array.isArray(graph.dependency_declarations)) failures.push('ARGUMENT_GRAPH.json must contain dependency_declarations.');

  const registeredClaimIds = new Set(
    [...claimsSource.matchAll(/^###\s+(CSA-(?:R)?\d+)\s*$/gm)].map((match) => match[1])
  );
  const sourceById = new Map((registry.sources || []).map((source) => [source.id, source]));
  const propositionById = new Map((graph.propositions || []).map((proposition) => [proposition.id, proposition]));

  for (const id of duplicates((graph.propositions || []).map((item) => item.id))) failures.push(`Duplicate proposition ID: ${id}`);
  for (const id of duplicates((graph.edges || []).map((item) => item.id))) failures.push(`Duplicate edge ID: ${id}`);
  for (const id of duplicates((graph.dependency_declarations || []).map((item) => item.id))) failures.push(`Duplicate dependency ID: ${id}`);

  const allowedRelationships = new Set(['direct', 'inferential', 'contextual', 'opposing', 'boundary']);
  const allowedPropositionStatuses = new Set(['established_background', 'contested_background', 'synthesis', 'proposed_contribution', 'speculation', 'rejected']);
  const allowedConfidence = new Set(['low', 'moderate', 'high']);
  const allowedVerification = new Set(['verified', 'partially_verified', 'unverified', 'provisional', 'rejected']);

  for (const proposition of graph.propositions || []) {
    const label = proposition.id || '<missing proposition id>';
    for (const field of ['id', 'text', 'ledger_claims', 'status', 'confidence', 'falsifier_or_revision_trigger']) {
      if (proposition[field] === undefined || proposition[field] === null) failures.push(`${label} is missing required field: ${field}`);
    }
    if (!/^C\d+-P\d{2}$/.test(proposition.id || '')) failures.push(`${label} has invalid proposition ID format.`);
    if (!Array.isArray(proposition.ledger_claims) || proposition.ledger_claims.length === 0) failures.push(`${label} must map to at least one claims-ledger ID.`);
    for (const claimId of proposition.ledger_claims || []) {
      if (!registeredClaimIds.has(claimId)) failures.push(`${label} references unknown claim ID: ${claimId}`);
    }
    if (!allowedPropositionStatuses.has(proposition.status)) failures.push(`${label} has invalid status: ${proposition.status}`);
    if (!allowedConfidence.has(proposition.confidence)) failures.push(`${label} has invalid confidence: ${proposition.confidence}`);
    if (typeof proposition.falsifier_or_revision_trigger !== 'string' || proposition.falsifier_or_revision_trigger.trim().length < 20) {
      failures.push(`${label} lacks a substantive falsifier or revision trigger.`);
    }
  }

  const edgeCountByProposition = new Map();
  const opposingCountByProposition = new Map();

  for (const edge of graph.edges || []) {
    const label = edge.id || '<missing edge id>';
    for (const field of ['id', 'proposition_id', 'source_id', 'relationship', 'support_scope', 'does_not_support', 'pinpoint_locator', 'proposition_verification']) {
      if (edge[field] === undefined) failures.push(`${label} is missing required field: ${field}`);
    }
    if (!/^EDGE-[A-Z0-9-]+$/.test(edge.id || '')) failures.push(`${label} has invalid edge ID format.`);
    if (!propositionById.has(edge.proposition_id)) failures.push(`${label} references unknown proposition: ${edge.proposition_id}`);
    if (!sourceById.has(edge.source_id)) failures.push(`${label} references unknown source: ${edge.source_id}`);
    if (!allowedRelationships.has(edge.relationship)) failures.push(`${label} has invalid relationship: ${edge.relationship}`);
    if (!allowedVerification.has(edge.proposition_verification)) failures.push(`${label} has invalid proposition_verification: ${edge.proposition_verification}`);
    if (typeof edge.support_scope !== 'string' || edge.support_scope.trim().length < 20) failures.push(`${label} lacks a substantive support_scope.`);
    if (typeof edge.does_not_support !== 'string' || edge.does_not_support.trim().length < 20) failures.push(`${label} lacks a substantive does_not_support boundary.`);

    edgeCountByProposition.set(edge.proposition_id, (edgeCountByProposition.get(edge.proposition_id) || 0) + 1);
    if (edge.relationship === 'opposing') opposingCountByProposition.set(edge.proposition_id, (opposingCountByProposition.get(edge.proposition_id) || 0) + 1);

    const source = sourceById.get(edge.source_id);
    if (source?.verification_status === 'provisional' && edge.decisive !== false) {
      failures.push(`${label} uses provisional source ${edge.source_id} without decisive:false.`);
    }
    if (edge.relationship === 'direct' && edge.proposition_verification === 'verified' && !edge.pinpoint_locator) {
      failures.push(`${label} is marked proposition-verified direct support without a pinpoint locator.`);
    }
    if (edge.pinpoint_locator === null) warnings.push(`${label} lacks a pinpoint locator.`);
  }

  for (const proposition of graph.propositions || []) {
    if (!edgeCountByProposition.has(proposition.id)) failures.push(`${proposition.id} has no evidential edges.`);
    if (!opposingCountByProposition.has(proposition.id)) warnings.push(`${proposition.id} has no explicit opposing edge.`);
  }

  for (const dependency of graph.dependency_declarations || []) {
    const label = dependency.id || '<missing dependency id>';
    if (!/^DEP-[A-Z0-9-]+$/.test(dependency.id || '')) failures.push(`${label} has invalid dependency ID format.`);
    if (!Array.isArray(dependency.members) || dependency.members.length < 2) failures.push(`${label} must contain at least two potentially dependent indicators.`);
    if (typeof dependency.risk !== 'string' || dependency.risk.trim().length < 20) failures.push(`${label} lacks a substantive double-counting risk.`);
    if (typeof dependency.default_treatment !== 'string' || !dependency.default_treatment.trim()) failures.push(`${label} lacks a default treatment.`);
  }

  const provisionalEdges = (graph.edges || []).filter((edge) => edge.proposition_verification === 'provisional').length;
  const verifiedEdges = (graph.edges || []).filter((edge) => edge.proposition_verification === 'verified').length;
  if (provisionalEdges > 0) warnings.push(`${provisionalEdges} edge(s) remain proposition-provisional.`);
  if (verifiedEdges === 0) warnings.push('No argument-graph edge is proposition-verified yet; metadata verification must not be confused with proposition verification.');
}

if (warnings.length) {
  console.warn('\nArgument graph validation warnings:\n');
  warnings.forEach((warning) => console.warn(`- ${warning}`));
}

if (failures.length) {
  console.error('\nArgument graph validation failed:\n');
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(`Validated ${(graph?.propositions || []).length} propositions, ${(graph?.edges || []).length} typed edges, and ${(graph?.dependency_declarations || []).length} dependency declarations.`);
