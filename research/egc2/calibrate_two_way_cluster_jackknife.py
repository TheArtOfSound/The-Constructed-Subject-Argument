from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from collections import defaultdict
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


def _contrast_from_totals(totals: dict[str, float], counts: dict[str, int]) -> float:
    if any(counts[c] <= 0 for c in sim.CLASSES):
        raise ValueError("every monitoring class must remain represented")
    return sum(COEFFICIENTS[c] * totals[c] / counts[c] for c in sim.CLASSES)


def _sufficient_statistics(rows: list[dict]) -> tuple[dict, dict, dict]:
    totals = {c: 0.0 for c in sim.CLASSES}
    counts = {c: 0 for c in sim.CLASSES}
    clusters: dict[str, dict[object, dict[str, list[float | int]]]] = {
        "item": defaultdict(lambda: {c: [0.0, 0] for c in sim.CLASSES}),
        "rater": defaultdict(lambda: {c: [0.0, 0] for c in sim.CLASSES}),
        "intersection": defaultdict(lambda: {c: [0.0, 0] for c in sim.CLASSES}),
    }
    for row in rows:
        c = row["class"]
        shift = row["late"] - row["early"]
        totals[c] += shift
        counts[c] += 1
        for axis, key in (
            ("item", row["item"]),
            ("rater", row["rater"]),
            ("intersection", (row["item"], row["rater"])),
        ):
            clusters[axis][key][c][0] += shift
            clusters[axis][key][c][1] += 1
    return totals, counts, clusters


def _delete_estimates(
    totals: dict[str, float],
    counts: dict[str, int],
    cluster_stats: dict[object, dict[str, list[float | int]]],
) -> list[float]:
    estimates = []
    for deleted in cluster_stats.values():
        kept_totals = {c: totals[c] - float(deleted[c][0]) for c in sim.CLASSES}
        kept_counts = {c: counts[c] - int(deleted[c][1]) for c in sim.CLASSES}
        estimates.append(_contrast_from_totals(kept_totals, kept_counts))
    if len(estimates) < 2:
        raise ValueError("at least two clusters are required on each jackknife axis")
    return estimates


def _cv3j(estimates: list[float]) -> float:
    center = statistics.fmean(estimates)
    g = len(estimates)
    return (g - 1) / g * sum((estimate - center) ** 2 for estimate in estimates)


def two_way_cluster_jackknife(rows: list[dict], repair: str = "max_one_way") -> dict:
    """Two-way CV3J inclusion-exclusion variance with the max-one-way repair.

    Each component is a delete-one-cluster CV3J variance centered on the mean of
    its deletion estimates. The raw two-way variance is item + rater minus the
    item-by-rater intersection. ``max_one_way`` replaces the raw scalar variance
    by max(raw, item, rater), the scalar form of the safeguard discussed by
    MacKinnon, Nielsen, and Webb. Raw values and every deletion estimate remain
    available for audit and influence diagnostics.
    """
    if not rows:
        raise ValueError("rows must be nonempty")
    if repair not in {"none", "max_one_way"}:
        raise ValueError("repair must be 'none' or 'max_one_way'")

    totals, counts, clusters = _sufficient_statistics(rows)
    point = _contrast_from_totals(totals, counts)
    deletions = {
        axis: _delete_estimates(totals, counts, clusters[axis])
        for axis in ("item", "rater", "intersection")
    }
    components = {axis: _cv3j(values) for axis, values in deletions.items()}
    variance_raw = components["item"] + components["rater"] - components["intersection"]
    variance = (
        max(variance_raw, components["item"], components["rater"])
        if repair == "max_one_way" else variance_raw
    )
    undefined = not math.isfinite(variance) or variance < 0.0
    standard_error = math.nan if undefined else math.sqrt(variance)
    df = min(len(deletions["item"]), len(deletions["rater"])) - 1
    critical = t_critical_975(df)
    ci = [math.nan, math.nan] if undefined else [
        point - critical * standard_error,
        point + critical * standard_error,
    ]
    influence = {
        axis: {
            "count": len(values),
            "mean_deleted_estimate": statistics.fmean(values),
            "max_absolute_change_from_full": max(abs(value - point) for value in values),
            "min_deleted_estimate": min(values),
            "max_deleted_estimate": max(values),
            "deleted_estimates": values,
        }
        for axis, values in deletions.items()
    }
    return {
        "point": point,
        "variance_raw": variance_raw,
        "variance": variance,
        "repair": repair,
        "repair_activated": variance != variance_raw,
        "undefined": undefined,
        "standard_error": standard_error,
        "degrees_of_freedom": df,
        "critical_value": critical,
        "ci95": ci,
        "components": components,
        "influence": influence,
    }


