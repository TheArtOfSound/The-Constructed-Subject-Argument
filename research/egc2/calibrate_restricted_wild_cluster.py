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
    """Return null-restricted class means and unrestricted class residuals.

    The class-mean vector is projected onto the hyperplane c'mu=0. This is the
    minimum-Euclidean-norm adjustment for the repository's fixed scalar contrast.
    Residuals are centered on unrestricted class means and receive one common
    Rademacher multiplier per rater in the bootstrap DGP.
    """
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
    out = []
    for row, residual in zip(rows, residuals):
        shift = restricted[row["class"]] + signs[row["rater"]] * residual
        copy = dict(row)
        copy["early"] = 0.0
        copy["late"] = shift
        out.append(copy)
    return out


def exact_restricted_rater_wild_test(rows: list[dict]) -> dict:
    """Exact restricted wild-cluster bootstrap-t over the rater dimension.

    The bootstrap DGP clusters on raters, while every draw is studentized with
    the repository's two-way CGM item+rater-intersection variance. With eight
    raters all 2^8 Rademacher vectors are enumerated, removing bootstrap Monte
    Carlo error. Undefined and negative-variance draws are retained explicitly.

    This is a narrowly scoped engineering candidate. It is not asserted to be a
    universally valid multiway bootstrap for arbitrary crossed designs.
    """
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
    raters = sorted({row["rater"] for row in rows})
    restricted, residuals = _restricted_components(rows)
    bootstrap_t: list[float] = []
    undefined = 0
    negative_variance = 0
    for pattern in itertools.product((-1, 1), repeat=len(raters)):
        signs = dict(zip(raters, pattern))
        draw = crve.two_way_crve(_bootstrap_rows(rows, restricted, residuals, signs))
        if draw["negative_variance_truncated"]:
            negative_variance += 1
        if draw["standard_error"] <= 0.0 or draw["negative_variance_truncated"]:
            undefined += 1
            continue
        bootstrap_t.append(draw["point"] / draw["standard_error"])
    if not bootstrap_t:
        return {
            "defined": False,
            "reason": "no_defined_bootstrap_statistics",
            "point": observed["point"],
            "observed": observed,
            "enumerated_patterns": 2 ** len(raters),
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
        "enumerated_patterns": 2 ** len(raters),
        "defined_patterns": len(bootstrap_t),
        "undefined_patterns": undefined,
        "negative_variance_patterns": negative_variance,
        "undefined_pattern_rate": undefined / (2 ** len(raters)),
        "observed": observed,
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
    return {
        "effect": effect,
        "method": "restricted_rater_wild_cluster_bootstrap_t_exact_rademacher_two_way_cgm",
        "trials": trials,
        "defined_trials": defined,
        "undefined_trials": undefined_observed,
        "undefined_trial_rate": undefined_observed / trials,
        "rejection_or_power_among_all_trials": rejected / trials,
        "rejection_or_power_among_defined_trials": rejected / defined if defined else None,
        "mean_p_value_among_defined_trials": statistics.fmean(p_values) if p_values else None,
        "mean_undefined_pattern_rate": (
            statistics.fmean(undefined_pattern_rates) if undefined_pattern_rates else None
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
        "schema_version": "egc-restricted-wild-cluster-calibration-0.1.0",
        "design_id": "complete_8x18_r8",
        "regime": "N1",
        "seed": args.seed,
        "bootstrap_dgp_cluster_dimension": "rater",
        "bootstrap_weights": "exact enumeration of all rater-level Rademacher sign vectors",
        "null_imposition": "minimum-norm projection of class means onto the scalar contrast null",
        "studentization": "two-way CGM item + rater - item-by-rater CRVE",
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
