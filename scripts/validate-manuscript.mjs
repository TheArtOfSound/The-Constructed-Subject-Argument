import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const failures = [];
const warnings = [];

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function words(text) {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

const requiredResearch = [
  'BOOK_CHARTER.md',
  'MANUSCRIPT.md',
  'MANUSCRIPT_STATUS.md',
  'UX_ARCHITECTURE.md',
  'research/CLAIMS_LEDGER.md',
  'research/CLAIMS_LEDGER_SUPPLEMENT.md',
  'research/ORIGINALITY_LEDGER.md',
  'research/ORIGINALITY_LEDGER_SUPPLEMENT.md',
  'research/LITERATURE_MAP.md',
  'research/SOURCE_REGISTRY.md',
  'research/PUBLICATION_AUDIT_MATRIX.md',
  'research/OBJECTIONS.md',
  'research/METHOD.md',
  'research/EXPERIMENTS.md',
  'reviews/01-biological-naturalist-hostile-review.md',
  'reviews/01-response-and-revision-decision.md',
  'reviews/02-functionalist-hostile-review.md',
  'reviews/02-response-and-revision-decision.md',
  'appendices/A-four-substrate-test.md',
  'appendices/B-dual-risk-decision-matrix.md',
  'appendices/C-theory-conditioned-interpretation.md'
];

for (const file of requiredResearch) {
  if (!fs.existsSync(path.join(root, file))) failures.push(`Missing manuscript dependency: ${file}`);
}

let registry;
try {
  registry = JSON.parse(read('chapters/chapters.json'));
} catch (error) {
  failures.push(`Invalid chapters/chapters.json: ${error.message}`);
}

const expectedIds = Array.from({ length: 21 }, (_, index) => String(index + 1).padStart(2, '0'));
const chapterStats = [];

if (registry?.chapters) {
  const ids = Object.keys(registry.chapters).sort((a, b) => Number(a) - Number(b));
  if (JSON.stringify(ids) !== JSON.stringify(expectedIds)) {
    failures.push(`Chapter registry must contain exactly 01–21. Found: ${ids.join(', ')}`);
  }

  const seenTitles = new Set();
  for (const id of expectedIds) {
    const chapter = registry.chapters[id];
    if (!chapter) continue;
    if (seenTitles.has(chapter.title)) failures.push(`Duplicate chapter title: ${chapter.title}`);
    seenTitles.add(chapter.title);

    const relativeFile = path.normalize(path.join('chapters', chapter.file));
    const absoluteFile = path.join(root, relativeFile);
    if (!fs.existsSync(absoluteFile)) {
      failures.push(`Chapter ${id} file missing: ${relativeFile}`);
      continue;
    }

    const source = fs.readFileSync(absoluteFile, 'utf8');
    const chapterNumber = Number(id);
    const headingPattern = new RegExp(`^# Chapter ${chapterNumber}\\s+[—-]`);
    if (!headingPattern.test(source)) failures.push(`Chapter ${id} must begin with “# Chapter ${chapterNumber} —/–/-”.`);
    if (!source.includes(chapter.title)) warnings.push(`Chapter ${id} registry title does not appear verbatim in its source.`);
    if (!/^##\s+/m.test(source)) failures.push(`Chapter ${id} has no section headings.`);
    if (!/## Research anchors|## Research Anchors|### Claim status|## Claim status/m.test(source)) {
      warnings.push(`Chapter ${id} has no explicit research-anchor or claim-status section.`);
    }

    const wordCount = words(source);
    if (wordCount < 1200) warnings.push(`Chapter ${id} is short for a full research draft: ${wordCount} words.`);
    chapterStats.push({ id, title: chapter.title, words: wordCount, file: relativeFile });
  }
} else {
  failures.push('Chapter registry has no chapters object.');
}

const manuscriptText = chapterStats.map(({ file }) => read(file)).join('\n\n');
const prohibitedPatterns = [
  { pattern: /CIAPARAGATAK/i, reason: 'hallucinated acronym from an external evaluation' },
  { pattern: /proves? that current (?:AI|language models?) (?:is|are) conscious/i, reason: 'unsupported current-system consciousness proof' },
  { pattern: /gradient descent (?:is|feels) pain/i, reason: 'optimization/valence collapse' },
  { pattern: /every (?:inference|input.?output|response) (?:is|creates) (?:a )?conscious/i, reason: 'unqualified event-consciousness claim' },
  { pattern: /first theory of AI consciousness/i, reason: 'unsupported priority claim' },
  { pattern: /no one has (?:ever )?(?:considered|proposed|written)/i, reason: 'unsupported universal originality claim' }
];

for (const { pattern, reason } of prohibitedPatterns) {
  const match = manuscriptText.match(pattern);
  if (match) failures.push(`Prohibited manuscript claim (${reason}): “${match[0]}”`);
}

const requiredFinalPhrases = [
  'Artificial construction does not settle subjectivity',
  'does not establish that current language models are conscious',
  'structured uncertainty'
];
const finalChapter = registry?.chapters?.['21'] ? read(path.normalize(path.join('chapters', registry.chapters['21'].file))) : '';
for (const phrase of requiredFinalPhrases) {
  if (!finalChapter.toLowerCase().includes(phrase.toLowerCase())) warnings.push(`Final chapter should preserve phrase or equivalent: ${phrase}`);
}

const totalWords = chapterStats.reduce((sum, chapter) => sum + chapter.words, 0);
if (totalWords < 30000) failures.push(`Complete manuscript unexpectedly short: ${totalWords} words.`);

if (!read('MANUSCRIPT_STATUS.md').includes('coverage**, not **certification')) {
  warnings.push('MANUSCRIPT_STATUS.md should preserve the coverage-not-certification distinction.');
}

if (failures.length) {
  console.error('\nManuscript validation failed:\n');
  failures.forEach((failure) => console.error(`- ${failure}`));
  if (warnings.length) {
    console.error('\nWarnings:\n');
    warnings.forEach((warning) => console.error(`- ${warning}`));
  }
  process.exit(1);
}

console.log(`Validated ${chapterStats.length} chapters, ${totalWords.toLocaleString()} manuscript words, registry continuity 01–21, research controls, hostile reviews, appendices, and prohibited-claim rules.`);

if (warnings.length) {
  console.warn('\nNon-blocking warnings:\n');
  warnings.forEach((warning) => console.warn(`- ${warning}`));
}

console.log('\nChapter word counts:');
chapterStats.forEach((chapter) => console.log(`${chapter.id} ${String(chapter.words).padStart(6)}  ${chapter.title}`));
