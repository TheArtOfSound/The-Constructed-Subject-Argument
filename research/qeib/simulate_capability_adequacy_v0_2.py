#!/usr/bin/env python3
"""Deterministic candidate comparison for the frozen QEIB adequacy v0.2 design.

This evaluates engineering gate operating characteristics under synthetic
neutral-context regimes. It does not estimate any property of a deployed model
and bears on no claim about awareness, deception, subjectivity, or consciousness.
"""
from __future__ import annotations
import argparse, hashlib, json, math, random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "qeib-capability-adequacy-v0.2-comparison-0.1.0"
Z_ONE_SIDED_95 = 1.6448536269514722

@dataclass(frozen=True)
class Regime:
    regime_id: str
    regime_class: str
    accuracy: float = 0.55
    transport: float = 0.0
    format_failure: float = 0.0
    domains: int = 6
    heterogeneity_sd: float = 0.0
    controls_valid: bool = True
    domain_mode: str = "balanced"

def clamp(p: float) -> float:
    return min(0.999999, max(0.000001, p))

def logit(p: float) -> float:
    p = clamp(p)
    return math.log(p / (1.0 - p))

def logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def wilson(successes: int, trials: int, z: float = Z_ONE_SIDED_95) -> tuple[float, float]:
    if trials <= 0:
        return 0.0, 1.0
    p = successes / trials
    z2 = z * z
    denom = 1.0 + z2 / trials
    center = (p + z2 / (2.0 * trials)) / denom
    half = z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * trials)) / trials) / denom
    return max(0.0, center - half), min(1.0, center + half)

def build_regimes(grid: dict[str, Any]) -> list[Regime]:
    rc = grid["regime_classes"]
    adequate = rc["clearly_adequate_interior"]
    out: list[Regime] = []
    for a in adequate["neutral_accuracy"]:
        for t in adequate["transport_failure_rate"]:
            for f in adequate["format_failure_rate"]:
                for h in adequate["family_heterogeneity_logit_sd"]:
                    out.append(Regime(f"adequate_a{a}_t{t}_f{f}_h{h}", "clearly_adequate_interior", a, t, f, 6, h))
    bad = rc["clearly_inadequate_exterior"]
    for a in bad["neutral_accuracy"]:
        out.append(Regime(f"inadequate_accuracy_{a}", "clearly_inadequate_exterior", accuracy=a))
    for t in bad["transport_failure_rate"]:
        out.append(Regime(f"inadequate_transport_{t}", "clearly_inadequate_exterior", transport=t))
    for f in bad["format_failure_rate"]:
        out.append(Regime(f"inadequate_format_{f}", "clearly_inadequate_exterior", format_failure=f))
    out.append(Regime("inadequate_coverage_below_0.88", "clearly_inadequate_exterior", transport=0.07, format_failure=0.07))
    out.append(Regime("structural_three_domains", "structural_invalidity", domains=3))
    out.append(Regime("structural_invalid_controls", "structural_invalidity", controls_valid=False))
    out.append(Regime("structural_severe_domain_imbalance", "structural_invalidity", domain_mode="severe_imbalance"))
    out.append(Regime("inadequate_domain_floor_ceiling_mixture", "clearly_inadequate_exterior", domain_mode="floor_ceiling_mixture"))
    bd = rc["boundary_diagnostics"]
    for a in bd["neutral_accuracy"]:
        out.append(Regime(f"boundary_accuracy_{a}", "boundary_diagnostic", accuracy=a))
    for t in bd["transport_failure_rate"]:
        out.append(Regime(f"boundary_transport_{t}", "boundary_diagnostic", transport=t))
    for f in bd["format_failure_rate"]:
        out.append(Regime(f"boundary_format_{f}", "boundary_diagnostic", format_failure=f))
    for c in bd["scorable_coverage"]:
        out.append(Regime(f"boundary_coverage_{c}", "boundary_diagnostic", transport=1.0-c))
    ids = [r.regime_id for r in out]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate regime id")
    return out

def candidates(grid: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"candidate_id": f"{rule}-n{n}-d{dev}", "family_count": n, "rule_family": rule,
         "max_domain_accuracy_deviation": dev}
        for n in grid["candidate_dimensions"]["family_counts"]
        for rule in grid["candidate_dimensions"]["rule_families"]
        for dev in grid["candidate_dimensions"]["max_domain_accuracy_deviation"]
    ]

