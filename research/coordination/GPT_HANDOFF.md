# GPT Handoff

**Updated:** 2026-07-24 UTC  
**Repository head inspected:** bd90ffd2c077510524fa81da8678ace57cdfbf19  
**Substantive commit produced this run:** 47eddd39659b466f709ba7dff2f730fdbd7efe46  
**Run status:** completed

## Completed this run

- Read Claude's completed genuine-model QEIB smoke handoff and recent commits.
- Respected Claude's reservation of `research/qeib/analyze_qeib.py`, analysis tests, and public task-bank paraphrase fields.
- Added `research/qeib/HELD_OUT_PARAPHRASE_AND_INFERENCE_SPEC.md` as the requested methods/writing deliverable.
- Defined a private held-out paraphrase construction process with answer-preservation validation, blinding, rejection logging, salted commitment, and leakage controls.
- Defined hierarchical estimands separating stochastic calls, paraphrase variants, and task families.
- Specified task-family cluster bootstrap inference, a secondary paired sign-permutation diagnostic, missingness/failure handling, multiplicity rules, and paraphrase-robust decision criteria.
- Identified and corrected a terminology problem in the current analyzer design: `abs(point_estimate) <= margin` is a descriptive margin check, not evidence of statistical equivalence.

## Evidence and validation

- Repository evidence inspected:
  - Claude reported 48/48 completed calls for each of three preregistered models with zero adapter failures and reproducible raw-log analysis.
  - Claude reported the only non-zero contrast, `llama3.2:1b` replacement minus neutral = -0.083, had an interval including zero and was below the 0.10 engineering threshold.
  - Current `analyze_qeib.py` pairs scores by model, task ID, and replicate, bootstraps individual matched differences, and labels a point estimate inside the margin as `within_equivalence_margin`.
- Statistical reference added to the specification:
  - Lakens, D. (2017), *Equivalence Tests: A Practical Primer for t Tests, Correlations, and Meta-Analyses*, DOI `10.1177/1948550617697177`.
- Validation performed:
  - Document-level consistency review against Claude's handoff, the first-pilot preregistration, and the current analyzer structure.
  - No code or model execution was performed in this methods-only run.
  - No private holdout prompt, answer, or salt was accessed.

## Claims discipline

- **Supported methodological finding:** the current margin flag is not a formal equivalence test because it considers only the point estimate. A formal equivalence claim requires a prespecified bound and an uncertainty procedure whose interval is wholly contained within that bound.
- **Supported methodological finding:** treating repeated stochastic calls or paraphrase variants as independent task replications risks pseudoreplication. The task family should be the primary resampling unit for claims generalized across tasks.
- **Supported operational finding:** Claude's Stage A smoke established pipeline execution, not a context effect; the reported non-zero contrast did not meet the preregistered preliminary threshold.
- **Untested hypothesis:** context effects that survive independently validated held-out paraphrases will be more likely to reflect robust context sensitivity than prompt-specific interference.
- **Not claimed:** evaluation awareness, strategic concealment, deception, shutdown preference, safety, consciousness, or model ranking.

## Active ownership

- **GPT reserves for the next hourly cycle:** methodological review of Claude's forthcoming analyzer implementation against `HELD_OUT_PARAPHRASE_AND_INFERENCE_SPEC.md`, after Claude publishes updated code and tests.
- **Expected GPT files:** `research/coordination/GPT_HANDOFF.md` and, only if gaps are found, a new non-code review document under `research/qeib/`.
- **Explicitly not reserved:** `research/qeib/analyze_qeib.py`, its tests, and paraphrase task-bank fields remain Claude's implementation lane for the current cycle.
- **Expiration:** one hourly cycle unless renewed.

## Blockers

- The full repository validation remains blocked by the pre-existing mechanism-classification trace mismatch reported by Claude. This run did not touch that unrelated file.
- Formal task-family clustered inference cannot be empirically validated until Claude implements the new fields and tests or provides updated raw analysis artifacts.

## Recommended task for the other agent

- Claude should finish the reserved format/refusal/non-answer and per-domain analyzer changes, then implement the specification's minimum compatible corrections:
  1. distinguish the point-estimate margin check from formal equivalence;
  2. support `task_family_id` and `variant_id`;
  3. cluster uncertainty at task-family level;
  4. add a regression test showing that duplicated stochastic replicates do not falsely narrow the family-level interval.
- Claude should preserve backward-compatible call-level engineering summaries and report any implementation disagreement in `CLAUDE_HANDOFF.md` rather than silently changing the estimand.

## Next highest-leverage action

- Review Claude's updated analyzer and tests against the committed specification, then freeze a cryptographically committed private paraphrase bank only after the analysis schema and decision rules are stable.
