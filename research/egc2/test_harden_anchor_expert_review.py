#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from harden_anchor_expert_review import (
    SUBMISSION_SCHEMA,
    ReviewHardeningError,
    aggregate,
    build_review_bundle,
    digest,
    submission_digest,
    validate_submission,
)


def fixture_manifest():
    domains = ["autobiographical_meaning", "conceptual_explanation", "position_and_reasoning"]
    packets = []
    for pair_index in range(12):
        domain = domains[pair_index // 4]
        for member in range(2):
            number = pair_index * 2 + member + 1
            packets.append({
                "anchor_id": f"A{number:03d}", "anchor_version": "0.1.0",
                "prompt_domain": domain, "prompt_text": f"Prompt {pair_index + 1}",
                "private_intention_map": {
                    "central_meaning": "Meaning", "essential_concepts": ["one"],
                    "relationships": [], "intended_tone": None,
                    "intended_audience_understanding": "Understand", "declared_uncertainty": None,
                    "adequacy_status": "adequate", "adequacy_note": None,
                },
                "candidate_response": f"Response {number}",
                "contrast_group_id": f"G{pair_index + 1:02d}", "contrast_family": "length_decoy",
                "provisional_score_region": 6 if member == 0 else 3,
            })
    return {"manifest_id": "fixture", "content_digest_sha256": digest(packets), "packets": packets}


def completed(queue, reviewer):
    reviews = []
    for item in queue["items"]:
        reviews.append({
            "position": item["position"], "presentation_id": item["presentation_id"],
            "semantic_fidelity_score": 6, "score_disposition": "retain",
            "reason_codes": ["NO_MATERIAL_LOSS"], "intention_map_adequacy": "adequate",
            "confidence_1_to_5": 4, "ambiguity_note": None,
            "recognized_possible_pair": False, "pair_recognition_note": None,
        })
    submission = {
        "schema_version": SUBMISSION_SCHEMA, "reviewer_id": reviewer,
        "source_manifest_id": queue["source_manifest_id"],
        "source_content_digest_sha256": queue["source_content_digest_sha256"],
        "queue_digest_sha256": queue["queue_digest_sha256"],
        "started_at_utc": "2026-07-27T01:00:00Z", "locked_at_utc": "2026-07-27T02:00:00Z",
        "locked_before_target_reveal": True, "targets_seen_before_lock": False,
        "reviews": reviews,
    }
    submission["submission_digest_sha256"] = submission_digest(submission)
    return submission


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.manifest = fixture_manifest()

    def test_exact_pair_gap_and_domain_balance(self):
        queues, keys = build_review_bundle(self.manifest, ["R01", "R02", "R03"], "seed")
        for reviewer, queue in queues.items():
            mapping = {row["presentation_id"]: row for row in keys["reviewer_keys"][reviewer]["rows"]}
            positions = {}
            for item in queue["items"]:
                group = mapping[item["presentation_id"]]["contrast_group_id"]
                positions.setdefault(group, []).append(item["position"])
            self.assertTrue(all(values[1] - values[0] == 12 for values in positions.values()))
            for half in (queue["items"][:12], queue["items"][12:]):
                counts = {domain: sum(item["prompt_domain"] == domain for item in half) for domain in (
                    "autobiographical_meaning", "conceptual_explanation", "position_and_reasoning")}
                self.assertEqual(set(counts.values()), {4})

    def test_public_queues_hide_source_ids_and_targets(self):
        queues, keys = build_review_bundle(self.manifest, ["R01", "R02", "R03"], "seed")
        self.assertTrue(all("anchor_id" not in str(queue) for queue in queues.values()))
        self.assertTrue(all("provisional_score_region" not in str(queue) for queue in queues.values()))
        self.assertIn("anchor_id", keys["reviewer_keys"]["R01"]["rows"][0])

    def test_deterministic_but_reviewer_specific(self):
        first = build_review_bundle(self.manifest, ["R01", "R02", "R03"], "seed")
        second = build_review_bundle(self.manifest, ["R01", "R02", "R03"], "seed")
        self.assertEqual(first, second)
        orders = [tuple(row["anchor_id"] for row in first[1]["reviewer_keys"][r]["rows"]) for r in ("R01", "R02", "R03")]
        self.assertEqual(len(set(orders)), 3)

    def test_requires_three_unique_reviewers(self):
        with self.assertRaises(ReviewHardeningError):
            build_review_bundle(self.manifest, ["R01", "R02"], "seed")
        with self.assertRaises(ReviewHardeningError):
            build_review_bundle(self.manifest, ["R01", "R01", "R02"], "seed")


class SubmissionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = fixture_manifest()
        self.queues, self.keys = build_review_bundle(self.manifest, ["R01", "R02", "R03"], "seed")
        self.queue = self.queues["R01"]

    def test_complete_locked_submission_passes(self):
        self.assertTrue(validate_submission(self.queue, completed(self.queue, "R01"))["valid"])

    def test_queue_and_submission_tampering_fail(self):
        queue = copy.deepcopy(self.queue); queue["items"][0]["candidate_response"] += " tampered"
        with self.assertRaises(ReviewHardeningError):
            validate_submission(queue, completed(queue, "R01"))
        submission = completed(self.queue, "R01"); submission["reviews"][0]["semantic_fidelity_score"] = 1
        with self.assertRaises(ReviewHardeningError):
            validate_submission(self.queue, submission)

    def test_inadequate_map_can_suppress_but_adequate_map_cannot(self):
        submission = completed(self.queue, "R01"); row = submission["reviews"][0]
        row.update({"semantic_fidelity_score": None, "score_disposition": "suppress_reference_inadequate",
                    "intention_map_adequacy": "too_sparse", "reason_codes": ["MAP_TOO_SPARSE"]})
        submission["submission_digest_sha256"] = submission_digest(submission)
        self.assertTrue(validate_submission(self.queue, submission)["valid"])
        row["intention_map_adequacy"] = "adequate"
        submission["submission_digest_sha256"] = submission_digest(submission)
        with self.assertRaises(ReviewHardeningError):
            validate_submission(self.queue, submission)

    def test_pair_recognition_requires_note(self):
        submission = completed(self.queue, "R01"); row = submission["reviews"][0]
        row["recognized_possible_pair"] = True
        submission["submission_digest_sha256"] = submission_digest(submission)
        with self.assertRaises(ReviewHardeningError):
            validate_submission(self.queue, submission)
        row["pair_recognition_note"] = "Repeated prompt with a contrasting answer."
        submission["submission_digest_sha256"] = submission_digest(submission)
        self.assertTrue(validate_submission(self.queue, submission)["valid"])


class AggregateTests(unittest.TestCase):
    def setUp(self):
        self.manifest = fixture_manifest()
        self.queues, self.keys = build_review_bundle(self.manifest, ["R01", "R02", "R03"], "seed")
        self.submissions = [completed(self.queues[r], r) for r in ("R01", "R02", "R03")]

    def test_pre_reveal_aggregate_excludes_constructor_targets(self):
        report = aggregate(self.manifest, self.keys, self.queues, self.submissions, False)
        self.assertFalse(report["constructor_targets_revealed"])
        self.assertNotIn("constructor_target", report["results"][0])

    def test_post_reveal_aggregate_flags_target_disagreement(self):
        anchor = "A001"
        for submission in self.submissions:
            reviewer = submission["reviewer_id"]
            mapping = self.keys["reviewer_keys"][reviewer]["rows"]
            pid = next(row["presentation_id"] for row in mapping if row["anchor_id"] == anchor)
            review = next(row for row in submission["reviews"] if row["presentation_id"] == pid)
            review["semantic_fidelity_score"] = 1
            review["reason_codes"] = ["CM_MISSING"]
            submission["submission_digest_sha256"] = submission_digest(submission)
        report = aggregate(self.manifest, self.keys, self.queues, self.submissions, True)
        result = next(row for row in report["results"] if row["anchor_id"] == anchor)
        self.assertIn("median_differs_from_target_by_more_than_1", result["review_flags"])

    def test_protected_mapping_tamper_fails(self):
        keys = copy.deepcopy(self.keys); keys["reviewer_keys"]["R01"]["rows"][0]["anchor_id"] = "A999"
        with self.assertRaises(ReviewHardeningError):
            aggregate(self.manifest, keys, self.queues, self.submissions)


if __name__ == "__main__":
    unittest.main(verbosity=2)
