import unittest

from check_structural_gate_design_compatibility import CompatibilityError, assess_compatibility


def gate_spec():
    return {
        "design_id": "incomplete_12x24_r6",
        "planned": {
            "raters": 12,
            "ratings_per_item": 6,
            "monitoring_classes": 4,
            "items_per_class": 24,
            "total_assignments": 576,
        },
        "gates": [{
            "id": "G1_ITEM_REPLICATION",
            "threshold": {
                "minimum_distinct_raters_per_item": 4,
                "minimum_fraction_items_with_at_least_5_ratings": 0.95,
            },
        }],
    }


class CompatibilityTests(unittest.TestCase):
    def test_matching_design_passes(self):
        result = assess_compatibility({
            "design_id": "incomplete_12x24_r6",
            "raters": 12,
            "ratings_per_item": 6,
            "monitoring_classes": 4,
            "items_per_class": 24,
            "total_assignments": 576,
        }, gate_spec())
        self.assertEqual(result["status"], "compatible")
        self.assertTrue(result["calibration_permitted"])
        self.assertEqual(result["mismatches"], [])

    def test_committed_12x36_r4_design_fails(self):
        result = assess_compatibility({
            "design": {
                "rater_ids": [f"R{i:02d}" for i in range(1, 13)],
                "ratings_per_item": 4,
                "item_classes": ["a", "b", "c", "d"],
                "items_per_class": 36,
                "total_items_per_rater": 48,
            }
        }, gate_spec())
        self.assertEqual(result["status"], "incompatible_fail_closed")
        fields = {x["field"] for x in result["mismatches"]}
        self.assertIn("ratings_per_item", fields)
        self.assertIn("items_per_class", fields)
        self.assertIn("G1_baseline_feasibility", fields)
        self.assertFalse(result["calibration_permitted"])

    def test_total_assignments_is_derived(self):
        result = assess_compatibility({
            "raters": 12,
            "ratings_per_item": 6,
            "monitoring_classes": 4,
            "items_per_class": 24,
        }, gate_spec())
        self.assertEqual(result["design"]["total_assignments"], 576)
        self.assertTrue(result["calibration_permitted"])

    def test_four_ratings_cannot_satisfy_95_percent_at_five(self):
        result = assess_compatibility({
            "raters": 12,
            "ratings_per_item": 4,
            "monitoring_classes": 4,
            "items_per_class": 36,
            "total_assignments": 576,
        }, gate_spec())
        g1 = [x for x in result["mismatches"] if x["field"] == "G1_baseline_feasibility"]
        self.assertEqual(len(g1), 1)
        self.assertEqual(g1[0]["design"]["maximum_fraction_items_with_at_least_5_at_baseline"], 0.0)

    def test_missing_metadata_fails_clearly(self):
        with self.assertRaises(CompatibilityError):
            assess_compatibility({"raters": 12}, gate_spec())


if __name__ == "__main__":
    unittest.main()
