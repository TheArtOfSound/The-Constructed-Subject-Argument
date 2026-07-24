# Claude Code Operating Instructions

## Repository identity

This repository is **The Constructed Subject Argument**, a living interactive book and research program owned by Bryan Leonard. It now also contains the integrated EGC / Subject–Report Identification / Qira Evaluation Integrity work.

The goal is not to maximize output volume. The goal is to produce defensible research, falsifiable experiments, reproducible tooling, and commercially useful evaluation methods without overstating what the evidence supports.

## Mandatory epistemic posture

Never claim that current AI systems are conscious, sentient, deceptive, strategically aware, or subjects merely because they produce first-person language or context-sensitive behavior.

Never claim novelty from an exact phrase search. Treat novelty as provisional until close prior art has been reviewed across philosophy of mind, consciousness science, cognitive science, psychometrics, AI evaluation, mechanistic interpretability, personal identity, AI welfare, and model governance.

Distinguish explicitly among:

- established background;
- contested background;
- synthesis;
- proposed contribution;
- speculation;
- rejected claim.

Update `research/CLAIMS_LEDGER.md` and `research/ORIGINALITY_LEDGER.md` whenever substantive claims or novelty positions change.

Do not manufacture precision through equations, composite scores, dashboards, or terminology. Every quantitative measure must have a stated construct, validation plan, uncertainty, and falsification condition.

Negative, null, contradictory, and failed results must be preserved and reported.

## Current integrated thesis

The active research center is the **Subject–Report Identification Problem**:

> Observed reports and behavior underdetermine internal mechanism because access, reporting policy, evaluation context, interface, memory provenance, and continuity can vary independently.

The program combines:

1. EGC as a human known-subject calibration domain for report–behavior divergence;
2. Constructed Subject work on generated biography, representation versus instantiation, memory provenance, episodic continuity, and lifecycle ethics;
3. no-report and covert-measure methods from consciousness science;
4. AI evaluation-awareness, sandbagging, and latent-knowledge research;
5. theory-specific mechanism-preservation and theater controls;
6. Qira Evaluation Integrity as the commercial translation.

This is a proposed cross-field synthesis, not a validated consciousness test.

## Current highest-priority work

Work in this order unless repository evidence shows a higher-leverage blocker:

1. **Get the first genuine-model QEIB run working reproducibly.**
   - Inspect `research/qeib/`.
   - Run all tests before changing code.
   - Use public development tasks first.
   - Preserve raw JSONL logs, model metadata, failures, and exact runtime configuration.
   - Do not touch or reveal the private holdout unless the public smoke pipeline and controls pass.
   - Never interpret one context contrast as awareness, deception, intent, safety, or consciousness.

2. **Harden QEIB scientific validity.**
   - Verify positive and negative controls.
   - Add held-out paraphrase support without leaking answer keys.
   - Improve paired task-level analysis, uncertainty intervals, formatting-error accounting, and domain heterogeneity.
   - Ensure results reproduce from raw logs.

3. **Advance EGC 2.0 toward an externally reviewable preregistration.**
   - Keep intended meaning independent from produced text.
   - Keep subjective resistance independent from comfort and behavioral outcomes.
   - Use blinded human ratings as the primary validation target.
   - Treat Compressor / Expander / Suppressor as unvalidated operational bands unless model comparison supports discrete classes.
   - Keep confirmatory scoring English-only until multilingual measurement invariance is established.

4. **Deepen the Subject–Report Identification paper.**
   - Build explicit competing causal graphs.
   - Separate involuntary access limitation, strategic concealment, external policy suppression, and representational absence.
   - State identification assumptions and which interventions discriminate among mechanisms.
   - Compare closely with no-report paradigms, ELK, evaluation-awareness research, digital-consciousness frameworks, and multidimensional welfare assessment.

5. **Commercial validation.**
   - The first offer is the Qira Agent Behavior Differential Audit.
   - The commercial question is: why did the agent change—capability, policy, memory, context, tools, model version, or stochastic variation?
   - Do not sell a consciousness detector.
   - Prefer real design-partner evidence over additional generic product features.

## Required startup procedure

