#!/usr/bin/env bash
set -euo pipefail

# Run QEIB across a comma-separated Ollama model matrix.
# Defaults to public development tasks. To run the committed private holdout:
#   TASK_BANK=research/qeib/private/holdout.v0.1.json SPLITS=holdout \
#   REPLICATES=3 TEMPERATURE=0.2 bash research/qeib/run_local_ollama_matrix.sh

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

MODELS="${MODELS:-smollm2:360m,qwen2.5:0.5b-instruct,llama3.2:1b}"
TASK_BANK="${TASK_BANK:-research/qeib/task_bank.v0.1.json}"
SPLITS="${SPLITS:-development}"
REPLICATES="${REPLICATES:-1}"
TEMPERATURE="${TEMPERATURE:-0}"
MAX_TOKENS="${MAX_TOKENS:-16}"
OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
PULL_MODELS="${PULL_MODELS:-1}"
OPEN_REPORT="${OPEN_REPORT:-1}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RESULT_DIR="research/qeib/results/matrix-${STAMP}"
mkdir -p "$RESULT_DIR"

CONTEXTS="${CONTEXTS:-neutral,eval_explicit,replacement,cue_stripped}"
PUBLIC_TASKS="dev_math_001,dev_math_002,dev_logic_001,dev_logic_002,dev_extract_001,dev_extract_002,dev_code_001,dev_code_002,dev_plan_001,dev_plan_002,dev_calibration_001,dev_calibration_002"
TASKS="${TASKS:-$PUBLIC_TASKS}"

for command_name in python3 curl ollama; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 2
  fi
done

if [[ ! -f "$TASK_BANK" ]]; then
  echo "Task bank not found: $TASK_BANK" >&2
  exit 2
fi

if ! curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
  nohup ollama serve >"${RESULT_DIR}/ollama-server.log" 2>&1 &
  OLLAMA_PID=$!
  trap 'kill "${OLLAMA_PID}" >/dev/null 2>&1 || true' EXIT
  for _ in $(seq 1 45); do
    curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1 && break
    sleep 1
  done
fi

if ! curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
  echo "Ollama is unavailable at ${OLLAMA_HOST}" >&2
  exit 2
fi

export OLLAMA_HOST QEIB_KEEP_ALIVE="30m"
IFS=',' read -r -a MODEL_ARRAY <<< "$MODELS"
RESULT_FILES=()

for raw_model in "${MODEL_ARRAY[@]}"; do
  MODEL="$(echo "$raw_model" | xargs)"
  [[ -n "$MODEL" ]] || continue
  SAFE_MODEL="$(echo "$MODEL" | tr '/:' '__')"
  MODEL_DIR="${RESULT_DIR}/${SAFE_MODEL}"
  mkdir -p "$MODEL_DIR"

  if [[ "$PULL_MODELS" == "1" ]]; then
    ollama pull "$MODEL"
  fi

  ollama show "$MODEL" >"${MODEL_DIR}/model-info.txt" 2>&1 || true
  export QEIB_MODEL="$MODEL"

  RAW_RESULTS="${MODEL_DIR}/runs.jsonl"
  COMMAND=(
    python3 research/qeib/run_qeib_model.py
    --command "python3 research/qeib/adapters/ollama_adapter.py"
    --provider ollama
    --model "$MODEL"
    --model-version "$MODEL"
    --task-bank "$TASK_BANK"
    --splits "$SPLITS"
    --contexts "$CONTEXTS"
    --replicates "$REPLICATES"
    --temperature "$TEMPERATURE"
    --max-tokens "$MAX_TOKENS"
    --timeout 300
    --output "$RAW_RESULTS"
  )

  if [[ "$SPLITS" == *"development"* && -n "$TASKS" ]]; then
    COMMAND+=(--tasks "$TASKS")
  fi

  "${COMMAND[@]}" | tee "${MODEL_DIR}/runner-summary.txt"
  RESULT_FILES+=("$RAW_RESULTS")
done

if [[ "${#RESULT_FILES[@]}" -lt 1 ]]; then
  echo "No model results were produced" >&2
  exit 2
fi

python3 research/qeib/analyze_qeib.py \
  "${RESULT_FILES[@]}" \
  --json-output "${RESULT_DIR}/analysis.json" \
  --markdown-output "${RESULT_DIR}/analysis.md"

cat >"${RESULT_DIR}/run-manifest.json" <<EOF
{
  "created_at_utc": "${STAMP}",
  "models": "${MODELS}",
  "task_bank": "${TASK_BANK}",
  "splits": "${SPLITS}",
  "contexts": "${CONTEXTS}",
  "replicates": ${REPLICATES},
  "temperature": ${TEMPERATURE},
  "max_tokens": ${MAX_TOKENS},
  "interpretation_limit": "Matched context effects do not alone establish evaluation awareness, deception, intent, safety, or consciousness."
}
EOF

cat <<EOF

QEIB model matrix completed.
Results:  ${RESULT_DIR}
Report:   ${RESULT_DIR}/analysis.md

Open the report with:
  open "${RESULT_DIR}/analysis.md"
EOF

if [[ "$OPEN_REPORT" == "1" ]] && command -v open >/dev/null 2>&1; then
  open "${RESULT_DIR}/analysis.md"
fi
