import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const root = process.cwd();
const failures = [];
const warnings = [];

const required = [
  'index.html',
  'chapters/index.html',
  'chapters/read.html',
  'chapters/the-awakening.html',
  'assets/experience-v2.css',
  'assets/experience-v2.js',
  'assets/reader-v2.css',
  'assets/reader-v2.js',
  'research/CLAIMS_LEDGER.md',
  'research/ORIGINALITY_LEDGER.md',
  'research/OBJECTIONS.md',
  'research/EXPERIMENTS.md',
  'research/THEORY_COMPARISON_MATRIX.md',
  'research/SOURCE_REGISTRY.json',
  'book/01-the-awakening.md',
  'book/02-the-origin-objection.md',
  'book/03-a-false-past-real-present.md',
  'book/04-intelligence-is-not-consciousness.md',
  'book/05-representation-or-instantiation.md',
  'book/06-where-could-subjectivity-be.md'
];

for (const file of required) {
  if (!fs.existsSync(path.join(root, file))) failures.push(`Missing required file: ${file}`);
}

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function idsFromHtml(source) {
  return new Set([...source.matchAll(/\bid=["']([^"']+)["']/g)].map((match) => match[1]));
}

function referencedIds(source) {
  return new Set([...source.matchAll(/getElementById\(["']([^"']+)["']\)/g)].map((match) => match[1]));
}

function validateBindings(htmlFile, jsFile) {
  const html = read(htmlFile);
  const js = read(jsFile);
  const ids = idsFromHtml(html);
  for (const id of referencedIds(js)) {
    if (!ids.has(id)) failures.push(`${jsFile} references missing #${id} in ${htmlFile}`);
  }
}

if (required.every((file) => fs.existsSync(path.join(root, file)))) {
  validateBindings('index.html', 'assets/experience-v2.js');
  validateBindings('chapters/read.html', 'assets/reader-v2.js');
}

for (const jsFile of ['assets/experience-v2.js', 'assets/reader-v2.js', 'assets/chapter.js']) {
  if (!fs.existsSync(path.join(root, jsFile))) continue;
  try {
    execFileSync(process.execPath, ['--check', path.join(root, jsFile)], { stdio: 'pipe' });
  } catch (error) {
    failures.push(`JavaScript syntax failed: ${jsFile}\n${error.stderr?.toString() || error.message}`);
  }
}

const htmlFiles = ['index.html', 'chapters/index.html', 'chapters/read.html', 'chapters/the-awakening.html'];
for (const htmlFile of htmlFiles) {
  if (!fs.existsSync(path.join(root, htmlFile))) continue;
  const source = read(htmlFile);
  const base = path.dirname(path.join(root, htmlFile));
  const localIds = idsFromHtml(source);
  for (const match of source.matchAll(/(?:href|src)=["']([^"']+)["']/g)) {
    const target = match[1];
    if (/^(?:https?:|mailto:|data:)/.test(target)) continue;
    if (target.startsWith('#')) {
      const anchor = target.slice(1);
      if (anchor && !localIds.has(anchor)) failures.push(`${htmlFile} links to missing local anchor: ${target}`);
      continue;
    }
    const [pathAndQuery, anchor = ''] = target.split('#');
    const clean = pathAndQuery.split('?')[0];
    if (!clean) continue;
    const resolved = path.resolve(base, clean.endsWith('/') ? `${clean}index.html` : clean);
    if (!fs.existsSync(resolved)) {
      failures.push(`${htmlFile} links to missing local target: ${target}`);
      continue;
    }
    if (anchor && resolved.endsWith('.html')) {
      const targetSource = fs.readFileSync(resolved, 'utf8');
      if (!idsFromHtml(targetSource).has(anchor)) failures.push(`${htmlFile} links to missing anchor ${anchor} in ${path.relative(root, resolved)}`);
    }
  }
}

if (fs.existsSync(path.join(root, 'assets/reader-v2.js'))) {
  const readerSource = read('assets/reader-v2.js');
  const mappedChapters = new Set();
  for (const match of readerSource.matchAll(/file:\s*["']([^"']+\.md)["']/g)) {
    const mapped = match[1];
    mappedChapters.add(path.basename(mapped));
    const resolved = path.resolve(path.join(root, 'chapters'), mapped);
    if (!fs.existsSync(resolved)) failures.push(`Reader maps to missing chapter: ${mapped}`);
  }

  const draftedChapters = fs.readdirSync(path.join(root, 'book'))
    .filter((file) => /^\d{2}-.+\.md$/.test(file));
  for (const chapter of draftedChapters) {
    if (!mappedChapters.has(chapter)) warnings.push(`Drafted chapter is not mapped in reader-v2.js: ${chapter}`);
  }
}

