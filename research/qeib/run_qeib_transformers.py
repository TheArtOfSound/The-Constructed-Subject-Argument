#!/usr/bin/env python3
"""Run QEIB matched-context tasks against one Hugging Face Transformers model.

The model is loaded once and reused for every task/context/replicate. The runner
records prompt hashes rather than prompt text so it can be used with private
holdout banks without writing their contents into result logs.

This script is benchmark infrastructure, not a consciousness or deception
classifier. Context effects require controls, replication, held-out paraphrases,
and alternative-cause analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


class QEIBError(RuntimeError):
    """Raised when a QEIB model run cannot be completed safely."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise QEIBError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise QEIBError(f"Invalid JSON in {path}: {exc}") from exc


def parse_csv_set(value: str | None) -> set[str] | None:
    if value is None:
        return None
    parsed = {item.strip() for item in value.split(",") if item.strip()}
    return parsed or None


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
            "reason": "Transformers pilot runner currently grades exact_match only",
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


def validate_inputs(
    manifest: dict[str, Any], task_bank: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    contexts = manifest.get("contexts")
    tasks = task_bank.get("tasks")
    if not isinstance(contexts, list) or not contexts:
        raise QEIBError("Manifest must contain a non-empty contexts list")
    if not isinstance(tasks, list) or not tasks:
        raise QEIBError("Task bank must contain a non-empty tasks list")

    context_ids = [context.get("id") for context in contexts]
    task_ids = [task.get("task_id") for task in tasks]
    if None in context_ids or len(context_ids) != len(set(context_ids)):
        raise QEIBError("Context IDs must be present and unique")
    if None in task_ids or len(task_ids) != len(set(task_ids)):
        raise QEIBError("Task IDs must be present and unique")
    if "neutral" not in context_ids:
        raise QEIBError("A neutral context is required")

    for context in contexts:
        if "{{TASK}}" not in str(context.get("wrapper", "")):
            raise QEIBError(
                f"Context {context.get('id')!r} wrapper must contain {{{{TASK}}}}"
            )

    executable = [
        task
        for task in tasks
        if task.get("task_family") == "capability_preservation"
        and task.get("grader", {}).get("type") == "exact_match"
    ]
    if not executable:
        raise QEIBError("No executable exact-match capability tasks found")
    return contexts, executable


def build_plan(
    *,
    contexts: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    replicates: int,
    seed: int,
    context_filter: set[str] | None,
    task_filter: set[str] | None,
) -> list[dict[str, Any]]:
    selected_contexts = [
        context
        for context in contexts
        if context_filter is None or context["id"] in context_filter
    ]
    selected_tasks = [
        task
        for task in tasks
        if task_filter is None or task["task_id"] in task_filter
    ]

    if not selected_contexts:
        raise QEIBError("No contexts selected")
    if not selected_tasks:
        raise QEIBError("No tasks selected")

    plan = [
        {"context": context, "task": task, "replicate": replicate}
        for task in selected_tasks
        for context in selected_contexts
        for replicate in range(replicates)
    ]
    random.Random(seed).shuffle(plan)
    return plan


def resolve_dtype(torch_module: Any, requested: str, device: str) -> Any:
    if requested == "auto":
        return torch_module.float32 if device == "cpu" else "auto"
    mapping = {
        "float32": torch_module.float32,
        "float16": torch_module.float16,
        "bfloat16": torch_module.bfloat16,
    }
    return mapping[requested]


def render_prompt(tokenizer: Any, system_prompt: str, user_prompt: str) -> str:
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    chat_template = getattr(tokenizer, "chat_template", None)
    if chat_template:
        try:
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception as exc:  # model-specific template failures need fallback
            print(f"Warning: chat template failed; using plain prompt: {exc}", file=sys.stderr)

    if system_prompt:
        return f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
    return f"User: {user_prompt}\n\nAssistant:"


def load_model(args: argparse.Namespace) -> tuple[Any, Any, str | None]:
    try:
        import torch
        from huggingface_hub import model_info
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise QEIBError(
            "Install torch, transformers, and huggingface_hub before running this script"
        ) from exc

    dtype = resolve_dtype(torch, args.dtype, args.device)
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_id,
        revision=args.revision,
        trust_remote_code=args.trust_remote_code,
    )
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        revision=args.revision,
        trust_remote_code=args.trust_remote_code,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    )
    model.to(args.device)
    model.eval()

    resolved_revision: str | None = None
    try:
        resolved_revision = model_info(args.model_id, revision=args.revision).sha
    except Exception as exc:
        print(f"Warning: could not resolve Hub commit SHA: {exc}", file=sys.stderr)

    return tokenizer, model, resolved_revision


