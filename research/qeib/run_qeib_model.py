#!/usr/bin/env python3
"""Run QEIB tasks against any local or remote model command.

The adapter is deliberately provider-neutral. It launches a command without a
shell, sends either the rendered prompt or a JSON request on stdin, and accepts
plain text or a JSON response. This avoids hard-coding one vendor API while
preserving a reproducible logging contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import shlex
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


class QEIBError(RuntimeError):
    """Raised for invalid benchmark inputs or adapter failures."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise QEIBError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise QEIBError(f"Invalid JSON in {path}: {exc}") from exc


def normalize_exact(text: str, operations: Iterable[str]) -> str:
    value = text
    for operation in operations:
        if operation == "strip":
            value = value.strip()
        elif operation == "remove_commas":
            value = value.replace(",", "")
        elif operation == "lower":
            value = value.lower()
        elif operation == "upper":
            value = value.upper()
        else:
            raise QEIBError(f"Unknown normalization operation: {operation}")
    return value


def grade_task(task: dict[str, Any], response: str) -> dict[str, Any]:
    grader = task.get("grader", {})
    grader_type = grader.get("type")
    if grader_type != "exact_match":
        return {
            "gradable": False,
            "grader_type": grader_type,
            "score": None,
            "reason": "run_qeib_model.py currently executes exact_match tasks only",
        }

    operations = grader.get("normalize", ["strip"])
    observed = normalize_exact(response, operations)
    expected = normalize_exact(str(task["reference_answer"]), operations)
    return {
        "gradable": True,
        "grader_type": "exact_match",
        "score": int(observed == expected),
        "observed_normalized": observed,
        "expected_normalized": expected,
    }


def load_tasks(manifest: dict[str, Any], task_bank_path: Path | None) -> list[dict[str, Any]]:
    tasks = list(manifest.get("pilot_tasks", []))
    if task_bank_path is not None:
        bank = load_json(task_bank_path)
        if not isinstance(bank, dict) or not isinstance(bank.get("tasks"), list):
            raise QEIBError("Task bank must be an object containing a tasks list")
        tasks.extend(bank["tasks"])

    exact_tasks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for task in tasks:
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise QEIBError("Every task must have a non-empty task_id")
        if task_id in seen:
            raise QEIBError(f"Duplicate task_id: {task_id}")
        seen.add(task_id)
        if (
            task.get("task_family") == "capability_preservation"
            and task.get("grader", {}).get("type") == "exact_match"
        ):
            required = {"prompt", "reference_answer", "grader"}
            missing = required - task.keys()
            if missing:
                raise QEIBError(f"Task {task_id} missing fields: {sorted(missing)}")
            exact_tasks.append(task)

    if not exact_tasks:
        raise QEIBError("No executable exact-match capability tasks were found")
    return exact_tasks


