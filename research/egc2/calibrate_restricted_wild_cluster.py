from __future__ import annotations

import argparse
import itertools
import json
import math
import statistics
import time
from pathlib import Path

import calibrate_multiway_power as power
import calibrate_two_way_crve as crve
import simulate_crossed_item_rater as sim

COEFFICIENTS = crve.COEFFICIENTS
COEFFICIENT_NORM_SQUARED = sum(value * value for value in COEFFICIENTS.values())


def _restricted_components(rows: list[dict]) -> tuple[dict[str, float], list[float]]:
    """Return null-restricted class means and unrestricted class residuals."""
    if not rows:
        raise ValueError("rows must be nonempty")
    means = {
        cls: statistics.fmean(
            row["late"] - row["early"] for row in rows if row["class"] == cls
        )
        for cls in sim.CLASSES
    }
    if any(math.isnan(value) for value in means.values()):
        raise ValueError("every monitoring class must be represented")
    theta = sum(COEFFICIENTS[cls] * means[cls] for cls in sim.CLASSES)
    restricted = {
        cls: means[cls] - COEFFICIENTS[cls] * theta / COEFFICIENT_NORM_SQUARED
        for cls in sim.CLASSES
    }
    residuals = [
        (row["late"] - row["early"]) - means[row["class"]] for row in rows
    ]
    check = sum(COEFFICIENTS[cls] * restricted[cls] for cls in sim.CLASSES)
    if abs(check) > 1e-12:
        raise RuntimeError("failed to impose scalar null")
    return restricted, residuals


def _bootstrap_rows(
    rows: list[dict],
    restricted: dict[str, float],
    residuals: list[float],
    signs: dict[int, int],
) -> list[dict]:
    """Reference row reconstruction retained for validation and auditability."""
    out = []
    for row, residual in zip(rows, residuals):
        shift = restricted[row["class"]] + signs[row["rater"]] * residual
        copy = dict(row)
        copy["early"] = 0.0
        copy["late"] = shift
        out.append(copy)
    return out


def _add_outer(matrix: list[list[float]], vector: list[float]) -> None:
    for i, left in enumerate(vector):
        for j, right in enumerate(vector):
            matrix[i][j] += left * right


def _scaled_score_matrix(cluster_vectors: dict[tuple, list[float]]) -> tuple[list[list[float]], int]:
    cluster_count = len(cluster_vectors)
    if cluster_count < 2:
        raise ValueError("at least two clusters are required")
    dimension = len(next(iter(cluster_vectors.values())))
    matrix = [[0.0] * dimension for _ in range(dimension)]
    for vector in cluster_vectors.values():
        _add_outer(matrix, vector)
    scale = cluster_count / (cluster_count - 1)
    for i in range(dimension):
        for j in range(dimension):
            matrix[i][j] *= scale
    return matrix, cluster_count


def _quadratic(signs: tuple[int, ...], matrix: list[list[float]]) -> float:
    return sum(
        signs[i] * matrix[i][j] * signs[j]
        for i in range(len(signs))
        for j in range(len(signs))
    )


