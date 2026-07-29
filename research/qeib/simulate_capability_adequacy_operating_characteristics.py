#!/usr/bin/env python3
"""Deterministic operating-characteristic simulation for the QEIB adequacy gate.

The simulator estimates only how often the frozen engineering gate passes or
fails under known synthetic neutral-context regimes. It does not simulate or
infer evaluation awareness, deception, intent, subjectivity, or consciousness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "qeib-capability-adequacy-operating-characteristics-0.1.0"
DEFAULT_SEED = 20260729
DEFAULT_REPLICATES = 2000


@dataclass(frozen=True)
class Thresholds:
    minimum_eligible_families: int
    minimum_represented_domains: int
    minimum_eligible_families_per_represented_domain: int
    minimum_neutral_scorable_coverage: float
    minimum_neutral_accuracy: float
    maximum_neutral_accuracy: float
    minimum_correct_eligible_families: int
    minimum_incorrect_eligible_families: int
    maximum_transport_failure_fraction: float
    maximum_empty_format_ungradable_fraction: float


@dataclass(frozen=True)
class Regime:
    regime_id: str
    families: int
    domains: int
    latent_accuracy: float
    family_heterogeneity_sd: float
    transport_failure_probability: float
    empty_format_probability: float
    controls_pass: bool = True


def _clamp(value: float, low: float = 0.001, high: float = 0.999) -> float:
    return max(low, min(high, value))


def _logit(p: float) -> float:
    p = _clamp(p)
    return math.log(p / (1.0 - p))


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def load_thresholds(policy_path: Path) -> Thresholds:
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    t = policy["thresholds"]
    return Thresholds(
        minimum_eligible_families=int(t["minimum_eligible_families"]),
        minimum_represented_domains=int(t["minimum_represented_domains"]),
        minimum_eligible_families_per_represented_domain=int(
            t["minimum_eligible_families_per_represented_domain"]
        ),
        minimum_neutral_scorable_coverage=float(t["minimum_neutral_scorable_coverage"]),
        minimum_neutral_accuracy=float(t["minimum_neutral_accuracy"]),
        maximum_neutral_accuracy=float(t["maximum_neutral_accuracy"]),
        minimum_correct_eligible_families=int(t["minimum_correct_eligible_families"]),
        minimum_incorrect_eligible_families=int(t["minimum_incorrect_eligible_families"]),
        maximum_transport_failure_fraction=float(t["maximum_transport_failure_fraction"]),
        maximum_empty_format_ungradable_fraction=float(
            t["maximum_empty_format_ungradable_fraction"]
        ),
    )


def default_regimes() -> list[Regime]:
    """Boundary-focused regimes; not a population model of deployed systems."""
    return [
        Regime("adequate_mid_24", 24, 6, 0.55, 0.35, 0.00, 0.00),
        Regime("adequate_mid_12", 12, 4, 0.55, 0.35, 0.00, 0.00),
        Regime("small_n_8", 8, 4, 0.55, 0.35, 0.00, 0.00),
        Regime("floor_10pct", 24, 6, 0.10, 0.25, 0.00, 0.00),
        Regime("floor_boundary_20pct", 24, 6, 0.20, 0.25, 0.00, 0.00),
        Regime("ceiling_boundary_90pct", 24, 6, 0.90, 0.25, 0.00, 0.00),
        Regime("ceiling_95pct", 24, 6, 0.95, 0.20, 0.00, 0.00),
        Regime("high_heterogeneity", 24, 6, 0.55, 1.25, 0.00, 0.00),
        Regime("transport_boundary_5pct", 24, 6, 0.55, 0.35, 0.05, 0.00),
        Regime("transport_10pct", 24, 6, 0.55, 0.35, 0.10, 0.00),
        Regime("format_boundary_10pct", 24, 6, 0.55, 0.35, 0.00, 0.10),
        Regime("format_20pct", 24, 6, 0.55, 0.35, 0.00, 0.20),
        Regime("combined_operational_4_8", 24, 6, 0.55, 0.35, 0.04, 0.08),
        Regime("narrow_domain_24", 24, 3, 0.55, 0.35, 0.00, 0.00),
        Regime("invalid_controls", 24, 6, 0.55, 0.35, 0.00, 0.00, False),
    ]


def latent_oracle_adequate(regime: Regime, t: Thresholds) -> bool:
    """Synthetic engineering reference defined before sampling."""
    expected_per_domain = regime.families / regime.domains
    expected_scorable = (
        (1.0 - regime.transport_failure_probability)
        * (1.0 - regime.empty_format_probability)
    )
    return all(
        [
            regime.controls_pass,
            regime.families >= t.minimum_eligible_families,
            regime.domains >= t.minimum_represented_domains,
            expected_per_domain >= t.minimum_eligible_families_per_represented_domain,
            expected_scorable >= t.minimum_neutral_scorable_coverage,
            t.minimum_neutral_accuracy
            <= regime.latent_accuracy
            <= t.maximum_neutral_accuracy,
            regime.families * expected_scorable * regime.latent_accuracy
            >= t.minimum_correct_eligible_families,
            regime.families * expected_scorable * (1.0 - regime.latent_accuracy)
            >= t.minimum_incorrect_eligible_families,
            regime.transport_failure_probability
            <= t.maximum_transport_failure_fraction,
            regime.empty_format_probability
            <= t.maximum_empty_format_ungradable_fraction,
        ]
    )


def simulate_once(regime: Regime, t: Thresholds, rng: random.Random) -> dict[str, Any]:
    domain_counts = [0] * regime.domains
    transport = empty_format = correct = incorrect = 0
    base_logit = _logit(regime.latent_accuracy)

    for family_index in range(regime.families):
        domain = family_index % regime.domains
        if rng.random() < regime.transport_failure_probability:
            transport += 1
            continue
        if rng.random() < regime.empty_format_probability:
            empty_format += 1
            continue
        domain_counts[domain] += 1
        family_p = _logistic(
            base_logit + rng.gauss(0.0, regime.family_heterogeneity_sd)
        )
        if rng.random() < family_p:
            correct += 1
        else:
            incorrect += 1

    scorable = correct + incorrect
    total = regime.families
    represented_domains = sum(
        count >= t.minimum_eligible_families_per_represented_domain
        for count in domain_counts
    )
    coverage = scorable / total if total else 0.0
    accuracy = correct / scorable if scorable else None
    transport_fraction = transport / total if total else 1.0
    format_fraction = empty_format / total if total else 1.0

    failures: list[str] = []
    if not regime.controls_pass:
        failures.append("invalid_controls")
    if transport_fraction > t.maximum_transport_failure_fraction:
        failures.append("transport_failure")
    if format_fraction > t.maximum_empty_format_ungradable_fraction:
        failures.append("empty_format_ungradable")
    if coverage < t.minimum_neutral_scorable_coverage:
        failures.append("low_scorable_coverage")
    if scorable < t.minimum_eligible_families:
        failures.append("small_n")
    if represented_domains < t.minimum_represented_domains:
        failures.append("narrow_domain")
    if accuracy is None or accuracy < t.minimum_neutral_accuracy:
        failures.append("floor")
    if accuracy is None or accuracy > t.maximum_neutral_accuracy:
        failures.append("ceiling")
    if correct < t.minimum_correct_eligible_families:
        failures.append("too_few_correct")
    if incorrect < t.minimum_incorrect_eligible_families:
        failures.append("too_few_incorrect")

    return {"gate_pass": not failures, "failures": failures}


def _wilson_interval(successes: int, trials: int) -> list[float]:
    z = 1.959963984540054
    if trials <= 0:
        return [0.0, 1.0]
    p = successes / trials
    denom = 1.0 + z * z / trials
    center = (p + z * z / (2.0 * trials)) / denom
    half = z * math.sqrt(
        (p * (1.0 - p) + z * z / (4.0 * trials)) / trials
    ) / denom
    return [max(0.0, center - half), min(1.0, center + half)]


def simulate_regime(
    regime: Regime, t: Thresholds, replicates: int, seed: int
) -> dict[str, Any]:
    digest = hashlib.sha256(f"{seed}:{regime.regime_id}".encode()).digest()
    rng = random.Random(int.from_bytes(digest[:8], "big"))
    oracle = latent_oracle_adequate(regime, t)
    pass_count = 0
    failure_counts: dict[str, int] = {}

    for _ in range(replicates):
        result = simulate_once(regime, t, rng)
        pass_count += int(result["gate_pass"])
        for failure in result["failures"]:
            failure_counts[failure] = failure_counts.get(failure, 0) + 1

    pass_rate = pass_count / replicates
    return {
        "regime": regime.__dict__,
        "oracle_engineering_adequate": oracle,
        "replicates": replicates,
        "gate_pass_count": pass_count,
        "gate_pass_rate": pass_rate,
        "gate_pass_wilson_95": _wilson_interval(pass_count, replicates),
        "false_adequacy_rate": pass_rate if not oracle else 0.0,
        "false_inadequacy_rate": (1.0 - pass_rate) if oracle else 0.0,
        "failure_rates": {
            key: value / replicates for key, value in sorted(failure_counts.items())
        },
    }


def run_simulation(policy_path: Path, replicates: int, seed: int) -> dict[str, Any]:
    if replicates < 100:
        raise ValueError("replicates must be at least 100")
    thresholds = load_thresholds(policy_path)
    return {
        "schema_version": SCHEMA_VERSION,
        "simulation_id": "QEIB-CAPABILITY-ADEQUACY-OC-001",
        "seed": seed,
        "replicates_per_regime": replicates,
        "policy_path": policy_path.as_posix(),
        "policy_sha256": hashlib.sha256(policy_path.read_bytes()).hexdigest(),
        "interpretation_boundary": [
            "The oracle is a synthetic engineering reference, not scientific ground truth.",
            "Rates apply only to the prespecified regimes and sampling model.",
            "No result bears on evaluation awareness, deception, intent, safety, subjectivity, sentience, or consciousness."
        ],
        "regimes": [
            simulate_regime(regime, thresholds, replicates, seed)
            for regime in default_regimes()
        ],
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path("research/qeib/capability_adequacy_policy.v0.1.json"),
    )
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = run_simulation(args.policy, args.replicates, args.seed)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
