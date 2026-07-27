#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from prepare_anchor_expert_review import (  # noqa: E402
    MIN_PAIR_GAP,
    ReviewValidationError,
    SUBMISSION_SCHEMA,
    aggregate_discrepancies,
    build_reviewer_queues,
    validate_queue_set,
    validate_submission,
)

MANIFEST_PATH = HERE / "anchor_development_manifest.v0.1.json"


def load_manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def completed_submission(queue, score=5):
    reviews = []
    for item in queue["items"]:
        reviews.append({
            "review_item_id": item["review_item_id"],
            "semantic_fidelity_score": score,
            "score_disposition": "retained_numeric",
            "reason_codes": ["NO_MATERIAL_LOSS"],
            "intention_map_adequacy": "adequate",
            "confidence_1_to_5": 4,
            "ambiguity_note": None,
            "pair_recognition_suspected": False,
        })
    return {
        "schema_version": SUBMISSION_SCHEMA,
        "reviewer_id": queue["reviewer_id"],
        "queue_digest_sha256": queue["queue_digest_sha256"],
        "source_content_digest_sha256": queue["source_content_digest_sha256"],
        "locked_before_target_reveal": True,
        "targets_seen_before_lock": False,
        "locked_at_utc": "2026-07-27T03:30:00Z",
        "reviews": reviews,
    }


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_manifest()
        self.queue_set = build_reviewer_queues(self.manifest)

    def test_deterministic_generation(self):
        self.assertEqual(self.queue_set, build_reviewer_queues(self.manifest))

    def test_three_reviewers_receive_every_item_once(self):
        summary = validate_queue_set(self.manifest, self.queue_set)
        self.assertEqual(summary["reviewer_count"], 3)
        self.assertEqual(summary["items_per_reviewer"], 24)

    def test_pair_separation(self):
        pair_by_id = {p["anchor_id"]: p["contrast_group_id"] for p in self.manifest["packets"]}
        for queue in self.queue_set["queues"]:
            positions = {}
            for index, item in enumerate(queue["items"]):
                positions.setdefault(pair_by_id[item["review_item_id"]], []).append(index)
            self.assertTrue(all(abs(v[0] - v[1]) >= MIN_PAIR_GAP for v in positions.values()))

    def test_queue_digest_tampering_fails(self):
        tampered = deepcopy(self.queue_set)
        tampered["queues"][0]["items"][0]["candidate_response"] += " tampered"
        with self.assertRaises(ReviewValidationError):
            validate_queue_set(self.manifest, tampered)

    def test_target_leakage_fails(self):
        tampered = deepcopy(self.queue_set)
        tampered["queues"][0]["items"][0]["provisional_score_region"] = 6
        # Recompute omitted intentionally: leakage must fail independently of digest.
        with self.assertRaises(ReviewValidationError):
            validate_queue_set(self.manifest, tampered)


class SubmissionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_manifest()
        self.queue_set = build_reviewer_queues(self.manifest)
        self.queue = self.queue_set["queues"][0]

    def test_complete_locked_submission_passes(self):
        summary = validate_submission(self.queue, completed_submission(self.queue))
        self.assertEqual(summary["review_count"], 24)

    def test_unlocked_submission_fails(self):
        submission = completed_submission(self.queue)
        submission["locked_before_target_reveal"] = False
        with self.assertRaises(ReviewValidationError):
            validate_submission(self.queue, submission)

    def test_review_order_must_match_queue(self):
        submission = completed_submission(self.queue)
        submission["reviews"][0], submission["reviews"][1] = submission["reviews"][1], submission["reviews"][0]
        with self.assertRaises(ReviewValidationError):
            validate_submission(self.queue, submission)

    def test_inadequate_reference_can_suppress_numeric_score(self):
        submission = completed_submission(self.queue)
        review = submission["reviews"][0]
        review.update({
            "semantic_fidelity_score": None,
            "score_disposition": "suppressed_reference_inadequate",
            "intention_map_adequacy": "too_sparse",
            "reason_codes": ["MAP_TOO_SPARSE"],
        })
        summary = validate_submission(self.queue, submission)
        self.assertEqual(summary["suppressed_count"], 1)

    def test_adequate_reference_cannot_suppress_score(self):
        submission = completed_submission(self.queue)
        review = submission["reviews"][0]
        review.update({
            "semantic_fidelity_score": None,
            "score_disposition": "suppressed_reference_inadequate",
            "intention_map_adequacy": "adequate",
        })
        with self.assertRaises(ReviewValidationError):
            validate_submission(self.queue, submission)

    def test_aggregation_fails_before_reveal_authorization(self):
        submissions = [completed_submission(q) for q in self.queue_set["queues"]]
        with self.assertRaises(ReviewValidationError):
            aggregate_discrepancies(self.manifest, self.queue_set, submissions, reveal_authorized=False)

    def test_authorized_aggregation_preserves_all_items(self):
        submissions = [completed_submission(q) for q in self.queue_set["queues"]]
        report = aggregate_discrepancies(self.manifest, self.queue_set, submissions, reveal_authorized=True)
        self.assertEqual(len(report["items"]), 24)
        self.assertTrue(report["reveal_authorized"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
