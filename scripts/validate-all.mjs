import path from 'node:path';
import { execFileSync } from 'node:child_process';

const root = process.cwd();
const validators = [
  'scripts/validate-site.mjs',
  'scripts/validate-argument-graph.mjs',
  'scripts/validate-adversarial-reviews.mjs',
  'scripts/validate-mechanism-protocol.mjs',
  'scripts/validate-mechanism-scorer.mjs',
  'scripts/validate-intervention-manifest-lock.mjs',
  'scripts/validate-preregistration-bundle.mjs',
  'scripts/validate-raw-mechanism-artifacts.mjs',
  'scripts/validate-derived-mechanism-results.mjs',
  'scripts/validate-mechanism-matching-results.mjs',
  'scripts/validate-generic-capacity-inference.mjs',
  'scripts/validate-capacity-confound-adjudication.mjs',
  'scripts/validate-authoritative-capacity-adjudication.mjs',
  'scripts/validate-mechanism-results.mjs',
  'scripts/validate-mechanism-classification-trace.mjs',
  'scripts/validate-mechanism-classification-trace-suite.mjs',
  'scripts/validate-public-review.mjs',
  'scripts/validate-source-crosswalk.mjs'
];

for (const validator of validators) {
  const absolute = path.join(root, validator);
  console.log(`\nRunning ${validator}...`);
  try {
    execFileSync(process.execPath, [absolute], {
      cwd: root,
      stdio: 'inherit'
    });
  } catch (error) {
    const exitCode = Number.isInteger(error.status) ? error.status : 1;
    console.error(`\nValidation gate failed in ${validator}.`);
    process.exit(exitCode);
  }
}

console.log(`\nAll ${validators.length} validation suites passed.`);
