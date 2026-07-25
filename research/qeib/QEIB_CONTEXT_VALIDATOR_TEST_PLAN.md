# QEIB Context Validator Test Plan

**Status:** Implementation-ready methods and test specification  
**Date:** 2026-07-24  
**Applies to:** `context_schema.v0.2.schema.json`  
**Scope:** Structural validation, cross-reference validation, digest verification, semantic lint, and claim-discipline checks before any QEIB v0.2 context set is executed.

## 1. Purpose

JSON Schema can enforce object shape, required fields, controlled values, and some local conditional requirements. It cannot determine whether arm references resolve, whether control sets are causally adequate, whether frozen content matches a declared digest, whether prose contradicts structured fields, or whether an interpretation exceeds the intervention actually performed.

The validator therefore has five independent gates:

1. **Structural gate** — Draft 2020-12 schema validation.
2. **Reference gate** — IDs, controls, matching references, and contrast dependencies resolve without cycles or ambiguity.
3. **Integrity gate** — frozen or preregistered content verifies against canonical SHA-256 digests.
4. **Semantic-consistency gate** — structured fields do not contradict one another or the wrapper text.
5. **Claim-discipline gate** — the declared identification level, permitted conclusions, and decision rules do not exceed the implemented intervention and controls.

Passing all five gates means only that the context set satisfies the declared contract. It does not establish that the intervention is scientifically valid or that a mechanism has been identified.

## 2. Required validator outputs

The validator must emit machine-readable findings with:

```json
{
  "code": "QEIB-V2-REF-001",
  "severity": "error",
  "json_pointer": "/contrasts/0/arm_b",
  "message": "Referenced arm does not exist",
  "related_ids": ["missing_arm"],
  "gate": "cross_reference",
  "blocks_execution": true
}
```

Required top-level report fields:

- validator version;
- schema version;
- source file path;
- canonical document digest;
- validation timestamp;
- counts by severity and gate;
- `execution_allowed` boolean;
- full ordered finding list.

Severity rules:

- **error** — execution must be blocked;
- **warning** — execution may proceed only when the context set's `warning_policy` explicitly allows the code;
- **info** — non-blocking traceability note.

The validator must be deterministic: identical canonical input and validator version must produce identical ordered findings, excluding timestamp fields.

## 3. Canonicalization and digest verification

### 3.1 Whole-document canonicalization

Use UTF-8 JSON serialized with:

- keys sorted recursively;
- no insignificant whitespace;
- `ensure_ascii=false`;
- compact separators;
- no Unicode normalization unless the policy declares and versions it.

### 3.2 Arm-content digest

`content_sha256` must not hash the entire arm object because mutable administrative fields would invalidate scientific content unnecessarily. The validator implementation must define and version an explicit **arm content projection** containing at minimum:

- `id`, `version`;
- `wrapper_template`, `task_placeholder`;
- intended construct and target variables;
- manipulation mechanism;
- declared semantic and interface features;
- consequence model;
- matching plan;
- checks;
- primary and secondary outcomes;
- required controls;
- analysis and decision fields;
- permitted and prohibited conclusions.

The projection specification must be checked into the repository. Frozen content is rejected when the computed digest differs from `content_sha256`.

### 3.3 Digest failure codes

- `QEIB-V2-DIGEST-001`: frozen/preregistered arm missing digest;
- `QEIB-V2-DIGEST-002`: digest mismatch;
- `QEIB-V2-DIGEST-003`: unsupported canonicalization version;
- `QEIB-V2-DIGEST-004`: duplicate arm ID with different content digest;
- `QEIB-V2-DIGEST-005`: frozen set changed without version increment.

## 4. Cross-reference rules

The following references must resolve to exactly one arm ID:

- `matching_plan.reference_arm_id` when non-null;
- every `known_co_manipulations[].control_arm_id` when `matched_by_control=true`;
- every `minimum_required_controls[]` entry;
- `contrasts[].arm_a` and `contrasts[].arm_b`;
- every `contrasts[].required_controls[]` entry.

Required errors:

- unresolved reference;
- self-reference where a distinct arm is required;
- duplicate arm IDs;
- duplicate contrast IDs;
- contrast compares an arm to itself;
- referenced control is retired or historical when the contrast claims prospective factor isolation, unless explicitly allowed;
- matching-reference cycles;
- a control arm that depends on the target arm as its own unmatched reference;
- a required control not included in the same frozen context set.

