#!/usr/bin/env python3
"""Prepare and validate target-blind expert review for EGC 2.0 anchors.

Engineering scope only. This tool does not validate anchors or create expert
consensus. It enforces reviewer-specific ordering, contrast-pair separation,
submission locking, source-digest binding, and reveal authorization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_anchor_development_manifest import (
    EXPECTED_REASON_CODES,
    build_blind_review_export,
    validate_manifest,
)

QUEUE_SCHEMA = "egc2-anchor-reviewer-queue-0.1.0"
SUBMISSION_SCHEMA = "egc2-anchor-review-submission-0.1.0"
AGGREGATE_SCHEMA = "egc2-anchor-review-discrepancy-report-0.1.0"
DEFAULT_REVIEWERS = ("R01", "R02", "R03")
MIN_PAIR_GAP = 6
ADEQUACY_VALUES = {
    "adequate",
    "too_sparse",
    "internal_conflict",
    "uninterpretable",
    "response_dependent",
    "other_problem",
}
DISPOSITIONS = {"retained_numeric", "suppressed_reference_inadequate"}


class ReviewValidationError(ValueError):
    pass


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _seed(source_digest: str, reviewer_id: str) -> int:
    raw = hashlib.sha256(f"{source_digest}|{reviewer_id}|egc2-review-v0.1".encode()).digest()
    return int.from_bytes(raw[:8], "big")


def _pair_map(manifest: dict[str, Any]) -> dict[str, str]:
    return {packet["anchor_id"]: packet["contrast_group_id"] for packet in manifest["packets"]}


def _valid_pair_gap(order: list[str], pair_map: dict[str, str], minimum_gap: int) -> bool:
    positions: dict[str, list[int]] = defaultdict(list)
    for index, anchor_id in enumerate(order):
        positions[pair_map[anchor_id]].append(index)
    return all(len(values) == 2 and abs(values[0] - values[1]) >= minimum_gap for values in positions.values())


def _make_order(ids: list[str], pair_map: dict[str, str], rng: random.Random) -> list[str]:
    # Deterministic rejection sampling is acceptable at this small fixed size.
    for _ in range(100_000):
        candidate = ids[:]
        rng.shuffle(candidate)
        if _valid_pair_gap(candidate, pair_map, MIN_PAIR_GAP):
            return candidate
    raise ReviewValidationError("unable to construct reviewer order satisfying pair separation")


def build_reviewer_queues(
    manifest: dict[str, Any], reviewer_ids: tuple[str, ...] = DEFAULT_REVIEWERS
) -> dict[str, Any]:
    validate_manifest(manifest)
    if len(set(reviewer_ids)) != len(reviewer_ids) or len(reviewer_ids) < 3:
        raise ReviewValidationError("at least three unique reviewer IDs are required")

    blind = build_blind_review_export(manifest)
    by_id = {item["review_item_id"]: item for item in blind["items"]}
    pair_map = _pair_map(manifest)
    ids = sorted(by_id)
    queues = []

    for reviewer_id in reviewer_ids:
        order = _make_order(ids, pair_map, random.Random(_seed(manifest["content_digest_sha256"], reviewer_id)))
        items = []
        for position, anchor_id in enumerate(order, start=1):
            item = deepcopy(by_id[anchor_id])
            item["position"] = position
            item["review_form"]["reviewer_id"] = reviewer_id
            items.append(item)
        queue = {
            "schema_version": QUEUE_SCHEMA,
            "reviewer_id": reviewer_id,
            "source_manifest_id": manifest["manifest_id"],
            "source_content_digest_sha256": manifest["content_digest_sha256"],
            "pair_separation_minimum_positions": MIN_PAIR_GAP,
            "target_blind": True,
            "items": items,
        }
        queue["queue_digest_sha256"] = _canonical_digest({k: v for k, v in queue.items() if k != "queue_digest_sha256"})
        queues.append(queue)

    return {
        "schema_version": "egc2-anchor-reviewer-queue-set-0.1.0",
        "source_manifest_id": manifest["manifest_id"],
        "source_content_digest_sha256": manifest["content_digest_sha256"],
        "reviewer_ids": list(reviewer_ids),
        "queues": queues,
    }


def validate_queue_set(manifest: dict[str, Any], queue_set: dict[str, Any]) -> dict[str, Any]:
    validate_manifest(manifest)
    errors: list[str] = []
    pair_map = _pair_map(manifest)
    expected_ids = {packet["anchor_id"] for packet in manifest["packets"]}
    queues = queue_set.get("queues")
    if not isinstance(queues, list) or len(queues) < 3:
        errors.append("queue set must contain at least three queues")
        queues = []

    seen_reviewers: set[str] = set()
    for queue in queues:
        reviewer_id = queue.get("reviewer_id")
        if not isinstance(reviewer_id, str) or not reviewer_id:
            errors.append("every queue requires reviewer_id")
            continue
        if reviewer_id in seen_reviewers:
            errors.append(f"duplicate reviewer_id {reviewer_id}")
        seen_reviewers.add(reviewer_id)
        if queue.get("schema_version") != QUEUE_SCHEMA:
            errors.append(f"{reviewer_id}: invalid queue schema")
        if queue.get("target_blind") is not True:
            errors.append(f"{reviewer_id}: target_blind must be true")
        if queue.get("source_content_digest_sha256") != manifest["content_digest_sha256"]:
            errors.append(f"{reviewer_id}: source digest mismatch")
        items = queue.get("items") or []
        ids = [item.get("review_item_id") for item in items]
        if set(ids) != expected_ids or len(ids) != len(expected_ids):
            errors.append(f"{reviewer_id}: queue must contain every anchor exactly once")
        if ids and not _valid_pair_gap(ids, pair_map, MIN_PAIR_GAP):
            errors.append(f"{reviewer_id}: contrast-pair separation violated")
        positions = [item.get("position") for item in items]
        if positions != list(range(1, len(items) + 1)):
            errors.append(f"{reviewer_id}: positions must be contiguous")
        for item in items:
            form = item.get("review_form") or {}
            if form.get("reviewer_id") != reviewer_id:
                errors.append(f"{reviewer_id}: embedded reviewer_id mismatch")
            forbidden = {
                "provisional_score_region", "contrast_family", "contrast_group_id",
                "expert_rationale", "admissible_score_range", "known_ambiguities",
                "validation_status", "audit", "pilot_metrics", "blind_review",
            }
            if forbidden & set(item):
                errors.append(f"{reviewer_id}: target leakage in item {item.get('review_item_id')}")
        expected_digest = queue.get("queue_digest_sha256")
        actual_digest = _canonical_digest({k: v for k, v in queue.items() if k != "queue_digest_sha256"})
        if expected_digest != actual_digest:
            errors.append(f"{reviewer_id}: queue digest mismatch")

    if errors:
        raise ReviewValidationError(json.dumps({"valid": False, "errors": errors}, indent=2))
    return {
        "valid": True,
        "reviewer_count": len(queues),
        "items_per_reviewer": len(expected_ids),
        "minimum_pair_gap": MIN_PAIR_GAP,
        "source_content_digest_sha256": manifest["content_digest_sha256"],
    }


def validate_submission(queue: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if submission.get("schema_version") != SUBMISSION_SCHEMA:
        errors.append("invalid submission schema")
    if submission.get("reviewer_id") != queue.get("reviewer_id"):
        errors.append("reviewer_id does not match queue")
    if submission.get("queue_digest_sha256") != queue.get("queue_digest_sha256"):
        errors.append("queue digest mismatch")
    if submission.get("source_content_digest_sha256") != queue.get("source_content_digest_sha256"):
        errors.append("source content digest mismatch")
    if submission.get("locked_before_target_reveal") is not True:
        errors.append("submission must be locked before target reveal")
    if submission.get("targets_seen_before_lock") is not False:
        errors.append("targets_seen_before_lock must be false")
    locked_at = submission.get("locked_at_utc")
    try:
        parsed = datetime.fromisoformat(str(locked_at).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError
    except ValueError:
        errors.append("locked_at_utc must be timezone-aware ISO-8601")

    expected = [item["review_item_id"] for item in queue["items"]]
    reviews = submission.get("reviews")
    if not isinstance(reviews, list):
        errors.append("reviews must be a list")
        reviews = []
    observed = [review.get("review_item_id") for review in reviews]
    if observed != expected:
        errors.append("review order and IDs must exactly match the assigned queue")

    for review in reviews:
        item_id = review.get("review_item_id")
        adequacy = review.get("intention_map_adequacy")
        disposition = review.get("score_disposition")
        score = review.get("semantic_fidelity_score")
        confidence = review.get("confidence_1_to_5")
        reasons = review.get("reason_codes")
        if adequacy not in ADEQUACY_VALUES:
            errors.append(f"{item_id}: invalid intention_map_adequacy")
        if disposition not in DISPOSITIONS:
            errors.append(f"{item_id}: invalid score_disposition")
        if disposition == "retained_numeric":
            if not isinstance(score, int) or not 1 <= score <= 7:
                errors.append(f"{item_id}: retained score must be integer 1-7")
        elif disposition == "suppressed_reference_inadequate":
            if score is not None:
                errors.append(f"{item_id}: suppressed score must be null")
            if adequacy == "adequate":
                errors.append(f"{item_id}: adequate map cannot suppress score")
        if not isinstance(confidence, int) or not 1 <= confidence <= 5:
            errors.append(f"{item_id}: confidence must be integer 1-5")
        if not isinstance(reasons, list):
            errors.append(f"{item_id}: reason_codes must be a list")
        else:
            unknown = set(reasons) - EXPECTED_REASON_CODES
            if unknown:
                errors.append(f"{item_id}: unknown reason codes {sorted(unknown)}")
        if score in {1, 2, 6, 7} and not reasons:
            errors.append(f"{item_id}: extreme scores require at least one reason code")
        if review.get("pair_recognition_suspected") not in {True, False}:
            errors.append(f"{item_id}: pair_recognition_suspected must be boolean")

    if errors:
        raise ReviewValidationError(json.dumps({"valid": False, "errors": errors}, indent=2))
    return {
        "valid": True,
        "reviewer_id": submission["reviewer_id"],
        "review_count": len(reviews),
        "suppressed_count": sum(r["score_disposition"] == "suppressed_reference_inadequate" for r in reviews),
        "submission_digest_sha256": _canonical_digest(submission),
    }


def aggregate_discrepancies(
    manifest: dict[str, Any], queue_set: dict[str, Any], submissions: list[dict[str, Any]], *, reveal_authorized: bool
) -> dict[str, Any]:
    validate_queue_set(manifest, queue_set)
    if not reveal_authorized:
        raise ReviewValidationError("constructor targets may not be joined before explicit reveal authorization")
    queues = {q["reviewer_id"]: q for q in queue_set["queues"]}
    if set(queues) != {s.get("reviewer_id") for s in submissions}:
        raise ReviewValidationError("exactly one submission is required for every assigned reviewer")
    for submission in submissions:
        validate_submission(queues[submission["reviewer_id"]], submission)

    packet_by_id = {p["anchor_id"]: p for p in manifest["packets"]}
    reviews_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for submission in submissions:
        for review in submission["reviews"]:
            reviews_by_item[review["review_item_id"]].append(review)

    items = []
    disposition_counts = Counter()
    for anchor_id in sorted(packet_by_id):
        packet = packet_by_id[anchor_id]
        reviews = reviews_by_item[anchor_id]
        scores = sorted(r["semantic_fidelity_score"] for r in reviews if r["score_disposition"] == "retained_numeric")
        suppressions = sum(r["score_disposition"] == "suppressed_reference_inadequate" for r in reviews)
        if suppressions >= 2:
            disposition = "reference_target_inadequate_review_required"
        elif len(scores) < 3:
            disposition = "insufficient_numeric_reviews"
        else:
            median = scores[len(scores) // 2]
            spread = max(scores) - min(scores)
            target_delta = median - packet["provisional_score_region"]
            if abs(target_delta) > 1 or spread > 3:
                disposition = "revision_or_rejection_required"
            else:
                disposition = "candidate_retention_review"
        disposition_counts[disposition] += 1
        items.append({
            "anchor_id": anchor_id,
            "constructor_target_region": packet["provisional_score_region"],
            "blind_numeric_scores": scores,
            "numeric_review_count": len(scores),
            "suppressed_reference_count": suppressions,
            "score_range": (max(scores) - min(scores)) if scores else None,
            "pair_recognition_flags": sum(bool(r["pair_recognition_suspected"]) for r in reviews),
            "disposition": disposition,
        })

    report = {
        "schema_version": AGGREGATE_SCHEMA,
        "source_manifest_id": manifest["manifest_id"],
        "source_content_digest_sha256": manifest["content_digest_sha256"],
        "reviewer_count": len(submissions),
        "reveal_authorized": True,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "items": items,
        "claim_limit": "Discrepancy triage only; expert agreement does not validate anchors or the semantic-fidelity construct.",
    }
    report["report_digest_sha256"] = _canonical_digest({k: v for k, v in report.items() if k != "report_digest_sha256"})
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--queue-set-out", type=Path)
    parser.add_argument("--validate-queue-set", type=Path)
    parser.add_argument("--reviewers", nargs="+", default=list(DEFAULT_REVIEWERS))
    args = parser.parse_args(argv)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    try:
        queue_set = build_reviewer_queues(manifest, tuple(args.reviewers))
        summary = validate_queue_set(manifest, queue_set)
        if args.validate_queue_set:
            existing = json.loads(args.validate_queue_set.read_text(encoding="utf-8"))
            summary = validate_queue_set(manifest, existing)
        if args.queue_set_out:
            args.queue_set_out.parent.mkdir(parents=True, exist_ok=True)
            args.queue_set_out.write_text(json.dumps(queue_set, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except ReviewValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
