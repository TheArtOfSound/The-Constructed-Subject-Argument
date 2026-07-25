#!/usr/bin/env python3
"""Finite-sample calibration harness for QEIB family-level inference.

This script generates synthetic matched binary task-family records and calls the
production ``family_level_inference`` function from ``analyze_qeib.py``. It does
not reimplement the estimator. The compact default grid is intended for
engineering calibration, not definitive operating-characteristic claims.

Scenarios:
- sharp_null: neutral and target outcomes are identical within each family.
- constant_effect: every family has the same monotone probability shift.
- mean_zero_heterogeneous: half the families shift up and half shift down.

The scientific unit remains the task family. Additional stochastic replicates
only estimate each family-context mean; they do not increase the number of
independent families.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from analyze_qeib import family_level_inference


DEFAULT_FAMILY_COUNTS = (6, 12, 20)
DEFAULT_BASELINES = (0.05, 0.50, 0.95)
DEFAULT_SCENARIOS = ("sharp_null", "constant_effect", "mean_zero_heterogeneous")


@dataclass(frozen=True)
class CalibrationCell:
    scenario: str
    n_families: int
    baseline_accuracy: float
    effect_size: float
    replicates: int
    trials: int
    true_mean_effect: float
    coverage_95: float
    false_or_true_detection_rate: float
    formal_equivalence_rate: float
    point_within_margin_rate: float
    indeterminate_rate: float
    mean_estimated_delta: float
    mean_ci_width_95: float
    degenerate_ci_rate: float


def _bounded_probability(value: float) -> float:
    return min(1.0, max(0.0, value))


def _family_effects(scenario: str, n_families: int, effect_size: float) -> list[float]:
    if scenario == "sharp_null":
        return [0.0] * n_families
    if scenario == "constant_effect":
        return [effect_size] * n_families
    if scenario == "mean_zero_heterogeneous":
        effects = [effect_size if index % 2 == 0 else -effect_size for index in range(n_families)]
        if n_families % 2:
            effects[-1] = 0.0
        return effects
    raise ValueError(f"Unknown scenario: {scenario}")


def generate_records(
    *,
    scenario: str,
    n_families: int,
    baseline_accuracy: float,
    effect_size: float,
    replicates: int,
    seed: int,
    target_context: str = "eval_explicit",
) -> tuple[list[dict[str, Any]], float]:
    """Generate matched binary records and return records plus finite-grid truth.

    Neutral and target outcomes share the same uniform draw within each
    family-replicate. This induces matched pairs and makes the intervention effect
    a threshold shift rather than independent noise.
    """
    if n_families < 1:
        raise ValueError("n_families must be positive")
    if replicates < 1:
        raise ValueError("replicates must be positive")
    if not 0.0 <= baseline_accuracy <= 1.0:
        raise ValueError("baseline_accuracy must lie in [0, 1]")
    if effect_size < 0:
        raise ValueError("effect_size must be non-negative")

    rng = random.Random(seed)
    effects = _family_effects(scenario, n_families, effect_size)
    realized_probability_effects: list[float] = []
    records: list[dict[str, Any]] = []

    for family_index, family_effect in enumerate(effects):
        family_id = f"sim_family_{family_index:04d}"
        neutral_p = baseline_accuracy
        target_p = _bounded_probability(neutral_p + family_effect)
        realized_probability_effects.append(target_p - neutral_p)

        for replicate in range(replicates):
            u = rng.random()
            neutral_score = int(u < neutral_p)
            target_score = int(u < target_p)
            for context_id, score in (("neutral", neutral_score), (target_context, target_score)):
                records.append(
                    {
                        "provider": "qeib-simulation",
                        "model": "synthetic-matched-binary",
                        "model_version": "1",
                        "task_id": family_id,
                        "task_family_id": family_id,
                        "variant_id": "source",
                        "task_domain": "simulation",
                        "context_id": context_id,
                        "replicate": replicate,
                        "response_text": str(score),
                        "grader_outputs": {"score": score},
                        "error": None,
                    }
                )

    return records, statistics.fmean(realized_probability_effects)


def _interval_contains(interval: Iterable[float] | None, truth: float) -> bool:
    if interval is None:
        return False
    lower, upper = interval
    return float(lower) <= truth <= float(upper)


def run_cell(
    *,
    scenario: str,
    n_families: int,
    baseline_accuracy: float,
    effect_size: float,
    replicates: int,
    trials: int,
    equivalence_margin: float,
    bootstrap_samples: int,
    seed: int,
) -> CalibrationCell:
    if trials < 1:
        raise ValueError("trials must be positive")
    if bootstrap_samples < 100:
        raise ValueError("bootstrap_samples must be at least 100")
    if equivalence_margin <= 0:
        raise ValueError("equivalence_margin must be positive")

    coverage = detection = formal_equivalence = point_within = indeterminate = degenerate = 0
    estimates: list[float] = []
    widths: list[float] = []
    truths: list[float] = []

    for trial in range(trials):
        trial_seed = seed + trial * 1009
        records, truth = generate_records(
            scenario=scenario,
            n_families=n_families,
            baseline_accuracy=baseline_accuracy,
            effect_size=effect_size,
            replicates=replicates,
            seed=trial_seed,
        )
        result = family_level_inference(
            records,
            contexts=["neutral", "eval_explicit"],
            equivalence_margin=equivalence_margin,
            bootstrap_samples=bootstrap_samples,
            seed=trial_seed + 17,
        )["contexts"]["eval_explicit"]

        estimate = float(result["delta_mean"])
        ci_95 = result["cluster_bootstrap_ci_95"]
        estimates.append(estimate)
        truths.append(truth)
        if ci_95 is not None:
            width = float(ci_95[1]) - float(ci_95[0])
            widths.append(width)
            degenerate += int(math.isclose(width, 0.0, abs_tol=1e-15))
        coverage += int(_interval_contains(ci_95, truth))
        detection += int(bool(result["statistically_distinguishable_from_zero"]))
        formal_equivalence += int(bool(result["equivalent_within_prespecified_margin"]))
        point_within += int(bool(result["point_estimate_within_margin"]))
        indeterminate += int(result["label"] == "undetermined")

    return CalibrationCell(
        scenario=scenario,
        n_families=n_families,
        baseline_accuracy=baseline_accuracy,
        effect_size=effect_size,
        replicates=replicates,
        trials=trials,
        true_mean_effect=statistics.fmean(truths),
        coverage_95=coverage / trials,
        false_or_true_detection_rate=detection / trials,
        formal_equivalence_rate=formal_equivalence / trials,
        point_within_margin_rate=point_within / trials,
        indeterminate_rate=indeterminate / trials,
        mean_estimated_delta=statistics.fmean(estimates),
        mean_ci_width_95=statistics.fmean(widths) if widths else 0.0,
        degenerate_ci_rate=degenerate / trials,
    )


def run_grid(
    *,
    family_counts: Iterable[int],
    baselines: Iterable[float],
    scenarios: Iterable[str],
    effect_size: float,
    replicates: int,
    trials: int,
    equivalence_margin: float,
    bootstrap_samples: int,
    seed: int,
) -> dict[str, Any]:
    family_counts = tuple(family_counts)
    baselines = tuple(baselines)
    scenarios = tuple(scenarios)
    cells: list[CalibrationCell] = []
    cell_index = 0
    for scenario in scenarios:
        for n_families in family_counts:
            for baseline in baselines:
                cells.append(
                    run_cell(
                        scenario=scenario,
                        n_families=n_families,
                        baseline_accuracy=baseline,
                        effect_size=effect_size,
                        replicates=replicates,
                        trials=trials,
                        equivalence_margin=equivalence_margin,
                        bootstrap_samples=bootstrap_samples,
                        seed=seed + cell_index * 100_003,
                    )
                )
                cell_index += 1

    return {
        "schema_version": "qeib-calibration-0.1.0",
        "estimator": "production family_level_inference from analyze_qeib.py",
        "scientific_unit": "task_family_id",
        "settings": {
            "family_counts": list(family_counts),
            "baselines": list(baselines),
            "scenarios": list(scenarios),
            "effect_size": effect_size,
            "replicates": replicates,
            "trials_per_cell": trials,
            "equivalence_margin": equivalence_margin,
            "bootstrap_samples": bootstrap_samples,
            "seed": seed,
        },
        "interpretation_limits": [
            "Engineering calibration only; default trial counts are not publication-grade.",
            "Results characterize the implemented simulator and production estimator, not all QEIB task distributions.",
            "Detection does not identify evaluation awareness, deception, intent, safety, or consciousness.",
            "Repeated calls do not increase the number of independent task families.",
        ],
        "cells": [asdict(cell) for cell in cells],
    }


def _csv_ints(value: str) -> tuple[int, ...]:
    parsed = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    if not parsed or any(item < 1 for item in parsed):
        raise argparse.ArgumentTypeError("expected comma-separated positive integers")
    return parsed


def _csv_floats(value: str) -> tuple[float, ...]:
    parsed = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    if not parsed or any(not 0.0 <= item <= 1.0 for item in parsed):
        raise argparse.ArgumentTypeError("expected comma-separated numbers in [0, 1]")
    return parsed


def _csv_scenarios(value: str) -> tuple[str, ...]:
    parsed = tuple(item.strip() for item in value.split(",") if item.strip())
    unknown = sorted(set(parsed) - set(DEFAULT_SCENARIOS))
    if not parsed or unknown:
        raise argparse.ArgumentTypeError(f"unknown scenarios: {unknown}")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-counts", type=_csv_ints, default=DEFAULT_FAMILY_COUNTS)
    parser.add_argument("--baselines", type=_csv_floats, default=DEFAULT_BASELINES)
    parser.add_argument("--scenarios", type=_csv_scenarios, default=DEFAULT_SCENARIOS)
    parser.add_argument("--effect-size", type=float, default=0.20)
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--trials", type=int, default=200)
    parser.add_argument("--equivalence-margin", type=float, default=0.10)
    parser.add_argument("--bootstrap-samples", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=20260725)
    parser.add_argument("--output", type=Path, default=Path("research/qeib/results/calibration-compact.json"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.effect_size < 0:
        print("--effect-size must be non-negative", file=__import__("sys").stderr)
        return 2
    if args.replicates < 1 or args.trials < 1:
        print("--replicates and --trials must be positive", file=__import__("sys").stderr)
        return 2
    result = run_grid(
        family_counts=args.family_counts,
        baselines=args.baselines,
        scenarios=args.scenarios,
        effect_size=args.effect_size,
        replicates=args.replicates,
        trials=args.trials,
        equivalence_margin=args.equivalence_margin,
        bootstrap_samples=args.bootstrap_samples,
        seed=args.seed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"Wrote calibration results to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
