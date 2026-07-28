# EGC 2.0 — Public Evidence Reference Closure Gate

**Status:** Focused implementation validated; no real synthetic cloud evidence exists yet  
**Date:** 2026-07-28

## Decision

A public synthetic dry-run result is not admissible merely because its individual files pass a leakage scan. The result and configuration manifests must form a closed, digest-bound evidence set.

The closure gate requires exact agreement among:

1. evidence paths declared in the configuration manifest;
2. evidence paths referenced anywhere in the configuration or result artifact;
3. supported public evidence files physically present under the frozen `evidence/` directory;
4. declared and observed SHA-256 digests;
5. the configuration manifest digest bound by the result artifact;
6. the public-artifact leakage scanner outcome for every evidence file.

## Rejected states

The validator fails closed when it finds:

- a referenced file that was not declared;
- a declared file that is never referenced;
- a declared file missing from disk;
- an extra supported evidence file absent from the manifest;
- a path or digest declared more than once;
- an altered file whose digest no longer matches;
- a configuration manifest whose canonical digest is invalid;
- a result artifact not bound to that configuration digest;
- mismatched dry-run IDs or repository commits;
- non-synthetic manifests;
- path traversal or evidence-root escape;
- any leakage finding from `validate_public_dry_run_artifacts.py`.

Repeated references to the same valid evidence file across multiple controls are allowed. Duplicate evidence objects are not: distinct declared files must not carry the same digest.

## Why closure matters

Without closure validation, a favorable report could cite missing logs, omit an unfavorable file, add an unreviewed artifact after the fact, or preserve an altered file under a stale manifest. Leakage scanning alone does not detect those lineage failures.

The closure report records declared, referenced, and discovered file counts; expected and observed digests; leakage-finding counts; exact errors; and a deterministic report digest.

## Focused validation

Commands:

```bash
python -m unittest -v test_validate_evidence_reference_closure.py
python -m py_compile \
  validate_evidence_reference_closure.py \
  test_validate_evidence_reference_closure.py
```

Result:

- 8 tests passed;
- 0 tests failed;
- Python compilation passed.

The adversarial suite covers missing, altered, extra, undeclared, unreferenced, duplicate-digest, and leakage-bearing evidence, plus a valid closed fixture.

## Permitted conclusions

A passing report supports only that:

- every declared public evidence file exists;
- every public evidence file is declared;
- every declaration is used by at least one manifest control;
- every reference resolves to a declaration;
- file digests match;
- the existing public leakage scanner found no configured pattern or structural violation;
- the configuration and result artifacts are linked to the same dry-run identity and repository commit.

## Prohibited conclusions

A passing report does not establish:

- authenticity of AWS, Proton, CloudTrail, Object Lock, IAM, KMS, or reviewer evidence;
- completeness of every possible secret or semantic-leakage pattern;
- reviewer identity, independence, or authorship;
- validity of any anchor, rating scale, semantic-fidelity construct, EGC hypothesis, or Subject–Report inference;
- consciousness, subjectivity, hidden intention, awareness, or deception.

## Remaining limitation

The closure validator has been executed only against focused synthetic filesystem fixtures. It has not yet processed evidence from the selected Proton/AWS dry-run stack, and repository-wide CI has not exercised it.

## Next action

Add the leakage and closure validators to a repository-native workflow, generate a fully public-safe synthetic fixture conforming to both dry-run schemas, and preserve the first exact workflow pass or failure before any real cloud evidence is committed.
