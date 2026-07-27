#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

SCALE_MIN = 1.0
SCALE_MAX = 7.0


class PairedSensitivityInputError(ValueError):
    """Raised when participant-paired sensitivity inputs violate the contract."""


@dataclass(frozen=True)
class PairedOutcome:
    participant_id: str
    condition_a_score: float | None
    condition_b_score: float | None


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_score(value: float | None, field: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PairedSensitivityInputError(f"{field} must be numeric or null")
    if not SCALE_MIN <= float(value) <= SCALE_MAX:
        raise PairedSensitivityInputError(f"{field} must lie within the 1-7 scale")


def validate_pairs(pairs: Sequence[PairedOutcome]) -> None:
    if not pairs:
        raise PairedSensitivityInputError("at least one participant pair is required")
    ids: set[str] = set()
    for pair in pairs:
        if not isinstance(pair.participant_id, str) or not pair.participant_id.strip():
            raise PairedSensitivityInputError("participant_id must be non-empty")
        if pair.participant_id in ids:
            raise PairedSensitivityInputError(
                f"duplicate participant_id {pair.participant_id}"
            )
        ids.add(pair.participant_id)
        _validate_score(
            pair.condition_a_score, f"{pair.participant_id}.condition_a_score"
        )
        _validate_score(
            pair.condition_b_score, f"{pair.participant_id}.condition_b_score"
        )


def observed_condition_means(
    pairs: Sequence[PairedOutcome],
) -> tuple[float, float]:
    observed_a = [
        float(pair.condition_a_score)
        for pair in pairs
        if pair.condition_a_score is not None
    ]
    observed_b = [
        float(pair.condition_b_score)
        for pair in pairs
        if pair.condition_b_score is not None
    ]
    if not observed_a or not observed_b:
        raise PairedSensitivityInputError(
            "gamma sensitivity requires at least one observed score in each condition"
        )
    return sum(observed_a) / len(observed_a), sum(observed_b) / len(observed_b)


def participant_difference_bounds(
    pair: PairedOutcome,
    *,
    a_missing_bounds: tuple[float, float] = (SCALE_MIN, SCALE_MAX),
    b_missing_bounds: tuple[float, float] = (SCALE_MIN, SCALE_MAX),
) -> dict[str, Any]:
    _validate_score(pair.condition_a_score, "condition_a_score")
    _validate_score(pair.condition_b_score, "condition_b_score")
    a_lower, a_upper = a_missing_bounds
    b_lower, b_upper = b_missing_bounds
    if not SCALE_MIN <= a_lower <= a_upper <= SCALE_MAX:
        raise PairedSensitivityInputError(
            "condition A missing bounds must lie within 1-7"
        )
    if not SCALE_MIN <= b_lower <= b_upper <= SCALE_MAX:
        raise PairedSensitivityInputError(
            "condition B missing bounds must lie within 1-7"
        )

    a_score = (
        None if pair.condition_a_score is None else float(pair.condition_a_score)
    )
    b_score = (
        None if pair.condition_b_score is None else float(pair.condition_b_score)
    )

    if a_score is not None and b_score is not None:
        lower = upper = b_score - a_score
        pattern = "complete_pair"
    elif a_score is not None:
        lower, upper = b_lower - a_score, b_upper - a_score
        pattern = "condition_b_suppressed"
    elif b_score is not None:
        lower, upper = b_score - a_upper, b_score - a_lower
        pattern = "condition_a_suppressed"
    else:
        lower, upper = b_lower - a_upper, b_upper - a_lower
        pattern = "both_suppressed"

    return {
        "participant_id": pair.participant_id,
        "pattern": pattern,
        "difference_lower": lower,
        "difference_upper": upper,
    }


def _sign_status(lower: float, upper: float) -> str:
    if lower > 0:
        return "positive_sign_robust"
    if upper < 0:
        return "negative_sign_robust"
    if lower == 0 and upper == 0:
        return "point_identified_zero"
    return "sign_not_robust"


def mean_difference_bounds(
    pairs: Sequence[PairedOutcome],
    *,
    a_missing_bounds: tuple[float, float] = (SCALE_MIN, SCALE_MAX),
    b_missing_bounds: tuple[float, float] = (SCALE_MIN, SCALE_MAX),
) -> dict[str, Any]:
    validate_pairs(pairs)
    rows = [
        participant_difference_bounds(
            pair,
            a_missing_bounds=a_missing_bounds,
            b_missing_bounds=b_missing_bounds,
        )
        for pair in pairs
    ]
    lower = sum(row["difference_lower"] for row in rows) / len(rows)
    upper = sum(row["difference_upper"] for row in rows) / len(rows)
    complete_differences = [
        row["difference_lower"]
        for row in rows
        if row["pattern"] == "complete_pair"
    ]
    patterns = (
        "complete_pair",
        "condition_a_suppressed",
        "condition_b_suppressed",
        "both_suppressed",
    )
    return {
        "participant_count": len(rows),
        "pattern_counts": {
            pattern: sum(row["pattern"] == pattern for row in rows)
            for pattern in patterns
        },
        "complete_pair_mean_difference": (
            sum(complete_differences) / len(complete_differences)
            if complete_differences
            else None
        ),
        "mean_difference_lower": lower,
        "mean_difference_upper": upper,
        "contains_zero": lower <= 0 <= upper,
        "sign_status": _sign_status(lower, upper),
        "participant_bounds": rows,
    }


def gamma_sensitivity(
    pairs: Sequence[PairedOutcome], gammas: Iterable[float]
) -> list[dict[str, Any]]:
    validate_pairs(pairs)
    mean_a, mean_b = observed_condition_means(pairs)
    output: list[dict[str, Any]] = []
    previous = -1.0
    for raw in gammas:
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise PairedSensitivityInputError("gamma values must be numeric")
        gamma = float(raw)
        if gamma < 0 or gamma < previous:
            raise PairedSensitivityInputError(
                "gamma values must be nonnegative and nondecreasing"
            )
        previous = gamma
        a_bounds = (
            max(SCALE_MIN, mean_a - gamma),
            min(SCALE_MAX, mean_a + gamma),
        )
        b_bounds = (
            max(SCALE_MIN, mean_b - gamma),
            min(SCALE_MAX, mean_b + gamma),
        )
        result = mean_difference_bounds(
            pairs, a_missing_bounds=a_bounds, b_missing_bounds=b_bounds
        )
        output.append(
            {
                "gamma": gamma,
                "condition_a_missing_score_bounds": list(a_bounds),
                "condition_b_missing_score_bounds": list(b_bounds),
                "mean_difference_lower": result["mean_difference_lower"],
                "mean_difference_upper": result["mean_difference_upper"],
                "contains_zero": result["contains_zero"],
                "sign_status": result["sign_status"],
            }
        )
    return output


def leave_one_participant_out(
    pairs: Sequence[PairedOutcome],
    *,
    a_missing_bounds: tuple[float, float] = (SCALE_MIN, SCALE_MAX),
    b_missing_bounds: tuple[float, float] = (SCALE_MIN, SCALE_MAX),
) -> dict[str, Any]:
    validate_pairs(pairs)
    if len(pairs) < 2:
        raise PairedSensitivityInputError(
            "leave-one-participant-out diagnostics require at least two participants"
        )
    full = mean_difference_bounds(
        pairs,
        a_missing_bounds=a_missing_bounds,
        b_missing_bounds=b_missing_bounds,
    )
    rows = []
    for omitted in pairs:
        retained = [
            pair for pair in pairs if pair.participant_id != omitted.participant_id
        ]
        result = mean_difference_bounds(
            retained,
            a_missing_bounds=a_missing_bounds,
            b_missing_bounds=b_missing_bounds,
        )
        rows.append(
            {
                "omitted_participant_id": omitted.participant_id,
                "mean_difference_lower": result["mean_difference_lower"],
                "mean_difference_upper": result["mean_difference_upper"],
                "sign_status": result["sign_status"],
                "changes_full_sample_sign_status": (
                    result["sign_status"] != full["sign_status"]
                ),
            }
        )
    return {
        "full_sample_sign_status": full["sign_status"],
        "minimum_lower_bound": min(
            row["mean_difference_lower"] for row in rows
        ),
        "maximum_lower_bound": max(
            row["mean_difference_lower"] for row in rows
        ),
        "minimum_upper_bound": min(
            row["mean_difference_upper"] for row in rows
        ),
        "maximum_upper_bound": max(
            row["mean_difference_upper"] for row in rows
        ),
        "sign_status_change_count": sum(
            row["changes_full_sample_sign_status"] for row in rows
        ),
        "diagnostics": rows,
    }


def analyze(
    pairs: Sequence[PairedOutcome],
    *,
    gammas: Iterable[float] = (0.0, 0.5, 1.0, 2.0, 3.0, 6.0),
) -> dict[str, Any]:
    validate_pairs(pairs)
    report = {
        "schema_version": "egc2-participant-paired-suppression-sensitivity-0.1.0",
        "estimand": (
            "mean within-participant semantic-fidelity difference: "
            "condition B minus condition A"
        ),
        "scale_bounds": [SCALE_MIN, SCALE_MAX],
        "worst_case_bounds": mean_difference_bounds(pairs),
        "gamma_sensitivity": gamma_sensitivity(pairs, gammas),
        "leave_one_participant_out": leave_one_participant_out(pairs),
        "claim_limit": (
            "These bounds preserve participant pairing under suppressed outcomes. "
            "They do not identify missing scores, establish ignorability, correct "
            "selection bias, validate semantic fidelity, or validate EGC."
        ),
    }
    report["analysis_digest_sha256"] = _canonical_digest(report)
    return report
