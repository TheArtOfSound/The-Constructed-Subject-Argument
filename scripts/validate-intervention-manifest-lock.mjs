#!/usr/bin/env node
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const readJson = (relative) => JSON.parse(fs.readFileSync(path.join(root, relative), 'utf8'));
const assert = (condition, message) => { if (!condition) throw new Error(message); };

const schema = readJson('research/MECHANISM_PRESERVATION_EMPIRICAL_SCHEMA.json');
const record = readJson('research/MECHANISM_PRESERVATION_EMPIRICAL_FIXTURE.json');
const lock = record.intervention_manifest_lock ?? {};

for (const field of schema.intervention_manifest_lock.required_fields) {
  assert(Object.hasOwn(lock, field), `Missing intervention manifest lock field: ${field}.`);
}

const manifestPath = path.join(root, lock.path);
assert(fs.existsSync(manifestPath), `Locked intervention manifest does not exist: ${lock.path}.`);
const manifestBytes = fs.readFileSync(manifestPath);
const manifest = JSON.parse(manifestBytes.toString('utf8'));

const gitBlobSha = crypto
  .createHash('sha1')
  .update(Buffer.from(`blob ${manifestBytes.length}\0`))
  .update(manifestBytes)
  .digest('hex');
const sha256 = crypto.createHash('sha256').update(manifestBytes).digest('hex');

assert(manifest.manifest_id === lock.manifest_id, 'Manifest ID differs from the empirical record lock.');
assert(manifest.protocol_id === record.protocol_id, 'Locked manifest targets a different protocol.');
assert(manifest.run_id === record.run_id, 'Locked manifest targets a different empirical run.');
assert(manifest.frozen_before_outcomes === true, 'Locked manifest is not declared frozen before outcomes.');
assert(lock.git_blob_sha === gitBlobSha, `Manifest Git blob SHA mismatch: expected ${lock.git_blob_sha}, derived ${gitBlobSha}.`);
assert(lock.sha256 === sha256, `Manifest SHA-256 mismatch: expected ${lock.sha256}, derived ${sha256}.`);
assert(/^[0-9a-f]{40}$/.test(lock.git_blob_sha), 'Manifest Git blob SHA is malformed.');
assert(/^[0-9a-f]{64}$/.test(lock.sha256), 'Manifest SHA-256 is malformed.');

console.log(`Validated intervention manifest lock ${manifest.manifest_id}.`);
console.log(`Git blob SHA: ${gitBlobSha}`);
console.log(`SHA-256: ${sha256}`);
console.log('Any byte-level manifest change now invalidates the empirical record until explicitly relocked.');