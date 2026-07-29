import process from 'node:process';

const [baseUrlArg, expectedSha] = process.argv.slice(2);

if (!baseUrlArg || !expectedSha) {
  console.error('Usage: node scripts/verify-pages-deployment.mjs <base-url> <expected-sha>');
  process.exit(2);
}

if (!/^[0-9a-f]{40}$/i.test(expectedSha)) {
  console.error(`Expected SHA must be a 40-character hexadecimal commit SHA: ${expectedSha}`);
  process.exit(2);
}

const baseUrl = new URL(baseUrlArg.endsWith('/') ? baseUrlArg : `${baseUrlArg}/`);
const retries = Number.parseInt(process.env.PAGES_VERIFY_RETRIES || '12', 10);
const delayMs = Number.parseInt(process.env.PAGES_VERIFY_DELAY_MS || '10000', 10);

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function fetchText(relativePath) {
  const url = new URL(relativePath, baseUrl);
  const response = await fetch(url, {
    headers: {
      'cache-control': 'no-cache',
      pragma: 'no-cache',
      'user-agent': 'constructed-subject-pages-verifier/1.0'
    }
  });
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`);
  return { url, text: await response.text() };
}

async function verifyOnce() {
  const manifestResponse = await fetchText(`deployment.json?sha=${expectedSha}`);
  let manifest;
  try {
    manifest = JSON.parse(manifestResponse.text);
  } catch (error) {
    throw new Error(`deployment.json was not valid JSON: ${error.message}`);
  }

  if (manifest.commit_sha !== expectedSha) {
    throw new Error(`deployed commit mismatch: expected ${expectedSha}, observed ${manifest.commit_sha ?? '<missing>'}`);
  }
  if (manifest.repository !== process.env.GITHUB_REPOSITORY && process.env.GITHUB_REPOSITORY) {
    throw new Error(`repository mismatch: expected ${process.env.GITHUB_REPOSITORY}, observed ${manifest.repository ?? '<missing>'}`);
  }

  const home = await fetchText(`?sha=${expectedSha}`);
  const program = await fetchText(`program.html?sha=${expectedSha}`);

  const requiredHomeMarkers = [
    'The Constructed Subject',
    'Research program',
    'program.html'
  ];
  const requiredProgramMarkers = [
    'Research Program',
    'Subject–Report Identification',
    'EGC 2.0',
    'QEIB',
    'expert_reviewer_dry_run_execution_readiness.v0.1.json',
    'expert_reviewer_dry_run_assignment_and_provisioning.v0.1.json'
  ];

  for (const marker of requiredHomeMarkers) {
    if (!home.text.includes(marker)) throw new Error(`homepage missing required marker: ${marker}`);
  }
  for (const marker of requiredProgramMarkers) {
    if (!program.text.includes(marker)) throw new Error(`program.html missing required marker: ${marker}`);
  }

  return {
    status: 'passed_pages_deployment_verification',
    commit_sha: manifest.commit_sha,
    repository: manifest.repository,
    workflow_run_id: manifest.workflow_run_id,
    deployed_at_utc: manifest.deployed_at_utc,
    page_url: baseUrl.toString(),
    verified_paths: [manifestResponse.url.toString(), home.url.toString(), program.url.toString()]
  };
}

let lastError;
for (let attempt = 1; attempt <= retries; attempt += 1) {
  try {
    const result = await verifyOnce();
    console.log(JSON.stringify({ ...result, attempt }, null, 2));
    process.exit(0);
  } catch (error) {
    lastError = error;
    console.error(`Pages verification attempt ${attempt}/${retries} failed: ${error.message}`);
    if (attempt < retries) await sleep(delayMs);
  }
}

console.error(`Pages deployment verification failed after ${retries} attempts: ${lastError?.message || 'unknown error'}`);
process.exit(1);