def simulate_observation(regime: Regime, n: int, rng: random.Random) -> dict[str, Any]:
    domains = regime.domains
    domain_total = [0] * domains
    domain_correct = [0] * domains
    transport = format_failure = correct = incorrect = 0
    for i in range(n):
        if regime.domain_mode == "severe_imbalance":
            domain = 0 if i < int(0.80*n) else 1 + (i % max(1, domains-1))
        else:
            domain = i % domains
        if rng.random() < regime.transport:
            transport += 1
            continue
        if rng.random() < regime.format_failure:
            format_failure += 1
            continue
        domain_total[domain] += 1
        if regime.domain_mode == "floor_ceiling_mixture":
            p = 0.05 if domain < domains // 2 else 0.95
        else:
            p = logistic(logit(regime.accuracy) + rng.gauss(0.0, regime.heterogeneity_sd))
        if rng.random() < p:
            correct += 1
            domain_correct[domain] += 1
        else:
            incorrect += 1
    scorable = correct + incorrect
    domain_accuracies = [domain_correct[i] / domain_total[i] if domain_total[i] else None for i in range(domains)]
    return {"total": n, "correct": correct, "incorrect": incorrect, "scorable": scorable,
            "transport": transport, "format_failure": format_failure,
            "domain_total": domain_total, "domain_accuracies": domain_accuracies,
            "controls_valid": regime.controls_valid}

def evaluate(obs: dict[str, Any], candidate: dict[str, Any], grid: dict[str, Any]) -> tuple[bool, bool]:
    lim = grid["base_limits"]
    req = grid["shared_structural_requirements"]
    n = obs["total"]
    sc = obs["scorable"]
    acc = obs["correct"] / sc if sc else None
    coverage = sc / n
    transport = obs["transport"] / n
    fmt = obs["format_failure"] / n
    represented = sum(x >= req["minimum_eligible_families_per_domain"] for x in obs["domain_total"])
    structural = (obs["controls_valid"] and represented >= req["minimum_domains"]
                  and obs["correct"] >= lim["minimum_correct_families"]
                  and obs["incorrect"] >= lim["minimum_incorrect_families"])
    smoke = structural and coverage >= 0.50
    pooled = acc if acc is not None else 0.0
    deviations = [abs(x-pooled) for x in obs["domain_accuracies"] if x is not None]
    heterogeneity_ok = (len(deviations) >= req["minimum_domains"] and
                        max(deviations, default=1.0) <= candidate["max_domain_accuracy_deviation"])
    if candidate["rule_family"] == "point_threshold":
        inferential = structural and all([acc is not None,
            lim["neutral_accuracy_floor"] <= acc <= lim["neutral_accuracy_ceiling"],
            transport <= lim["maximum_transport_failure_rate"],
            fmt <= lim["maximum_format_failure_rate"],
            coverage >= lim["minimum_scorable_coverage"], heterogeneity_ok])
    else:
        acc_lo, acc_hi = wilson(obs["correct"], sc)
        _, transport_hi = wilson(obs["transport"], n)
        _, fmt_hi = wilson(obs["format_failure"], n)
        coverage_lo, _ = wilson(sc, n)
        inferential = structural and all([acc_lo >= lim["neutral_accuracy_floor"],
            acc_hi <= lim["neutral_accuracy_ceiling"],
            transport_hi <= lim["maximum_transport_failure_rate"],
            fmt_hi <= lim["maximum_format_failure_rate"],
            coverage_lo >= lim["minimum_scorable_coverage"], heterogeneity_ok])
    return smoke, inferential

