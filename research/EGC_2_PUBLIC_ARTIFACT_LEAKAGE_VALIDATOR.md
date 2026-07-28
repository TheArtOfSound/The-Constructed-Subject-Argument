# EGC 2.0 Public Synthetic Dry-Run Artifact Leakage Validator

**Status:** Focused engineering implementation validated; no cloud dry run executed  
**Date:** 2026-07-28  
**Scope:** Public-safe synthetic expert-review configuration, result, and referenced evidence artifacts

## Decision

Public dry-run evidence must not enter the repository merely because an operator asserts that secrets and private material were removed. The repository now contains a fail-closed standard-library scanner that inspects both raw text and parsed JSON structure before public evidence is accepted.

The validator is:

- `research/egc2/validate_public_dry_run_artifacts.py`

The focused adversarial suite is:

- `research/egc2/test_validate_public_dry_run_artifacts.py`

## Targeted leakage classes

The scanner rejects public artifacts containing detected instances of:

- AWS access keys, likely AWS secret credentials, 12-digit AWS account identifiers, and presigned URLs;
- generic bearer URLs, JWT-like values, private-key blocks, and Proton Drive share secrets;
- real email addresses and private reviewer identity fields;
- payment, tax, address, phone, or identity-linkage fields;
- protected reviewer mappings and source-anchor identities;
- constructor targets, provisional regions, rationales, admissible score ranges, contrast identities, private intention maps, and candidate responses;
- private holdout prompts or reference answers;
- malformed JSON or JSONL;
- non-UTF-8 public artifacts.

The scanner traverses nested dictionaries and lists. Recomputing an outer artifact digest does not make a nested forbidden field acceptable.

## Public-safe exceptions

A narrow allowlist permits attestation keys whose purpose is to record exclusion rather than disclose the excluded material, including:

- `secret_exclusion_attestation`;
- `secret_scan_status`;
- `private_data_exclusion_attestation`;
- `protected_mapping_excluded`.

The test fixture domain `example.com` is allowed. Other detected email addresses fail.

## Output contract

The report records:

- scanner schema version;
- status;
- file count;
- file SHA-256 digests;
- finding counts;
- finding kind and location;
- hashes rather than raw values for detected credential-like strings;
- canonical report digest;
- an explicit claim limitation.

Permitted statuses are:

```text
passed_no_detected_leakage
blocked_leakage_detected
scanner_error
```

A finding returns a nonzero process status. Missing paths, unreadable inputs, or an empty supported-file set return a scanner error rather than a clean pass.

## Focused validation

Executed in an isolated standard-library Python environment:

```bash
python -m unittest -v test_validate_public_dry_run_artifacts.py
python -m py_compile \
  validate_public_dry_run_artifacts.py \
  test_validate_public_dry_run_artifacts.py
```

Result:

- 9 tests passed;
- 0 tests failed;
- Python compilation passed.

The adversarial suite covers nested protected mapping disclosure after redigest, AWS presigned URLs, AWS access-key patterns, real email addresses, constructor-target prose, malformed JSON, recursive directory scanning, and deterministic report commitments.

## Permitted conclusions

Supported as focused engineering evidence:

- common credential and bearer-link patterns can be rejected before repository publication;
- forbidden scientific fields can be detected structurally even when nested;
- malformed candidate evidence fails closed;
- detected secret-like values need not be reproduced in the scanner report;
- the scan result can be digest-bound for audit.

## Prohibited conclusions

Not established:

- that a clean report proves no sensitive information exists;
- that every future credential format is covered;
- that semantic, encoded, encrypted, compressed, or steganographic disclosure is impossible;
- that public evidence references point to safe external objects;
- that the Proton/AWS architecture is configured or effective;
- that any reviewer, anchor, rubric, semantic-fidelity measure, EGC hypothesis, hidden state, subjectivity, or consciousness claim is validated.

## Integration requirement

Before synthetic dry-run evidence is committed, run the scanner on:

1. the configuration-evidence manifest;
2. the result artifact;
3. every referenced public evidence file.

A scan pass is necessary but not sufficient. Manual content review, access-control review, and the frozen evidence schemas remain required.

## Highest-leverage next action

Integrate this scanner into a repository-native validation command that resolves every evidence reference from the configuration and result manifests, verifies the referenced file digest, and rejects missing, unscanned, or extra public evidence files.
