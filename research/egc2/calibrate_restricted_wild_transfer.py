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
REGIMES = {
    "N1": dict(
        item_sd=0.25,
        ambiguity_sd=0.15,
        rater_sd=0.20,
        domain_interaction_sd=0.10,
        dropout="none",
    ),
    "N2": dict(
        item_sd=1.00,
        ambiguity_sd=0.35,
        rater_sd=0.50,
        domain_interaction_sd=0.25,
        dropout="none",
    ),
    "N3": dict(
        item_sd=0.60,
        ambiguity_sd=0.35,
        rater_sd=1.00,
        domain_interaction_sd=0.75,
        dropout="none",
    ),
}
DESIGN_IDS = ("complete_8x18_r8", "incomplete_12x24_r6")


def design(design_id: str):
    matches = [candidate for candidate in sim.DESIGNS if candidate.design_id == design_id]
    if len(matches) != 1:
        raise ValueError(f"unknown design_id: {design_id}")
    return matches[0]


def simulate_cell_data(design_id: str, regime: str, effect: float, seed: int) -> dict:
    selected_design = design(design_id)
    if regime not in REGIMES:
        raise ValueError(f"unknown regime: {regime}")
    if effect < 0:
        raise ValueError("effect must be nonnegative")
    if effect == 0:
        return sim.simulate(
            selected_design,
            "global_stability",
            seed,
            **REGIMES[regime],
        )

    key = f"transfer_power_{effect:.12g}"
    previous = sim.TRUTH.get(key)
    sim.TRUTH[key] = power.truth_profile(effect)
    try:
        return sim.simulate(selected_design, key, seed, **REGIMES[regime])
    finally:
        if previous is None:
            sim.TRUTH.pop(key, None)
        else:
            sim.TRUTH[key] = previous


def _restricted_components(rows: list[dict]) -> tuple[dict[str, float], list[float]]:
    if not rows:
        raise ValueError("rows must be nonempty")
    means = {
        cls: statistics.fmean(
            row["late"] - row["early"] for row in rows if row["class"] == cls
        )
        for cls in sim.CLASSES
    }
    theta = sum(COEFFICIENTS[cls] * means[cls] for cls in sim.CLASSES)
    restricted = {
        cls: means[cls]
        - COEFFICIENTS[cls] * theta / COEFFICIENT_NORM_SQUARED
        for cls in sim.CLASSES
    }
    residuals = [
        (row["late"] - row["early"]) - means[row["class"]] for row in rows
    ]
    return restricted, residuals


def _add_outer(matrix: list[list[float]], vector: list[float]) -> None:
    for i, left in enumerate(vector):
        for j, right in enumerate(vector):
            matrix[i][j] += left * right


def _scaled_score_matrix(
    cluster_vectors: dict[tuple, list[float]],
) -> tuple[list[list[float]], int]:
    cluster_count = len(cluster_vectors)
    if cluster_count < 2:
        raise ValueError("at least two clusters are required")
    dimension = len(next(iter(cluster_vectors.values())))
    matrix = [[0.0] * dimension for _ in range(dimension)]
    for vector in cluster_vectors.values():
        _add_outer(matrix, vector)
    scale = cluster_count / (cluster_count - 1)
    return [[value * scale for value in row] for row in matrix], cluster_count


def _quadratic(signs: tuple[int, ...], matrix: list[list[float]]) -> float:
    return sum(
        signs[i] * matrix[i][j] * signs[j]
        for i in range(len(signs))
        for j in range(len(signs))
    )


def _prepare(rows: list[dict]) -> dict:
    raters = sorted({row["rater"] for row in rows})
    rater_index = {rater: index for index, rater in enumerate(raters)}
    dimension = len(raters)
    _, residuals = _restricted_components(rows)
    counts = {
        cls: sum(row["class"] == cls for row in rows) for cls in sim.CLASSES
    }
    residual_by_class_rater = {
        cls: [0.0] * dimension for cls in sim.CLASSES
    }
    for row, residual in zip(rows, residuals):
        residual_by_class_rater[row["class"]][rater_index[row["rater"]]] += residual

    point_vector = [
        sum(
            COEFFICIENTS[cls]
            * residual_by_class_rater[cls][index]
            / counts[cls]
            for cls in sim.CLASSES
        )
        for index in range(dimension)
    ]

    cluster_keys = (("item",), ("rater",), ("item", "rater"))
    destinations: list[dict[tuple, list[float]]] = [{}, {}, {}]
    for row, residual in zip(rows, residuals):
        cls = row["class"]
        row_rater = rater_index[row["rater"]]
        weight = COEFFICIENTS[cls] / counts[cls]
        coefficient = [
            -weight * residual_by_class_rater[cls][index] / counts[cls]
            for index in range(dimension)
        ]
        coefficient[row_rater] += weight * residual
        for destination, keys in zip(destinations, cluster_keys):
            cluster = tuple(row[key] for key in keys)
            vector = destination.setdefault(cluster, [0.0] * dimension)
            for index, value in enumerate(coefficient):
                vector[index] += value

    matrices = [_scaled_score_matrix(destination)[0] for destination in destinations]
    return {
        "raters": raters,
        "point_vector": point_vector,
        "matrices": {
            "item": matrices[0],
            "rater": matrices[1],
            "intersection": matrices[2],
        },
    }


