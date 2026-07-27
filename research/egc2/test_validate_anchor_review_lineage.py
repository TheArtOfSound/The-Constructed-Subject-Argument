#!/usr/bin/env python3
from __future__ import annotations

import unittest
from copy import deepcopy

from validate_anchor_review_lineage import (
    KEY_SCHEMA,
    QUEUE_SCHEMA,
    SUBMISSION_SCHEMA,
    LineageValidationError,
    canonical_digest,
    validate_review_lineage,
)


def fixture():
    packets = [{"anchor_id": f"A{i:03d}"} for i in range(1, 25)]
    manifest = {
        "manifest_id": "manifest-v1",
        "content_digest_sha256": "a" * 64,
        "packets": packets,
    }
    queues = {}
    keys = {}
    submissions = []
    for reviewer_index, reviewer in enumerate(("R01", "R02", "R03"), start=1):
        items = [
            {"position": position, "presentation_id": f"P-{reviewer_index}-{position:02d}"}
            for position in range(1, 25)
        ]
        queue_core = {
            "schema_version": QUEUE_SCHEMA,
            "reviewer_id": reviewer,
            "source_manifest_id": manifest["manifest_id"],
            "source_content_digest_sha256": manifest["content_digest_sha256"],
            "items": items,
        }
        queue = {**queue_core, "queue_digest_sha256": canonical_digest(queue_core)}
        queues[reviewer] = queue

        rows = [
            {
                "position": position,
                "presentation_id": f"P-{reviewer_index}-{position:02d}",
                "anchor_id": f"A{position:03d}",
            }
            for position in range(1, 25)
        ]
        key_core = {
            "schema_version": KEY_SCHEMA,
            "reviewer_id": reviewer,
            "source_content_digest_sha256": manifest["content_digest_sha256"],
            "queue_digest_sha256": queue["queue_digest_sha256"],
            "rows": rows,
        }
        keys[reviewer] = {**key_core, "key_digest_sha256": canonical_digest(key_core)}

        reviews = [
            {
                "position": position,
                "presentation_id": f"P-{reviewer_index}-{position:02d}",
                "score_disposition": "retain",
                "reason_codes": ["NO_MATERIAL_LOSS"],
            }
            for position in range(1, 25)
        ]
        submission_core = {
            "schema_version": SUBMISSION_SCHEMA,
            "reviewer_id": reviewer,
            "source_manifest_id": manifest["manifest_id"],
            "source_content_digest_sha256": manifest["content_digest_sha256"],
            "queue_digest_sha256": queue["queue_digest_sha256"],
            "locked_before_target_reveal": True,
            "targets_seen_before_lock": False,
            "reviews": reviews,
        }
        submissions.append({
            **submission_core,
            "submission_digest_sha256": canonical_digest(submission_core),
        })

    bundle_core = {
        "schema_version": KEY_SCHEMA,
        "source_manifest_id": manifest["manifest_id"],
        "source_content_digest_sha256": manifest["content_digest_sha256"],
        "reviewer_keys": keys,
    }
    bundle = {**bundle_core, "bundle_digest_sha256": canonical_digest(bundle_core)}
    return manifest, queues, bundle, submissions


def redigest_queue_related(queues, bundle, submissions, reviewer):
    queue = queues[reviewer]
    core = deepcopy(queue)
    core.pop("queue_digest_sha256", None)
    queue["queue_digest_sha256"] = canonical_digest(core)
    key = bundle["reviewer_keys"][reviewer]
    key["queue_digest_sha256"] = queue["queue_digest_sha256"]
    key_core = deepcopy(key)
    key_core.pop("key_digest_sha256", None)
    key["key_digest_sha256"] = canonical_digest(key_core)
    submission = next(s for s in submissions if s["reviewer_id"] == reviewer)
    submission["queue_digest_sha256"] = queue["queue_digest_sha256"]
    submission_core = deepcopy(submission)
    submission_core.pop("submission_digest_sha256", None)
    submission["submission_digest_sha256"] = canonical_digest(submission_core)
    bundle_core = deepcopy(bundle)
    bundle_core.pop("bundle_digest_sha256", None)
    bundle["bundle_digest_sha256"] = canonical_digest(bundle_core)