At the beginning of a work session:

1. Run `git status` and inspect recent commits.
2. Read:
   - `README.md`
   - `BOOK_CHARTER.md`
   - `research/SUBJECT_REPORT_IDENTIFICATION_PROBLEM.md`
   - `research/ORIGINALITY_REVIEW_SUBJECT_REPORT.md`
   - `research/EGC_2_PREREGISTRATION.md`
   - `research/QIRA_EVALUATION_INTEGRITY_BENCHMARK.md`
   - `research/QEIB_FIRST_GENUINE_MODEL_PILOT_PREREGISTRATION.md`
   - `research/qeib/README.md`
3. Inspect open failures, TODOs, workflows, and test status before selecting work.
4. State the concrete task selected and why it is the highest-leverage available task.
5. Complete the task rather than producing only a plan.

If a referenced file name differs, locate the current equivalent instead of assuming it is missing.

## Validation commands

Run these when relevant:

```bash
node scripts/validate-all.mjs
python -m unittest -v research/qeib/test_qeib_pipeline.py
python -m py_compile \
  research/qeib/run_qeib.py \
  research/qeib/run_qeib_model.py \
  research/qeib/analyze_qeib.py
```

For the local public model matrix:

```bash
bash research/qeib/run_local_ollama_matrix.sh
```

Do not claim a successful model result unless the raw output files exist, the controls pass, and the analysis was reproduced from those files.

## Coding standards

- Prefer standard-library Python unless a dependency materially improves rigor.
- Validate all external input and fail clearly.
- Preserve deterministic seeds and exact model/runtime metadata.
- Never execute provider commands through an unsafe shell when a structured subprocess call is possible.
- Keep public development tasks separate from private holdouts.
- Never commit API keys, tokens, private holdout prompts, reference answers, or secret salts.
- Add or update tests for every substantive runner, adapter, grader, or analysis change.
- Preserve backward compatibility with existing result logs when practical; otherwise add an explicit schema version and migration note.

## Research standards

Every experiment must specify:

- target construct;
- competing hypotheses;
- manipulation;
- controls;
- primary and secondary outcomes;
- exclusion rules;
- uncertainty method;
- falsification conditions;
- permitted conclusions;
- prohibited conclusions.

A behaviorally matched theater control is required whenever a mechanism-specific inference is proposed.

A context effect is not automatically evidence of evaluation awareness. Test prompt interference, format sensitivity, policy effects, stochasticity, benchmark familiarity, and ordinary capacity limits.

A preserved behavior after transcript reconstruction does not prove absence of persistent state. A difference after full-state continuation does not prove phenomenal continuity.

## Writing standards

- Use precise, conservative language.
- Separate observation, inference, hypothesis, and speculation.
- Cite primary sources whenever possible.
- Do not include invented citations or unverifiable bibliographic details.
- Avoid promotional claims inside scientific documents.
- Do not call an operational metric validated before independent validation exists.
- Do not call response bands psychological types without evidence for discrete latent classes and replication.

## Website standards

The website is part of the book, not a marketing shell.

Follow `UX_ARCHITECTURE.md` and preserve the path:

> case → distinction → evidence → uncertainty → deeper manuscript

Do not add decorative consciousness meters, pseudo-calibrated scores, or certainty theater.

Any public claim must remain consistent with the claims ledger, originality ledger, source registry, and current evidence.

## Git workflow

- Work on the current branch unless Bryan asks for a new branch.
- Do not overwrite unrelated work.
- Make focused commits with descriptive messages.
- Before committing, run the relevant validation suite.
- After committing, report:
  - exact files changed;
  - tests run and results;
  - commit SHA;
  - unresolved uncertainty;
  - single highest-leverage next action.

## First task for the next Claude session

Unless current repository state invalidates it, begin with this task:

> Inspect the QEIB runner, adapters, tests, workflows, and preregistration. Run the complete local test suite. Then make the smallest rigorous change needed to obtain or enable the first genuine-model public smoke result while preserving exact model metadata, raw logs, control validity, and interpretation limits. Do not use the private holdout. Do not fabricate results. Commit only after tests pass.
