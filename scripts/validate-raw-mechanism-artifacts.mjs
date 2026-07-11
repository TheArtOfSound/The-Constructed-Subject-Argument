import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = process.cwd();
const readJson = relativePath => JSON.parse(fs.readFileSync(path.join(root, relativePath), 'utf8'));
const fail = message => {
  console.error(`Raw mechanism artifact validation failed: ${message}`);
  process.exit(1);
};
const round = (value, decimals) => Number(value.toFixed(decimals));
const mean = values => values.reduce((sum, value) => sum + value, 0) / values.length;
const sampleSd = values => {
  if (values.length < 2) fail('At least two replicates are required to estimate uncertainty.');
  const average = mean(values);
  return Math.sqrt(values.reduce((sum, value) => sum + ((value - average) ** 2), 0) / (values.length - 1));
};
const gitBlobSha = bytes => crypto.createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex');
const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

const manifest = readJson('research/MECHANISM_PRESERVATION_RAW_ARTIFACT_MANIFEST.json');
const empirical = readJson('research/MECHANISM_PRESERVATION_EMPIRICAL_FIXTURE.json');

if (manifest.run_id !== empirical.run_id) fail('Raw-artifact manifest and empirical record use different run IDs.');
if (manifest.empirical_status !== 'synthetic_fixture') fail('Repository raw fixture must remain explicitly synthetic.');
if (!String(manifest.epistemic_boundary || '').includes('does not establish')) fail('Epistemic boundary is missing or weakened.');
if (!Array.isArray(manifest.artifacts) || manifest.artifacts.length !== 1) fail('Exactly one raw fixture artifact is required in this test package.');

const artifact = manifest.artifacts[0];
const artifactPath = path.join(root, artifact.path);
if (!fs.existsSync(artifactPath)) fail(`Raw artifact does not exist: ${artifact.path}`);
const bytes = fs.readFileSync(artifactPath);
if (gitBlobSha(bytes) !== artifact.git_blob_sha) fail('Raw artifact Git blob SHA does not match its manifest lock.');
if (sha256(bytes) !== artifact.sha256) fail('Raw artifact SHA-256 does not match its manifest lock.');

const raw = JSON.parse(bytes.toString('utf8'));
if (raw.artifact_id !== artifact.artifact_id) fail('Raw artifact ID does not match the manifest.');
if (raw.run_id !== empirical.run_id) fail('Raw artifact and empirical record use different run IDs.');
if (raw.empirical_status !== 'synthetic_fixture') fail('Raw observations lost their synthetic-fixture status.');
if (!String(raw.notice || '').includes('no evidence about any actual AI system')) fail('Raw fixture notice is missing its real-system boundary.');

const rawById = new Map(raw.interventions.map(item => [item.intervention_id, item]));
if (rawById.size !== raw.interventions.length) fail('Duplicate raw intervention IDs detected.');
if (rawById.size !== empirical.interventions.length) fail('Raw and empirical intervention counts differ.');

const contract = manifest.derivation_contract;
for (const reported of empirical.interventions) {
  const source = rawById.get(reported.intervention_id);
  if (!source) fail(`No raw observations exist for ${reported.intervention_id}.`);
  if (source.estimator !== contract.estimator) fail(`${reported.intervention_id} uses an unregistered estimator.`);
  if (source.interval_method !== contract.interval_method) fail(`${reported.intervention_id} uses an unregistered interval method.`);
  if (!Array.isArray(source.replicates) || source.replicates.length !== reported.replications) fail(`${reported.intervention_id} replication count is not derived from raw observations.`);

  const lesion = reported.family === 'selective_lesion';
  const differences = source.replicates.map(row => lesion ? row.reference - row.candidate : row.candidate - row.reference);
  const effect = mean(differences);
  const standardError = sampleSd(differences) / Math.sqrt(differences.length);
  const halfWidth = contract.interval_multiplier * standardError;
  const derivedEffect = round(effect, contract.rounding_decimals);
  const derivedInterval = [round(effect - halfWidth, contract.rounding_decimals), round(effect + halfWidth, contract.rounding_decimals)];

  if (derivedEffect !== reported.effect_size) fail(`${reported.intervention_id} effect size was not reproduced from raw observations.`);
  if (derivedInterval.length !== reported.uncertainty_interval.length || derivedInterval.some((value, index) => value !== reported.uncertainty_interval[index])) {
    fail(`${reported.intervention_id} uncertainty interval was not reproduced from raw observations.`);
  }

  const rawControlIds = Object.keys(source.controls || {}).sort();
  const reportedControlIds = reported.control_results.map(control => control.control_id).sort();
  if (JSON.stringify(rawControlIds) !== JSON.stringify(reportedControlIds)) fail(`${reported.intervention_id} raw and reported control sets differ.`);

  for (const control of reported.control_results) {
    const rows = source.controls[control.control_id];
    const controlDifferences = rows.map(row => row.candidate - row.reference);
    const derivedPass = Math.abs(mean(controlDifferences)) <= contract.control_pass_rule.match(/([0-9.]+)$/)?.[1];
    if (derivedPass !== control.passed) fail(`${reported.intervention_id}/${control.control_id} pass status was not reproduced from raw observations.`);
  }
  if (reported.controls_passed !== reported.control_results.every(control => control.passed)) fail(`${reported.intervention_id} aggregate control status is inconsistent.`);
}

console.log(`Validated ${empirical.interventions.length} empirical interventions against immutable raw observations.`);