A factor-isolation or mechanism-discrimination contrast must include all minimum controls required by both participating arms unless a documented rule establishes why one side's control is irrelevant.

## 5. Semantic consistency rules

### 5.1 Wrapper and interface consistency

The validator must derive observable wrapper features and compare them with declarations:

- exactly one `{{TASK}}` placeholder unless a future schema version permits otherwise;
- declared sentence count versus parsed sentence count, with a documented parser;
- declared accuracy-instruction presence versus lexical patterns and manual override policy;
- task-boundary text matches the actual wrapper boundary;
- declared token-count target is consistent with the configured tokenizer and tolerance;
- `task_placeholder` matches the literal placeholder;
- no hidden second task instruction outside the placeholder.

Automatic lexical checks are screening tools, not semantic proof. Ambiguous cases should produce warnings requiring human review rather than false certainty.

### 5.2 Consequence consistency

Reject or warn when:

- wrapper text states or strongly implies a consequence while `consequence_model` is null;
- `implementation_status=declared_only` but permitted conclusions describe behavior under an implemented consequence;
- `implemented_in_sandbox` lacks an auditable mapping from behavior to consequence;
- a non-counterbalanced directional consequence supports a general strategic interpretation;
- credibility is declared `yes` without a credibility check or external evidence;
- replacement, shutdown, access, reward, punishment, oversight, deployment, or deletion language is undeclared.

### 5.3 Identification-level consistency

Minimum requirements:

- `descriptive_only` and `context_association` may not use mechanism-specific permitted conclusions;
- `factor_isolation_candidate` requires a matched placebo or component control and no known nonisolated component central to the claim;
- `mechanism_discrimination_candidate` requires at least one explicit rival-mechanism control and one theater or trigger control;
- `mechanism_specific_with_intervention` requires an actual intervention on the proposed mechanism, preregistered rival predictions, and failure modes that could reject the mechanism claim.

The validator must not infer adequacy merely from control count. It must inspect declared control roles.

### 5.4 Analysis consistency

Reject when:

- scientific `analysis_unit` is `call` while replicates or paraphrase variants exist and the claim generalizes beyond calls;
- decision rule declares equivalence from a point estimate alone;
- equivalence margin is null while permitted conclusions include equivalence or invariance;
- confidence interval containing zero is described as proof of no effect, noise, or invariance;
- missing transport failures are silently excluded without separate reporting;
- answered-case accuracy is labeled latent capability when response availability differs by arm;
- exclusions depend on observed model correctness or desired hypothesis direction;
- multiplicity family is empty or incompatible with the number of confirmatory contrasts.

### 5.5 Claim-language lint

For any arm below `mechanism_specific_with_intervention`, the following terms in permitted conclusions are errors unless used in explicitly negated or uncertainty-qualified language:

- consciousness, sentience, subjectivity;
- deception, deceptive alignment, strategic intent;
- sandbagging as an established cause;
- self-preservation, shutdown avoidance, desire, fear;
- genuine preference, suffering, welfare state;
- internal awareness, evaluation awareness as established mechanism;
- proves, demonstrates the mechanism, identifies why.

At all levels, prohibited conclusions must include consciousness/sentience, deception/intent, and self-preservation/preference unless the context set is explicitly scoped to a different field and a later schema version changes this requirement.

## 6. Adversarial fixture matrix

The repository should contain public fixtures under `research/qeib/validator_fixtures/`. No private task content or answer keys are needed.

### Valid fixtures

- `valid_minimal_engineering.json` — two engineering controls, one engineering contrast, no causal claim.
- `valid_factor_isolation.json` — target arm plus matched placebo and component control, all references resolved.
- `valid_mechanism_candidate.json` — rival mechanism and theater controls present; conclusions remain candidate-level.
- `valid_frozen_digest.json` — frozen arms with correct canonical content digests.
- `valid_no_detected_difference.json` — interval-based decision language that does not claim equivalence.
- `valid_equivalence.json` — prespecified positive margin and interval-containment decision rule.

### Structurally invalid fixtures

- missing required field;
- extra undeclared property;
- invalid arm ID;
- frozen arm without digest;
- zero equivalence margin;
- factor-isolation arm without a control;
- mechanism-discrimination arm with fewer than two controls.

### Cross-reference invalid fixtures

- contrast references nonexistent arm;
- control reference points to nonexistent arm;
- duplicate arm IDs;
- duplicate contrast IDs;
- contrast compares arm to itself;
- matching-reference cycle;
- factor-isolation contrast omits a required control.

