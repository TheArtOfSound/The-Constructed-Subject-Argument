from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path

import simulate_crossed_item_rater as sim

DESIGN_IDS = ("complete_8x18_r8", "incomplete_12x24_r6", "incomplete_16x24_r6")
DRAW_LEVELS = (100, 500, 2000)
REGIMES = {
    "N1": dict(item_sd=0.25, ambiguity_sd=0.15, rater_sd=0.20, domain_interaction_sd=0.10, dropout="none"),
    "N2": dict(item_sd=1.00, ambiguity_sd=0.35, rater_sd=0.50, domain_interaction_sd=0.25, dropout="none"),
    "N3": dict(item_sd=0.60, ambiguity_sd=0.35, rater_sd=1.00, domain_interaction_sd=0.75, dropout="none"),
}
METHODS = ("item", "rater", "pigeonhole_multinomial")


def stable_seed(base_seed: int, *parts: object) -> int:
    payload = "|".join([str(base_seed), *(str(p) for p in parts)]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") & 0x7FFFFFFF


def _design(design_id: str):
    matches = [d for d in sim.DESIGNS if d.design_id == design_id]
    if len(matches) != 1:
        raise ValueError(f"unknown design_id: {design_id}")
    return matches[0]


def _draws(data: dict, method: str, samples: int, seed: int) -> list[float]:
    rows = data["rows"]
    rng = random.Random(seed)
    out: list[float] = []
    for _ in range(samples):
        if method == "item":
            value = sim._point_metrics(sim._resample_clusters(rows, "item", rng))["contrast"]
        elif method == "rater":
            value = sim._point_metrics(sim._resample_clusters(rows, "rater", rng))["contrast"]
        elif method == "pigeonhole_multinomial":
            value = sim._pigeonhole_draw(rows, rng)
        else:
            raise ValueError(f"unknown method: {method}")
        out.append(value)
    return out


def interval(draws: list[float]) -> tuple[float, float] | None:
    valid = [x for x in draws if math.isfinite(x)]
    if not valid:
        return None
    return sim.percentile(valid, 0.025), sim.percentile(valid, 0.975)


def _binomial_cdf(k: int, n: int, p: float) -> float:
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    term = (1.0 - p) ** n
    total = term
    for i in range(0, k):
        term *= (n - i) / (i + 1) * p / (1.0 - p)
        total += term
    return min(1.0, max(0.0, total))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> list[float]:
    if n <= 0 or not (0 <= k <= n):
        raise ValueError("require 0 <= k <= n and n > 0")
    if k == 0:
        lo = 0.0
    else:
        target = 1.0 - alpha / 2.0
        a, b = 0.0, k / n
        for _ in range(80):
            m = (a + b) / 2.0
            if _binomial_cdf(k - 1, n, m) > target:
                a = m
            else:
                b = m
        lo = (a + b) / 2.0
    if k == n:
        hi = 1.0
    else:
        target = alpha / 2.0
        a, b = k / n, 1.0
        for _ in range(80):
            m = (a + b) / 2.0
            if _binomial_cdf(k, n, m) > target:
                a = m
            else:
                b = m
        hi = (a + b) / 2.0
    return [lo, hi]


def _quantile(values: list[float], p: float) -> float:
    return sim.percentile(values, p) if values else math.nan


def run_cell(design_id: str, regime: str, method: str, trials: int, max_draws: int,
             base_seed: int, draw_levels: tuple[int, ...] = DRAW_LEVELS) -> dict:
    if regime not in REGIMES:
        raise ValueError(f"unknown regime: {regime}")
    if method not in METHODS:
        raise ValueError(f"unknown method: {method}")
    levels = tuple(sorted(set(draw_levels)))
    if not levels or levels[-1] > max_draws or levels[0] < 1:
        raise ValueError("draw levels must be positive and <= max_draws")
    design = _design(design_id)
    false_positive = {b: 0 for b in levels}
    covered = {b: 0 for b in levels}
    widths = {b: [] for b in levels}
    undefined = {b: 0 for b in levels}
    movement_100_500: list[float] = []
    movement_500_2000: list[float] = []
    decision_change_100_500 = 0
    decision_change_500_2000 = 0
    trial_records = []
    started = time.monotonic()

    for t in range(trials):
        data_seed = stable_seed(base_seed, design_id, regime, t, "data")
        draw_seed = stable_seed(base_seed, design_id, regime, t, method, "draws")
        data = sim.simulate(design, "global_stability", data_seed, **REGIMES[regime])
        draws = _draws(data, method, max_draws, draw_seed)
        trial_intervals = {}
        decisions = {}
        for b in levels:
            ci = interval(draws[:b])
            trial_intervals[str(b)] = ci
            if ci is None:
                undefined[b] += 1
                decisions[b] = None
                continue
            lo, hi = ci
            reject = lo > 0.0 or hi < 0.0
            decisions[b] = reject
            false_positive[b] += int(reject)
            covered[b] += int(lo <= 0.0 <= hi)
            widths[b].append(hi - lo)
        if 100 in levels and 500 in levels and trial_intervals["100"] and trial_intervals["500"]:
            c100, c500 = trial_intervals["100"], trial_intervals["500"]
            movement_100_500.append(max(abs(c100[0]-c500[0]), abs(c100[1]-c500[1])))
            decision_change_100_500 += int(decisions[100] != decisions[500])
        if 500 in levels and 2000 in levels and trial_intervals["500"] and trial_intervals["2000"]:
            c500, c2000 = trial_intervals["500"], trial_intervals["2000"]
            movement_500_2000.append(max(abs(c500[0]-c2000[0]), abs(c500[1]-c2000[1])))
            decision_change_500_2000 += int(decisions[500] != decisions[2000])
        trial_records.append({"trial": t, "data_seed": data_seed, "draw_seed": draw_seed,
                              "intervals": trial_intervals, "decisions": {str(k): v for k,v in decisions.items()},
                              "undefined_draws": sum(not math.isfinite(x) for x in draws)})

    summary = {}
    for b in levels:
        completed = trials - undefined[b]
        fp = false_positive[b]
        summary[str(b)] = {
            "false_positive_count": fp,
            "false_positive_rate": fp / completed if completed else None,
            "false_positive_binomial_ci95": clopper_pearson(fp, completed) if completed else None,
            "coverage": covered[b] / completed if completed else None,
            "mean_interval_width": statistics.fmean(widths[b]) if widths[b] else None,
            "undefined_trial_count": undefined[b],
        }
    return {
        "schema_version": "egc-multiway-calibration-cell-0.1.0",
        "design_id": design_id,
        "null_regime": regime,
        "method": method,
        "trials_planned": trials,
        "trials_completed": trials,
        "bootstrap_draws_max": max_draws,
        "nested_draw_levels": list(levels),
        "summary_by_draw_level": summary,
        "median_endpoint_movement_100_to_500": _quantile(movement_100_500, 0.5),
        "median_endpoint_movement_500_to_2000": _quantile(movement_500_2000, 0.5),
        "p95_endpoint_movement_500_to_2000": _quantile(movement_500_2000, 0.95),
        "decision_change_rate_100_to_500": decision_change_100_500 / len(movement_100_500) if movement_100_500 else None,
        "decision_change_rate_500_to_2000": decision_change_500_2000 / len(movement_500_2000) if movement_500_2000 else None,
        "runtime_seconds": time.monotonic() - started,
        "trial_records": trial_records,
        "status": "completed",
    }


def cell_key(row: dict) -> tuple:
    return (row["design_id"], row["null_regime"], row["method"], row["trials_planned"], row["bootstrap_draws_max"])


def load_completed(path: Path) -> dict[tuple, dict]:
    out = {}
    if not path.exists():
        return out
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        key = cell_key(row)
        if key in out and out[key] != row:
            raise ValueError(f"conflicting duplicate cell at line {line_no}: {key}")
        out[key] = row
    return out


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())


