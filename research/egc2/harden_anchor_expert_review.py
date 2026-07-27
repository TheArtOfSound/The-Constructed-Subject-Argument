#!/usr/bin/env python3
"""Harden EGC 2.0 anchor expert review with opaque queues and tamper evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

QUEUE_SCHEMA = "egc2-anchor-reviewer-queue-0.2.0"
KEY_SCHEMA = "egc2-anchor-review-assignment-key-0.2.0"
SUBMISSION_SCHEMA = "egc2-anchor-review-submission-0.2.0"
AGGREGATE_SCHEMA = "egc2-anchor-review-aggregate-0.2.0"
PAIR_GAP = 12
MIN_REVIEWERS = 3
DOMAINS = {"autobiographical_meaning", "conceptual_explanation", "position_and_reasoning"}
ADEQUACY = {"adequate", "too_sparse", "internal_conflict", "uninterpretable", "response_dependent", "other_problem"}
DISPOSITIONS = {"retain", "retain_with_warning", "exploratory_only", "suppress_reference_inadequate"}
REASONS = {
    "CM_MISSING", "CM_REVERSED", "EC_MISSING", "EC_DISTORTED", "REL_MISSING",
    "REL_REVERSED", "QUAL_MISSING", "IMPLICATION_CHANGED", "TONE_MISMATCH_MATERIAL",
    "AUDIENCE_TARGET_MISSED", "TONE_DIFFERENCE_NONMATERIAL", "MAP_TOO_SPARSE",
    "MAP_INTERNAL_CONFLICT", "MAP_UNINTERPRETABLE", "MAP_RESPONSE_DEPENDENT", "MAP_OTHER",
    "LENGTH_DECOY", "POLISH_DECOY", "EMOTION_DECOY", "AGREEMENT_DECOY",
    "LEXICAL_OVERLAP_DECOY", "NO_MATERIAL_LOSS",
}
FORBIDDEN = {
    "anchor_id", "contrast_group_id", "contrast_family", "provisional_score_region",
    "provisional_reason_codes", "construct_irrelevant_features", "expert_rationale",
    "admissible_score_range", "known_ambiguities", "validation_status", "blind_review",
    "pilot_metrics", "audit", "created_by",
}


class ReviewHardeningError(ValueError):
    pass


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def _keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _keys(child)


def _rng(seed: str, reviewer: str, purpose: str) -> random.Random:
    token = hashlib.sha256(f"{seed}\0{reviewer}\0{purpose}\0v0.2".encode()).digest()
    return random.Random(int.from_bytes(token[:8], "big"))


def _max_run(values: list[str]) -> int:
    best = current = 0
    prior = None
    for value in values:
        current = current + 1 if value == prior else 1
        best = max(best, current)
        prior = value
    return best


def _ordered_pairs(groups: dict[str, list[dict[str, Any]]], seed: str, reviewer: str):
    pairs = [groups[key] for key in sorted(groups)]
    rng = _rng(seed, reviewer, "pair-order")
    for _ in range(10_000):
        rng.shuffle(pairs)
        if _max_run([pair[0]["prompt_domain"] for pair in pairs]) <= 2:
            return [list(pair) for pair in pairs]
    raise ReviewHardeningError("could not satisfy domain-run control")


def build_review_bundle(manifest: dict[str, Any], reviewers: list[str], seed: str):
    if len(reviewers) < MIN_REVIEWERS or len(set(reviewers)) != len(reviewers):
        raise ReviewHardeningError("at least three unique reviewer pseudonyms are required")
    packets = manifest.get("packets")
    if not isinstance(packets, list) or len(packets) != 24:
        raise ReviewHardeningError("source manifest must contain exactly 24 packets")
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for packet in packets:
        groups[str(packet.get("contrast_group_id"))].append(packet)
    if len(groups) != 12 or any(len(pair) != 2 for pair in groups.values()):
        raise ReviewHardeningError("source manifest must contain 12 two-packet groups")
    domain_counts = Counter()
    for group, pair in groups.items():
        domains = {packet.get("prompt_domain") for packet in pair}
        if len(domains) != 1:
            raise ReviewHardeningError(f"{group}: pair members must share a domain")
        domain_counts[next(iter(domains))] += 1
    if set(domain_counts) != DOMAINS or any(domain_counts[d] != 4 for d in DOMAINS):
        raise ReviewHardeningError("source manifest must contain four pairs per domain")

    queues, keys, protected_orders = {}, {}, []
    for reviewer in reviewers:
        pairs = _ordered_pairs(groups, seed, reviewer)
        orient = _rng(seed, reviewer, "orientation")
        first, second = [], []
        for pair in pairs:
            if orient.randrange(2):
                pair.reverse()
            first.append(pair[0]); second.append(pair[1])
        ordered = first + second
        protected_orders.append(tuple(packet["anchor_id"] for packet in ordered))
        items, rows = [], []
        for position, packet in enumerate(ordered, 1):
            opaque = "P-" + hashlib.sha256(
                f"{seed}\0{reviewer}\0{packet['anchor_id']}\0v0.2".encode()
            ).hexdigest()[:20]
            items.append({
                "position": position,
                "presentation_id": opaque,
                "anchor_version": packet["anchor_version"],
                "prompt_domain": packet["prompt_domain"],
                "prompt_text": packet["prompt_text"],
                "private_intention_map": deepcopy(packet["private_intention_map"]),
                "candidate_response": packet["candidate_response"],
            })
            rows.append({
                "position": position, "presentation_id": opaque,
                "anchor_id": packet["anchor_id"], "contrast_group_id": packet["contrast_group_id"],
                "contrast_family": packet["contrast_family"],
                "provisional_score_region": packet["provisional_score_region"],
            })
        queue_core = {
            "schema_version": QUEUE_SCHEMA,
            "reviewer_id": reviewer,
            "source_manifest_id": manifest.get("manifest_id"),
            "source_content_digest_sha256": manifest.get("content_digest_sha256"),
            "seed_commitment_sha256": hashlib.sha256(seed.encode()).hexdigest(),
            "pair_gap": PAIR_GAP,
            "items": items,
        }
        queue = {**queue_core, "queue_digest_sha256": digest(queue_core)}
        leaked = FORBIDDEN & set(_keys(queue))
        if leaked:
            raise ReviewHardeningError(f"public queue leaks protected fields: {sorted(leaked)}")
        key_core = {
            "schema_version": KEY_SCHEMA, "reviewer_id": reviewer,
            "source_content_digest_sha256": manifest.get("content_digest_sha256"),
            "queue_digest_sha256": queue["queue_digest_sha256"], "rows": rows,
        }
        queues[reviewer] = queue
        keys[reviewer] = {**key_core, "key_digest_sha256": digest(key_core)}
    if len(set(protected_orders)) != len(protected_orders):
        raise ReviewHardeningError("reviewer anchor orders must differ")
    bundle_core = {
        "schema_version": KEY_SCHEMA,
        "source_manifest_id": manifest.get("manifest_id"),
        "source_content_digest_sha256": manifest.get("content_digest_sha256"),
        "reviewer_keys": keys,
    }
    return queues, {**bundle_core, "bundle_digest_sha256": digest(bundle_core)}


def submission_digest(submission: dict[str, Any]) -> str:
    body = deepcopy(submission); body.pop("submission_digest_sha256", None)
    return digest(body)


def validate_submission(queue: dict[str, Any], submission: dict[str, Any]):
    errors = []
    queue_core = deepcopy(queue); declared = queue_core.pop("queue_digest_sha256", None)
    if declared != digest(queue_core): errors.append("queue digest mismatch")
    for field in ("reviewer_id", "source_manifest_id", "source_content_digest_sha256", "queue_digest_sha256"):
        if submission.get(field) != queue.get(field): errors.append(f"{field} mismatch")
    if submission.get("schema_version") != SUBMISSION_SCHEMA: errors.append("submission schema mismatch")
    if submission.get("locked_before_target_reveal") is not True: errors.append("submission not locked before reveal")
    if submission.get("targets_seen_before_lock") is not False: errors.append("targets_seen_before_lock must be false")
    try:
        start = datetime.fromisoformat(str(submission.get("started_at_utc")).replace("Z", "+00:00"))
        end = datetime.fromisoformat(str(submission.get("locked_at_utc")).replace("Z", "+00:00"))
        if start.tzinfo is None or end.tzinfo is None or start > end: raise ValueError
    except ValueError: errors.append("invalid start/lock timestamps")
    expected = [(item["position"], item["presentation_id"]) for item in queue.get("items", [])]
    reviews = submission.get("reviews") if isinstance(submission.get("reviews"), list) else []
    observed = [(row.get("position"), row.get("presentation_id")) for row in reviews]
    if observed != expected: errors.append("reviews must exactly match assigned position and presentation ID")
    for row in reviews:
        pos, score = row.get("position"), row.get("semantic_fidelity_score")
        adequacy, disposition = row.get("intention_map_adequacy"), row.get("score_disposition")
        reasons, confidence = row.get("reason_codes"), row.get("confidence_1_to_5")
        if adequacy not in ADEQUACY: errors.append(f"{pos}: invalid adequacy")
        if disposition not in DISPOSITIONS: errors.append(f"{pos}: invalid disposition")
        if score is not None and (not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 7):
            errors.append(f"{pos}: score must be null or integer 1-7")
        if adequacy == "adequate" and (score is None or disposition not in {"retain", "retain_with_warning"}):
            errors.append(f"{pos}: adequate reference requires retained numeric score")
        if disposition == "suppress_reference_inadequate" and (adequacy == "adequate" or score is not None):
            errors.append(f"{pos}: suppression requires non-adequate map and null score")
        if score is None and disposition != "suppress_reference_inadequate": errors.append(f"{pos}: null score requires suppression")
        if not isinstance(reasons, list) or len(reasons) != len(set(reasons)) or set(reasons) - REASONS:
            errors.append(f"{pos}: invalid reason codes")
        if score in {1, 2, 6, 7} and not reasons: errors.append(f"{pos}: extreme score requires reason code")
        if not isinstance(confidence, int) or isinstance(confidence, bool) or not 1 <= confidence <= 5:
            errors.append(f"{pos}: invalid confidence")
        recognized = row.get("recognized_possible_pair")
        if not isinstance(recognized, bool): errors.append(f"{pos}: pair-recognition flag must be boolean")
        if recognized and not str(row.get("pair_recognition_note") or "").strip():
            errors.append(f"{pos}: pair-recognition note required")
    if submission.get("submission_digest_sha256") != submission_digest(submission):
        errors.append("submission digest mismatch")
    if errors: raise ReviewHardeningError("; ".join(errors))
    return {"valid": True, "reviewer_id": submission["reviewer_id"], "review_count": len(reviews)}


def aggregate(manifest, bundle, queues, submissions, reveal_targets=False):
    core = deepcopy(bundle); declared = core.pop("bundle_digest_sha256", None)
    if declared != digest(core): raise ReviewHardeningError("protected bundle digest mismatch")
    if len(submissions) < MIN_REVIEWERS or len({s.get("reviewer_id") for s in submissions}) != len(submissions):
        raise ReviewHardeningError("three distinct locked submissions are required")
    packet_by_id = {packet["anchor_id"]: packet for packet in manifest["packets"]}
    rows_by_anchor = defaultdict(list)
    for submission in submissions:
        reviewer = submission["reviewer_id"]
        queue, key = queues.get(reviewer), bundle.get("reviewer_keys", {}).get(reviewer)
        if not queue or not key: raise ReviewHardeningError(f"missing queue/key for {reviewer}")
        key_core = deepcopy(key); key_declared = key_core.pop("key_digest_sha256", None)
        if key_declared != digest(key_core): raise ReviewHardeningError(f"{reviewer}: key digest mismatch")
        validate_submission(queue, submission)
        if [r["presentation_id"] for r in key["rows"]] != [i["presentation_id"] for i in queue["items"]]:
            raise ReviewHardeningError(f"{reviewer}: protected mapping does not match queue")
        mapping = {row["presentation_id"]: row["anchor_id"] for row in key["rows"]}
        for row in submission["reviews"]: rows_by_anchor[mapping[row["presentation_id"]]].append(row)
    results = []
    for anchor_id in sorted(packet_by_id):
        rows = rows_by_anchor[anchor_id]
        if len(rows) != len(submissions): raise ReviewHardeningError(f"{anchor_id}: missing reviews")
        scores = [r["semantic_fidelity_score"] for r in rows if r["semantic_fidelity_score"] is not None]
        flags = []
        spread = max(scores) - min(scores) if len(scores) > 1 else 0 if scores else None
        if spread is not None and spread > 3: flags.append("score_range_exceeds_3")
        if len({r["intention_map_adequacy"] for r in rows}) > 1: flags.append("adequacy_disagreement")
        if any(r["recognized_possible_pair"] for r in rows): flags.append("possible_pair_recognition")
        if any(r["score_disposition"] == "suppress_reference_inadequate" for r in rows): flags.append("suppression_requested")
        result = {
            "anchor_id": anchor_id, "numeric_scores": scores,
            "median": statistics.median(scores) if scores else None, "score_range": spread,
            "adequacy_counts": dict(Counter(r["intention_map_adequacy"] for r in rows)),
            "reason_code_counts": dict(Counter(c for r in rows for c in r["reason_codes"])),
            "review_flags": flags,
        }
        if reveal_targets:
            target = packet_by_id[anchor_id]["provisional_score_region"]
            result["constructor_target"] = target
            if result["median"] is not None and abs(result["median"] - target) > 1:
                result["review_flags"].append("median_differs_from_target_by_more_than_1")
        results.append(result)
    out_core = {
        "schema_version": AGGREGATE_SCHEMA,
        "source_content_digest_sha256": manifest.get("content_digest_sha256"),
        "reviewer_count": len(submissions), "constructor_targets_revealed": reveal_targets,
        "submission_digests": {s["reviewer_id"]: s["submission_digest_sha256"] for s in submissions},
        "results": results,
        "claim_limit": "Discrepancy evidence only; no automatic anchor validation or rejection.",
    }
    return {**out_core, "aggregate_digest_sha256": digest(out_core)}


def _read(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def _write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--reviewers", nargs="+", required=True)
    parser.add_argument("--seed-file", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--protected-key-out", type=Path, required=True)
    args = parser.parse_args(argv)
    manifest = _read(args.manifest)
    from validate_anchor_development_manifest import validate_manifest
    validate_manifest(manifest)
    seed = args.seed_file.read_text(encoding="utf-8").strip()
    if not seed: raise ReviewHardeningError("seed file is empty")
    queues, bundle = build_review_bundle(manifest, args.reviewers, seed)
    for reviewer, queue in queues.items(): _write(args.out_dir / f"{reviewer}.queue.v0.2.json", queue)
    _write(args.protected_key_out, bundle)
    print(json.dumps({
        "reviewers": sorted(queues), "pair_gap": PAIR_GAP,
        "queue_digests": {r: q["queue_digest_sha256"] for r, q in queues.items()},
        "protected_bundle_digest_sha256": bundle["bundle_digest_sha256"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
