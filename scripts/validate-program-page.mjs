import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const root = process.cwd();
const failures = [];

const required = [
  'program.html',
  'assets/program.css',
  'assets/program.js',
  'assets/program-home.css',
  'assets/experience-v2.js',
  'sitemap.xml',
  'research/egc2/expert_reviewer_dry_run_execution_readiness.v0.1.json',
  'research/egc2/expert_reviewer_dry_run_assignment_and_provisioning.v0.1.json',
  'research/EGC_2_DRY_RUN_ASSIGNMENT_AND_PROVISIONING_STANDARD.md',
  'research/EGC_2_DRY_RUN_READINESS_CONSISTENCY_GATE.md',
  'research/EGC_2_DRY_RUN_READINESS_CI_EXECUTION_RECORD.md',
  'research/EGC_2_PUBLIC_EVIDENCE_CI_GATE.md',
  'research/EGC_2_PUBLIC_EVIDENCE_CI_EXECUTION_RECORD.md'
];

for (const file of required) {
  if (!fs.existsSync(path.join(root, file))) failures.push(`Missing visual-program dependency: ${file}`);
}

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function idsFromHtml(source) {
  return new Set([...source.matchAll(/\bid=["']([^"']+)["']/g)].map((match) => match[1]));
}

if (fs.existsSync(path.join(root, 'program.html'))) {
  const html = read('program.html');
  const ids = idsFromHtml(html);

  for (const match of html.matchAll(/(?:href|src)=["']([^"']+)["']/g)) {
    const target = match[1];
    if (/^(?:https?:|mailto:|data:)/.test(target)) continue;
    if (target.startsWith('#')) {
      const id = target.slice(1);
      if (id && !ids.has(id)) failures.push(`program.html links to missing local anchor: ${target}`);
      continue;
    }

    const [pathAndQuery, anchor = ''] = target.split('#');
    const clean = pathAndQuery.split('?')[0];
    if (!clean) continue;
    const resolved = path.resolve(root, clean.endsWith('/') ? `${clean}index.html` : clean);
    if (!fs.existsSync(resolved)) {
      failures.push(`program.html links to missing local target: ${target}`);
      continue;
    }
    if (anchor && resolved.endsWith('.html')) {
      const targetIds = idsFromHtml(fs.readFileSync(resolved, 'utf8'));
      if (!targetIds.has(anchor)) failures.push(`program.html links to missing anchor ${anchor} in ${path.relative(root, resolved)}`);
    }
  }

  if (!html.includes('live evidence, incomplete claims')) failures.push('program.html is missing the explicit incomplete-claims boundary.');
  if (!html.includes('Private holdout exclusion from public UI')) failures.push('program.html is missing the private-holdout exclusion statement.');
}

for (const jsFile of ['assets/program.js', 'assets/experience-v2.js']) {
  if (!fs.existsSync(path.join(root, jsFile))) continue;
  try {
    execFileSync(process.execPath, ['--check', path.join(root, jsFile)], { stdio: 'pipe' });
  } catch (error) {
    failures.push(`JavaScript syntax failed: ${jsFile}\n${error.stderr?.toString() || error.message}`);
  }
}

if (required.every((file) => fs.existsSync(path.join(root, file)))) {
  const html = read('program.html');
  const ids = idsFromHtml(html);
  const js = read('assets/program.js');
  for (const match of js.matchAll(/getElementById\(["']([^"']+)["']\)/g)) {
    if (!ids.has(match[1])) failures.push(`assets/program.js references missing #${match[1]} in program.html`);
  }

  const homeJs = read('assets/experience-v2.js');
  for (const token of ['program.html', 'program-launch', 'program-home.css']) {
    if (!homeJs.includes(token)) failures.push(`Homepage script is missing visual-program integration token: ${token}`);
  }

  const sitemap = read('sitemap.xml');
  if (!sitemap.includes('/program.html')) failures.push('sitemap.xml does not include program.html.');

  let readiness;
  let provisioning;
  try {
    readiness = JSON.parse(read('research/egc2/expert_reviewer_dry_run_execution_readiness.v0.1.json'));
    provisioning = JSON.parse(read('research/egc2/expert_reviewer_dry_run_assignment_and_provisioning.v0.1.json'));
  } catch (error) {
    failures.push(`Live-state JSON parse failed: ${error.message}`);
  }

  if (readiness) {
    if (readiness.execution_allowed !== false) failures.push('Readiness record no longer preserves execution_allowed=false.');
    if (readiness.status !== 'blocked') failures.push(`Unexpected readiness status: ${readiness.status}`);
    if (!Array.isArray(readiness.preflight_gates) || readiness.preflight_gates.length !== 12) failures.push('Readiness record must expose exactly 12 preflight gates.');
  }

  if (provisioning) {
    if (provisioning.execution_allowed !== false) failures.push('Provisioning record no longer preserves execution_allowed=false.');
    if (provisioning.status !== 'blocked_unassigned_unprovisioned') failures.push(`Unexpected provisioning status: ${provisioning.status}`);
    if (!Array.isArray(provisioning.assignments?.ownership_roles) || provisioning.assignments.ownership_roles.length !== 6) failures.push('Provisioning record must expose exactly 6 ownership roles.');
    if (!Array.isArray(provisioning.resource_controls) || provisioning.resource_controls.length !== 8) failures.push('Provisioning record must expose exactly 8 resource controls.');
  }
}

if (failures.length) {
  console.error('\nVisual research program validation failed:\n');
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(`Validated visual research program: ${required.length} dependencies, local links, JS bindings, homepage integration, sitemap entry, and blocked public-safe state.`);