def exact_test(rows: list[dict], max_undefined_pattern_rate: float = 0.10) -> dict:
    if not 0 <= max_undefined_pattern_rate < 1:
        raise ValueError("max_undefined_pattern_rate must be in [0,1)")
    observed = crve.two_way_crve(rows)
    if observed["standard_error"] <= 0 or observed["negative_variance_truncated"]:
        return {
            "status": "indeterminate",
            "defined": False,
            "reason": "observed_two_way_variance_nonpositive",
            "point": observed["point"],
            "observed": observed,
            "enumerated_patterns": 0,
            "defined_patterns": 0,
        }

    observed_t = observed["point"] / observed["standard_error"]
    prepared = _prepare(rows)
    bootstrap_t: list[float] = []
    undefined = 0
    negative = 0
    for pattern in itertools.product((-1, 1), repeat=len(prepared["raters"])):
        point = sum(
            value * sign
            for value, sign in zip(prepared["point_vector"], pattern)
        )
        matrices = prepared["matrices"]
        variance_raw = (
            _quadratic(pattern, matrices["item"])
            + _quadratic(pattern, matrices["rater"])
            - _quadratic(pattern, matrices["intersection"])
        )
        if variance_raw <= 0:
            undefined += 1
            negative += int(variance_raw < 0)
            continue
        bootstrap_t.append(point / math.sqrt(variance_raw))

    enumerated = 2 ** len(prepared["raters"])
    if not bootstrap_t:
        return {
            "status": "indeterminate",
            "defined": False,
            "reason": "no_defined_bootstrap_statistics",
            "point": observed["point"],
            "enumerated_patterns": enumerated,
            "defined_patterns": 0,
            "undefined_patterns": undefined,
            "negative_variance_patterns": negative,
        }

    extreme = sum(abs(value) >= abs(observed_t) for value in bootstrap_t)
    p_value = extreme / len(bootstrap_t)
    undefined_pattern_rate = undefined / enumerated
    fail_closed = undefined_pattern_rate > max_undefined_pattern_rate
    return {
        "status": (
            "indeterminate"
            if fail_closed
            else ("reject" if p_value <= 0.05 else "not_reject")
        ),
        "defined": not fail_closed,
        "reason": "excessive_undefined_pattern_fraction" if fail_closed else None,
        "point": observed["point"],
        "observed_t": observed_t,
        "p_value_two_sided": p_value,
        "reject_0_05": p_value <= 0.05,
        "enumerated_patterns": enumerated,
        "defined_patterns": len(bootstrap_t),
        "undefined_patterns": undefined,
        "negative_variance_patterns": negative,
        "undefined_pattern_rate": undefined_pattern_rate,
        "max_undefined_pattern_rate": max_undefined_pattern_rate,
        "observed": observed,
    }


def run_cell(
    design_id: str,
    regime: str,
    effect: float,
    trials: int,
    seed: int,
    max_undefined_pattern_rate: float = 0.10,
) -> dict:
    if trials < 1:
        raise ValueError("trials must be positive")
    rejected = 0
    defined = 0
    indeterminate = 0
    reasons: dict[str, int] = {}
    undefined_pattern_rates: list[float] = []
    started = time.monotonic()

    for trial in range(trials):
        data_seed = power.stable_seed(seed, design_id, regime, trial, "data")
        data = simulate_cell_data(design_id, regime, effect, data_seed)
        result = exact_test(data["rows"], max_undefined_pattern_rate)
        if not result["defined"]:
            indeterminate += 1
            reason = result["reason"]
            reasons[reason] = reasons.get(reason, 0) + 1
            continue
        defined += 1
        rejected += int(result["reject_0_05"])
        undefined_pattern_rates.append(result["undefined_pattern_rate"])

    return {
        "design_id": design_id,
        "regime": regime,
        "effect": effect,
        "trials": trials,
        "defined_trials": defined,
        "indeterminate_trials": indeterminate,
        "indeterminate_rate": indeterminate / trials,
        "indeterminate_reasons": reasons,
        "rejections": rejected,
        "rejection_or_power_among_all_trials": rejected / trials,
        "rejection_or_power_among_defined_trials": (
            rejected / defined if defined else None
        ),
        "mean_undefined_pattern_rate_defined": (
            statistics.fmean(undefined_pattern_rates)
            if undefined_pattern_rates
            else None
        ),
        "max_undefined_pattern_rate_defined": (
            max(undefined_pattern_rates) if undefined_pattern_rates else None
        ),
        "enumerated_patterns": 2 ** design(design_id).raters,
        "runtime_seconds": time.monotonic() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--trials", type=int, default=30)
    parser.add_argument("--effect", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=20260726)
    parser.add_argument("--max-undefined-pattern-rate", type=float, default=0.10)
    parser.add_argument("--designs", nargs="+", default=list(DESIGN_IDS))
    parser.add_argument("--regimes", nargs="+", default=["N2", "N3"])
    args = parser.parse_args()

    result = {
        "schema_version": "egc-restricted-wild-transfer-0.1.0",
        "seed": args.seed,
        "effect": args.effect,
        "fail_closed_rule": {
            "observed_variance_nonpositive": "indeterminate",
            "undefined_pattern_rate_gt": args.max_undefined_pattern_rate,
            "denominator_policy": (
                "indeterminate trials remain in the all-trial rate and are not "
                "silently omitted"
            ),
        },
        "cells": [
            run_cell(
                design_id,
                regime,
                args.effect,
                args.trials,
                args.seed,
                args.max_undefined_pattern_rate,
            )
            for design_id in args.designs
            for regime in args.regimes
        ],
        "status": "engineering_transfer_falsification_not_confirmatory",
    }
    Path(args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
