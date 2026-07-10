import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const failures = [];

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function parse(relativePath) {
  try {
    return JSON.parse(read(relativePath));
  } catch (error) {
    failures.push(`${relativePath} is not valid JSON: ${error.message}`);
    return null;
  }
}

const required = [
  'assets/reader-v2.js',
  'assets/reader-v2.css',
  'research/ADVERSARIAL_REVIEWS.json',
  'research/ADVERSARIAL_EVIDENCE.json',
  'research/MECHANISM_PRESERVATION_PROTOCOL.json'
];

for (const file of required) {
  if (!fs.existsSync(path.join(root, file))) failures.push(`Missing public-review dependency: ${file}`);
}

if (failures.length === 0) {
  const reader = read('assets/reader-v2.js');
  const styles = read('assets/reader-v2.css');
  const reviewsPayload = parse('research/ADVERSARIAL_REVIEWS.json');
  const evidencePayload = parse('research/ADVERSARIAL_EVIDENCE.json');
  const protocolPayload = parse('research/MECHANISM_PRESERVATION_PROTOCOL.json');

  for (const dependency of [
    '../research/ADVERSARIAL_REVIEWS.json',
    '../research/ADVERSARIAL_EVIDENCE.json',
    '../research/MECHANISM_PRESERVATION_PROTOCOL.json'
  ]) {
    if (!reader.includes(`fetch('${dependency}')`)) failures.push(`Reader does not fetch ${dependency}.`);
  }

  if (!reader.includes("chapterId === '06'")) failures.push('Adversarial review panel is not scoped to Chapter 6.');
  if (!reader.includes('Strongest live countermodel')) failures.push('Public review omits the strongest countermodel.');
  if (!reader.includes('Concession forced by the objection')) failures.push('Public review omits forced concessions.');
  if (!reader.includes('What would lower confidence?')) failures.push('Public review omits confidence-lowering tests.');
  if (!reader.includes('Does not establish:')) failures.push('Public review omits source-scope boundaries.');
  if (!reader.includes('It does not determine phenomenal consciousness, sentience, personhood, or moral status.')) {
    failures.push('Public review omits the mechanism-versus-consciousness boundary.');
  }

  for (const className of ['adversarial-review-panel', 'adversarial-card', 'review-state', 'review-evidence', 'missing-evidence']) {
    if (!styles.includes(`.${className}`)) failures.push(`Reader stylesheet is missing .${className}.`);
  }

  if (reviewsPayload && evidencePayload && protocolPayload) {
    const reviews = reviewsPayload.reviews || [];
    const edges = evidencePayload.edges || [];
    const sourceIds = new Set((evidencePayload.sources || []).map((source) => source.id));
    const survived = reviews.filter((review) => review.current_state === 'survives_review').length;

    if (reviews.length === 0) failures.push('Public review has no review records to render.');
    if (!protocolPayload.epistemic_boundary?.tests) failures.push('Mechanism protocol lacks a public epistemic boundary.');

    for (const review of reviews) {
      for (const field of ['proposition_id', 'current_state', 'strongest_countermodel', 'forced_concession', 'confidence_lowering_test', 'surviving_narrowed_claim', 'required_next_evidence']) {
        if (!review[field]) failures.push(`${review.proposition_id || '<unknown review>'} lacks public field: ${field}`);
      }
      if (!Array.isArray(review.critic_inferential_route) || review.critic_inferential_route.length < 2) {
        failures.push(`${review.proposition_id || '<unknown review>'} lacks a substantive public critic route.`);
      }
      for (const edgeId of review.adversarial_evidence_edges || []) {
        const edge = edges.find((candidate) => candidate.id === edgeId);
        if (!edge) failures.push(`${review.proposition_id} exposes unknown adversarial edge ${edgeId}.`);
        else if (!sourceIds.has(edge.source_id)) failures.push(`${edgeId} exposes unknown source ${edge.source_id}.`);
      }
    }

    const displayedSurvived = reader.match(/<strong>(\d+)<\/strong> survived experimental review/);
    if (!displayedSurvived) failures.push('Reader does not expose an experimental-review completion count.');
    else if (Number(displayedSurvived[1]) !== survived) {
      failures.push(`Reader displays ${displayedSurvived[1]} survived reviews, but the ledger contains ${survived}.`);
    }
  }
}

if (failures.length) {
  console.error('\nPublic adversarial review validation failed:\n');
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log('Validated Chapter 6 public adversarial review wiring, evidence scope, and displayed review state.');