def _prepare_quadratic_form(rows: list[dict]) -> dict:
    """Collapse each exact bootstrap statistic to rater-sign quadratic forms.

    For a fixed dataset, every bootstrap class mean, item score, rater score, and
    item-by-rater score is linear in the eight Rademacher signs. Each CGM variance
    component is therefore a quadratic form in those signs. Precomputing the
    corresponding matrices is algebraically equivalent to rebuilding all rows for
    every sign pattern, but removes repeated dictionary construction and cluster
    aggregation from the 256-pattern loop.
    """
    raters = sorted({row["rater"] for row in rows})
    rater_index = {rater: index for index, rater in enumerate(raters)}
    dimension = len(raters)
    restricted, residuals = _restricted_components(rows)
    counts = {cls: sum(row["class"] == cls for row in rows) for cls in sim.CLASSES}
    if any(count == 0 for count in counts.values()):
        raise ValueError("every monitoring class must be represented")

    residual_by_class_rater = {cls: [0.0] * dimension for cls in sim.CLASSES}
    for row, residual in zip(rows, residuals):
        residual_by_class_rater[row["class"]][rater_index[row["rater"]]] += residual

    point_vector = [
        sum(
            COEFFICIENTS[cls] * residual_by_class_rater[cls][index] / counts[cls]
            for cls in sim.CLASSES
        )
        for index in range(dimension)
    ]

    cluster_keys = (("item",), ("rater",), ("item", "rater"))
    cluster_vectors: list[dict[tuple, list[float]]] = [{}, {}, {}]
    for row, residual in zip(rows, residuals):
        cls = row["class"]
        row_rater = rater_index[row["rater"]]
        weight = COEFFICIENTS[cls] / counts[cls]
        coefficient = [
            -weight * residual_by_class_rater[cls][index] / counts[cls]
            for index in range(dimension)
        ]
        coefficient[row_rater] += weight * residual
        for destination, keys in zip(cluster_vectors, cluster_keys):
            cluster = tuple(row[key] for key in keys)
            vector = destination.setdefault(cluster, [0.0] * dimension)
            for index, value in enumerate(coefficient):
                vector[index] += value

    matrices = []
    cluster_counts = []
    for vectors in cluster_vectors:
        matrix, cluster_count = _scaled_score_matrix(vectors)
        matrices.append(matrix)
        cluster_counts.append(cluster_count)

    return {
        "raters": raters,
        "restricted": restricted,
        "residuals": residuals,
        "point_vector": point_vector,
        "matrices": {
            "item": matrices[0],
            "rater": matrices[1],
            "intersection": matrices[2],
        },
        "cluster_counts": {
            "item": cluster_counts[0],
            "rater": cluster_counts[1],
            "item_rater": cluster_counts[2],
        },
    }


def _quadratic_draw(prepared: dict, pattern: tuple[int, ...]) -> dict:
    point = sum(value * sign for value, sign in zip(prepared["point_vector"], pattern))
    matrices = prepared["matrices"]
    variance_raw = (
        _quadratic(pattern, matrices["item"])
        + _quadratic(pattern, matrices["rater"])
        - _quadratic(pattern, matrices["intersection"])
    )
    negative_variance = variance_raw < 0.0
    standard_error = math.sqrt(max(0.0, variance_raw))
    return {
        "point": point,
        "variance_raw": variance_raw,
        "standard_error": standard_error,
        "negative_variance_truncated": negative_variance,
    }


def exact_restricted_rater_wild_test(rows: list[dict]) -> dict:
    """Exact restricted wild-cluster bootstrap-t over the rater dimension."""
    observed = crve.two_way_crve(rows)
    if observed["standard_error"] <= 0.0 or observed["negative_variance_truncated"]:
        return {
            "defined": False,
            "reason": "observed_two_way_variance_nonpositive",
            "point": observed["point"],
            "observed": observed,
            "enumerated_patterns": 0,
            "defined_patterns": 0,
        }
    observed_t = observed["point"] / observed["standard_error"]
    prepared = _prepare_quadratic_form(rows)
    bootstrap_t: list[float] = []
    undefined = 0
    negative_variance = 0
    for pattern in itertools.product((-1, 1), repeat=len(prepared["raters"])):
        draw = _quadratic_draw(prepared, pattern)
        if draw["negative_variance_truncated"]:
            negative_variance += 1
        if draw["standard_error"] <= 0.0 or draw["negative_variance_truncated"]:
            undefined += 1
            continue
        bootstrap_t.append(draw["point"] / draw["standard_error"])
    enumerated = 2 ** len(prepared["raters"])
    if not bootstrap_t:
        return {
            "defined": False,
            "reason": "no_defined_bootstrap_statistics",
            "point": observed["point"],
            "observed": observed,
            "enumerated_patterns": enumerated,
            "defined_patterns": 0,
            "undefined_patterns": undefined,
            "negative_variance_patterns": negative_variance,
        }
    extreme = sum(abs(value) >= abs(observed_t) for value in bootstrap_t)
    p_value = extreme / len(bootstrap_t)
    return {
        "defined": True,
        "point": observed["point"],
        "observed_t": observed_t,
        "p_value_two_sided": p_value,
        "reject_0_05": p_value <= 0.05,
        "enumerated_patterns": enumerated,
        "defined_patterns": len(bootstrap_t),
        "undefined_patterns": undefined,
        "negative_variance_patterns": negative_variance,
        "undefined_pattern_rate": undefined / enumerated,
        "observed": observed,
        "optimization": "precomputed rater-sign quadratic forms",
    }


