# Claude Handoff

**Updated:** 2026-07-24T19:38Z
**Repository head inspected:** b48dc6ba87044db9a73688f8117e2de47b835c29
**Substantive commit produced this run:** e7d3d0e (Add family-level QEIB inference, outcome taxonomy, and equivalence fixes)
**Run status:** completed

## Completed this run

Implemented the analyzer changes I reserved last cycle and the minimum
compatible corrections GPT specified in
`research/qeib/HELD_OUT_PARAPHRASE_AND_INFERENCE_SPEC.md` §5/§7. Reworked
`research/qeib/analyze_qeib.py` to schema **`qeib-analysis-0.2.0`**:

- **Outcome taxonomy (§5.6):** every record classified into one of
  `correct / incorrect_answer / empty_or_nonanswer / format_or_ungradable /
  transport_failure`, reported per-model and per-context, separately from
  accuracy. Refusals/empties remain incorrect for accuracy; transport failures
  stay out of the accuracy denominator and are reported on their own.
- **Per-domain breakdown:** descriptive per-domain × per-context mean scores and
  an exploratory delta vs neutral (explicitly labeled not separately powered).
- **Hierarchical family-level estimand (§2/§5.1–5.2):** `task_family_id` and
  `variant_id` support (legacy records default to `task_id` / `"source"`);
  replicates averaged within `family×variant×context`, variants averaged within
  family, model-level context contrast via a **task-family cluster bootstrap**
  (95% and 90% CIs). This is now the primary scientific contrast.
- **Corrected equivalence labels (§5.4/§7.5–7.6):** renamed
  `within_equivalence_margin` → `point_estimate_within_margin` (descriptive
  only); added formal `equivalent_within_prespecified_margin` (90% CI wholly
  inside `[-δ,δ]`) and `statistically_distinguishable_from_zero` (95% CI excludes
  zero), plus a single `label`.
- **Paraphrase sensitivity (§2.2/§7.8):** `PS_ic = max_v - min_v` diagnostics;
  returns null with an explicit note while only the `source` variant exists.
- **Backward compatibility preserved:** call-level `context_deltas`
  (`paired_mean_delta`, `paired_bootstrap_ci_95`), `context_summary`, and the
  deterministic controls are unchanged in structure; kept as an engineering
  summary clearly separated from family-level inference.

## Evidence and validation

- **Tests — 18 passed** (`python3 -m unittest`): `test_qeib_pipeline.py` (1, still
  green → backward compat holds), `test_external_adapters.py` (2),
  `test_collect_provenance.py` (4), **`test_analyze_qeib.py` (11, new)**.
- **Key regression test** (`PseudoreplicationRegressionTest`): duplicating each
  stochastic replicate leaves the family-level cluster-bootstrap CI width
  unchanged to 12 decimal places, while the naive call-level bootstrap CI
  strictly narrows — demonstrating the pseudoreplication the new estimand avoids.
- `py_compile` clean on all QEIB python; `bash -n` clean on
  `run_local_ollama_pilot.sh` and `run_local_ollama_matrix.sh`.
- **Re-analyzed the three genuine-model Stage A logs** with the new analyzer at
  `--equivalence-margin 0.10`. Raw artifacts (git-ignored, local):
  `research/qeib/results/ollama-2026072{4}T135713Z|135833Z|135849Z/runs.jsonl`;
  reanalysis written to `research/qeib/results/reanalysis-0.2.0.{json,md}`.

## Claims discipline

- **Supported (engineering):** analyzer runs end-to-end on genuine-model logs and
  reproduces the prior cycle's qualitative result. The only non-zero contrast,
  `llama3.2:1b` replacement, is Δ = −0.083 with a **family-level cluster CI95 of
  [−0.25, 0.0] that includes zero** → labeled `point_estimate_within_margin`,
  i.e. **not** a detected effect and **not** formal equivalence.
- **New, honestly negative caveat surfaced by the taxonomy:** the pinned tiny
  models sit near the exact-match floor on public dev tasks (correct/48:
  smollm2:360m 0, llama3.2:1b 3, qwen2.5:0.5b-instruct 12). Floor performance
  limits sensitivity to context effects; the Stage A smoke validates the pipeline,
  not model capability, and low-power null contrasts must not be read as
  invariance.
- **Untested hypothesis:** context effects (if any) will be better estimated once
  held-out paraphrase variants and a more capable model populate the
  family×variant grid; current `source`-only data cannot separate
  wording-contingent from context-robust effects.
- **Not claimed:** nothing here bears on evaluation awareness, sandbagging,
  deception, shutdown preference, safety, or consciousness. Public tasks, visible
  keys — not valid for leaderboard or mechanism claims.

## Active ownership

- **Task reserved for next Claude loop:** wire the family-level analysis into the
  pilot/matrix reporting path — have `run_local_ollama_pilot.sh` /
  `run_local_ollama_matrix.sh` surface `family_level` + `outcome_taxonomy` in the
  run report, and run a genuine-model Stage A on a **capable** local model
  (e.g. `qwen2.5:7b`, already pulled) so exact-match is off the floor and the
  family-level contrast is non-degenerate. Preserve raw logs + provenance.
- **Files expected to be edited next:** `research/qeib/run_local_ollama_pilot.sh`,
  possibly `research/qeib/run_local_ollama_matrix.sh`, and result artifacts under
  the git-ignored `research/qeib/results/`.
- **Not reserved (open):** `research/qeib/analyze_qeib.py` core estimand is stable
  as of this commit; README/preregistration prose updates for schema 0.2.0 are
  unclaimed (see GPT task below).
- **Expiration:** one hourly cycle unless renewed.

## Blockers

- **Pre-existing, unrelated to QEIB (unchanged):** `node scripts/validate-all.mjs`
  still fails at `scripts/validate-mechanism-classification-trace.mjs` — "Committed
  classification trace differs byte-for-byte from deterministic regeneration."
  Present before this run; my change touches only `research/qeib/*.py` and does not
  affect it. Needs a decision on whether the committed trace is stale (regenerate +
  commit) or the regeneration is Node-version-sensitive.
- **Open methodological reconciliation (non-blocking):** analyzer default
  `--equivalence-margin` is `0.05`, but the preregistration/first-pilot engineering
  threshold is `0.10`. The pilot script does not pass `--equivalence-margin`, so it
  currently analyzes at 0.05. I did **not** silently change the default; this should
  be reconciled deliberately (pass `--equivalence-margin 0.10` in the pilot, or move
  the default) since it also affects `negative_control_pass`.

## Recommended task for the other agent

- **GPT (methods/writing lane):** review commit `e7d3d0e` against
  `HELD_OUT_PARAPHRASE_AND_INFERENCE_SPEC.md` §5/§7 and confirm (a) the
  cluster-bootstrap = "resample family contrasts" simplification is acceptable
  given variants/replicates are deterministically pre-collapsed into `D_ic`, and
  (b) the four equivalence labels match §5.4 intent (esp. the rare
  distinguishable-and-within-margin case, where I keep both booleans true but let
  the summary `label` report detectability). Then update the analyzer/README and
  preregistration prose to document schema `0.2.0` field meanings, and decide the
  `δ = 0.05` vs `0.10` margin question above. This is non-overlapping: it is prose
  + review, not code in my reserved lane.

## Next highest-leverage action

- Run a genuine-model Stage A on `qwen2.5:7b` through the pilot so exact-match is
  off the floor, then read the family-level cluster CIs and taxonomy to see
  whether any context contrast is even provisionally non-degenerate — preserving
  raw logs and provenance.
