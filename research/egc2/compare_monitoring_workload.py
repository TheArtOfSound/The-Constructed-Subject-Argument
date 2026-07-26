#!/usr/bin/env python3
"""Compare EGC monitoring designs under workload, recognition, drift, and dropout.

Synthetic sensitivity analysis only. Parameters are engineering regimes, not
estimates of real raters. The comparison asks whether the larger incomplete-
block design retains its prior detector sensitivity once per-rater workload and
informative dropout are modeled.
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
DESIGNS = {
    "complete_8x18": {"raters": 8, "items_per_class": 18, "items_per_rater_per_class": 18},
    "incomplete_12x36": {"raters": 12, "items_per_class": 36, "items_per_rater_per_class": 12},
}
REGIMES = {
    "reference": {"fatigue": 0.35, "recognition": 0.65, "novel_drift": 0.70, "noise": 0.45, "dropout": 0.08},
    "high_fatigue": {"fatigue": 0.80, "recognition": 0.65, "novel_drift": 0.70, "noise": 0.45, "dropout": 0.12},
    "high_noise": {"fatigue": 0.35, "recognition": 0.65, "novel_drift": 0.70, "noise": 0.80, "dropout": 0.10},
    "informative_dropout": {"fatigue": 0.50, "recognition": 0.65, "novel_drift": 0.70, "noise": 0.50, "dropout": 0.30},
    "null_generalized_learning": {"fatigue": 0.35, "recognition": 0.0, "novel_drift": 0.0, "noise": 0.45, "dropout": 0.08},
}


def canonical_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _class_signal(item_class: str, progress: float, recognition: float, novel_drift: float, null: bool) -> float:
    if null:
        return 0.35 * progress
    if item_class == "exact_anchor":
        return recognition * progress
    if item_class == "surface_variant":
        return 0.30 * recognition * progress
    if item_class == "structural_transfer":
        return -0.45 * novel_drift * progress
    return -novel_drift * progress


def _assignment(design: dict[str, int], rng: random.Random) -> list[tuple[int, str, int]]:
    """Return (rater, class, item_index) with balanced incomplete assignment."""
    raters = design["raters"]
    items = design["items_per_class"]
    per_rater = design["items_per_rater_per_class"]
    rows: list[tuple[int, str, int]] = []
    for cls in ITEM_CLASSES:
        for r in range(raters):
            start = (r * per_rater) % items
            chosen = [(start + k) % items for k in range(per_rater)]
            rng.shuffle(chosen)
            rows.extend((r, cls, i) for i in chosen)
    return rows


def generate_trial(seed: int, design_name: str, regime_name: str, baseline: float = 4.0) -> list[dict[str, Any]]:
    if design_name not in DESIGNS:
        raise ValueError(f"unknown design: {design_name}")
    if regime_name not in REGIMES:
        raise ValueError(f"unknown regime: {regime_name}")
    d = DESIGNS[design_name]
    g = REGIMES[regime_name]
    rng = random.Random(seed)
    severity = [rng.gauss(0, 0.35) for _ in range(d["raters"])]
    rows = _assignment(d, rng)
    by_rater: dict[int, list[tuple[int, str, int]]] = {r: [] for r in range(d["raters"])}
    for row in rows:
        by_rater[row[0]].append(row)
    out: list[dict[str, Any]] = []
    null = regime_name == "null_generalized_learning"
    for rater, assigned in by_rater.items():
        rng.shuffle(assigned)
        load = len(assigned)
        latent_disagreement = abs(severity[rater]) + rng.random() * 0.4
        dropout_prob = min(0.85, g["dropout"] * (0.35 + latent_disagreement))
        dropout_point = load
        if rng.random() < dropout_prob:
            dropout_point = rng.randint(max(4, load // 2), load - 1)
        for pos, (_, cls, item_idx) in enumerate(assigned):
            if pos >= dropout_point:
                continue
            session_progress = pos / max(1, load - 1)
            item_progress = item_idx / max(1, d["items_per_class"] - 1)
            fatigue_effect = -g["fatigue"] * max(0.0, (session_progress - 0.45) / 0.55)
            signal = _class_signal(cls, item_progress, g["recognition"], g["novel_drift"], null)
            latent = baseline - severity[rater] + signal + fatigue_effect + rng.gauss(0, g["noise"])
            score = max(1, min(7, int(math.floor(latent + 0.5))))
            out.append({
                "rater_id": f"R{rater+1:02d}", "item_class": cls,
                "item_progress": item_progress, "session_progress": session_progress,
                "score": score,
            })
    return out


def _shift(rows: list[dict[str, Any]], cls: str) -> float | None:
    early = [x["score"] for x in rows if x["item_class"] == cls and x["item_progress"] <= 0.25]
    late = [x["score"] for x in rows if x["item_class"] == cls and x["item_progress"] >= 0.75]
    if len(early) < 4 or len(late) < 4:
        return None
    return statistics.fmean(late) - statistics.fmean(early)


def summarize(rows: list[dict[str, Any]], delta: float = 0.20) -> dict[str, Any]:
    shifts = {c: _shift(rows, c) for c in ITEM_CLASSES}
    if any(v is None for v in shifts.values()):
        return {"status": "indeterminate", "shifts": shifts, "completion": len(rows)}
    false_reassurance = shifts["exact_anchor"] >= delta and shifts["novel"] <= -delta
    stable = abs(shifts["novel"]) < delta and abs(shifts["exact_anchor"]) < delta
    return {
        "status": "supported" if false_reassurance else ("rejected" if stable else "indeterminate"),
        "shifts": shifts, "completion": len(rows),
    }


def run_cell(design: str, regime: str, trials: int, seed: int, delta: float) -> dict[str, Any]:
    summaries = [summarize(generate_trial(seed + i * 1009, design, regime), delta) for i in range(trials)]
    statuses = [s["status"] for s in summaries]
    valid_shifts = [s for s in summaries if all(v is not None for v in s["shifts"].values())]
    return {
        "design": design, "regime": regime, "trials": trials,
        "support_rate": statuses.count("supported") / trials,
        "rejection_rate": statuses.count("rejected") / trials,
        "indeterminate_rate": statuses.count("indeterminate") / trials,
        "mean_completed_ratings": statistics.fmean(s["completion"] for s in summaries),
        "mean_shifts": {c: statistics.fmean(s["shifts"][c] for s in valid_shifts) if valid_shifts else None for c in ITEM_CLASSES},
    }


def compact_run(trials: int = 120, seed: int = 20260725, delta: float = 0.20) -> dict[str, Any]:
    started = time.time()
    cells = []
    for di, design in enumerate(DESIGNS):
        for ri, regime in enumerate(REGIMES):
            cells.append(run_cell(design, regime, trials, seed + di * 1000000 + ri * 100000, delta))
    payload = {
        "schema_version": "egc2-workload-monitoring-comparison-0.1.0",
        "scope": "synthetic sensitivity analysis; parameters are not empirical estimates",
        "seed": seed, "trials_per_cell": trials, "material_change": delta,
        "python_version": platform.python_version(), "runtime_seconds": round(time.time() - started, 3),
        "designs": DESIGNS, "regimes": REGIMES, "cells": cells,
    }
    payload["content_sha256"] = canonical_hash(payload)
    return payload


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trials", type=int, default=120)
    p.add_argument("--seed", type=int, default=20260725)
    p.add_argument("--delta", type=float, default=0.20)
    p.add_argument("--output", type=Path, default=Path("research/egc2/results/workload_monitoring_comparison.json"))
    a = p.parse_args()
    if a.trials < 20 or a.delta <= 0:
        return 2
    payload = compact_run(a.trials, a.seed, a.delta)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
