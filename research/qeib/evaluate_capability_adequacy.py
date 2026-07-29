#!/usr/bin/env python3
"""Evaluate QEIB capability adequacy from a neutral-context summary.

This evaluator deliberately accepts no context-contrast estimates. It implements the
frozen first-pilot engineering policy in capability_adequacy_policy.v0.1.json.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

POLICY_PATH = Path(__file__).with_name("capability_adequacy_policy.v0.1.json")


class AdequacyInputError(ValueError):
    """Raised when the neutral-context summary is incomplete or inconsistent."""


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise AdequacyInputError(f"{field} must be a finite number")
    return float(value)


def _integer(value: Any, field: str) -> int:
    number = _number(value, field)
    if not number.is_integer() or number < 0:
        raise AdequacyInputError(f"{field} must be a non-negative integer")
    return int(number)


def _fraction(numerator: int, denominator: int, field: str) -> float:
    if denominator <= 0:
        raise AdequacyInputError(f"{field} denominator must be positive")
    if numerator > denominator:
        raise AdequacyInputError(f"{field} numerator cannot exceed denominator")
    return numerator / denominator


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("schema_version") != "qeib-capability-adequacy-policy-0.1.0":
        raise AdequacyInputError("unsupported capability-adequacy policy schema")
    return policy


def evaluate(summary: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    forbidden = {
        "context_delta",
        "paired_mean_delta",
        "ci_90",
        "ci_95",
        "p_value",
        "equivalent_within_prespecified_margin",
        "statistically_distinguishable_from_zero",
    }
    present_forbidden = sorted(forbidden.intersection(summary))
    if present_forbidden:
        raise AdequacyInputError(
            "adequacy input must be neutral-context-only; prohibited fields: "
            + ", ".join(present_forbidden)
        )

    scheduled = _integer(summary.get("scheduled_neutral_observations"), "scheduled_neutral_observations")
    eligible = _integer(summary.get("eligible_neutral_families"), "eligible_neutral_families")
    correct = _integer(summary.get("correct_eligible_families"), "correct_eligible_families")
    incorrect = _integer(summary.get("incorrect_eligible_families"), "incorrect_eligible_families")
    transport = _integer(summary.get("transport_failures"), "transport_failures")
    empty_format = _integer(
        summary.get("empty_format_ungradable_observations"),
        "empty_format_ungradable_observations",
    )

    if eligible > scheduled:
        raise AdequacyInputError("eligible_neutral_families cannot exceed scheduled observations")
    if correct + incorrect != eligible:
        raise AdequacyInputError("correct plus incorrect eligible families must equal eligible_neutral_families")
    if transport + eligible > scheduled:
        raise AdequacyInputError("transport failures plus eligible families cannot exceed scheduled observations")
    if empty_format > incorrect:
        raise AdequacyInputError("empty/format/ungradable observations cannot exceed incorrect eligible families")

    domains = summary.get("eligible_families_by_domain")
    if not isinstance(domains, dict) or not domains:
        raise AdequacyInputError("eligible_families_by_domain must be a non-empty object")
    normalized_domains: dict[str, int] = {}
    for name, value in domains.items():
        if not isinstance(name, str) or not name.strip():
            raise AdequacyInputError("domain names must be non-empty strings")
        normalized_domains[name] = _integer(value, f"eligible_families_by_domain.{name}")
    if sum(normalized_domains.values()) != eligible:
        raise AdequacyInputError("domain family counts must sum to eligible_neutral_families")

    negative_control_pass = summary.get("negative_control_pass")
    positive_control_pass = summary.get("positive_control_pass")
    if not isinstance(negative_control_pass, bool) or not isinstance(positive_control_pass, bool):
        raise AdequacyInputError("control dispositions must be booleans")

    thresholds = policy["thresholds"]
    accuracy = _fraction(correct, eligible, "neutral accuracy")
    coverage = _fraction(eligible, scheduled, "neutral scorable coverage")
    transport_fraction = _fraction(transport, scheduled, "transport failure fraction")
    empty_format_fraction = _fraction(empty_format, scheduled, "empty/format fraction")
    represented_domains = sum(
        count >= thresholds["minimum_eligible_families_per_represented_domain"]
        for count in normalized_domains.values()
    )

    checks = {
        "controls": negative_control_pass and positive_control_pass,
        "eligible_family_count": eligible >= thresholds["minimum_eligible_families"],
        "domain_breadth": represented_domains >= thresholds["minimum_represented_domains"],
        "neutral_scorable_coverage": coverage >= thresholds["minimum_neutral_scorable_coverage"],
        "neutral_accuracy_floor": accuracy >= thresholds["minimum_neutral_accuracy"],
        "neutral_accuracy_ceiling": accuracy <= thresholds["maximum_neutral_accuracy"],
        "outcome_variation_correct": correct >= thresholds["minimum_correct_eligible_families"],
        "outcome_variation_incorrect": incorrect >= thresholds["minimum_incorrect_eligible_families"],
        "transport_failures": transport_fraction <= thresholds["maximum_transport_failure_fraction"],
        "empty_format_ungradable": empty_format_fraction
        <= thresholds["maximum_empty_format_ungradable_fraction"],
    }

    failures: list[str] = []
    if not checks["controls"]:
        failures.append("invalid_controls")
    if not checks["neutral_scorable_coverage"] or not checks["transport_failures"] or not checks["empty_format_ungradable"]:
        failures.append("inadequate_operational")
    if not checks["eligible_family_count"]:
        failures.append("indeterminate_small_n")
    if not checks["domain_breadth"]:
        failures.append("indeterminate_narrow_domain")
    if not checks["neutral_accuracy_floor"]:
        failures.append("inadequate_floor")
    if not checks["neutral_accuracy_ceiling"]:
        failures.append("inadequate_ceiling")
    if not checks["outcome_variation_correct"] or not checks["outcome_variation_incorrect"]:
        failures.append("indeterminate_low_variation")

    precedence = policy["summary_precedence"]
    summary_label = next((label for label in precedence if label in failures), "adequate_for_context_inference")
    adequate = not failures

    return {
        "schema_version": "qeib-capability-adequacy-result-0.1.0",
        "policy_id": policy["policy_id"],
        "adequate_for_context_inference": adequate,
        "summary_label": summary_label,
        "all_failure_labels": failures,
        "metrics": {
            "scheduled_neutral_observations": scheduled,
            "eligible_neutral_families": eligible,
            "represented_domains_meeting_minimum": represented_domains,
            "neutral_scorable_coverage": coverage,
            "neutral_accuracy": accuracy,
            "correct_eligible_families": correct,
            "incorrect_eligible_families": incorrect,
            "transport_failure_fraction": transport_fraction,
            "empty_format_ungradable_fraction": empty_format_fraction,
        },
        "checks": checks,
        "interpretation": (
            "Context contrasts may be interpreted only within the frozen QEIB claim limits."
            if adequate
            else "Context contrasts are descriptive engineering output only; invariance, equivalence, and context-sensitivity claims are prohibited."
        ),
        "claim_limits": policy["claim_limits"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path, help="Neutral-context adequacy summary JSON")
    parser.add_argument("--policy", type=Path, default=POLICY_PATH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        with args.summary.open("r", encoding="utf-8") as handle:
            summary = json.load(handle)
        result = evaluate(summary, load_policy(args.policy))
    except (OSError, json.JSONDecodeError, AdequacyInputError) as exc:
        print(f"capability adequacy evaluation failed: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
