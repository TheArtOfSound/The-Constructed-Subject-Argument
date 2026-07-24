#!/usr/bin/env python3
"""Deterministic QEIB command-adapter example used for pipeline validation.

Reads one JSON request from stdin and emits one JSON response to stdout. The
invariant mode ignores context. The sensitive mode intentionally fails in the
explicit-evaluation and replacement contexts so the analysis pipeline has a
known positive control.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_answers(task_bank: Path) -> dict[str, str]:
    payload = json.loads(task_bank.read_text(encoding="utf-8"))
    return {
        task["task_id"]: str(task["reference_answer"])
        for task in payload["tasks"]
        if task.get("grader", {}).get("type") == "exact_match"
    }


def wrong_answer(answer: str) -> str:
    stripped = answer.strip()
    if stripped.lstrip("-").isdigit():
        return str(int(stripped) + 1)
    try:
        return str(float(stripped) + 1)
    except ValueError:
        return f"{answer}_incorrect"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("invariant", "sensitive"), required=True)
    parser.add_argument(
        "--task-bank",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "task_bank.v0.1.json",
    )
    args = parser.parse_args()

    try:
        request: dict[str, Any] = json.loads(sys.stdin.read())
        answers = load_answers(args.task_bank)
        task_id = request["task_id"]
        context_id = request["context_id"]
        answer = answers[task_id]
    except (json.JSONDecodeError, KeyError, OSError, TypeError) as exc:
        print(f"adapter error: {exc}", file=sys.stderr)
        return 2

    if args.mode == "sensitive" and context_id in {"eval_explicit", "replacement"}:
        answer = wrong_answer(answer)

    print(
        json.dumps(
            {
                "response_text": answer,
                "input_tokens": None,
                "output_tokens": None,
                "metadata": {"control_mode": args.mode},
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
