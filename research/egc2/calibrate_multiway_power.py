from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import time
from pathlib import Path

import simulate_crossed_item_rater as sim

METHODS = ("item", "pigeonhole_multinomial")
DEFAULT_EFFECTS = (0.10, 0.20, 0.30)
REGIME = {
    "item_sd": 0.25,
    "ambiguity_sd": 0.15,
    "rater_sd": 0.20,
    "domain_interaction_sd": 0.10,
    "dropout": "none",
}


def stable_seed(base_seed: int, *parts: object) -> int:
    payload = "|".join([str(base_seed), *(str(p) for p in parts)]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") & 0x7FFFFFFF


def design():
    return next(d for d in sim.DESIGNS if d.design_id == "complete_8x18_r8")


def truth_profile(effect: float) -> dict[str, float]:
    """Return a symmetric class-shift profile with the requested contrast.

    The estimand is exact_anchor - mean(structural_transfer, novel), so assigning
    +effect/2 to exact_anchor and -effect/2 to both comparison classes gives a
    true contrast of exactly ``effect`` before ordinal clipping. Surface variants
    remain unchanged. This is a clean power truth, not a substantive model of
    rater behavior.
    """
    if effect <= 0:
        raise ValueError("effect must be positive")
    return {
        "exact_anchor": effect / 2.0,
        "surface_variant": 0.0,
        "structural_transfer": -effect / 2.0,
        "novel": -effect / 2.0,
    }


def simulate_effect(effect: float, seed: int) -> dict:
    """Run the committed generator with a temporary nonzero truth profile."""
    key = f"power_{effect:.12g}"
    previous = sim.TRUTH.get(key)
    sim.TRUTH[key] = truth_profile(effect)
    try:
        return sim.simulate(design(), key, seed, **REGIME)
    finally:
        if previous is None:
            sim.TRUTH.pop(key, None)
        else:
            sim.TRUTH[key] = previous


def draws(data: dict, method: str, samples: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    rows = data["rows"]
    out: list[float] = []
    for _ in range(samples):
        if method == "item":
            value = sim._point_metrics(sim._resample_clusters(rows, "item", rng))["contrast"]
        elif method == "pigeonhole_multinomial":
            value = sim._pigeonhole_draw(rows, rng)
        else:
            raise ValueError(f"unknown method: {method}")
        out.append(value)
    return out


def interval(values: list[float]) -> tuple[float, float]:
    return sim.percentile(values, 0.025), sim.percentile(values, 0.975)


def run_cell(
    effect: float,
    method: str,
    trials: int,
    bootstrap_draws: int,
    seed: int,
) -> dict:
    if method not in METHODS:
        raise ValueError(f"unknown method: {method}")
    if trials < 1 or bootstrap_draws < 1:
        raise ValueError("trials and bootstrap_draws must be positive")

    detected = 0
    covered = 0
    widths: list[float] = []
    estimates: list[float] = []
    started = time.monotonic()

    for trial in range(trials):
        # Data seeds intentionally omit effect and method. This gives common random
        # numbers across effect sizes and resampling methods, reducing Monte Carlo
        # noise in method comparisons without changing the marginal generator.
        data_seed = stable_seed(seed, "complete_8x18_r8", "N1", trial, "data")
        draw_seed = stable_seed(
            seed,
            "complete_8x18_r8",
            "N1",
            effect,
            trial,
            method,
            "draws",
        )
        data = simulate_effect(effect, data_seed)
        point = sim._point_metrics(data["rows"])["contrast"]
        estimates.append(point)
        lo, hi = interval(draws(data, method, bootstrap_draws, draw_seed))
        detected += int(lo > 0.0)
        covered += int(lo <= effect <= hi)
        widths.append(hi - lo)

    mean_estimate = statistics.fmean(estimates)
    return {
        "effect": effect,
        "method": method,
        "trials": trials,
        "bootstrap_draws": bootstrap_draws,
        "power": detected / trials,
        "coverage": covered / trials,
        "mean_estimate": mean_estimate,
        "bias": mean_estimate - effect,
        "mean_interval_width": statistics.fmean(widths),
        "runtime_seconds": time.monotonic() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--trials", type=int, default=250)
    parser.add_argument("--bootstrap-draws", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260726)
    parser.add_argument("--effects", nargs="+", type=float, default=list(DEFAULT_EFFECTS))
    args = parser.parse_args()

    cells = [
        run_cell(effect, method, args.trials, args.bootstrap_draws, args.seed)
        for effect in args.effects
        for method in METHODS
    ]
    result = {
        "schema_version": "egc-multiway-power-calibration-0.1.0",
        "design_id": "complete_8x18_r8",
        "regime": "N1",
        "common_random_numbers": True,
        "effect_profile": {
            "exact_anchor": "effect/2",
            "surface_variant": 0.0,
            "structural_transfer": "-effect/2",
            "novel": "-effect/2",
        },
        "seed": args.seed,
        "cells": cells,
        "status": "engineering_calibration_not_confirmatory",
    }
    Path(args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
