import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const failures = [];
const warnings = [];

function read(relativePath) {
  const absolute = path.join(root, relativePath);
  if (!fs.existsSync(absolute)) {
    failures.push(`Missing required file: ${relativePath}`);
    return '';
  }
  return fs.readFileSync(absolute, 'utf8');
}

function readJson(relativePath) {
  const source = read(relativePath);
  if (!source) return null;
  try {
    return JSON.parse(source);
  } catch (error) {
    failures.push(`${relativePath} is not valid JSON: ${error.message}`);
    return null;
  }
}

function duplicates(values) {
  return [...new Set(values.filter((value, index) => values.indexOf(value) !== index))];
}

const humanRegistry = read('research/SOURCE_REGISTRY.md');
const structuredRegistry = readJson('research/SOURCE_REGISTRY.json');
const crosswalk = readJson('research/SOURCE_ID_CROSSWALK.json');

if (humanRegistry && structuredRegistry && crosswalk) {
  if (crosswalk.schema_version !== '1.0.0') failures.push('SOURCE_ID_CROSSWALK.json must declare schema_version 1.0.0.');
  if (!Array.isArray(crosswalk.mappings) || crosswalk.mappings.length === 0) failures.push('SOURCE_ID_CROSSWALK.json must contain mappings.');

  const declaredMatchTypes = new Set(Object.keys(crosswalk.match_types || {}));
  const humanIds = new Set([...humanRegistry.matchAll(/^##\s+(SRC-[A-Z]\d{3})\b/gm)].map((match) => match[1]));
  const structuredIds = new Set((structuredRegistry.sources || []).map((source) => source.id));
  const mappedStructuredIds = [];

  for (const legacyId of duplicates((crosswalk.mappings || []).map((mapping) => mapping.legacy_id))) {
    failures.push(`Duplicate legacy source mapping: ${legacyId}`);
  }

  for (const mapping of crosswalk.mappings || []) {
    const label = mapping.legacy_id || '<missing legacy id>';
    if (!/^SRC-[A-Z]\d{3}$/.test(mapping.legacy_id || '')) failures.push(`${label} has invalid legacy ID format.`);
    if (!humanIds.has(mapping.legacy_id)) failures.push(`${label} does not exist in SOURCE_REGISTRY.md.`);
    if (!declaredMatchTypes.has(mapping.match_type)) failures.push(`${label} uses undeclared match_type: ${mapping.match_type}`);
    if (!Array.isArray(mapping.structured_ids) || mapping.structured_ids.length === 0) failures.push(`${label} must map to at least one structured source.`);
    if (mapping.match_type === 'exact' && mapping.structured_ids?.length !== 1) failures.push(`${label} is marked exact but does not map one-to-one.`);
    if (typeof mapping.migration_action !== 'string' || mapping.migration_action.trim().length < 20) failures.push(`${label} lacks a substantive migration action.`);

    for (const structuredId of mapping.structured_ids || []) {
      mappedStructuredIds.push(structuredId);
      if (!structuredIds.has(structuredId)) failures.push(`${label} references unknown structured source: ${structuredId}`);
    }
  }

  for (const structuredId of duplicates(mappedStructuredIds)) {
    failures.push(`${structuredId} is assigned to more than one legacy source record.`);
  }

  for (const structuredId of structuredIds) {
    if (!mappedStructuredIds.includes(structuredId)) failures.push(`${structuredId} has no legacy-registry crosswalk entry.`);
  }

  const splitCount = (crosswalk.mappings || []).filter((mapping) => mapping.match_type === 'cluster_overlap_requires_split').length;
  if (splitCount > 0) warnings.push(`${splitCount} legacy source cluster(s) still require conceptual splitting before migration is complete.`);
}

if (warnings.length) {
  console.warn('\nSource crosswalk validation warnings:\n');
  warnings.forEach((warning) => console.warn(`- ${warning}`));
}

if (failures.length) {
  console.error('\nSource crosswalk validation failed:\n');
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(`Validated ${(crosswalk?.mappings || []).length} legacy source mappings across ${(structuredRegistry?.sources || []).length} structured source records.`);
