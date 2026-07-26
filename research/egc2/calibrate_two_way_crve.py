from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path

import calibrate_multiway_power as power
import simulate_crossed_item_rater as sim

COEFFICIENTS = {
    "exact_anchor": 1.0,
    "surface_variant": 0.0,
    "structural_transfer": -0.5,
    "novel": -0.5,
}
DEFAULT_EFFECTS = (0.10, 0.20, 0.30)

# Two-sided 0.975 Student-t critical values. The tested design has eight raters,
# so the primary reference distribution uses df=min(G_item, G_rater)-1=7.
T_975 = {
    1: 12.7062, 2: 4.3027, 3: 3.1824, 4: 2.7764, 5: 2.5706,
    6: 2.4469, 7: 2.3646, 8: 2.3060, 9: 2.2622, 10: 2.2281,
    11: 2.2010, 12: 2.1788, 13: 2.1604, 14: 2.1448, 15: 2.1314,
    16: 2.1199, 17: 2.1098, 18: 2.1009, 19: 2.0930, 20: 2.0860,
    21: 2.0796, 22: 2.0739, 23: 2.0687, 24: 2.0639, 25: 2.0595,
    26: 2.0555, 27: 2.0518, 28: 2.0484, 29: 2.0452, 30: 2.0423,
}


def t_critical_975(df: int) -> float:
    if df < 1:
        raise ValueError("degrees of freedom must be positive")
    return T_975[df] if df <= 30 else 1.96


def _cluster_component(rows: list[dict], influence: list[float], keys: tuple[str, ...]) -> tuple[float, int]:
    cluster_scores: dict[tuple, float] = {}
    for row, score in zip(rows, influence):
        cluster = tuple(row[key] for key in keys)
        cluster_scores[cluster] = cluster_scores.get(cluster, 0.0) + score
    cluster_count = len(cluster_scores)
    if cluster_count < 2:
        return math.nan, cluster_count
    raw = sum(score * score for score in cluster_scores.values())
    return cluster_count / (cluster_count - 1) * raw, cluster_count


def two_way_crve(rows: list[dict]) -> dict:
    """Analytic item-by-rater cluster-robust interval for the mean contrast.

    The variance uses Cameron-Gelbach-Miller inclusion-exclusion:
    V_item + V_rater - V_item×rater. Influence contributions are derived for the
    repository's linear contrast of class-specific mean early-to-late shifts.
    Negative estimates are retained as a diagnostic flag and truncated to zero
    only to make the interval numerically representable.
    """
    if not rows:
        raise ValueError("rows must be nonempty")

    point = sim._point_metrics(rows)["contrast"]
    counts = {c: sum(row["class"] == c for row in rows) for c in sim.CLASSES}
    if any(counts[c] == 0 for c in sim.CLASSES):
        raise ValueError("every monitoring class must be represented")
    means = {
        c: statistics.fmean(
            row["late"] - row["early"] for row in rows if row["class"] == c
        )
        for c in sim.CLASSES
    }
    influence = [
        COEFFICIENTS[row["class"]]
        * ((row["late"] - row["early"]) - means[row["class"]])
        / counts[row["class"]]
        for row in rows
    ]

    item_component, item_clusters = _cluster_component(rows, influence, ("item",))
    rater_component, rater_clusters = _cluster_component(rows, influence, ("rater",))
    intersection_component, intersection_clusters = _cluster_component(
        rows, influence, ("item", "rater")
    )
    variance_raw = item_component + rater_component - intersection_component
    negative_variance = variance_raw < 0.0
    variance = max(0.0, variance_raw)
    standard_error = math.sqrt(variance)
    degrees_of_freedom = min(item_clusters, rater_clusters) - 1
    critical_value = t_critical_975(degrees_of_freedom)
    lower = point - critical_value * standard_error
    upper = point + critical_value * standard_error
    return {
        "point": point,
        "variance_raw": variance_raw,
        "variance": variance,
        "standard_error": standard_error,
        "degrees_of_freedom": degrees_of_freedom,
        "critical_value": critical_value,
        "ci95": [lower, upper],
        "negative_variance_truncated": negative_variance,
        "clusters": {
            "item": item_clusters,
            "rater": rater_clusters,
            "item_rater": intersection_clusters,
        },
        "components": {
            "item": item_component,
            "rater": rater_component,
            "intersection": intersection_component,
        },
    }


def run_cell(effect: float, trials: int, seed: int) -> dict:
    if effect < 0:
        raise ValueError("effect must be nonnegative")
    if trials < 1:
        raise ValueError("trials must be positive")

    positive_rejections = 0
    negative_rejections = 0
    covered = 0
    negative_variances = 0
    estimates: list[float] = []
    widths: list[float] = []
    standard_errors: list[float] = []
    started = time.monotonic()

    for trial in range(trials):
        # This matches the common-random-number data seeds used by the committed
        # percentile-bootstrap null and power calibrations.
        data_seed = power.stable_seed(seed, "complete_8x18_r8", "N1", trial, "data")
        data = power.simulate_effect(effect, data_seed) if effect else sim.simulate(
            power.design(), "global_stability", data_seed, **power.REGIME
        )
        result = two_way_crve(data["rows"])
        lower, upper = result["ci95"]
        positive_rejections += int(lower > 0.0)
        negative_rejections += int(upper < 0.0)
        covered += int(lower <= effect <= upper)
        negative_variances += int(result["negative_variance_truncated"])
        estimates.append(result["point"])
        widths.append(upper - lower)
        standard_errors.append(result["standard_error"])

    mean_estimate = statistics.fmean(estimates)
    return {
        "effect": effect,
        "method": "two_way_crve_cgm_t_min_clusters",
        "trials": trials,
        "positive_direction_rejection_or_power": positive_rejections / trials,
        "negative_direction_rejection": negative_rejections / trials,
        "two_sided_rejection_rate": (positive_rejections + negative_rejections) / trials,
        "coverage": covered / trials,
        "mean_estimate": mean_estimate,
        "bias": mean_estimate - effect,
        "mean_interval_width": statistics.fmean(widths),
        "mean_standard_error": statistics.fmean(standard_errors),
        "negative_variance_rate": negative_variances / trials,
        "degrees_of_freedom": power.design().raters - 1,
        "runtime_seconds": time.monotonic() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--null-trials", type=int, default=1000)
    parser.add_argument("--power-trials", type=int, default=250)
    parser.add_argument("--seed", type=int, default=20260726)
    parser.add_argument("--effects", nargs="+", type=float, default=list(DEFAULT_EFFECTS))
    args = parser.parse_args()

    cells = [run_cell(0.0, args.null_trials, args.seed)] + [
        run_cell(effect, args.power_trials, args.seed) for effect in args.effects
    ]
    result = {
        "schema_version": "egc-two-way-crve-calibration-0.1.0",
        "design_id": "complete_8x18_r8",
        "regime": "N1",
        "seed": args.seed,
        "common_random_number_data_seeds": True,
        "estimator": (
            "Cameron-Gelbach-Miller inclusion-exclusion CRVE: "
            "item + rater - item-by-rater intersection"
        ),
        "small_sample_reference": (
            "two-sided Student-t with df=min(item clusters, rater clusters)-1"
        ),
        "cells": cells,
        "status": "engineering_calibration_not_confirmatory",
    }
    Path(args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
