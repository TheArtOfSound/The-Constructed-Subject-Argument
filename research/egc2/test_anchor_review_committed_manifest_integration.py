#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from harden_anchor_expert_review import (  # noqa: E402
    PAIR_GAP,
    SUBMISSION_SCHEMA,
    build_review_bundle,
    submission_digest,
    validate_submission,
)
from validate_anchor_development_manifest import validate_manifest  # noqa: E402
from validate_anchor_review_lineage import validate_review_lineage  # noqa: E402

MANIFEST_PATH = HERE / "anchor_development_manifest.v0.1.json"
REVIEWERS = ["INTEGRATION_R01", "INTEGRATION_R02", "INTEGRATION_R03"]
TEST_ONLY_SEED = "egc2-committed-manifest-integration-test-only-not-for-live-review"


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def synthetic_locked_submission(queue: dict) -> dict:
    """Create deterministic non-human fixture data for pipeline integration only."""
    reviews = [
        {
            "position": item["position"],
            "presentation_id": item["presentation_id"],
            "semantic_fidelity_score": 4,
            "score_disposition": "retain",
            "reason_codes": [],
            "intention_map_adequacy": "adequate",
            "confidence_1_to_5": 3,
            "ambiguity_note": "Synthetic integration fixture; not an expert judgment.",
            "recognized_possible_pair": False,
            "pair_recognition_note": None,
        }
        for item in queue["items"]
    ]
    submission = {
        "schema_version": SUBMISSION_SCHEMA,
        "reviewer_id": queue["reviewer_id"],
        "source_manifest_id": queue["source_manifest_id"],
        "source_content_digest_sha256": queue["source_content_digest_sha256"],
        "queue_digest_sha256": queue["queue_digest_sha256"],
        "started_at_utc": "2026-07-27T04:00:00Z",
        "locked_at_utc": "2026-07-27T04:01:00Z",
        "locked_before_target_reveal": True,
        "targets_seen_before_lock": False,
        "reviews": reviews,
        "submission_digest_sha256": "",
    }
    submission["submission_digest_sha256"] = submission_digest(submission)
    return submission


class CommittedManifestIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()
        validate_manifest(cls.manifest)
        cls.queues, cls.bundle = build_review_bundle(
            cls.manifest, REVIEWERS, TEST_ONLY_SEED
        )

    def test_committed_manifest_builds_three_distinct_opaque_queues(self):
        self.assertEqual(set(self.queues), set(REVIEWERS))
        orders = []
        for reviewer, queue in self.queues.items():
            self.assertEqual(len(queue["items"]), 24)
            self.assertTrue(all(item["presentation_id"].startswith("P-") for item in queue["items"]))
            self.assertTrue(all("anchor_id" not in item for item in queue["items"]))
            orders.append(tuple(item["presentation_id"] for item in queue["items"]))
        self.assertEqual(len(set(orders)), 3)

    def test_exact_pair_gap_and_half_domain_balance_hold_on_committed_manifest(self):
        for reviewer, queue in self.queues.items():
            key_rows = self.bundle["reviewer_keys"][reviewer]["rows"]
            by_group: dict[str, list[int]] = {}
            for row in key_rows:
                by_group.setdefault(row["contrast_group_id"], []).append(row["position"])
            self.assertTrue(all(sorted(pos)[1] - sorted(pos)[0] == PAIR_GAP for pos in by_group.values()))

            first_half = Counter(item["prompt_domain"] for item in queue["items"][:12])
            second_half = Counter(item["prompt_domain"] for item in queue["items"][12:])
            self.assertEqual(set(first_half.values()), {4})
            self.assertEqual(set(second_half.values()), {4})

    def test_synthetic_fixture_submissions_validate_and_lineage_closes(self):
        submissions = []
        for reviewer in REVIEWERS:
            submission = synthetic_locked_submission(self.queues[reviewer])
            validate_submission(self.queues[reviewer], submission)
            submissions.append(submission)

        summary = validate_review_lineage(
            self.manifest, self.queues, self.bundle, submissions
        )
        self.assertTrue(summary["valid"])
        self.assertEqual(summary["reviewer_count"], 3)
        self.assertEqual(summary["item_count"], 24)
        self.assertEqual(len(summary["review_run_commitment_sha256"]), 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)
