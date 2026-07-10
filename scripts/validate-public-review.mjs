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

function headingAnchors(markdown) {
  const used = new Set();
  const anchors = new Map();
  for (const line of markdown.replace(/\r/g, '').split('\n')) {
    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (!heading) continue;
    const text = heading[2].replace(/\*\*/g, '').trim();
    let slug = text.toLowerCase().replace(/[^a-z0-9\s-]/g, '').trim().replace(/\s+/g, '-').slice(0, 70) || 'section';
    const base = slug;
    let n = 2;
    while (used.has(slug)) slug = `${base}-${n++}`;
    used.add(slug);
    anchors.set(slug, text);
  }
  return anchors;
}

const required = [
  'assets/reader-v2.js',
  'assets/reader-v2.css',
  'book/06-where-could-subjectivity-be.md',
  'research/ADVERSARIAL_REVIEWS.json',
  'research/ADVERSARIAL_EVIDENCE.json',
  'research/MECHANISM_PRESERVATION_PROTOCOL.json',
  'research/MANUSCRIPT_PROPOSITION_LINKS.json'
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
  const linksPayload = parse('research/MANUSCRIPT_PROPOSITION_LINKS.json');
  const anchors = headingAnchors(read('book/06-where-could-subjectivity-be.md'));

  for (const dependency of [
    '../research/ADVERSARIAL_REVIEWS.json',
    '../research/ADVERSARIAL_EVIDENCE.json',
    '../research/MECHANISM_PRESERVATION_PROTOCOL.json',
    '../research/MANUSCRIPT_PROPOSITION_LINKS.json'
  ]) {
    if (!reader.includes(`fetch('${dependency}')`)) failures.push(`Reader does not fetch ${dependency}.`);
  }

  if (!reader.includes("chapterId === '06'")) failures.push('Adversarial review panel is not scoped to Chapter 6.');
  if (!reader.includes('Strongest live countermodel')) failures.push('Public review omits the strongest countermodel.');
  if (!reader.includes('Concession forced by the objection')) failures.push('Public review omits forced concessions.');
  if (!reader.includes('What would lower confidence?')) failures.push('Public review omits confidence-lowering tests.');
  if (!reader.includes('Does not establish:')) failures.push('Public review omits source-scope boundaries.');
  if (!reader.includes('Read the claim in the chapter')) failures.push('Public review omits manuscript trace links.');
  if (!reader.includes("text: 'Adversarial review — live research state'")) failures.push('Chapter 6 table of contents omits the live review panel.');
  if (!reader.includes("reviews.filter((review) => review.current_state === 'survives_review').length")) {
    failures.push('Experimental-review total is not derived from the review ledger at runtime.');
  }
  if (!reader.includes('It does not determine phenomenal consciousness, sentience, personhood, or moral status.')) {
    failures.push('Public review omits the mechanism-versus-consciousness boundary.');
  }

  for (const className of ['adversarial-review-panel', 'adversarial-card', 'review-state', 'review-evidence', 'missing-evidence']) {
    if (!styles.includes(`.${className}`)) failures.push(`Reader stylesheet is missing .${className}.`);
  }

  if (reviewsPayload && evidencePayload && protocolPayload && linksPayload) {
    const reviews = reviewsPayload.reviews || [];
    const edges = evidencePayload.edges || [];
    const links = linksPayload.links || [];
    const sourceIds = new Set((evidencePayload.sources || []).map((source) => source.id));
    const reviewIds = new Set(reviews.map((review) => review.proposition_id));

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

      const matchingLinks = links.filter((link) => link.proposition_id === review.proposition_id && link.chapter_id === '06');
      if (matchingLinks.length !== 1) failures.push(`${review.proposition_id} must have exactly one Chapter 6 manuscript link; found ${matchingLinks.length}.`);
    }

    for (const link of links) {
      if (!reviewIds.has(link.proposition_id)) failures.push(`Manuscript link references unknown review ${link.proposition_id}.`);
      if (link.chapter_id !== '06') failures.push(`${link.proposition_id} public review link targets unsupported chapter ${link.chapter_id}.`);
      if (link.relation !== 'primary_argument') failures.push(`${link.proposition_id} manuscript link must be primary_argument.`);
      if (!link.rationale || link.rationale.length < 40) failures.push(`${link.proposition_id} manuscript link lacks a substantive rationale.`);
      const resolvedHeading = anchors.get(link.anchor);
      if (!resolvedHeading) failures.push(`${link.proposition_id} manuscript anchor does not resolve: #${link.anchor}`);
      else if (resolvedHeading !== link.heading) failures.push(`${link.proposition_id} heading mismatch: registry says "${link.heading}" but anchor resolves to "${resolvedHeading}".`);
    }
  }
}

if (failures.length) {
  console.error('\nPublic adversarial review validation failed:\n');
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log('Validated Chapter 6 public review wiring, source scope, derived status totals, and manuscript proposition traceability.');