class LineageTests(unittest.TestCase):
    def test_complete_lineage_passes(self):
        summary = validate_review_lineage(*fixture())
        self.assertTrue(summary["valid"])
        self.assertEqual(summary["reviewer_count"], 3)
        self.assertEqual(summary["item_count"], 24)
        self.assertEqual(len(summary["review_run_commitment_sha256"]), 64)

    def test_reviewer_subset_fails(self):
        manifest, queues, bundle, submissions = fixture()
        submissions.pop()
        with self.assertRaises(LineageValidationError):
            validate_review_lineage(manifest, queues, bundle, submissions)

    def test_bundle_manifest_mismatch_fails_even_when_redigested(self):
        manifest, queues, bundle, submissions = fixture()
        bundle["source_manifest_id"] = "other-manifest"
        core = deepcopy(bundle); core.pop("bundle_digest_sha256")
        bundle["bundle_digest_sha256"] = canonical_digest(core)
        with self.assertRaises(LineageValidationError):
            validate_review_lineage(manifest, queues, bundle, submissions)

    def test_queue_source_mismatch_fails_even_when_chain_redigested(self):
        manifest, queues, bundle, submissions = fixture()
        queues["R01"]["source_content_digest_sha256"] = "b" * 64
        redigest_queue_related(queues, bundle, submissions, "R01")
        with self.assertRaises(LineageValidationError):
            validate_review_lineage(manifest, queues, bundle, submissions)

    def test_protected_mapping_missing_anchor_fails(self):
        manifest, queues, bundle, submissions = fixture()
        rows = bundle["reviewer_keys"]["R01"]["rows"]
        rows[-1]["anchor_id"] = rows[-2]["anchor_id"]
        key = bundle["reviewer_keys"]["R01"]
        key_core = deepcopy(key); key_core.pop("key_digest_sha256")
        key["key_digest_sha256"] = canonical_digest(key_core)
        bundle_core = deepcopy(bundle); bundle_core.pop("bundle_digest_sha256")
        bundle["bundle_digest_sha256"] = canonical_digest(bundle_core)
        with self.assertRaises(LineageValidationError):
            validate_review_lineage(manifest, queues, bundle, submissions)

    def test_submission_order_mismatch_fails_even_when_redigested(self):
        manifest, queues, bundle, submissions = fixture()
        submission = submissions[0]
        submission["reviews"][0], submission["reviews"][1] = submission["reviews"][1], submission["reviews"][0]
        core = deepcopy(submission); core.pop("submission_digest_sha256")
        submission["submission_digest_sha256"] = canonical_digest(core)
        with self.assertRaises(LineageValidationError):
            validate_review_lineage(manifest, queues, bundle, submissions)

    def test_suppression_requires_map_reason(self):
        manifest, queues, bundle, submissions = fixture()
        row = submissions[0]["reviews"][0]
        row["score_disposition"] = "suppress_reference_inadequate"
        row["reason_codes"] = ["EC_MISSING"]
        core = deepcopy(submissions[0]); core.pop("submission_digest_sha256")
        submissions[0]["submission_digest_sha256"] = canonical_digest(core)
        with self.assertRaises(LineageValidationError):
            validate_review_lineage(manifest, queues, bundle, submissions)

    def test_valid_suppression_reason_passes_lineage(self):
        manifest, queues, bundle, submissions = fixture()
        row = submissions[0]["reviews"][0]
        row["score_disposition"] = "suppress_reference_inadequate"
        row["reason_codes"] = ["MAP_TOO_SPARSE"]
        core = deepcopy(submissions[0]); core.pop("submission_digest_sha256")
        submissions[0]["submission_digest_sha256"] = canonical_digest(core)
        summary = validate_review_lineage(manifest, queues, bundle, submissions)
        self.assertTrue(summary["valid"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