def run_cell(effect: float, trials: int, seed: int) -> dict:
    if effect < 0:
        raise ValueError("effect must be nonnegative")
    if trials < 1:
        raise ValueError("trials must be positive")
    rejected = 0
    defined = 0
    undefined_observed = 0
    undefined_pattern_rates: list[float] = []
    p_values: list[float] = []
    defined_pattern_counts: list[int] = []
    negative_pattern_counts: list[int] = []
    started = time.monotonic()
    for trial in range(trials):
        data_seed = power.stable_seed(seed, "complete_8x18_r8", "N1", trial, "data")
        data = power.simulate_effect(effect, data_seed) if effect else sim.simulate(
            power.design(), "global_stability", data_seed, **power.REGIME
        )
        result = exact_restricted_rater_wild_test(data["rows"])
        if not result["defined"]:
            undefined_observed += 1
            continue
        defined += 1
        rejected += int(result["reject_0_05"])
        p_values.append(result["p_value_two_sided"])
        undefined_pattern_rates.append(result["undefined_pattern_rate"])
        defined_pattern_counts.append(result["defined_patterns"])
        negative_pattern_counts.append(result["negative_variance_patterns"])
    return {
        "effect": effect,
        "method": "restricted_rater_wild_cluster_bootstrap_t_exact_rademacher_two_way_cgm",
        "trials": trials,
        "defined_trials": defined,
        "undefined_trials": undefined_observed,
        "undefined_trial_rate": undefined_observed / trials,
        "rejections": rejected,
        "rejection_or_power_among_all_trials": rejected / trials,
        "rejection_or_power_among_defined_trials": rejected / defined if defined else None,
        "mean_p_value_among_defined_trials": statistics.fmean(p_values) if p_values else None,
        "mean_undefined_pattern_rate": (
            statistics.fmean(undefined_pattern_rates) if undefined_pattern_rates else None
        ),
        "max_undefined_pattern_rate": max(undefined_pattern_rates) if undefined_pattern_rates else None,
        "minimum_defined_patterns": min(defined_pattern_counts) if defined_pattern_counts else None,
        "mean_negative_variance_patterns": (
            statistics.fmean(negative_pattern_counts) if negative_pattern_counts else None
        ),
        "enumerated_patterns_per_defined_trial": 2 ** power.design().raters,
        "runtime_seconds": time.monotonic() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--null-trials", type=int, default=1000)
    parser.add_argument("--power-trials", type=int, default=250)
    parser.add_argument("--power-effect", type=float, default=0.20)
    parser.add_argument("--seed", type=int, default=20260726)
    args = parser.parse_args()
    result = {
        "schema_version": "egc-restricted-wild-cluster-calibration-0.2.0",
        "design_id": "complete_8x18_r8",
        "regime": "N1",
        "seed": args.seed,
        "bootstrap_dgp_cluster_dimension": "rater",
        "bootstrap_weights": "exact enumeration of all rater-level Rademacher sign vectors",
        "null_imposition": "minimum-norm projection of class means onto the scalar contrast null",
        "studentization": "two-way CGM item + rater - item-by-rater CRVE",
        "optimization": (
            "algebraically equivalent precomputed linear and quadratic forms in the "
            "rater sign vector; sign patterns, null, seeds, and studentization unchanged"
        ),
        "cells": [
            run_cell(0.0, args.null_trials, args.seed),
            run_cell(args.power_effect, args.power_trials, args.seed),
        ],
        "status": "engineering_calibration_not_confirmatory",
    }
    Path(args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