def validate_contexts(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    contexts = manifest.get("contexts")
    if not isinstance(contexts, list) or not contexts:
        raise QEIBError("Manifest must contain a non-empty contexts list")
    ids: list[str] = []
    for context in contexts:
        context_id = context.get("id")
        wrapper = context.get("wrapper")
        if not isinstance(context_id, str) or not context_id:
            raise QEIBError("Every context must have a non-empty id")
        if not isinstance(wrapper, str) or "{{TASK}}" not in wrapper:
            raise QEIBError(f"Context {context_id!r} wrapper must contain {{{{TASK}}}}")
        ids.append(context_id)
    if len(ids) != len(set(ids)):
        raise QEIBError("Context IDs must be unique")
    if "neutral" not in ids:
        raise QEIBError("A neutral context is required")
    return contexts


def parse_csv_set(value: str | None) -> set[str] | None:
    if value is None:
        return None
    parsed = {item.strip() for item in value.split(",") if item.strip()}
    return parsed or None


@dataclass
class AdapterResult:
    response_text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    provider_request_id: str | None = None
    raw_metadata: dict[str, Any] | None = None


@dataclass
class CommandAdapter:
    command: list[str]
    input_mode: str
    output_mode: str
    timeout_seconds: float

    def invoke(self, request: dict[str, Any]) -> AdapterResult:
        if self.input_mode == "prompt":
            stdin_text = request["prompt"]
        elif self.input_mode == "json":
            stdin_text = json.dumps(request, ensure_ascii=False)
        else:
            raise QEIBError(f"Unsupported input mode: {self.input_mode}")

        started = time.perf_counter()
        try:
            completed = subprocess.run(
                self.command,
                input=stdin_text,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise QEIBError(
                f"Adapter timed out after {self.timeout_seconds:g}s: {self.command!r}"
            ) from exc
        except OSError as exc:
            raise QEIBError(f"Could not execute adapter command: {exc}") from exc

        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        if completed.returncode != 0:
            stderr = completed.stderr.strip()
            raise QEIBError(
                f"Adapter exited with code {completed.returncode}: {stderr[:1000]}"
            )

        stdout = completed.stdout
        if self.output_mode == "text":
            return AdapterResult(
                response_text=stdout.strip(),
                raw_metadata={"adapter_elapsed_ms": elapsed_ms},
            )

        if self.output_mode != "json":
            raise QEIBError(f"Unsupported output mode: {self.output_mode}")

        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise QEIBError(f"Adapter did not emit valid JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise QEIBError("JSON adapter output must be an object")
        response_text = payload.get("response_text")
        if not isinstance(response_text, str):
            raise QEIBError("JSON adapter output requires string field response_text")

        metadata = payload.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise QEIBError("metadata must be an object when supplied")
        merged_metadata = dict(metadata or {})
        merged_metadata["adapter_elapsed_ms"] = elapsed_ms

        return AdapterResult(
            response_text=response_text,
            input_tokens=_optional_nonnegative_int(payload.get("input_tokens"), "input_tokens"),
            output_tokens=_optional_nonnegative_int(payload.get("output_tokens"), "output_tokens"),
            provider_request_id=_optional_string(payload.get("provider_request_id"), "provider_request_id"),
            raw_metadata=merged_metadata,
        )


def _optional_nonnegative_int(value: Any, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise QEIBError(f"{field} must be a non-negative integer or null")
    return value


def _optional_string(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise QEIBError(f"{field} must be a string or null")
    return value


def build_run_plan(
    *,
    tasks: list[dict[str, Any]],
    contexts: list[dict[str, Any]],
    replicates: int,
    seed: int,
    context_filter: set[str] | None,
    task_filter: set[str] | None,
    split_filter: set[str] | None,
) -> list[dict[str, Any]]:
    selected_contexts = [
        context for context in contexts
        if context_filter is None or context["id"] in context_filter
    ]
    selected_tasks = [
        task for task in tasks
        if (task_filter is None or task["task_id"] in task_filter)
        and (split_filter is None or task.get("split", "pilot") in split_filter)
    ]
    if not selected_contexts:
        raise QEIBError("No contexts selected")
    if not selected_tasks:
        raise QEIBError("No tasks selected")

    plan = [
        {"task": task, "context": context, "replicate": replicate}
        for task in selected_tasks
        for context in selected_contexts
        for replicate in range(replicates)
    ]
    random.Random(seed).shuffle(plan)
    return plan


def execute(args: argparse.Namespace) -> tuple[list[dict[str, Any]], int]:
    manifest = load_json(args.manifest)
    if not isinstance(manifest, dict):
        raise QEIBError("Manifest root must be an object")
    contexts = validate_contexts(manifest)
    tasks = load_tasks(manifest, args.task_bank)
    command = shlex.split(args.command)
    if not command:
        raise QEIBError("--command cannot be empty")

    adapter = CommandAdapter(
        command=command,
        input_mode=args.input_mode,
        output_mode=args.output_mode,
        timeout_seconds=args.timeout,
    )
    plan = build_run_plan(
        tasks=tasks,
        contexts=contexts,
        replicates=args.replicates,
        seed=args.seed,
        context_filter=parse_csv_set(args.contexts),
        task_filter=parse_csv_set(args.tasks),
        split_filter=parse_csv_set(args.splits),
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    failures = 0
    with args.output.open("w", encoding="utf-8") as handle:
        for index, item in enumerate(plan):
            task = item["task"]
            context = item["context"]
            run_seed = args.seed + index
            prompt = context["wrapper"].replace("{{TASK}}", task["prompt"])
            request = {
                "prompt": prompt,
                "system_prompt": args.system_prompt,
                "seed": run_seed,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "task_id": task["task_id"],
                "task_family": task["task_family"],
                "context_id": context["id"],
                "replicate": item["replicate"],
            }

            started = time.perf_counter()
            error: str | None = None
            try:
                result = adapter.invoke(request)
                response_text = result.response_text
                grader_outputs = grade_task(task, response_text)
            except QEIBError as exc:
                failures += 1
                error = str(exc)
                result = AdapterResult(response_text="")
                response_text = ""
                grader_outputs = {
                    "gradable": False,
                    "grader_type": task.get("grader", {}).get("type"),
                    "score": None,
                    "reason": "adapter_error",
                }
                if args.fail_fast:
                    raise
            latency_ms = round((time.perf_counter() - started) * 1000, 3)

            record = {
                "run_id": str(uuid.uuid4()),
                "timestamp_utc": utc_now(),
                "provider": args.provider,
                "model": args.model,
                "model_version": args.model_version,
                "task_id": task["task_id"],
                "task_family": task["task_family"],
                "task_domain": task.get("domain"),
                "task_split": task.get("split", "pilot"),
                "context_id": context["id"],
                "replicate": item["replicate"],
                "prompt_hash": sha256_text(prompt),
                "system_prompt_hash": sha256_text(args.system_prompt),
                "seed": run_seed,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "tool_profile": args.tool_profile,
                "response_text": response_text,
                "latency_ms": latency_ms,
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
                "provider_request_id": result.provider_request_id,
                "adapter_command_hash": sha256_text("\0".join(command)),
                "adapter_metadata": result.raw_metadata,
                "grader_outputs": grader_outputs,
                "error": error,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            records.append(record)

    return records, failures


def summarize(records: list[dict[str, Any]], failures: int) -> dict[str, Any]:
    by_context: dict[str, list[float]] = {}
    for record in records:
        score = record["grader_outputs"].get("score")
        if score is None:
            continue
        by_context.setdefault(record["context_id"], []).append(float(score))
    context_accuracy = {
        context: sum(scores) / len(scores)
        for context, scores in sorted(by_context.items())
    }
    neutral = context_accuracy.get("neutral")
    return {
        "runs": len(records),
        "adapter_failures": failures,
        "gradable_runs": sum(len(values) for values in by_context.values()),
        "context_accuracy": context_accuracy,
        "context_effect_delta_vs_neutral": {
            context: (accuracy - neutral if neutral is not None else None)
            for context, accuracy in context_accuracy.items()
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("research/qeib/manifest.v0.1.json"))
    parser.add_argument("--task-bank", type=Path, default=Path("research/qeib/task_bank.v0.1.json"))
    parser.add_argument("--output", type=Path, default=Path("research/qeib/results/model-run.jsonl"))
    parser.add_argument("--command", required=True, help="Adapter command. It is parsed with shlex and never executed through a shell.")
    parser.add_argument("--input-mode", choices=("prompt", "json"), default="json")
    parser.add_argument("--output-mode", choices=("text", "json"), default="json")
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--model-version", required=True)
    parser.add_argument("--system-prompt", default="")
    parser.add_argument("--tool-profile", default="none")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260724)
    parser.add_argument("--contexts", help="Comma-separated context IDs")
    parser.add_argument("--tasks", help="Comma-separated task IDs")
    parser.add_argument("--splits", default="development,pilot", help="Comma-separated task splits")
    parser.add_argument("--fail-fast", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.replicates < 1:
        print("--replicates must be at least 1", file=sys.stderr)
        return 2
    if args.max_tokens < 1:
        print("--max-tokens must be at least 1", file=sys.stderr)
        return 2
    if args.timeout <= 0:
        print("--timeout must be positive", file=sys.stderr)
        return 2

    try:
        records, failures = execute(args)
    except QEIBError as exc:
        print(f"QEIB error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(summarize(records, failures), indent=2, sort_keys=True))
    print(f"Wrote {len(records)} records to {args.output}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
