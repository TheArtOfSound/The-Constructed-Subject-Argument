import http from 'node:http';
import { spawnSync } from 'node:child_process';
import process from 'node:process';

const expectedSha = '0123456789abcdef0123456789abcdef01234567';
const repository = 'TheArtOfSound/The-Constructed-Subject-Argument';

const server = http.createServer((request, response) => {
  const url = new URL(request.url, 'http://127.0.0.1');
  response.setHeader('content-type', url.pathname.endsWith('.json') ? 'application/json' : 'text/html');
  if (url.pathname === '/deployment.json') {
    response.end(JSON.stringify({
      schema_version: 'constructed-subject-pages-deployment-1.0.0',
      repository,
      commit_sha: expectedSha,
      workflow_run_id: 'test-run',
      deployed_at_utc: '2026-07-29T01:00:00Z'
    }));
    return;
  }
  if (url.pathname === '/program.html') {
    response.end(`<!doctype html><title>Research Program</title>
      Subject–Report Identification EGC 2.0 QEIB
      expert_reviewer_dry_run_execution_readiness.v0.1.json
      expert_reviewer_dry_run_assignment_and_provisioning.v0.1.json`);
    return;
  }
  response.end('<!doctype html><title>The Constructed Subject</title>Research program <a href="program.html">program.html</a>');
});

await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const { port } = server.address();
const baseUrl = `http://127.0.0.1:${port}/`;

function run(sha) {
  return spawnSync(process.execPath, ['scripts/verify-pages-deployment.mjs', baseUrl, sha], {
    cwd: process.cwd(),
    encoding: 'utf8',
    env: {
      ...process.env,
      GITHUB_REPOSITORY: repository,
      PAGES_VERIFY_RETRIES: '1',
      PAGES_VERIFY_DELAY_MS: '1'
    }
  });
}

const pass = run(expectedSha);
if (pass.status !== 0 || !pass.stdout.includes('passed_pages_deployment_verification')) {
  console.error(pass.stdout);
  console.error(pass.stderr);
  server.close();
  throw new Error('Expected exact deployment fixture to pass.');
}

const mismatch = run('ffffffffffffffffffffffffffffffffffffffff');
if (mismatch.status === 0 || !mismatch.stderr.includes('deployed commit mismatch')) {
  console.error(mismatch.stdout);
  console.error(mismatch.stderr);
  server.close();
  throw new Error('Expected mismatched deployment SHA to fail closed.');
}

server.close();
console.log('Pages deployment verifier tests passed: exact match accepted; stale/mismatched deployment rejected.');
