import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const read = (relative) => fs.readFileSync(path.join(root, relative), 'utf8');
const fail = (message) => {
  console.error(`Classifier audit validation failed: ${message}`);
  process.exit(1);
};

const html = read('classifier-audit.html');
const css = read('assets/classifier-audit.css');
const js = read('assets/classifier-audit.js');
const chapters = read('chapters/index.html');
const report = JSON.parse(read('research/MECHANISM_PRESERVATION_CLASSIFICATION_MUTATION_REPORT.json'));

const requiredFiles = [
  'assets/classifier-audit.css',
  'assets/classifier-audit.js',
  'research/MECHANISM_PRESERVATION_CLASSIFICATION_MUTATION_REPORT.json'
];
for (const relative of requiredFiles) {
  if (!fs.existsSync(path.join(root, relative))) fail(`missing ${relative}`);
}

const requiredHtml = [
  'SYNTHETIC FIXTURES — SOFTWARE AUDIT ONLY',
  'does not test whether any actual AI system is conscious',
  'It does not prove that the original threshold or ontology is scientifically correct',
  'id="mutationList"',
  'id="mutationDetail"',
  'data-filter="threshold"',
  'data-filter="priority"',
  'data-filter="connective"',
  'data-filter="fallback"',
  'research/MECHANISM_PRESERVATION_CLASSIFICATION_POLICY.json',
  'research/MECHANISM_PRESERVATION_CLASSIFICATION_POLICY_MUTATIONS.json'
];
for (const fragment of requiredHtml) {
  if (!html.includes(fragment)) fail(`public page missing required fragment: ${fragment}`);
}

if (!chapters.includes('../classifier-audit.html')) fail('chapter map does not expose the classifier audit');
if (!chapters.includes('uses synthetic fixtures and does not concern the consciousness of any actual AI system')) fail('chapter map omits the synthetic-system boundary');

if (!js.includes("const REPORT_PATH = 'research/MECHANISM_PRESERVATION_CLASSIFICATION_MUTATION_REPORT.json'")) fail('client does not load the canonical report');
if (!js.includes('weighted score') || !js.includes('Evidence held fixed')) fail('client does not expose weighted-score invariance');
if (!js.includes('does not establish that the unmutated policy is scientifically optimal')) fail('client omits normative-truth limitation');
if (!js.includes("activeFilter === 'all' || categoryFor(result) === activeFilter")) fail('client mutation filters are not connected');

if (!css.includes('.audit-warning') || !css.includes('.comparison') || !css.includes('.mutation-detail')) fail('audit presentation primitives are incomplete');

if (report.status !== 'generated_synthetic_mutation_analysis') fail('canonical report is not marked generated synthetic analysis');
if (report.summary.mutation_count !== report.results.length) fail('report mutation count does not match results');
if (report.summary.survived_count > 0 && !html.includes('Survived')) fail('public page cannot surface surviving mutations');
if (!report.epistemic_boundary.includes('actual AI system')) fail('canonical report lacks actual-system boundary');
if (!report.epistemic_boundary.includes('consciousness')) fail('canonical report lacks consciousness boundary');

const categories = new Set(report.results.map((result) => {
  if (result.target.operation === 'replace_priority') return result.mutation_id.includes('fallback') ? 'fallback' : 'priority';
  if (result.target.operation === 'replace_rule_match' || result.target.to === 'all_true' || result.target.to === 'any_true') return 'connective';
  return 'threshold';
}));
for (const expected of ['threshold', 'priority', 'connective', 'fallback']) {
  if (!categories.has(expected)) fail(`canonical report has no mutation in public category ${expected}`);
}

console.log(`Classifier audit page validated against ${report.results.length} registered synthetic mutations.`);