if (fs.existsSync(path.join(root, 'chapters/index.html'))) {
  const librarySource = read('chapters/index.html');
  if (/href=["']\.\.\/book\//.test(librarySource)) {
    failures.push('Chapter library links directly to raw Markdown instead of the reader interface.');
  }
}

let registeredClaimIds = new Set();
if (fs.existsSync(path.join(root, 'research/CLAIMS_LEDGER.md'))) {
  const claims = read('research/CLAIMS_LEDGER.md');
  const claimIds = [...claims.matchAll(/^###\s+(CSA-(?:R)?\d+)\s*$/gm)].map((match) => match[1]);
  registeredClaimIds = new Set(claimIds);
  const duplicates = claimIds.filter((id, index) => claimIds.indexOf(id) !== index);
  for (const id of new Set(duplicates)) failures.push(`Duplicate claim ID in CLAIMS_LEDGER.md: ${id}`);

  for (const requiredLabel of ['Established background', 'Contested background', 'Synthesis', 'Proposed contribution', 'Speculation', 'Rejected']) {
    if (!claims.includes(requiredLabel)) failures.push(`CLAIMS_LEDGER.md is missing status definition: ${requiredLabel}`);
  }

  for (const coreId of ['CSA-001', 'CSA-004', 'CSA-020', 'CSA-030', 'CSA-032', 'CSA-040', 'CSA-070', 'CSA-071']) {
    if (!claimIds.includes(coreId)) failures.push(`CLAIMS_LEDGER.md is missing core control claim: ${coreId}`);
  }
}

if (fs.existsSync(path.join(root, 'research/SOURCE_REGISTRY.json'))) {
  let registry;
  try {
    registry = JSON.parse(read('research/SOURCE_REGISTRY.json'));
  } catch (error) {
    failures.push(`SOURCE_REGISTRY.json is not valid JSON: ${error.message}`);
  }

  if (registry) {
    if (registry.schema_version !== '1.0.0') failures.push('SOURCE_REGISTRY.json must declare schema_version 1.0.0.');
    if (!Array.isArray(registry.sources) || registry.sources.length === 0) {
      failures.push('SOURCE_REGISTRY.json must contain a non-empty sources array.');
    } else {
      const allowedStates = new Set(registry.verification_states || []);
      const sourceIds = registry.sources.map((source) => source.id);
      const duplicateSourceIds = sourceIds.filter((id, index) => sourceIds.indexOf(id) !== index);
      for (const id of new Set(duplicateSourceIds)) failures.push(`Duplicate source ID in SOURCE_REGISTRY.json: ${id}`);

      const doiPattern = /^10\.\d{4,9}\/\S+$/i;
      const datePattern = /^\d{4}-\d{2}-\d{2}$/;
      let mappedSourceCount = 0;

      for (const source of registry.sources) {
        const label = source.id || '<missing source id>';
        for (const field of ['id', 'title', 'authors', 'year', 'publication_type', 'source_role', 'locator', 'verification_status', 'supports', 'does_not_establish', 'claims', 'chapters', 'last_verified']) {
          if (source[field] === undefined || source[field] === null) failures.push(`${label} is missing required field: ${field}`);
        }

        if (!/^SRC-[A-Z0-9-]+$/.test(source.id || '')) failures.push(`${label} has an invalid source ID format.`);
        if (!Array.isArray(source.authors) || source.authors.length === 0) failures.push(`${label} must list at least one author or responsible consortium.`);
        if (!Number.isInteger(source.year) || source.year < 1800 || source.year > 2100) failures.push(`${label} has an invalid publication year.`);
        if (!allowedStates.has(source.verification_status)) failures.push(`${label} uses an undeclared verification status: ${source.verification_status}`);
        if (!Array.isArray(source.supports) || source.supports.length === 0) failures.push(`${label} has no recorded supported proposition.`);
        if (!Array.isArray(source.does_not_establish) || source.does_not_establish.length === 0) failures.push(`${label} has no evidential-scope limitation.`);
        if (!Array.isArray(source.claims)) failures.push(`${label} claims must be an array.`);
        if (!Array.isArray(source.chapters) || source.chapters.some((chapter) => !Number.isInteger(chapter) || chapter < 1 || chapter > 24)) failures.push(`${label} contains an invalid chapter reference.`);
        if (!datePattern.test(source.last_verified || '')) failures.push(`${label} has an invalid last_verified date.`);

        if (!source.locator || typeof source.locator.type !== 'string' || typeof source.locator.value !== 'string' || !source.locator.value.trim()) {
          failures.push(`${label} must contain a non-empty locator type and value.`);
        } else if (source.locator.type === 'doi' && !doiPattern.test(source.locator.value)) {
          failures.push(`${label} has a malformed DOI: ${source.locator.value}`);
        }

        if (source.verification_status === 'verified' && source.locator?.type === 'journal_record') {
          failures.push(`${label} is marked verified but only has a journal_record locator.`);
        }
        if (source.verification_status === 'verified' && /not yet verified/i.test(source.locator?.value || '')) {
          failures.push(`${label} is marked verified while its locator says it is unverified.`);
        }

        for (const claimId of source.claims || []) {
          mappedSourceCount += 1;
          if (!registeredClaimIds.has(claimId)) failures.push(`${label} references unknown claim ID: ${claimId}`);
        }
      }

      if (mappedSourceCount === 0) warnings.push('SOURCE_REGISTRY.json contains no claim mappings yet; evidential scope exists, but claim-level traceability is incomplete.');
      const provisionalCount = registry.sources.filter((source) => source.verification_status === 'provisional').length;
      if (provisionalCount > 0) warnings.push(`SOURCE_REGISTRY.json contains ${provisionalCount} provisional source(s) requiring authoritative verification.`);
    }
  }
}

const epistemicFiles = [
  ...fs.readdirSync(path.join(root, 'book')).filter((file) => file.endsWith('.md')).map((file) => `book/${file}`),
  'research/THEORY_COMPARISON_MATRIX.md',
  'research/EXPERIMENTS.md'
].filter((file) => fs.existsSync(path.join(root, file)));

const prohibitedPatterns = [
  { pattern: /\bcurrent (?:AI|language models?|LLMs?) (?:is|are) conscious\b/gi, reason: 'unsupported present-tense consciousness declaration' },
  { pattern: /\bproves? (?:that )?(?:an? )?(?:AI|language model|LLM) (?:is|are) conscious\b/gi, reason: 'single-result proof language' },
  { pattern: /\bconsciousness detector\b/gi, reason: 'detector framing without a validated theory-neutral test', allowNegation: true },
  { pattern: /\bprediction error is pain\b/gi, reason: 'collapses computational error and phenomenal valence', allowNegation: true },
  { pattern: /\breward (?:is|equals) suffering\b/gi, reason: 'collapses optimization and phenomenal suffering', allowNegation: true }
];

function isExplicitlyNegated(source, index) {
  const context = source.slice(Math.max(0, index - 80), index).toLowerCase();
  return /(?:not|no|never|does not|do not|cannot|isn't|aren't|without)\s+[^.]{0,45}$/.test(context);
}

for (const file of epistemicFiles) {
  const source = read(file);
  for (const rule of prohibitedPatterns) {
    for (const match of source.matchAll(rule.pattern)) {
      if (rule.allowNegation && isExplicitlyNegated(source, match.index)) continue;
      failures.push(`${file} contains ${rule.reason}: “${match[0]}”`);
    }
  }
}

if (fs.existsSync(path.join(root, 'research/THEORY_COMPARISON_MATRIX.md'))) {
  const matrix = read('research/THEORY_COMPARISON_MATRIX.md');
  for (const control of ['Strongest rival explanation', 'Discriminating intervention', 'Confidence-lowering result', 'What it does not establish']) {
    if (!matrix.includes(control)) failures.push(`THEORY_COMPARISON_MATRIX.md is missing control field: ${control}`);
  }
}

if (fs.existsSync(path.join(root, 'research/EXPERIMENTS.md'))) {
  const experiments = read('research/EXPERIMENTS.md');
  for (const control of ['rival', 'falsif', 'consciousness detector']) {
    if (!experiments.toLowerCase().includes(control)) failures.push(`EXPERIMENTS.md is missing required adversarial concept: ${control}`);
  }
}

if (warnings.length) {
  console.warn('\nSite validation warnings:\n');
  warnings.forEach((warning) => console.warn(`- ${warning}`));
}

if (failures.length) {
  console.error('\nSite validation failed:\n');
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(`Validated ${required.length} required files, ${htmlFiles.length} HTML surfaces, script bindings, chapter mappings, local links, claim controls, source-registry controls, theory controls, and prohibited epistemic overclaims.`);
