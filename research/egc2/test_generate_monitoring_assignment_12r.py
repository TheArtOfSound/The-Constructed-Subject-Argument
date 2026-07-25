from __future__ import annotations

import copy
import unittest

from generate_monitoring_assignment_12r import CLASSES, generate, validate


class MonitoringAssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = generate(20260725)

    def test_default_design_is_valid(self) -> None:
        self.assertEqual([], self.payload["validation_errors"])
        self.assertEqual(144, len(self.payload["items"]))
        self.assertEqual(576, len(self.payload["assignments"]))

    def test_exact_per_rater_and_per_class_load(self) -> None:
        for rows in self.payload["audit_schedule"].values():
            self.assertEqual(48, len(rows))
            for item_class in CLASSES:
                self.assertEqual(12, sum(row["item_class"] == item_class for row in rows))

    def test_rater_queue_conceals_monitoring_class(self) -> None:
        for rows in self.payload["rater_queues"].values():
            self.assertTrue(all(set(row) == {"position", "presentation_id", "item_id"} for row in rows))

    def test_session_mixes_classes_and_quartiles(self) -> None:
        for rows in self.payload["audit_schedule"].values():
            classes = [row["item_class"] for row in rows]
            self.assertTrue(all(a != b for a, b in zip(classes, classes[1:])))
            for start in range(0, 48, 12):
                quartile = classes[start:start + 12]
                counts = [quartile.count(item_class) for item_class in CLASSES]
                self.assertLessEqual(max(counts) - min(counts), 1)

    def test_exhaustive_dropout_audit_passes(self) -> None:
        one = self.payload["dropout_audit"]["1"]
        two = self.payload["dropout_audit"]["2"]
        self.assertEqual(12, one["scenario_count"])
        self.assertEqual(66, two["scenario_count"])
        self.assertEqual(0, one["failure_count"])
        self.assertEqual(0, two["failure_count"])
        self.assertEqual(3, one["minimum_remaining_ratings_per_item"])
        self.assertEqual(2, two["minimum_remaining_ratings_per_item"])

    def test_fixed_seed_is_deterministic(self) -> None:
        second = generate(20260725)
        self.assertEqual(self.payload["content_sha256"], second["content_sha256"])
        self.assertEqual(self.payload, second)

    def test_validator_detects_metadata_leak(self) -> None:
        broken = copy.deepcopy(self.payload)
        rater = broken["design"]["rater_ids"][0]
        broken["rater_queues"][rater][0]["item_class"] = "novel_response"
        self.assertIn(f"PUBLIC_METADATA_LEAK:{rater}", validate(broken))

    def test_validator_detects_rating_loss(self) -> None:
        broken = copy.deepcopy(self.payload)
        broken["assignments"].pop()
        self.assertIn("RATINGS_PER_ITEM", validate(broken))


if __name__ == "__main__":
    unittest.main()
