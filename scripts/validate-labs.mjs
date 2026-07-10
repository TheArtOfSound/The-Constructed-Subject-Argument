import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const root = process.cwd();
const failures = [];
const required = [
  'labs/index.html',
  'labs/uncertainty-ledger.html',
  'assets/ledger.css',
  'assets/ledger.js',
  'assets/experience-v2.css',
  'assets/favicon.svg',
  'chapters/read.html',
  'research/METHOD.md',
  'research/EXPERIMENTS.md'
];

for (const file of required) {
  if (!fs.existsSync(path.join(root, file))) failures.push(`Missing required lab dependency: ${file}`);
}

function idsFromHtml(source) {
  return new Set([...source.matchAll(/\bid=["']([^"']+)["']/g)].map((match) => match[1]));
}

function referencedIds(source) {
  return new Set([...source.matchAll(/getElementById\(["']([^"']+)["']\)/g)].map((match) => match[1]));
}

function validateLocalLinks(htmlFile) {
  const fullPath = path.join(root, htmlFile);
  const source = fs.readFileSync(fullPath, 'utf8');
  const base = path.dirname(fullPath);
  const ids = idsFromHtml(source);

  for (const match of source.matchAll(/(?:href|src)=["']([^"']+)["']/g)) {
    const target = match[1];
    if (/^(?:https?:|mailto:|data:)/.test(target)) continue;
    if (target.startsWith('#')) {
      const id = target.slice(1);
      if (id && !ids.has(id)) failures.push(`${htmlFile} links to missing local anchor ${target}`);
      continue;
    }
    const [pathAndQuery, anchor = ''] = target.split('#');
    const clean = pathAndQuery.split('?')[0];
    if (!clean) continue;
    const resolved = path.resolve(base, clean.endsWith('/') ? `${clean}index.html` : clean);
    if (!fs.existsSync(resolved)) {
      failures.push(`${htmlFile} links to missing target ${target}`);
      continue;
    }
    if (anchor && resolved.endsWith('.html')) {
      const targetSource = fs.readFileSync(resolved, 'utf8');
      if (!idsFromHtml(targetSource).has(anchor)) failures.push(`${htmlFile} links to missing anchor ${anchor} in ${path.relative(root, resolved)}`);
    }
  }
}

for (const htmlFile of ['labs/index.html', 'labs/uncertainty-ledger.html']) validateLocalLinks(htmlFile);

try {
  execFileSync(process.execPath, ['--check', path.join(root, 'assets/ledger.js')], { stdio: 'pipe' });
} catch (error) {
  failures.push(`JavaScript syntax failed: assets/ledger.js\n${error.stderr?.toString() || error.message}`);
}

const ledgerHtml = fs.readFileSync(path.join(root, 'labs/uncertainty-ledger.html'), 'utf8');
const ledgerJs = fs.readFileSync(path.join(root, 'assets/ledger.js'), 'utf8');
const ledgerIds = idsFromHtml(ledgerHtml);
for (const id of referencedIds(ledgerJs)) {
  if (!ledgerIds.has(id)) failures.push(`assets/ledger.js references missing #${id} in labs/uncertainty-ledger.html`);
}

const requiredHypotheses = [
  'Phenomenal consciousness',
  'Valenced consciousness',
  'Functional self-modeling',
  'Agency',
  'Autonomy',
  'Diachronic continuity',
  'Personhood',
  'Moral patienthood'
];
for (const hypothesis of requiredHypotheses) {
  if (!ledgerJs.includes(hypothesis)) failures.push(`Ledger is missing hypothesis: ${hypothesis}`);
}

const prohibitedPatterns = [
  /consciousness score/i,
  /sentience score/i,
  /probability of consciousness\s*[:=]\s*\d/i,
  /\d+%\s*(?:conscious|sentient)/i
];
for (const pattern of prohibitedPatterns) {
  if (pattern.test(ledgerJs)) failures.push(`Ledger JavaScript contains prohibited pseudo-quantification pattern: ${pattern}`);
}

if (!ledgerHtml.includes('Not a consciousness detector')) failures.push('Ledger must display its non-detector warning prominently.');
if (!ledgerHtml.includes('What would lower your confidence?')) failures.push('Ledger must require a confidence-lowering audit section.');
if (!ledgerJs.includes('Strongest rival')) failures.push('Ledger results must expose rival explanations.');
if (!ledgerJs.includes('Next discriminating test')) failures.push('Ledger results must expose a next discriminating test.');

if (failures.length) {
  console.error('\nLab validation failed:\n');
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(`Validated ${required.length} lab dependencies, 2 HTML surfaces, JavaScript syntax, DOM bindings, eight hypothesis ledgers, local links, rival explanations, falsification prompts, and anti-pseudo-quantification rules.`);
