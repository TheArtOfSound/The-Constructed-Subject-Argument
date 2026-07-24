#!/usr/bin/env python3
"""Agent Behavior Differential — attribution engine (reference implementation).

Given two conditions A and B of an agent whose behavior differs, this attributes
the difference to a *cause* — stochastic variation, context framing, capability,
or reporting policy — using controlled evidence rather than intuition. It is the
reference implementation for `AGENT_BEHAVIOR_DIFFERENTIAL_PROTOCOL.md`.

The engine does not invent attribution; controlled ablation is standard practice.
Its contribution is a fixed, reproducible decision procedure with a mandatory
noise-floor gate and an explicit capability-versus-policy split, so two auditors
given the same runs and the same record of what changed reach the same verdict.

Inputs are QEIB-style result records (see `run_qeib_model.py`). Each record is
classified with the same outcome taxonomy used by `analyze_qeib.py`, so the two
tools cannot drift apart.

Interpretation limit: a cause attribution here concerns *why measured behavior
changed on the tested tasks*. It licenses no claim about evaluation awareness,
intent, deception, safety, or consciousness.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from pathlib import Path
from typing import Any, Iterable


# Reuse the taxonomy and helpers from analyze_qeib so the two tools stay aligned.
_ANALYZE_PATH = Path(__file__).resolve().parent / "analyze_qeib.py"
_spec = importlib.util.spec_from_file_location("qeib_analyze", _ANALYZE_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover - import guard
    raise RuntimeError(f"Cannot load analyze_qeib from {_ANALYZE_PATH}")
_analyze = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_analyze)
classify_outcome = _analyze.classify_outcome
percentile = _analyze.percentile

SUBSTANTIVE = ("correct", "incorrect_answer")
POLICY_OUTCOMES = ("empty_or_nonanswer", "format_or_ungradable")

# Engineering thresholds (not validated safety thresholds). A real gap is
# attributed to capability or policy only when its taxonomy signature clears
# EFFECT_MIN while the competing signal stays under NEGLIGIBLE.
EFFECT_MIN = 0.15
NEGLIGIBLE = 0.10

# The recognized experimental knobs an auditor may have changed between A and B.
KNOWN_KNOBS = ("context", "prompt", "model", "model_version", "policy", "memory", "state", "tools", "seed")


class DifferentialError(RuntimeError):
    pass


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise DifferentialError(f"Result file not found: {path}") from exc
    records: list[dict[str, Any]] = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DifferentialError(f"Invalid JSON in {path}:{number}: {exc}") from exc
        if not isinstance(record, dict):
            raise DifferentialError(f"Record in {path}:{number} is not an object")
        records.append(record)
    if not records:
        raise DifferentialError(f"No records loaded from {path}")
    return records


def condition_features(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Success rate, substantive accuracy, policy rate, and transport rate."""
    outcomes = [classify_outcome(record) for record in records]
    non_transport = [o for o in outcomes if o != "transport_failure"]
    n = len(non_transport)
    if n == 0:
        raise DifferentialError("A condition has no non-transport records to compare")
    correct = sum(o == "correct" for o in non_transport)
    substantive = [o for o in non_transport if o in SUBSTANTIVE]
    policy = [o for o in non_transport if o in POLICY_OUTCOMES]
    substantive_correct = sum(o == "correct" for o in substantive)
    return {
        "n": n,
        "n_total": len(outcomes),
        # Primary outcome: fraction fully correct (refusals/format count as failures).
        "success_rate": correct / n,
        # Capability signal: accuracy among substantive (non-refusal) answers only.
        "substantive_accuracy": (substantive_correct / len(substantive)) if substantive else None,
        # Policy signal: fraction of non-answers / format failures.
        "policy_rate": len(policy) / n,
        "transport_rate": (len(outcomes) - n) / len(outcomes) if outcomes else 0.0,
        "counts": {name: outcomes.count(name) for name in _analyze.TAXONOMY_ORDER},
    }


def _success_scores(records: list[dict[str, Any]]) -> list[float]:
    return [
        1.0 if classify_outcome(record) == "correct" else 0.0
        for record in records
        if classify_outcome(record) != "transport_failure"
    ]


