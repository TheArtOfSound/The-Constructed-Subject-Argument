#!/usr/bin/env python3
"""Compare rater count versus item coverage for the EGC anchor detector.

This targeted synthetic calibration preserves the committed simulator's random
number sequence and scoring model while aggregating only the rater-level early
versus late shifts required by the detector. Parameters are engineering stress
regimes, not empirical estimates of real raters.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import statistics
import time
from pathlib import Path
from typing import Any

ITEM_CLASSES = ("exact_anchor", "surface_variant", "structural_transfer", "novel")
REGIMES = ("generalized_learning", "pure_memorization", "memorization_plus_novel_drift")
DESIGNS = ((8, 18), (8, 36), (12, 18), (12, 36), (16, 18), (16, 36))
SCENARIOS = (
    {"scenario_id": "interior", "baseline_score": 4.0, "noise_sd": 0.45},
    {"scenario_id": "low_noise", "baseline_score": 4.0, "noise_sd": 0.25},
    {"scenario_id": "high_noise", "baseline_score": 4.0, "noise_sd": 0.80},
    {"scenario_id": "floor", "baseline_score": 1.4, "noise_sd": 0.45},
    {"scenario_id": "ceiling", "baseline_score": 6.6, "noise_sd": 0.45},
)


def canonical_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def class_effect(regime: str, item_class: str, progress: float,
                 learning_gain: float, novel_drift: float) -> float:
    if regime == "generalized_learning":
        return learning_gain * progress
    if regime == "pure_memorization":
        return learning_gain * progress if item_class == "exact_anchor" else 0.0
    if regime == "memorization_plus_novel_drift":
        if item_class == "exact_anchor":
            return learning_gain * progress
        if item_class == "surface_variant":
            return 0.35 * learning_gain * progress
        if item_class == "structural_transfer":
            return -0.5 * novel_drift * progress
        return -novel_drift * progress
    raise ValueError(f"unknown regime: {regime}")


def generate_rater_shifts(seed: int, regime: str, raters: int,
                           items_per_class: int, baseline_score: float,
                           noise_sd: float, learning_gain: float = 0.6,
                           novel_drift: float = 0.7) -> dict[str, list[float]]:
    """Generate exact-anchor and novel shifts using the committed RNG sequence."""
    if raters < 2 or items_per_class < 4:
        raise ValueError("raters >= 2 and items_per_class >= 4 required")
    rng = random.Random(seed)
    severity = [rng.gauss(0, 0.35) for _ in range(raters)]
    shifts = {"exact_anchor": [], "novel": []}
    for rater in range(raters):
        bins = {name: {"early": [], "late": []} for name in shifts}
        for item_class in ITEM_CLASSES:
            for item_index in range(items_per_class):
                progress = item_index / max(1, items_per_class - 1)
                latent = (
                    baseline_score + rng.gauss(0, 0.25) - severity[rater]
                    + class_effect(regime, item_class, progress, learning_gain, novel_drift)
                    + rng.gauss(0, noise_sd)
                )
                score = max(1, min(7, int(math.floor(latent + 0.5))))
                if item_class in bins:
                    if progress <= 0.25:
                        bins[item_class]["early"].append(score)
                    if progress >= 0.75:
                        bins[item_class]["late"].append(score)
        for item_class in shifts:
            shifts[item_class].append(
                statistics.fmean(bins[item_class]["late"])
                - statistics.fmean(bins[item_class]["early"])
            )
    return shifts


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    fraction = position - low
    return ordered[low] * (1 - fraction) + ordered[high] * fraction


def bootstrap_ci(shifts: list[float], samples: int, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    count = len(shifts)
    estimates = [
        statistics.fmean(rng.choice(shifts) for _ in range(count))
        for _ in range(samples)
    ]
    return percentile(estimates, 0.025), percentile(estimates, 0.975)


def classify(shifts: dict[str, list[float]], threshold: float,
             bootstrap_samples: int, seed: int) -> str:
    exact_ci = bootstrap_ci(shifts["exact_anchor"], bootstrap_samples, seed + 11)
    novel_ci = bootstrap_ci(shifts["novel"], bootstrap_samples, seed + 29)
    supported = exact_ci[0] >= threshold and novel_ci[1] <= -threshold
    rejected = exact_ci[1] < threshold or novel_ci[0] > -threshold
    return "supported" if supported else "rejected" if rejected else "indeterminate"


def run_cell(regime: str, scenario: dict[str, Any], raters: int,
             items_per_class: int, threshold: float, trials: int,
             bootstrap_samples: int, seed: int) -> dict[str, Any]:
    statuses = []
    for trial in range(trials):
        trial_seed = seed + trial * 1009
        shifts = generate_rater_shifts(
            trial_seed, regime, raters, items_per_class,
            scenario["baseline_score"], scenario["noise_sd"]
        )
        statuses.append(classify(shifts, threshold, bootstrap_samples, trial_seed + 500000))
    return {
        "scenario_id": scenario["scenario_id"], "raters": raters,
        "items_per_class": items_per_class, "regime": regime,
        "supported_rate": statuses.count("supported") / trials,
        "rejected_rate": statuses.count("rejected") / trials,
        "indeterminate_rate": statuses.count("indeterminate") / trials,
    }


def compare(trials: int = 100, bootstrap_samples: int = 100,
            threshold: float = 0.20, seed: int = 20260725) -> dict[str, Any]:
    started = time.time()
    cells = []
    for scenario_index, scenario in enumerate(SCENARIOS):
        for design_index, (raters, items_per_class) in enumerate(DESIGNS):
            for regime_index, regime in enumerate(REGIMES):
                cell_seed = seed + scenario_index * 10_000_000 + design_index * 1_000_000 + regime_index * 100_000
                cells.append(run_cell(regime, scenario, raters, items_per_class,
                                      threshold, trials, bootstrap_samples, cell_seed))
    payload = {
        "schema_version": "egc2-anchor-detector-design-comparison-0.1.0",
        "scope": "synthetic targeted design comparison",
        "seed": seed, "trials_per_cell": trials,
        "bootstrap_samples": bootstrap_samples, "threshold": threshold,
        "designs": [{"raters": r, "items_per_class": i} for r, i in DESIGNS],
        "scenarios": list(SCENARIOS), "cells": cells,
        "python_version": platform.python_version(),
        "runtime_seconds": round(time.time() - started, 3),
        "limitations": [
            "Engineering-scale calibration; tail-rate estimates remain imprecise.",
            "Synthetic parameters are not empirical rater estimates.",
            "Percentile rater-cluster bootstrap coverage is not established.",
            "Floor and ceiling regimes compress observable effects.",
        ],
    }
    payload["content_sha256"] = canonical_hash(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--bootstrap-samples", type=int, default=100)
    parser.add_argument("--threshold", type=float, default=0.20)
    parser.add_argument("--seed", type=int, default=20260725)
    parser.add_argument("--output", type=Path, default=Path("research/egc2/results/anchor_detector_design_comparison.json"))
    args = parser.parse_args()
    if args.trials < 20 or args.bootstrap_samples < 50 or args.threshold <= 0:
        raise SystemExit("trials >= 20, bootstrap-samples >= 50, and threshold > 0 required")
    payload = compare(args.trials, args.bootstrap_samples, args.threshold, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"content_sha256": payload["content_sha256"], "runtime_seconds": payload["runtime_seconds"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
