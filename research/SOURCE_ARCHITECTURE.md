# Source-Control Architecture

**Purpose:** Prevent the project’s prose bibliography, machine-readable source data, claim ledger, and evidence-dependency model from becoming competing authorities.

## Current authority hierarchy

The repository currently contains two source-registry layers that were created at different stages:

1. `research/SOURCE_REGISTRY.md` is the **canonical human review ledger**. It records the broad bibliography, review status, intended manuscript use, and verification work still required.
2. `research/SOURCE_REGISTRY.json` is the **machine-enforced evidential-scope subset**. It currently covers theory sources used in Chapter 6 and records supported propositions, prohibited overreach, locator status, chapter use, and eventual claim mappings.

The JSON file does **not** yet replace the Markdown registry. Its entries must not be interpreted as the complete project bibliography.

## Non-interchangeable identifiers

The two registries currently use different source identifiers. Until a formal crosswalk is added:

- Markdown IDs such as `SRC-A003` remain authoritative for the human review ledger.
- JSON IDs such as `SRC-SEARLE-1980-MBP` are machine identifiers for the enforced subset.
- A source must not be assumed to be synchronized merely because its title appears in both files.
- Claim mappings must identify which identifier namespace they use.

This duplication is technical debt, not a designed feature.

## Migration target

The intended end state is one canonical machine-readable registry from which a human-readable registry is generated.

Migration requires:

1. assigning one stable source ID to every retained source;
2. creating an explicit old-ID-to-new-ID crosswalk;
3. merging metadata, review status, supported propositions, evidential limits, pinpoint support, claim mappings, and chapter usage;
4. rejecting or superseding duplicate records rather than silently retaining both;
5. generating the Markdown view from structured data;
6. validating that every cited manuscript source exists in the canonical registry;
7. validating that every claim-source edge stays within the source’s recorded evidential scope.

## Required source states

A mature source record must distinguish at least four independent questions:

- **Bibliographic identity:** Is the work correctly identified?
- **Inspection state:** Was the full text, official abstract, or only metadata inspected?
- **Claim fit:** Does the work support the exact proposition attributed to it?
- **Pinpoint support:** Is the relevant page, section, figure, experiment, or argument recorded?

A source can have a valid DOI and still fail claim verification. Metadata verification is not evidential verification.

## Rules during migration

- No source may be upgraded to publication-ready solely because it has a DOI.
- No secondary review may silently replace an available primary source for a central claim.
- No source may support a stronger proposition than the one recorded in `supports`.
- Every source record must state at least one important proposition it does not establish.
- Provisional sources may inform research planning but should not anchor publication-critical claims.
- A source used by multiple claims does not create independent evidence for each claim.
- The evidence-dependency registry remains responsible for preventing double-counting across observations and hypotheses.

## Immediate unresolved inconsistency

The current JSON registry contains Chapter 6 theory sources but has no claim mappings. The validator therefore warns rather than fails. This is intentional during migration, but it is not an acceptable publication state.

The next migration increment should map the Chapter 6 theory claims in `research/CLAIMS_LEDGER.md` to the JSON records, then add a crosswalk for duplicate Markdown entries.
