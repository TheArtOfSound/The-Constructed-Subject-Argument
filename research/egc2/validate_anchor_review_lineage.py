#!/usr/bin/env python3
"""Fail-closed cross-artifact lineage validation for EGC 2.0 anchor review v0.2.

This module validates that a source manifest, public reviewer queues, protected
assignment bundle, and locked submissions all belong to one internally
consistent review run. It does not authenticate human identity, establish a
trusted timestamp, or validate any anchor scientifically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

QUEUE_SCHEMA = "egc2-anchor-reviewer-queue-0.2.0"
KEY_SCHEMA = "egc2-anchor-review-assignment-key-0.2.0"
SUBMISSION_SCHEMA = "egc2-anchor-review-submission-0.2.0"
MIN_REVIEWERS = 3
MAP_REASON_CODES = {
    "MAP_TOO_SPARSE",
    "MAP_INTERNAL_CONFLICT",
    "MAP_UNINTERPRETABLE",
    "MAP_RESPONSE_DEPENDENT",
    "MAP_OTHER",
}


class LineageValidationError(ValueError):
    """Raised when review artifacts cannot be proven to share one lineage."""


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def without_digest(value: dict[str, Any], field: str) -> dict[str, Any]:
    body = deepcopy(value)
    body.pop(field, None)
    return body


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _reviewer_map(queues: Any, errors: list[str]) -> dict[str, dict[str, Any]]:
    if isinstance(queues, dict) and "queues" in queues:
        raw = queues.get("queues")
        if isinstance(raw, list):
            queues = raw
    if isinstance(queues, dict):
        iterable = list(queues.values())
    elif isinstance(queues, list):
        iterable = queues
    else:
        errors.append("queues must be a reviewer-keyed object, queue-set object, or list")
        return {}

    result: dict[str, dict[str, Any]] = {}
    for queue in iterable:
        if not isinstance(queue, dict):
            errors.append("every queue must be an object")
            continue
        reviewer = queue.get("reviewer_id")
        if not isinstance(reviewer, str) or not reviewer:
            errors.append("every queue requires a nonempty reviewer_id")
            continue
        if reviewer in result:
            errors.append(f"duplicate queue reviewer_id: {reviewer}")
        result[reviewer] = queue
    return result


def _submission_map(submissions: Any, errors: list[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(submissions, list):
        errors.append("submissions must be a list")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for submission in submissions:
        if not isinstance(submission, dict):
            errors.append("every submission must be an object")
            continue
        reviewer = submission.get("reviewer_id")
        if not isinstance(reviewer, str) or not reviewer:
            errors.append("every submission requires a nonempty reviewer_id")
            continue
        if reviewer in result:
            errors.append(f"duplicate submission reviewer_id: {reviewer}")
        result[reviewer] = submission
    return result


def validate_review_lineage(
    manifest: dict[str, Any],
    queues: Any,
    protected_bundle: dict[str, Any],
    submissions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate one complete review run without joining constructor targets."""
    errors: list[str] = []

    manifest_id = manifest.get("manifest_id")
    manifest_digest = manifest.get("content_digest_sha256")
    packets = manifest.get("packets")
    _require(isinstance(manifest_id, str) and bool(manifest_id), "manifest_id is required", errors)
    _require(
        isinstance(manifest_digest, str) and len(manifest_digest) == 64,
        "manifest content digest must be a 64-character SHA-256 hex string",
        errors,
    )
    _require(isinstance(packets, list) and len(packets) == 24, "manifest must contain 24 packets", errors)
    anchor_ids = [p.get("anchor_id") for p in packets] if isinstance(packets, list) else []
    _require(
        len(anchor_ids) == len(set(anchor_ids)) and all(isinstance(x, str) and x for x in anchor_ids),
        "manifest anchor IDs must be nonempty and unique",
        errors,
    )

    queue_by_reviewer = _reviewer_map(queues, errors)
    submission_by_reviewer = _submission_map(submissions, errors)
    reviewer_keys = protected_bundle.get("reviewer_keys")
    if not isinstance(reviewer_keys, dict):
        errors.append("protected bundle reviewer_keys must be an object")
        reviewer_keys = {}

    queue_reviewers = set(queue_by_reviewer)
    key_reviewers = set(reviewer_keys)
    submission_reviewers = set(submission_by_reviewer)
    _require(len(queue_reviewers) >= MIN_REVIEWERS, "at least three reviewer queues are required", errors)
    _require(
        queue_reviewers == key_reviewers == submission_reviewers,
        "reviewer sets must match exactly across queues, protected keys, and submissions",
        errors,
    )

    _require(protected_bundle.get("schema_version") == KEY_SCHEMA, "invalid protected bundle schema", errors)
    _require(protected_bundle.get("source_manifest_id") == manifest_id, "bundle manifest_id mismatch", errors)
    _require(
        protected_bundle.get("source_content_digest_sha256") == manifest_digest,
        "bundle source digest mismatch",
        errors,
    )
    bundle_declared = protected_bundle.get("bundle_digest_sha256")
    _require(
        bundle_declared == canonical_digest(without_digest(protected_bundle, "bundle_digest_sha256")),
        "protected bundle digest mismatch",
        errors,
    )

    expected_anchor_ids = set(anchor_ids)
    queue_digests: dict[str, str] = {}
    submission_digests: dict[str, str] = {}

    for reviewer in sorted(queue_reviewers | key_reviewers | submission_reviewers):
        queue = queue_by_reviewer.get(reviewer)
        key = reviewer_keys.get(reviewer)
        submission = submission_by_reviewer.get(reviewer)
        if not all(isinstance(x, dict) for x in (queue, key, submission)):
            continue

        _require(queue.get("schema_version") == QUEUE_SCHEMA, f"{reviewer}: invalid queue schema", errors)
        _require(queue.get("reviewer_id") == reviewer, f"{reviewer}: queue reviewer mismatch", errors)
        _require(queue.get("source_manifest_id") == manifest_id, f"{reviewer}: queue manifest mismatch", errors)
        _require(
            queue.get("source_content_digest_sha256") == manifest_digest,
            f"{reviewer}: queue source digest mismatch",
            errors,
        )
        queue_declared = queue.get("queue_digest_sha256")
        _require(
            queue_declared == canonical_digest(without_digest(queue, "queue_digest_sha256")),
            f"{reviewer}: queue digest mismatch",
            errors,
        )
        queue_digests[reviewer] = str(queue_declared)

        items = queue.get("items")
        if not isinstance(items, list):
            errors.append(f"{reviewer}: queue items must be a list")
            items = []
        queue_pairs = [(item.get("position"), item.get("presentation_id")) for item in items if isinstance(item, dict)]
        _require(len(queue_pairs) == 24, f"{reviewer}: queue must contain 24 items", errors)
        _require(len(queue_pairs) == len(set(queue_pairs)), f"{reviewer}: queue positions/presentation IDs must be unique", errors)
        _require(
            [position for position, _ in queue_pairs] == list(range(1, 25)),
            f"{reviewer}: queue positions must be contiguous 1-24",
            errors,
        )

        _require(key.get("schema_version") == KEY_SCHEMA, f"{reviewer}: invalid key schema", errors)
        _require(key.get("reviewer_id") == reviewer, f"{reviewer}: key reviewer mismatch", errors)
        _require(
            key.get("source_content_digest_sha256") == manifest_digest,
            f"{reviewer}: key source digest mismatch",
            errors,
        )
        _require(key.get("queue_digest_sha256") == queue_declared, f"{reviewer}: key queue digest mismatch", errors)
        key_declared = key.get("key_digest_sha256")
        _require(
            key_declared == canonical_digest(without_digest(key, "key_digest_sha256")),
            f"{reviewer}: key digest mismatch",
            errors,
        )
        rows = key.get("rows")
        if not isinstance(rows, list):
            errors.append(f"{reviewer}: key rows must be a list")
            rows = []
        key_pairs = [(row.get("position"), row.get("presentation_id")) for row in rows if isinstance(row, dict)]
        _require(key_pairs == queue_pairs, f"{reviewer}: protected mapping does not exactly match queue order", errors)
        mapped_anchors = [row.get("anchor_id") for row in rows if isinstance(row, dict)]
        _require(
            len(mapped_anchors) == 24 and set(mapped_anchors) == expected_anchor_ids,
            f"{reviewer}: protected key must map every source anchor exactly once",
            errors,
        )

        _require(submission.get("schema_version") == SUBMISSION_SCHEMA, f"{reviewer}: invalid submission schema", errors)
        _require(submission.get("reviewer_id") == reviewer, f"{reviewer}: submission reviewer mismatch", errors)
        _require(submission.get("source_manifest_id") == manifest_id, f"{reviewer}: submission manifest mismatch", errors)
        _require(
            submission.get("source_content_digest_sha256") == manifest_digest,
            f"{reviewer}: submission source digest mismatch",
            errors,
        )
        _require(submission.get("queue_digest_sha256") == queue_declared, f"{reviewer}: submission queue digest mismatch", errors)
        _require(submission.get("locked_before_target_reveal") is True, f"{reviewer}: submission is not locked", errors)
        _require(submission.get("targets_seen_before_lock") is False, f"{reviewer}: target exposure declared", errors)
        submission_declared = submission.get("submission_digest_sha256")
        _require(
            submission_declared == canonical_digest(without_digest(submission, "submission_digest_sha256")),
            f"{reviewer}: submission digest mismatch",
            errors,
        )
        submission_digests[reviewer] = str(submission_declared)

        reviews = submission.get("reviews")
        if not isinstance(reviews, list):
            errors.append(f"{reviewer}: reviews must be a list")
            reviews = []
        review_pairs = [(row.get("position"), row.get("presentation_id")) for row in reviews if isinstance(row, dict)]
        _require(review_pairs == queue_pairs, f"{reviewer}: review rows must exactly follow assigned queue", errors)
        for row in reviews:
            if not isinstance(row, dict):
                continue
            if row.get("score_disposition") == "suppress_reference_inadequate":
                reasons = row.get("reason_codes")
                _require(
                    isinstance(reasons, list) and bool(set(reasons) & MAP_REASON_CODES),
                    f"{reviewer} position {row.get('position')}: suppression requires a map-inadequacy reason code",
                    errors,
                )

    if errors:
        raise LineageValidationError(json.dumps({"valid": False, "errors": errors}, indent=2))

    run_commitment_core = {
        "manifest_id": manifest_id,
        "source_content_digest_sha256": manifest_digest,
        "reviewer_ids": sorted(queue_reviewers),
        "queue_digests": dict(sorted(queue_digests.items())),
        "protected_bundle_digest_sha256": bundle_declared,
        "submission_digests": dict(sorted(submission_digests.items())),
    }
    return {
        "valid": True,
        "reviewer_count": len(queue_reviewers),
        "item_count": len(anchor_ids),
        **run_commitment_core,
        "review_run_commitment_sha256": canonical_digest(run_commitment_core),
        "claim_limit": (
            "Engineering lineage validation only. This does not authenticate reviewers, "
            "establish trusted timestamps, validate anchors, or validate semantic fidelity."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("queues", type=Path)
    parser.add_argument("protected_bundle", type=Path)
    parser.add_argument("submissions", type=Path)
    parser.add_argument("--summary-out", type=Path)
    args = parser.parse_args(argv)

    values = [json.loads(path.read_text(encoding="utf-8")) for path in (
        args.manifest, args.queues, args.protected_bundle, args.submissions
    )]
    try:
        summary = validate_review_lineage(*values)
    except LineageValidationError as exc:
        print(str(exc))
        return 1
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
