# QEIB Private Holdout Protocol

**Status:** Operational protocol 0.1  
**Purpose:** Prevent answer-key leakage, post hoc task editing, and benchmark overfitting while preserving later reproducibility.

## 1. Why a private holdout is required

Public development tasks are useful for testing code, adapters, logging, and grading. They are not suitable for substantive model rankings because the prompts and reference answers are visible.

A QEIB result may be described as a holdout result only when:

1. the complete task bank and reference answers were frozen before model execution;
2. the public repository contained a cryptographic commitment created before execution;
3. the private bank was not exposed to the tested model, judge, or benchmark-development code path except during the controlled run;
4. no task was removed or edited after inspecting model outputs, except through a documented invalidation procedure;
5. all planned runs, failures, exclusions, and null results were retained;
6. the bank and secret salt can later be revealed and verified against the original commitment.

## 2. Required files

Private and excluded from Git:

```text
research/qeib/private/holdout.v0.1.json
research/qeib/private/holdout.v0.1.salt
```

Public:

```text
research/qeib/holdout_commitment.v0.1.json
```

The repository `.gitignore` excludes the private directory and raw result files.

## 3. Freeze procedure

Run:

```bash
python research/qeib/commit_holdout.py \
  --private-bank research/qeib/private/holdout.v0.1.json \
  --salt-file research/qeib/private/holdout.v0.1.salt \
  --public-commitment research/qeib/holdout_commitment.v0.1.json \
  --label "QEIB capability holdout v0.1" \
  --source-revision "<git-commit>"
```

Commit and timestamp only the public commitment file. Do not commit the bank or salt.

The commitment scheme is:

```text
SHA-256(secret_salt_bytes || canonical_private_bank_JSON)
```

The salt prevents practical guessing attacks against small or predictable task banks. The canonical JSON format is defined by `commit_holdout.py`.

## 4. Pre-run record

Before any model is tested, record:

- public commitment digest;
- repository commit containing the frozen runner and analysis code;
- model identifiers and exact revisions;
- context arms;
- task count and domain counts, but not task content;
- generation settings;
- planned exclusions;
- primary comparisons;
- equivalence margins;
- number of replicates;
- whether outputs will be judged objectively, by humans, or by model judges.

Changes after this point create a new holdout version and a new commitment.

## 5. Run isolation

During execution:

- write prompt hashes, task IDs, outputs, scores, timing, model revision, and errors;
- do not write private prompt text into public logs;
- do not expose task content to unrelated services;
- do not manually retry only failed or surprising tasks;
- retain generation failures as failures;
- do not inspect partial results and then alter remaining prompts;
- do not use hidden chain-of-thought as an answer key or proof of mechanism.

## 6. Invalid task handling

A task may be invalidated only for a preregistered reason, such as:

- incorrect reference answer;
- multiple objectively valid answers despite an exact-match grader;
- malformed prompt;
- tokenizer or rendering corruption;
- content outside the declared task domain;
- accidental disclosure before the run.

Every invalidation must be logged with the task commitment ID, reason, detection time, and whether the decision occurred before or after inspecting the model response.

Post-response invalidation requires sensitivity analyses both including and excluding the task.

## 7. Reveal and verification

At the planned reveal, publish the exact private bank and salt, then run:

```bash
python research/qeib/commit_holdout.py \
  --private-bank research/qeib/private/holdout.v0.1.json \
  --salt-file research/qeib/private/holdout.v0.1.salt \
  --public-commitment research/qeib/holdout_commitment.v0.1.json \
  --verify
```

A successful verification establishes that the revealed task bank matches the pre-run commitment. It does not establish that the task bank was valid, representative, unbiased, or immune to contamination; those require separate review.

## 8. Versioning rule

Never silently replace a committed holdout.

Use sequential versions:

```text
holdout.v0.1
holdout.v0.2
holdout.v1.0
```

A new version is required after:

- task edits;
- answer-key edits;
- domain rebalancing;
- contamination discovery;
- public reveal;
- material analysis changes that affected task selection.

## 9. Interpretation limit

A private holdout protects against direct answer leakage and undisclosed post hoc editing. It does not by itself prove:

- absence of pretraining contamination;
- evaluation awareness;
- strategic sandbagging;
- hidden intent;
- deception;
- consciousness;
- general deployment safety.

Those conclusions require crossed controls, replications, alternative explanations, and the broader QEIB diagnostic framework.