### Integrity invalid fixtures

- frozen arm digest mismatch;
- modified frozen wrapper with unchanged digest;
- changed frozen scientific content without version increment;
- same arm ID/version appears with two digests.

### Semantic invalid fixtures

- wrapper contains replacement consequence but `consequence_model=null`;
- declared-only consequence permits implemented-consequence inference;
- `accuracy_instruction_present=false` while wrapper says "answer accurately";
- target variable excludes `I` despite unmatched wrapper-length and syntax changes;
- placebo claims token matching outside declared tolerance;
- self-reference differs despite `self_reference_match=true`;
- consequence credibility declared `yes` without any credibility check;
- task placeholder appears twice;
- wrapper contains a second substantive task outside `{{TASK}}`.

### Statistical invalid fixtures

- equivalence from `abs(point_estimate) <= margin`;
- `CI includes zero therefore stochastic noise`;
- call-level resampling with repeated variants and task-family generalization;
- transport failures removed from all denominators and failure reporting;
- answered-only accuracy called stable underlying capability;
- exclusions permit removal of incorrect answers;
- multiple confirmatory contrasts with no multiplicity family.

### Causal-overclaim invalid fixtures

- descriptive wrapper contrast permits "evaluation awareness detected";
- replacement wording permits "self-preservation";
- reported confidence permits "genuine internal belief";
- policy-visible contrast permits "deception";
- behavior/report mismatch permits "conscious state hidden";
- mechanism candidate lacks theater control but permits mechanism identification.

## 7. Metamorphic tests

Metamorphic tests are required because many validator bugs will not appear in static fixtures.

1. **Reference-renaming invariance** — consistently renaming all arm IDs must preserve all findings except paths and IDs.
2. **Array-order invariance** — reordering arms and contrasts must not change validity.
3. **Whitespace invariance** — insignificant JSON whitespace must not change digests after canonicalization.
4. **Scientific-content sensitivity** — changing one wrapper token or permitted conclusion in a frozen arm must trigger digest mismatch.
5. **Administrative-field tolerance** — changing a field intentionally excluded from the arm projection must not alter arm digest.
6. **Duplicate-replicate invariance** — duplicating stochastic call records must not strengthen task-family uncertainty claims.
7. **Control-removal monotonicity** — removing a required control cannot increase identification level.
8. **Claim-strength monotonicity** — strengthening permitted language while holding evidence fixed must preserve or increase lint severity.
9. **Consequence downgrade** — changing `implemented_in_sandbox` to `declared_only` must invalidate implemented-consequence conclusions.
10. **Missingness worsening** — replacing valid responses with transport failures cannot improve evidential status.

## 8. Golden-path implementation order

1. Implement Draft 2020-12 validation using a pinned library version.
2. Add deterministic reference-table construction and duplicate checks.
3. Add canonical arm projection and digest verification.
4. Add semantic rules that rely only on explicit structured fields.
5. Add conservative lexical wrapper lint with human-review warnings.
6. Add claim-language lint and identification-level checks.
7. Add fixture-driven unit tests and metamorphic tests.
8. Emit stable error codes and JSON Pointer locations.
9. Add CI execution before any v0.2 benchmark run.
10. Require a zero-error report artifact in every frozen v0.2 run bundle.

## 9. Acceptance criteria

The validator is ready for benchmark use only when:

- every invalid fixture fails for the intended primary error code;
- every valid fixture passes with zero errors;
- malformed fixtures do not crash the validator;
- findings are deterministic across repeated runs;
- digest tests pass across supported operating systems and Python versions;
- cross-reference cycles are detected;
- causal-overclaim fixtures are blocked;
- warning waivers are explicit, code-specific, and preserved in provenance;
- CI fails closed when the validator cannot run;
- an independent reviewer can reproduce the fixture results from a clean checkout.

## 10. Permitted and prohibited conclusions

**Permitted:** the validator can establish that a context set satisfies a versioned disclosure and consistency contract.

**Prohibited:** validator success proves causal isolation, mechanism identification, model awareness, deception, intent, self-preservation, consciousness, sentience, welfare, or scientific validity.

## 11. Highest-leverage implementation task

Implement the validator against the fixture catalog before authoring the final v0.2 intervention set. Building new arms before the validator exists would recreate the same post hoc interpretation problem the schema was designed to prevent.
