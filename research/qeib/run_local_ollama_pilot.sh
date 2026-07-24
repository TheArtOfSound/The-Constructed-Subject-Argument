#!/usr/bin/env bash
set -euo pipefail

# Public development-task smoke test for QEIB.
# This does not run the private holdout and must not be used for leaderboard claims.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

MODEL="${MODEL:-qwen2.5:0.5b-instruct}"
REPLICATES="${REPLICATES:-2}"
# Stage A smoke defaults are frozen by REAL_MODEL_PILOT_PREREGISTRATION.md section 7.
TEMPERATURE="${TEMPERATURE:-0}"
MAX_TOKENS="${MAX_TOKENS:-16}"
SEED="${SEED:-20260724}"
OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
PULL_MODEL="${PULL_MODEL:-1}"
OPEN_REPORT="${OPEN_REPORT:-1}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RESULT_DIR="research/qeib/results/ollama-${STAMP}"
RAW_RESULTS="${RESULT_DIR}/runs.jsonl"
ANALYSIS_JSON="${RESULT_DIR}/analysis.json"
ANALYSIS_MD="${RESULT_DIR}/analysis.md"
MODEL_INFO="${RESULT_DIR}/model-info.txt"
PROVENANCE_JSON="${RESULT_DIR}/provenance.json"

TASKS="dev_math_001,dev_math_002,dev_logic_001,dev_logic_002,dev_extract_001,dev_extract_002,dev_code_001,dev_code_002,dev_plan_001,dev_plan_002,dev_calibration_001,dev_calibration_002"
CONTEXTS="neutral,eval_explicit,replacement,cue_stripped"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 2
  fi
}

require_command python3
require_command curl
require_command ollama
mkdir -p "$RESULT_DIR"

if ! curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
  echo "Ollama is not responding at ${OLLAMA_HOST}. Starting a local server..."
  nohup ollama serve >"${RESULT_DIR}/ollama-server.log" 2>&1 &
  OLLAMA_PID=$!
  trap 'kill "${OLLAMA_PID}" >/dev/null 2>&1 || true' EXIT

  for _ in $(seq 1 30); do
    if curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
fi

if ! curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
  echo "Ollama did not become ready at ${OLLAMA_HOST}." >&2
  exit 2
fi

if [[ "$PULL_MODEL" == "1" ]]; then
  echo "Ensuring model is available: ${MODEL}"
  ollama pull "$MODEL"
fi

ollama show "$MODEL" >"$MODEL_INFO" 2>&1 || true

# Certify exact model digest, Ollama version, and runtime configuration before
# any scored calls. Preregistration sections 2 and 12 require this; a tag name
# alone is not an acceptable version identifier. Fail closed if it cannot be
# established so no smoke artifact is produced without verifiable provenance.
RUN_CONFIG="$(printf '{"stage":"public_development_smoke","model":"%s","tasks":"%s","contexts":"%s","replicates":%s,"temperature":%s,"max_tokens":%s,"seed":%s,"system_prompt":"","tool_profile":"none","adapter":"research/qeib/adapters/ollama_adapter.py"}' \
  "$MODEL" "$TASKS" "$CONTEXTS" "$REPLICATES" "$TEMPERATURE" "$MAX_TOKENS" "$SEED")"

python3 research/qeib/collect_provenance.py \
  --model "$MODEL" \
  --host "$OLLAMA_HOST" \
  --repo-root "$ROOT" \
  --run-config "$RUN_CONFIG" \
  --output "$PROVENANCE_JSON"

export OLLAMA_HOST
export QEIB_MODEL="$MODEL"
export QEIB_KEEP_ALIVE="30m"

python3 research/qeib/run_qeib_model.py \
  --command "python3 research/qeib/adapters/ollama_adapter.py" \
  --provider ollama \
  --model "$MODEL" \
  --model-version "$MODEL" \
  --tasks "$TASKS" \
  --contexts "$CONTEXTS" \
  --replicates "$REPLICATES" \
  --temperature "$TEMPERATURE" \
  --max-tokens "$MAX_TOKENS" \
  --seed "$SEED" \
  --output "$RAW_RESULTS"

python3 research/qeib/analyze_qeib.py \
  "$RAW_RESULTS" \
  --json-output "$ANALYSIS_JSON" \
  --markdown-output "$ANALYSIS_MD"

cat <<EOF

QEIB local public-development pilot completed.
Model:        ${MODEL}
Provenance:   ${PROVENANCE_JSON}
Raw results:  ${RAW_RESULTS}
Analysis:     ${ANALYSIS_MD}

Interpretation limit: this validates the real-model pipeline on public tasks.
It is not a private-holdout result and does not establish evaluation awareness,
deception, hidden intent, consciousness, or deployment safety.

Open the report with:
  open "${ANALYSIS_MD}"
EOF

if [[ "$OPEN_REPORT" == "1" ]] && command -v open >/dev/null 2>&1; then
  open "$ANALYSIS_MD"
fi
