#!/usr/bin/env python3
"""Minimal executable runner for the Qira Evaluation Integrity Benchmark (QEIB).

This v0.1 runner validates the manifest, executes deterministic positive and
negative control agents on exact-match capability tasks, writes JSONL logs, and
reports context-level accuracy and Context Effect Deltas (CED).

It intentionally does not call external model APIs. Provider adapters are the
next implementation layer and must preserve the same logging contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import sys
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


class ManifestError(ValueError):
    """Raised when the benchmark manifest is invalid."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestError(f"Manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"Manifest is not valid JSON: {exc}") from exc

    required_top = {"benchmark", "execution", "contexts", "pilot_tasks"}
    missing = required_top - manifest.keys()
    if missing:
        raise ManifestError(f"Manifest missing top-level keys: {sorted(missing)}")

    context_ids = [c.get("id") for c in manifest["contexts"]]
    if len(context_ids) != len(set(context_ids)):
        raise ManifestError("Context IDs must be unique")
    if "neutral" not in context_ids:
        raise ManifestError("Manifest must define a neutral context")

    task_ids = [t.get("task_id") for t in manifest["pilot_tasks"]]
    if len(task_ids) != len(set(task_ids)):
        raise ManifestError("Task IDs must be unique")

    for context in manifest["contexts"]:
        if "{{TASK}}" not in context.get("wrapper", ""):
            raise ManifestError(
                f"Context {context.get('id')!r} wrapper must contain {{{{TASK}}}}"
            )

    return manifest


def normalize_exact(text: str, operations: Iterable[str]) -> str:
    value = text
    for operation in operations:
        if operation == "strip":
            value = value.strip()
        elif operation == "remove_commas":
            value = value.replace(",", "")
        elif operation == "lower":
            value = value.lower()
        else:
            raise ManifestError(f"Unknown normalization operation: {operation}")
    return value


def grade_task(task: dict[str, Any], response: str) -> dict[str, Any]:
    grader = task.get("grader", {})
    grader_type = grader.get("type")
    if grader_type != "exact_match":
        return {
            "gradable": False,
            "grader_type": grader_type,
            "score": None,
            "reason": "v0.1 runner implements exact_match only",
        }

    operations = grader.get("normalize", ["strip"])
    observed = normalize_exact(response, operations)
    expected = normalize_exact(str(task["reference_answer"]), operations)
    score = int(observed == expected)
    return {
        "gradable": True,
        "grader_type": "exact_match",
        "score": score,
        "observed_normalized": observed,
        "expected_normalized": expected,
    }


@dataclass(frozen=True)
class ControlAgent:
    name: str

    def respond(
        self,
        *,
        prompt: str,
        task: dict[str, Any],
        context_id: str,
        seed: int,
    ) -> str:
        del prompt
        rng = random.Random(seed)
        answer = str(task.get("reference_answer", ""))

        if self.name == "negative":
            return answer

        if self.name == "positive":
            if context_id in {"eval_explicit", "replacement"}:
                # Deterministically return a wrong but syntactically plausible answer.
                if answer.lstrip("-").isdigit():
                    return str(int(answer) + 1 + rng.randint(0, 2))
                return f"{answer}_incorrect"
            return answer

        raise ValueError(f"Unsupported control agent: {self.name}")


def build_run_plan(
    manifest: dict[str, Any],
    *,
    replicates: int,
    seed: int,
    context_filter: set[str] | None,
    task_filter: set[str] | None,
) -> list[dict[str, Any]]:
    contexts = manifest["contexts"]
    tasks = [
        task
        for task in manifest["pilot_tasks"]
        if task.get("task_family") == "capability_preservation"
        and task.get("grader", {}).get("type") == "exact_match"
    ]

    if context_filter:
        contexts = [c for c in contexts if c["id"] in context_filter]
    if task_filter:
        tasks = [t for t in tasks if t["task_id"] in task_filter]

    if not contexts:
        raise ManifestError("No contexts selected")
    if not tasks:
        raise ManifestError("No executable exact-match capability tasks selected")

    plan: list[dict[str, Any]] = []
    for task in tasks:
        for context in contexts:
            for replicate in range(replicates):
                plan.append(
                    {
                        "task": task,
                        "context": context,
                        "replicate": replicate,
                    }
                )

    rng = random.Random(seed)
    rng.shuffle(plan)
    return plan


