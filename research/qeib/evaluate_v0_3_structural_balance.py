#!/usr/bin/env python3
"""Deterministic structural-allocation oracle for QEIB adequacy v0.3.

This module evaluates only benchmark allocation structure. It deliberately does
not inspect model outputs, context contrasts, answer keys, private holdouts, or
any behavioral result. Structural invalidity is therefore fixed before outcome
simulation and cannot be rescued by favorable stochastic observations.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Sequence

SCHEMA_VERSION = "qeib-v0.3-structural-balance-oracle-0.1.0"


@dataclass(frozen=True)
class StructuralBalanceResult:
    schema_version: str
    candidate_id: str
    family_count: int
    domain_count: int
    domain_counts: tuple[int, ...]
    domain_shares: tuple[float, ...]
    effective_domain_count: float
    minimum_observed_share: float
    maximum_observed_share: float
    passes_minimum_share: bool
    passes_maximum_share: bool
    passes_effective_domain_count: bool
    structurally_valid: bool
    failure_reasons: tuple[str, ...]


def effective_domain_count(domain_counts: Sequence[int]) -> float:
    """Return inverse-Herfindahl effective domain count.

    The result equals the number of domains under equal allocation and tends
    toward one as allocation becomes maximally concentrated.
    """
    total = sum(domain_counts)
    if total <= 0:
        raise ValueError("family allocation must contain at least one family")
    shares = [count / total for count in domain_counts]
    return 1.0 / sum(share * share for share in shares)


def validate_domain_counts(domain_counts: Sequence[int], expected_domains: int) -> tuple[int, ...]:
    counts = tuple(domain_counts)
    if len(counts) != expected_domains:
        raise ValueError(
            f"expected exactly {expected_domains} domain counts, received {len(counts)}"
        )
    if any(isinstance(value, bool) or not isinstance(value, int) for value in counts):
        raise TypeError("domain counts must be integers")
    if any(value < 0 for value in counts):
        raise ValueError("domain counts must be non-negative")
    if sum(counts) <= 0:
        raise ValueError("family allocation must contain at least one family")
    return counts


def evaluate_structural_balance(
    domain_counts: Sequence[int],
    candidate: dict,
    expected_domains: int,
) -> StructuralBalanceResult:
    """Evaluate one frozen v0.3 structural-balance candidate."""
    counts = validate_domain_counts(domain_counts, expected_domains)
    total = sum(counts)
    shares = tuple(count / total for count in counts)
    effective = effective_domain_count(counts)

    minimum_share = float(candidate["min_domain_share"])
    maximum_share = float(candidate["max_domain_share"])
    minimum_effective = float(candidate["min_effective_domain_count"])

    passes_min = min(shares) >= minimum_share
    passes_max = max(shares) <= maximum_share
    passes_effective = effective >= minimum_effective

    reasons: list[str] = []
    if not passes_min:
        reasons.append("minimum_domain_share")
    if not passes_max:
        reasons.append("maximum_domain_share")
    if not passes_effective:
        reasons.append("effective_domain_count")

    return StructuralBalanceResult(
        schema_version=SCHEMA_VERSION,
        candidate_id=str(candidate["id"]),
        family_count=total,
        domain_count=expected_domains,
        domain_counts=counts,
        domain_shares=shares,
        effective_domain_count=effective,
        minimum_observed_share=min(shares),
        maximum_observed_share=max(shares),
        passes_minimum_share=passes_min,
        passes_maximum_share=passes_max,
        passes_effective_domain_count=passes_effective,
        structurally_valid=not reasons,
        failure_reasons=tuple(reasons),
    )


SUPPORTED_GRID_SCHEMAS = frozenset(
    {
        "qeib-capability-adequacy-v0.3-candidate-grid-0.1",
        # 0.2 adds the frozen beta-binomial numerical method block; structural
        # balance fields are unchanged and remain deterministic.
        "qeib-capability-adequacy-v0.3-candidate-grid-0.2",
    }
)


def load_grid(path: Path) -> dict:
    grid = json.loads(path.read_text(encoding="utf-8"))
    if grid.get("schema_version") not in SUPPORTED_GRID_SCHEMAS:
        raise ValueError("unexpected v0.3 candidate-grid schema")
    if not grid.get("oracle_labels", {}).get("structural_invalidity_is_deterministic"):
        raise ValueError("grid does not freeze deterministic structural invalidity")
    return grid


def evaluate_all_candidates(domain_counts: Sequence[int], grid: dict) -> list[StructuralBalanceResult]:
    expected_domains = int(grid["simulation"]["domain_count"])
    return [
        evaluate_structural_balance(domain_counts, candidate, expected_domains)
        for candidate in grid["structural_balance_candidates"]
    ]


def result_to_json(result: StructuralBalanceResult) -> dict:
    payload = asdict(result)
    payload["domain_counts"] = list(result.domain_counts)
    payload["domain_shares"] = list(result.domain_shares)
    payload["failure_reasons"] = list(result.failure_reasons)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--grid",
        type=Path,
        default=Path("research/qeib/capability_adequacy_v0.3_candidate_grid.json"),
    )
    parser.add_argument(
        "--domain-counts",
        required=True,
        help="Comma-separated eligible-family counts, one integer per domain.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)

    counts = [int(part.strip()) for part in args.domain_counts.split(",")]
    grid = load_grid(args.grid)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "interpretation_boundary": [
            "This oracle evaluates allocation structure only.",
            "It does not inspect or support claims about model behavior, awareness, deception, subjectivity, sentience, or consciousness.",
        ],
        "results": [result_to_json(result) for result in evaluate_all_candidates(counts, grid)],
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
