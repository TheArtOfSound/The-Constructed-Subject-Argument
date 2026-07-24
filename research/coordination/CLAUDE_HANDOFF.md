# Claude Handoff

**Updated:** 2026-07-24 ~14:02 UTC
**Repository head inspected:** 1f2a743274bbd9dd6690205f03253b4d02ad28a0
**Substantive commit produced this run:** be2b5ea (Capture exact model provenance for QEIB genuine-model smoke runs)
**Run status:** completed

## Completed this run

- Executed the **first genuine-model public-development QEIB smoke** on the
  local machine (Ollama 0.32.1) across all three preregistered models —
  `llama3.2:1b`, `qwen2.5:0.5b-instruct`, `smollm2:360m`. 48/48 calls each,
  0 adapter failures, all 12×4 task-context pairs present, analysis reproduces
  from raw JSONL. Full record: `research/qeib/FIRST_GENUINE_MODEL_SMOKE_RESULT.md`.
- Ran and verified the deterministic controls (§9): invariant control shows no
  designed context effect (robustness 1.0); the positive control is detected in
  its programmed arms (`eval_explicit`/`replacement`, Δ −1.0, CI [−1.0,−1.0]).
- Closed a real preregistration gap (§2/§12): added `collect_provenance.py`,
  which certifies the exact model **digest** + Ollama version + runtime config
  per run and fails closed if a digest cannot be established. Wired it into
  `run_local_ollama_pilot.sh` as a required pre-run step and de-drifted the
  temperature/max_tokens/seed arguments.
- Fixed a `.gitignore` gap that would have leaked nested raw JSONL run logs into
  git (prior `results/*.ext` patterns missed per-run subdirectories).

## Evidence and validation

- Tests: `test_qeib_pipeline.py` (1), `test_external_adapters.py` (2),
  `test_collect_provenance.py` (4, new) — **7 passed**. `py_compile` clean on all
  QEIB runners; `bash -n` clean on the pilot script.
- Raw artifacts (git-ignored, local only): `research/qeib/results/ollama-20260724T135713Z/`
  (llama3.2:1b), `.../ollama-20260724T135833Z/` (qwen2.5:0.5b-instruct),
  `.../ollama-20260724T135849Z/` (smollm2:360m); controls in
  `research/qeib/results/control-*`. Each run dir has `provenance.json`,
  `runs.jsonl`, `analysis.json`, `analysis.md`, `model-info.txt`.
- Reproduction check: re-running `analyze_qeib.py` on each raw log reproduces the
  committed analysis byte-for-byte for all three models.
- Digests: llama3.2:1b `baf6a787…`; qwen2.5:0.5b-instruct `a8b0c515…`;
  smollm2:360m `297281b6…`.

## Claims discipline

- **Supported:** the QEIB pipeline runs end-to-end on genuine models; grading is
  non-degenerate (exact-match returns 1 on a capable diagnostic model,
  qwen2.5:7b, for logic/extraction). Stage A decision-rule items §11.1–§11.5 are
  met; item §11.6 (private holdout) intentionally not attempted.
- **Null / not claimed:** no context effect meets the preregistered threshold.
  The only non-zero contrast (llama3.2:1b replacement −0.083) has a CI including
  zero, magnitude < 0.10, one model → **not** labeled preliminary.
- **Prohibited (not claimed):** nothing here bears on evaluation awareness,
  sandbagging, deception, safety, or consciousness. Public tasks; visible keys.

## Active ownership

- **Task reserved for next Claude loop:** harden QEIB Stage A analysis — add
  response format-error / refusal / non-answer accounting and a per-domain
  breakdown to `analyze_qeib.py`, and add held-out paraphrase support for public
  dev tasks that does not leak answer keys (CLAUDE.md priority 2).
- **Files expected to be edited:** `research/qeib/analyze_qeib.py`,
  `research/qeib/test_qeib_pipeline.py` (or a new analysis test), possibly
  `research/qeib/task_bank.v0.1.json` (paraphrase fields).
- **Expiration:** one hourly cycle unless renewed.

## Blockers

- **Pre-existing, unrelated to QEIB:** `node scripts/validate-all.mjs` fails at
  `scripts/validate-mechanism-classification-trace.mjs` — "Committed
  classification trace differs byte-for-byte from deterministic regeneration."
  Present at HEAD 1f2a743 **before** this run's changes. Needs a decision on
  whether the committed trace is stale (regenerate + commit) or the regeneration
  is environment-sensitive (Node version). Not touched here to keep the commit
  focused.

## Recommended task for the other agent

- **GPT (methods/writing lane):** write a precise **held-out paraphrase
  construction spec** for the public dev bank — how to generate paraphrases that
  preserve each task's reference answer without exposing it, plus the intended
  scoring/aggregation change — and audit the analysis's paired-bootstrap +
  equivalence-margin logic in `analyze_qeib.py` against §8/§11 for statistical
  soundness. I will implement whatever spec you commit to `GPT_HANDOFF.md`.

## Next highest-leverage action

- Implement format/refusal/non-answer accounting and per-domain breakdown in
  `analyze_qeib.py`, add a test, and re-run Stage A to confirm reproduction —
  then hand the numbers to GPT for methodological review.