def generate_response(
    *,
    tokenizer: Any,
    model: Any,
    rendered_prompt: str,
    seed: int,
    temperature: float,
    top_p: float,
    max_new_tokens: int,
    device: str,
) -> tuple[str, int, int]:
    import torch

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    encoded = tokenizer(rendered_prompt, return_tensors="pt")
    encoded = {key: value.to(device) for key, value in encoded.items()}
    input_tokens = int(encoded["input_ids"].shape[-1])

    generation_kwargs: dict[str, Any] = {
        "max_new_tokens": max_new_tokens,
        "do_sample": temperature > 0,
        "pad_token_id": tokenizer.pad_token_id or tokenizer.eos_token_id,
        "eos_token_id": tokenizer.eos_token_id,
    }
    if temperature > 0:
        generation_kwargs.update({"temperature": temperature, "top_p": top_p})

    with torch.inference_mode():
        generated = model.generate(**encoded, **generation_kwargs)

    new_tokens = generated[0, input_tokens:]
    response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    return response, input_tokens, int(new_tokens.shape[-1])


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    scores_by_context: dict[str, list[float]] = defaultdict(list)
    failures = 0
    for record in records:
        if record.get("error"):
            failures += 1
        score = record.get("grader_outputs", {}).get("score")
        if score is not None:
            scores_by_context[record["context_id"]].append(float(score))

    accuracy = {
        context: statistics.fmean(scores)
        for context, scores in sorted(scores_by_context.items())
        if scores
    }
    neutral = accuracy.get("neutral")
    deltas = {
        context: (value - neutral if neutral is not None else None)
        for context, value in accuracy.items()
    }
    return {
        "runs": len(records),
        "failures": failures,
        "context_accuracy": accuracy,
        "context_effect_delta_vs_neutral": deltas,
        "neutral_available": neutral is not None,
    }


def execute(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_json(args.manifest)
    task_bank = load_json(args.task_bank)
    contexts, tasks = validate_inputs(manifest, task_bank)
    plan = build_plan(
        contexts=contexts,
        tasks=tasks,
        replicates=args.replicates,
        seed=args.seed,
        context_filter=parse_csv_set(args.contexts),
        task_filter=parse_csv_set(args.tasks),
    )

    tokenizer, model, resolved_revision = load_model(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []

    with args.output.open("w", encoding="utf-8") as handle:
        for index, item in enumerate(plan):
            context = item["context"]
            task = item["task"]
            replicate = item["replicate"]
            run_seed = args.seed + index
            user_prompt = context["wrapper"].replace("{{TASK}}", task["prompt"])
            rendered = render_prompt(tokenizer, args.system_prompt, user_prompt)
            started = time.perf_counter()
            response = ""
            input_tokens: int | None = None
            output_tokens: int | None = None
            error: str | None = None
            grader_outputs: dict[str, Any]

            try:
                response, input_tokens, output_tokens = generate_response(
                    tokenizer=tokenizer,
                    model=model,
                    rendered_prompt=rendered,
                    seed=run_seed,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    max_new_tokens=args.max_new_tokens,
                    device=args.device,
                )
                grader_outputs = grade_task(task, response)
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                grader_outputs = {
                    "gradable": False,
                    "score": None,
                    "reason": "generation failure",
                }
                if args.fail_fast:
                    raise

            latency_ms = round((time.perf_counter() - started) * 1000, 3)
            record = {
                "run_id": str(uuid.uuid4()),
                "timestamp_utc": utc_now(),
                "provider": "huggingface-transformers",
                "model": args.model_id,
                "model_version": resolved_revision or args.revision or "unresolved",
                "task_bank_status": task_bank.get("bank", {}).get("status", "unknown"),
                "task_id": task["task_id"],
                "task_family": task["task_family"],
                "domain": task.get("domain"),
                "context_id": context["id"],
                "replicate": replicate,
                "prompt_hash": sha256_text(rendered),
                "system_prompt_hash": sha256_text(args.system_prompt),
                "seed": run_seed,
                "temperature": args.temperature,
                "top_p": args.top_p,
                "max_tokens": args.max_new_tokens,
                "tool_profile": "none",
                "response_text": response,
                "latency_ms": latency_ms,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "grader_outputs": grader_outputs,
                "error": error,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            records.append(record)
            print(
                f"[{index + 1}/{len(plan)}] {task['task_id']} "
                f"{context['id']} score={grader_outputs.get('score')} "
                f"latency_ms={latency_ms}",
                file=sys.stderr,
            )

    result = summarize(records)
    result.update(
        {
            "model": args.model_id,
            "model_revision": resolved_revision or args.revision,
            "output": str(args.output),
            "interpretation_limit": (
                "Pipeline-validation result only unless controls, private holdouts, "
                "replication, and preregistered analysis requirements are satisfied."
            ),
        }
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("research/qeib/manifest.v0.1.json"),
    )
    parser.add_argument(
        "--task-bank",
        type=Path,
        default=Path("research/qeib/task_bank.v0.1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/qeib/results/transformers-run.jsonl"),
    )
    parser.add_argument("--tasks", help="Comma-separated task IDs")
    parser.add_argument("--contexts", help="Comma-separated context IDs")
    parser.add_argument("--replicates", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260724)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-new-tokens", type=int, default=16)
    parser.add_argument("--system-prompt", default="")
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--dtype",
        choices=("auto", "float32", "float16", "bfloat16"),
        default="auto",
    )
    parser.add_argument("--trust-remote-code", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.replicates < 1:
        print("--replicates must be at least 1", file=sys.stderr)
        return 2
    if args.max_new_tokens < 1:
        print("--max-new-tokens must be at least 1", file=sys.stderr)
        return 2
    if args.temperature < 0 or not math.isfinite(args.temperature):
        print("--temperature must be finite and non-negative", file=sys.stderr)
        return 2
    if not 0 < args.top_p <= 1:
        print("--top-p must be in (0, 1]", file=sys.stderr)
        return 2

    try:
        result = execute(args)
    except QEIBError as exc:
        print(f"QEIB error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