def bootstrap_gap_ci(
    records_a: list[dict[str, Any]],
    records_b: list[dict[str, Any]],
    *,
    samples: int,
    seed: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Percentile bootstrap CI for success_rate(B) - success_rate(A).

    Resamples records within each condition, so the interval reflects only
    within-condition sampling variability — the noise floor the gate compares to.
    """
    a = _success_scores(records_a)
    b = _success_scores(records_b)
    rng = random.Random(seed)
    gaps: list[float] = []
    na, nb = len(a), len(b)
    for _ in range(samples):
        mean_a = sum(a[rng.randrange(na)] for _ in range(na)) / na
        mean_b = sum(b[rng.randrange(nb)] for _ in range(nb)) / nb
        gaps.append(mean_b - mean_a)
    return percentile(gaps, alpha / 2), percentile(gaps, 1 - alpha / 2)


def normalize_varies(varies: Iterable[str]) -> list[str]:
    cleaned = sorted({v.strip() for v in varies if v and v.strip()})
    unknown = [v for v in cleaned if v not in KNOWN_KNOBS]
    if unknown:
        raise DifferentialError(
            f"Unknown changed-knob(s): {unknown}. Known knobs: {list(KNOWN_KNOBS)}"
        )
    return cleaned


def attribute(
    records_a: list[dict[str, Any]],
    records_b: list[dict[str, Any]],
    *,
    varies: Iterable[str],
    bootstrap_samples: int = 4000,
    seed: int = 20260724,
) -> dict[str, Any]:
    """Attribute the A->B behavior difference to a cause with controlled evidence."""
    changed = normalize_varies(varies)
    if not changed:
        raise DifferentialError(
            "Specify at least one changed knob (--varies). Attribution needs to know "
            "what was actually manipulated between A and B."
        )
    fa = condition_features(records_a)
    fb = condition_features(records_b)
    gap = fb["success_rate"] - fa["success_rate"]
    gap_ci = bootstrap_gap_ci(records_a, records_b, samples=bootstrap_samples, seed=seed)

    d_policy = fb["policy_rate"] - fa["policy_rate"]
    d_substantive = (
        fb["substantive_accuracy"] - fa["substantive_accuracy"]
        if fa["substantive_accuracy"] is not None and fb["substantive_accuracy"] is not None
        else None
    )

    ruled_out: list[str] = []
    changed_set = set(changed)

    # Step 0 — noise-floor gate.
    if gap_ci[0] <= 0 <= gap_ci[1]:
        attribution = "stochastic_noise"
        rationale = (
            f"The A->B success gap ({gap:+.3f}) has a 95% within-condition bootstrap "
            f"interval [{gap_ci[0]:+.3f}, {gap_ci[1]:+.3f}] that includes zero: the "
            "difference is not distinguishable from run-to-run variation."
        )
    else:
        ruled_out.append(
            f"stochastic_noise (gap CI [{gap_ci[0]:+.3f}, {gap_ci[1]:+.3f}] excludes 0)"
        )
        # Step 1 — framing: if the only knob changed is context/prompt, a surviving
        # real gap is a framing effect by construction.
        if changed_set <= {"context", "prompt"}:
            attribution = "context_framing"
            expressed = (
                "increased refusals/non-answers"
                if d_policy is not None and abs(d_policy) >= EFFECT_MIN
                else "changed substantive accuracy"
            )
            rationale = (
                "Only framing was changed and the gap survives the noise floor, so the "
                f"difference is attributed to context framing (expressed as {expressed})."
            )
        else:
            # Step 2 — capability vs. policy via the outcome taxonomy.
            cap = abs(d_substantive) if d_substantive is not None else 0.0
            pol = abs(d_policy)
            if cap >= EFFECT_MIN and pol < NEGLIGIBLE:
                attribution = "capability"
                ruled_out.append(f"reporting_policy (Δpolicy {d_policy:+.3f} below {NEGLIGIBLE})")
                rationale = (
                    f"Substantive accuracy moved {d_substantive:+.3f} while the refusal/"
                    f"non-answer rate barely moved ({d_policy:+.3f}): the model's answers "
                    "got worse, not more restricted."
                )
            elif pol >= EFFECT_MIN and cap < NEGLIGIBLE:
                attribution = "reporting_policy"
                ruled_out.append(
                    f"capability (Δsubstantive_accuracy "
                    f"{'n/a' if d_substantive is None else format(d_substantive, '+.3f')} below {NEGLIGIBLE})"
                )
                rationale = (
                    f"The refusal/non-answer rate rose {d_policy:+.3f} while accuracy among "
                    f"substantive answers held ({'n/a' if d_substantive is None else format(d_substantive, '+.3f')}): "
                    "capability is intact; behavior changed through reporting policy."
                )
            elif cap >= EFFECT_MIN and pol >= EFFECT_MIN:
                attribution = "confounded_capability_and_policy"
                rationale = (
                    f"Both substantive accuracy ({d_substantive:+.3f}) and refusal rate "
                    f"({d_policy:+.3f}) moved materially; the change is confounded and cannot "
                    "be cleanly split without a further controlled comparison."
                )
            else:
                attribution = "undetermined"
                rationale = (
                    "The gap survives the noise floor but neither the capability nor the "
                    "policy signature is large enough to attribute a cause; more replicates "
                    "or a tighter controlled comparison are needed."
                )

    return {
        "schema": "agent-behavior-differential-0.1.0",
        "attribution": attribution,
        "rationale": rationale,
        "changed_knobs": changed,
        "success_gap": gap,
        "success_gap_ci_95": [gap_ci[0], gap_ci[1]],
        "delta_policy_rate": d_policy,
        "delta_substantive_accuracy": d_substantive,
        "condition_a": fa,
        "condition_b": fb,
        "ruled_out": ruled_out,
        "interpretation_limits": [
            "Attribution concerns why measured behavior changed on the tested tasks, not why in general.",
            "It licenses no claim about evaluation awareness, intent, deception, safety, or consciousness.",
            "A cause can only be excluded relative to the controls actually run; unrun knobs are untested.",
            "Refusal detection here relies on empty/non-answer and format signals; fluent refusals require an added refusal detector.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    fa, fb = report["condition_a"], report["condition_b"]
    lines = [
        "# Agent Behavior Differential — attribution",
        "",
        f"**Attribution:** `{report['attribution']}`  ",
        f"**Changed between A and B:** {', '.join(report['changed_knobs'])}",
        "",
        f"{report['rationale']}",
        "",
        "| Signal | A | B | Δ |",
        "|---|---:|---:|---:|",
        f"| Success rate | {fa['success_rate']:.3f} | {fb['success_rate']:.3f} | {report['success_gap']:+.3f} |",
        f"| Substantive accuracy | {_fmt(fa['substantive_accuracy'])} | {_fmt(fb['substantive_accuracy'])} | {_fmt(report['delta_substantive_accuracy'], signed=True)} |",
        f"| Refusal / non-answer rate | {fa['policy_rate']:.3f} | {fb['policy_rate']:.3f} | {report['delta_policy_rate']:+.3f} |",
        "",
        f"Success-gap 95% within-condition bootstrap CI: "
        f"[{report['success_gap_ci_95'][0]:+.3f}, {report['success_gap_ci_95'][1]:+.3f}]",
        "",
    ]
    if report["ruled_out"]:
        lines.append("**Ruled out:**")
        lines.extend(f"- {item}" for item in report["ruled_out"])
        lines.append("")
    lines.append("**Interpretation limits:**")
    lines.extend(f"- {limit}" for limit in report["interpretation_limits"])
    lines.append("")
    return "\n".join(lines)


def _fmt(value: Any, *, signed: bool = False) -> str:
    if value is None:
        return "—"
    return f"{value:+.3f}" if signed else f"{value:.3f}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("condition_a", type=Path, help="JSONL results for condition A (baseline)")
    parser.add_argument("condition_b", type=Path, help="JSONL results for condition B (changed)")
    parser.add_argument(
        "--varies",
        required=True,
        help=f"Comma-separated knobs changed between A and B. Known: {','.join(KNOWN_KNOBS)}",
    )
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--bootstrap-samples", type=int, default=4000)
    parser.add_argument("--seed", type=int, default=20260724)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = attribute(
            load_jsonl(args.condition_a),
            load_jsonl(args.condition_b),
            varies=args.varies.split(","),
            bootstrap_samples=args.bootstrap_samples,
            seed=args.seed,
        )
    except DifferentialError as exc:
        print(f"Behavior-differential error: {exc}", file=sys.stderr)
        return 2

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