def repository_sha() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    p.add_argument("--trials", type=int, default=1000)
    p.add_argument("--max-draws", type=int, default=2000)
    p.add_argument("--seed", type=int, default=20260726)
    p.add_argument("--designs", nargs="+", default=list(DESIGN_IDS), choices=DESIGN_IDS)
    p.add_argument("--regimes", nargs="+", default=["N1", "N2", "N3"], choices=tuple(REGIMES))
    p.add_argument("--methods", nargs="+", default=list(METHODS), choices=METHODS)
    p.add_argument("--stop-after-cells", type=int)
    a = p.parse_args()
    if a.trials < 1 or a.max_draws < 1:
        p.error("trials and max-draws must be positive")
    levels = tuple(b for b in DRAW_LEVELS if b <= a.max_draws)
    if not levels:
        levels = (a.max_draws,)
    output = Path(a.output)
    completed = load_completed(output)
    produced = 0
    for design_id in a.designs:
        for regime in a.regimes:
            for method in a.methods:
                key = (design_id, regime, method, a.trials, a.max_draws)
                if key in completed:
                    continue
                row = run_cell(design_id, regime, method, a.trials, a.max_draws, a.seed, levels)
                row["provenance"] = {
                    "repository_sha": repository_sha(),
                    "python_version": sys.version,
                    "platform": platform.platform(),
                    "command": sys.argv,
                    "base_seed": a.seed,
                }
                append_jsonl(output, row)
                produced += 1
                if a.stop_after_cells is not None and produced >= a.stop_after_cells:
                    return


if __name__ == "__main__":
    main()
