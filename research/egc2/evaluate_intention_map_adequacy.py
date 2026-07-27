#!/usr/bin/env python3
"""Fail-closed adjudication of intention-map adequacy for EGC 2.0.

This module decides whether a semantic-fidelity score has a usable reference target.
It does not score fidelity, infer hidden intention, or validate EGC. Rules are
provisional pilot rules and must be calibrated before confirmatory use.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any

SCHEMA_VERSION = "egc2-intention-map-adequacy-decision-0.1.0"
ADEQUACY_VALUES = {
    "adequate",
    "too_sparse",
    "internal_conflict",
    "uninterpretable",
    "response_dependent",
    "other_problem",
}
NONADEQUATE = ADEQUACY_VALUES - {"adequate"}
VALID_DISPOSITIONS = {
    "retain_numeric_score",
    "suppress_numeric_score_reference_inadequate",
    "blind_adjudication_required",
    "indeterminate_insufficient_review",
}

class AdequacyDecisionError(ValueError):
    pass


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def evaluate_adequacy(
    reviews: list[dict[str, Any]],
    *,
    minimum_reviewers: int = 3,
    suppression_threshold: int | None = None,
    require_reason_for_nonadequate: bool = True,
) -> dict[str, Any]:
    """Return a deterministic reference-target disposition.

    Rules:
    - fewer than minimum complete unique reviews -> indeterminate;
    - >= suppression_threshold non-adequate judgments -> suppress numeric score;
    - unanimous adequate -> retain numeric score;
    - every other complete pattern -> blind adjudication required.

    Suppression is about the reference target, not the quality of the response.
    """
    if minimum_reviewers < 3:
        raise AdequacyDecisionError("minimum_reviewers must be at least 3")
    if suppression_threshold is not None and suppression_threshold < 2:
        raise AdequacyDecisionError("suppression_threshold must be at least 2")
    if not isinstance(reviews, list):
        raise AdequacyDecisionError("reviews must be a list")

    errors: list[str] = []
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, review in enumerate(reviews):
        if not isinstance(review, dict):
            errors.append(f"review[{index}] must be an object")
            continue
        reviewer_id = review.get("reviewer_id")
        adequacy = review.get("intention_map_adequacy")
        reason_codes = review.get("reason_codes")
        confidence = review.get("confidence_1_to_5")
        if not isinstance(reviewer_id, str) or not reviewer_id:
            errors.append(f"review[{index}] requires reviewer_id")
        elif reviewer_id in seen:
            errors.append(f"duplicate reviewer_id {reviewer_id}")
        else:
            seen.add(reviewer_id)
        if adequacy not in ADEQUACY_VALUES:
            errors.append(f"review[{index}] has invalid intention_map_adequacy")
        if not isinstance(reason_codes, list):
            errors.append(f"review[{index}] reason_codes must be a list")
            reason_codes = []
        if require_reason_for_nonadequate and adequacy in NONADEQUATE and not reason_codes:
            errors.append(f"review[{index}] non-adequate judgment requires reason evidence")
        if not isinstance(confidence, int) or not 1 <= confidence <= 5:
            errors.append(f"review[{index}] confidence_1_to_5 must be integer 1-5")
        normalized.append({
            "reviewer_id": reviewer_id,
            "intention_map_adequacy": adequacy,
            "reason_codes": reason_codes,
            "confidence_1_to_5": confidence,
        })

    if errors:
        raise AdequacyDecisionError(json.dumps({"valid": False, "errors": errors}, indent=2))

    effective_threshold = suppression_threshold if suppression_threshold is not None else (len(normalized) // 2 + 1)
    if effective_threshold > len(normalized) and len(normalized) >= minimum_reviewers:
        raise AdequacyDecisionError("suppression_threshold cannot exceed complete review count")

    counts = Counter(r["intention_map_adequacy"] for r in normalized)
    nonadequate_count = sum(counts[value] for value in NONADEQUATE)
    adequate_count = counts["adequate"]

    if len(normalized) < minimum_reviewers:
        disposition = "indeterminate_insufficient_review"
        numeric_score_permitted = False
        confirmatory_item_permitted = False
    elif nonadequate_count >= effective_threshold:
        disposition = "suppress_numeric_score_reference_inadequate"
        numeric_score_permitted = False
        confirmatory_item_permitted = False
    elif adequate_count == len(normalized):
        disposition = "retain_numeric_score"
        numeric_score_permitted = True
        confirmatory_item_permitted = True
    else:
        disposition = "blind_adjudication_required"
        numeric_score_permitted = False
        confirmatory_item_permitted = False

    result = {
        "schema_version": SCHEMA_VERSION,
        "review_count": len(normalized),
        "minimum_reviewers": minimum_reviewers,
        "suppression_threshold": effective_threshold,
        "adequacy_counts": dict(sorted(counts.items())),
        "nonadequate_count": nonadequate_count,
        "disposition": disposition,
        "numeric_score_permitted": numeric_score_permitted,
        "confirmatory_item_permitted": confirmatory_item_permitted,
        "preserve_raw_fidelity_scores": True,
        "selection_warning": (
            "Suppressed or adjudicated items must remain in recruitment and item-flow reporting; "
            "they may not be silently deleted or replaced based on condition effects."
        ),
        "claim_limit": (
            "This adjudicates reference-target usability only. It does not recover true intention, "
            "score semantic fidelity, or validate EGC."
        ),
    }
    if disposition not in VALID_DISPOSITIONS:
        raise AssertionError("unexpected disposition")
    result["decision_digest_sha256"] = _digest(result)
    return result