def run_cell(effect: float, trials: int, seed: int, repair: str = "max_one_way") -> dict:
    if effect < 0:
        raise ValueError("effect must be nonnegative")
    if trials < 1:
        raise ValueError("trials must be positive")
    positive = negative = covered = undefined = repaired = 0
    estimates, widths, ses = [], [], []
    max_item, max_rater = [], []
    started = time.monotonic()
    for trial in range(trials):
        data_seed = power.stable_seed(seed, "complete_8x18_r8", "N1", trial, "data")
        data = power.simulate_effect(effect, data_seed) if effect else sim.simulate(
            power.design(), "global_stability", data_seed, **power.REGIME
        )
        result = two_way_cluster_jackknife(data["rows"], repair)
        estimates.append(result["point"])
        repaired += int(result["repair_activated"])
        max_item.append(result["influence"]["item"]["max_absolute_change_from_full"])
        max_rater.append(result["influence"]["rater"]["max_absolute_change_from_full"])
        if result["undefined"]:
            undefined += 1
            continue
        lo, hi = result["ci95"]
        positive += int(lo > 0.0)
        negative += int(hi < 0.0)
        covered += int(lo <= effect <= hi)
        widths.append(hi - lo)
        ses.append(result["standard_error"])
    valid = trials - undefined
    mean_estimate = statistics.fmean(estimates)
    return {
        "effect": effect,
        "method": f"two_way_cv3j_{repair}_t_min_clusters",
        "trials": trials,
        "valid_trials": valid,
        "undefined_rate": undefined / trials,
        "positive_direction_rejection_or_power": positive / valid if valid else math.nan,
        "negative_direction_rejection": negative / valid if valid else math.nan,
        "two_sided_rejection_rate": (positive + negative) / valid if valid else math.nan,
        "coverage": covered / valid if valid else math.nan,
        "mean_estimate": mean_estimate,
        "bias": mean_estimate - effect,
        "mean_interval_width": statistics.fmean(widths) if widths else math.nan,
        "mean_standard_error": statistics.fmean(ses) if ses else math.nan,
        "repair_activation_rate": repaired / trials,
        "mean_max_item_deletion_influence": statistics.fmean(max_item),
        "mean_max_rater_deletion_influence": statistics.fmean(max_rater),
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
    parser.add_argument("--repair", choices=("none", "max_one_way"), default="max_one_way")
    args = parser.parse_args()
    cells = [run_cell(0.0, args.null_trials, args.seed, args.repair)] + [
        run_cell(effect, args.power_trials, args.seed, args.repair) for effect in args.effects
    ]
    result = {
        "schema_version": "egc-two-way-cluster-jackknife-calibration-0.1.0",
        "design_id": "complete_8x18_r8",
        "regime": "N1",
        "seed": args.seed,
        "common_random_number_data_seeds": True,
        "estimator": "two-way CV3J: item + rater - item-by-rater intersection",
        "repair": (
            "max(raw two-way variance, item CV3J, rater CV3J)"
            if args.repair == "max_one_way" else "none"
        ),
        "small_sample_reference": "two-sided Student-t with df=min(item clusters, rater clusters)-1",
        "cells": cells,
        "status": "engineering_calibration_not_confirmatory",
    }
    Path(args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