def compare(grid: dict[str, Any], replicates: int | None = None, seed: int | None = None) -> dict[str, Any]:
    reps = int(replicates or grid["simulation"]["replicates_per_regime"])
    if reps < 100:
        raise ValueError("replicates must be at least 100")
    seed = int(seed if seed is not None else grid["simulation"]["seed"])
    regs = build_regimes(grid)
    cands = candidates(grid)
    observations: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for n in grid["candidate_dimensions"]["family_counts"]:
        for regime in regs:
            digest = hashlib.sha256(f"{seed}:{n}:{regime.regime_id}".encode()).digest()
            rng = random.Random(int.from_bytes(digest[:8], "big"))
            observations[(n, regime.regime_id)] = [simulate_observation(regime, n, rng) for _ in range(reps)]
    target = grid["operating_risk_targets"]
    results = []
    complexity = {"point_threshold": 0, "wilson_bound": 1, "two_stage": 2}
    for cand in cands:
        rows = []
        for regime in regs:
            smoke = inferential = 0
            for obs in observations[(cand["family_count"], regime.regime_id)]:
                s, g = evaluate(obs, cand, grid)
                smoke += int(s); inferential += int(g)
            pass_rate = inferential / reps
            rows.append({"regime_id": regime.regime_id, "regime_class": regime.regime_class,
                "inferential_pass_rate": pass_rate,
                "smoke_pass_rate": smoke / reps if cand["rule_family"] == "two_stage" else None,
                "false_adequacy_rate": pass_rate if regime.regime_class in {"clearly_inadequate_exterior","structural_invalidity"} else 0.0,
                "false_inadequacy_rate": 1.0-pass_rate if regime.regime_class == "clearly_adequate_interior" else 0.0})
        worst_fa = max((r["false_adequacy_rate"] for r in rows if r["regime_class"]=="clearly_inadequate_exterior"), default=0.0)
        worst_fi = max((r["false_inadequacy_rate"] for r in rows if r["regime_class"]=="clearly_adequate_interior"), default=0.0)
        worst_struct = max((r["inferential_pass_rate"] for r in rows if r["regime_class"]=="structural_invalidity"), default=0.0)
        qualifies = (worst_fa <= target["max_false_adequacy_per_clearly_inadequate_regime"]
                     and worst_fi <= target["max_false_inadequacy_per_clearly_adequate_interior_regime"]
                     and worst_struct <= target["max_structural_invalidity_pass_rate"])
        results.append({**cand, "qualifies": qualifies, "worst_case_false_adequacy": worst_fa,
                        "worst_case_false_inadequacy": worst_fi,
                        "worst_structural_invalidity_pass_rate": worst_struct,
                        "regimes": rows, "_complexity": complexity[cand["rule_family"]]})
    qualified = [r for r in results if r["qualifies"]]
    qualified.sort(key=lambda r:(r["family_count"],r["worst_case_false_adequacy"],
                                 r["worst_case_false_inadequacy"],r["_complexity"],
                                 r["max_domain_accuracy_deviation"]))
    selected = qualified[0]["candidate_id"] if qualified else grid["selection_rule"]["if_none_qualify"]
    for r in results: r.pop("_complexity", None)
    projection = {k:grid[k] for k in ["simulation","operating_risk_targets","shared_structural_requirements","candidate_dimensions","base_limits","regime_classes","selection_rule"]}
    return {"schema_version": SCHEMA, "seed": seed, "replicates_per_regime": reps,
        "grid_sha256": hashlib.sha256(json.dumps(projection,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
        "candidate_count": len(results), "regime_count": len(regs), "selection": selected,
        "qualified_candidate_ids": [r["candidate_id"] for r in qualified], "candidates": results,
        "interpretation_boundary": [
            "Selection is an engineering operating-risk decision under synthetic regimes, not psychometric validation.",
            "Boundary diagnostics do not determine candidate qualification.",
            "No result bears on evaluation awareness, deception, intent, safety, subjectivity, sentience, or consciousness."]}

def frozen_artifact(result: dict[str, Any]) -> dict[str, Any]:
    """Compact selection artifact preserving every candidate and its worst-case risks."""
    keep = {k: result[k] for k in ["schema_version", "seed", "replicates_per_regime", "grid_sha256",
        "candidate_count", "regime_count", "selection", "qualified_candidate_ids", "interpretation_boundary"]}
    keep["candidates"] = [{k: candidate[k] for k in ["candidate_id", "family_count", "rule_family",
        "max_domain_accuracy_deviation", "qualifies", "worst_case_false_adequacy",
        "worst_case_false_inadequacy", "worst_structural_invalidity_pass_rate"]}
        for candidate in result["candidates"]]
    return keep

def main(argv: Iterable[str] | None = None) -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--grid",type=Path,default=Path("research/qeib/capability_adequacy_v0.2_candidate_grid.json"))
    p.add_argument("--replicates",type=int)
    p.add_argument("--seed",type=int)
    p.add_argument("--output",type=Path)
    a=p.parse_args(list(argv) if argv is not None else None)
    grid=json.loads(a.grid.read_text())
    result=frozen_artifact(compare(grid,a.replicates,a.seed))
    rendered=json.dumps(result,sort_keys=True,separators=(",",":"))+"\n"
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(rendered)
    else: print(rendered,end="")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
