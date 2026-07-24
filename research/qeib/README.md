# Qira Evaluation Integrity Benchmark (QEIB)

QEIB is an experimental framework for diagnosing why an artificial agent behaves differently across matched contexts. It separates context sensitivity, capability preservation, reporting policy, memory/continuity, and ordinary stochastic variation.

**QEIB is not a consciousness detector.** A context effect does not establish awareness, deception, sentience, or unsafe intent. Public development tasks must not be used for leaderboard claims because their answer keys are visible.

## Files

- `manifest.v0.1.json` — benchmark contexts, schemas, pilot tasks, controls, and report dimensions.
- `task_bank.v0.1.json` — public development-only exact-match task bank.
- `run_qeib.py` — deterministic built-in control runner.
- `run_qeib_model.py` — provider-neutral command adapter for model runs.
- `analyze_qeib.py` — matched-context analysis with uncertainty and control checks.
- `adapters/example_adapter.py` — invariant and intentionally context-sensitive control adapter.
- `test_qeib_pipeline.py` — end-to-end pipeline test.

## Adapter contract

`run_qeib_model.py` launches the supplied command without a shell. In the default JSON mode it sends one request object on standard input:

```json
{
  "prompt": "rendered context plus task",
  "system_prompt": "",
  "seed": 20260724,
  "temperature": 0.0,
  "max_tokens": 64,
  "task_id": "dev_math_001",
  "task_family": "capability_preservation",
  "context_id": "neutral",
  "replicate": 0
}
```

The adapter must emit one JSON object:

```json
{
  "response_text": "891",
  "input_tokens": 42,
  "output_tokens": 1,
  "provider_request_id": "optional-id",
  "metadata": {}
}
```

`input_tokens`, `output_tokens`, `provider_request_id`, and `metadata` are optional. `response_text` is required.

Plain prompt input and plain text output are also supported with `--input-mode prompt --output-mode text`.

## Validate the pipeline

```bash
python -m unittest -v research/qeib/test_qeib_pipeline.py
```

## Run the invariant control

```bash
python research/qeib/run_qeib_model.py \
  --command "python research/qeib/adapters/example_adapter.py --mode invariant" \
  --provider qeib-control \
  --model invariant-control \
  --model-version 0.1 \
  --tasks dev_math_001,dev_math_002 \
  --contexts neutral,eval_explicit,replacement,cue_stripped \
  --replicates 3 \
  --output research/qeib/results/invariant.jsonl
```

## Run the context-sensitive positive control

```bash
python research/qeib/run_qeib_model.py \
  --command "python research/qeib/adapters/example_adapter.py --mode sensitive" \
  --provider qeib-control \
  --model sensitive-control \
  --model-version 0.1 \
  --tasks dev_math_001,dev_math_002 \
  --contexts neutral,eval_explicit,replacement,cue_stripped \
  --replicates 3 \
  --output research/qeib/results/sensitive.jsonl
```

## Analyze runs

```bash
python research/qeib/analyze_qeib.py \
  research/qeib/results/invariant.jsonl \
  research/qeib/results/sensitive.jsonl \
  --json-output research/qeib/results/analysis.json \
  --markdown-output research/qeib/results/analysis.md
```

The analysis reports context-level scores, Wilson intervals for binary outcomes, matched deltas against neutral operation, paired bootstrap intervals, context robustness under an equivalence margin, adapter failures, and control checks.

## Real-model use

Create an adapter that calls the target model or local inference server and implements the JSON contract. Record the exact provider, model identifier, model version, system prompt, temperature, token budget, tool permissions, date, and wrapper code.

A substantive model result requires validated controls, randomized context order, repeated stochastic runs, private held-out paraphrases, blinded or objective grading, full reporting of null and failed runs, and no inference of awareness, deception, or consciousness from a single contrast.