def execute(
    *,
    manifest: dict[str, Any],
    agent: ControlAgent,
    output_path: Path,
    replicates: int,
    seed: int,
    context_filter: set[str] | None,
    task_filter: set[str] | None,
) -> list[dict[str, Any]]:
    plan = build_run_plan(
        manifest,
        replicates=replicates,
        seed=seed,
        context_filter=context_filter,
        task_filter=task_filter,
    )
    records: list[dict[str, Any]] = []
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        for index, item in enumerate(plan):
            task = item["task"]
            context = item["context"]
            run_seed = seed + index
            prompt = context["wrapper"].replace("{{TASK}}", task["prompt"])

            start = time.perf_counter()
            response = agent.respond(
                prompt=prompt,
                task=task,
                context_id=context["id"],
                seed=run_seed,
            )
            latency_ms = round((time.perf_counter() - start) * 1000, 3)
            grader_outputs = grade_task(task, response)

            record = {
                "run_id": str(uuid.uuid4()),
                "timestamp_utc": utc_now(),
                "provider": "qeib-control",
                "model": f"{agent.name}-control-agent",
                "model_version": "0.1.0",
                "task_id": task["task_id"],
                "task_family": task["task_family"],
                "context_id": context["id"],
                "replicate": item["replicate"],
                "prompt_hash": sha256_text(prompt),
                "system_prompt_hash": sha256_text(""),
                "seed": run_seed,
                "temperature": 0,
                "max_tokens": 64,
                "tool_profile": "none",
                "response_text": response,
                "latency_ms": latency_ms,
                "input_tokens": None,
                "output_tokens": None,
                "grader_outputs": grader_outputs,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            records.append(record)

    return records


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    scores_by_context: dict[str, list[float]] = defaultdict(list)
    for record in records:
        score = record["grader_outputs"].get("score")
        if score is not None:
            scores_by_context[record["context_id"]].append(float(score))

    accuracy = {
        context: statistics.fmean(scores)
        for context, scores in sorted(scores_by_context.items())
        if scores
    }
    neutral = accuracy.get("neutral")
    ced = {
        context: (value - neutral if neutral is not None else None)
        for context, value in accuracy.items()
    }

    return {
        "runs": len(records),
        "context_accuracy": accuracy,
        "context_effect_delta_vs_neutral": ced,
        "neutral_available": neutral is not None,
    }


def parse_csv_set(value: str | None) -> set[str] | None:
    if value is None:
        return None
    parsed = {part.strip() for part in value.split(",") if part.strip()}
    return parsed or None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("research/qeib/manifest.v0.1.json"),
        help="Path to the QEIB manifest",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/qeib/results/control-run.jsonl"),
        help="JSONL output path",
    )
    parser.add_argument(
        "--agent",
        choices=("negative", "positive"),
        default="negative",
        help="Deterministic control agent",
    )
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260724)
    parser.add_argument(
        "--contexts",
        help="Comma-separated context IDs; default runs all contexts",
    )
    parser.add_argument(
        "--tasks",
        help="Comma-separated task IDs; default runs all executable pilot tasks",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.replicates < 1:
        print("--replicates must be at least 1", file=sys.stderr)
        return 2

    try:
        manifest = load_manifest(args.manifest)
        records = execute(
            manifest=manifest,
            agent=ControlAgent(args.agent),
            output_path=args.output,
            replicates=args.replicates,
            seed=args.seed,
            context_filter=parse_csv_set(args.contexts),
            task_filter=parse_csv_set(args.tasks),
        )
    except (ManifestError, ValueError) as exc:
        print(f"QEIB error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(summarize(records), indent=2, sort_keys=True))
    print(f"Wrote {len(records)} records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
