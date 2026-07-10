import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const root = process.cwd();
const failures = [];
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
  'research/EXPERIMENTS.md'
];

for (const file of required) {
  if (!fs.existsSync(path.join(root, file))) failures.push(`Missing required file: ${file}`);
}

function idsFromHtml(source) {
  return new Set([...source.matchAll(/\bid=["']([^"']+)["']/g)].map((match) => match[1]));
}

function referencedIds(source) {
  return new Set([...source.matchAll(/getElementById\(["']([^"']+)["']\)/g)].map((match) => match[1]));
}

function validateBindings(htmlFile, jsFile) {
  const html = fs.readFileSync(path.join(root, htmlFile), 'utf8');
  const js = fs.readFileSync(path.join(root, jsFile), 'utf8');
  const ids = idsFromHtml(html);
  for (const id of referencedIds(js)) {
    if (!ids.has(id)) failures.push(`${jsFile} references missing #${id} in ${htmlFile}`);
  }
}

validateBindings('index.html', 'assets/experience-v2.js');
validateBindings('chapters/read.html', 'assets/reader-v2.js');

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
  const source = fs.readFileSync(path.join(root, htmlFile), 'utf8');
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

const readerSource = fs.readFileSync(path.join(root, 'assets/reader-v2.js'), 'utf8');
for (const match of readerSource.matchAll(/file:\s*["']([^"']+\.md)["']/g)) {
  const resolved = path.resolve(path.join(root, 'chapters'), match[1]);
  if (!fs.existsSync(resolved)) failures.push(`Reader maps to missing chapter: ${match[1]}`);
}

const librarySource = fs.readFileSync(path.join(root, 'chapters/index.html'), 'utf8');
if (/href=["']\.\.\/book\//.test(librarySource)) {
  failures.push('Chapter library links directly to raw Markdown instead of the reader interface.');
}

if (failures.length) {
  console.error('\nSite validation failed:\n');
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(`Validated ${required.length} required files, ${htmlFiles.length} HTML surfaces, script bindings, chapter mappings, local links, and cross-page anchors.`);
