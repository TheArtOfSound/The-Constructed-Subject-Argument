import copy
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("generate_rater_pilot_assignment.py")
spec = importlib.util.spec_from_file_location("assignment", MODULE_PATH)
assignment = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(assignment)


class AssignmentDesignTests(unittest.TestCase):
    def setUp(self):
        self.payload = assignment.generate(seed=20260725)

    def test_default_design_is_valid(self):
        self.assertEqual([], self.payload["validation_errors"])
        self.assertEqual(60, self.payload["design"]["response_count"])
        self.assertEqual(240, self.payload["summary"]["primary_assignment_count"])
        self.assertEqual(168, self.payload["summary"]["anchor_assignment_count"])
        self.assertEqual(12, self.payload["summary"]["blind_repeat_count"])

    def test_every_response_has_four_ratings(self):
        self.assertEqual({4}, set(self.payload["summary"]["ratings_per_response"].values()))

    def test_no_rater_sees_both_paired_responses(self):
        self.assertEqual(1, self.payload["summary"]["max_responses_per_participant_per_rater"])

    def test_rater_primary_domain_and_condition_balance(self):
        for loads in self.payload["summary"]["domain_load_by_rater"].values():
            self.assertEqual({10}, set(loads.values()))
        for loads in self.payload["summary"]["condition_load_by_rater"].values():
            self.assertEqual({15}, set(loads.values()))

    def test_anchor_load_is_balanced(self):
        self.assertEqual({21}, set(self.payload["summary"]["anchor_load_by_rater"].values()))

    def test_generation_is_deterministic(self):
        second = assignment.generate(seed=20260725)
        self.assertEqual(self.payload["content_sha256"], second["content_sha256"])
        third = assignment.generate(seed=20260726)
        self.assertNotEqual(self.payload["content_sha256"], third["content_sha256"])

    def test_validator_detects_paired_response_leakage(self):
        broken = copy.deepcopy(self.payload)
        first = broken["assignments"]["primary"][0]
        participant = first["participant_id"]
        rater = first["rater_id"]
        other = next(
            row for row in broken["assignments"]["primary"]
            if row["participant_id"] == participant
            and row["response_id"] != first["response_id"]
        )
        other["rater_id"] = rater
        self.assertIn(
            "RATER_SAW_BOTH_PARTICIPANT_RESPONSES",
            assignment.validate_design(broken),
        )

    def test_validator_detects_repeat_without_source(self):
        broken = copy.deepcopy(self.payload)
        broken["assignments"]["blind_repeats"][0]["repeat_of_response_id"] = "MISSING"
        self.assertIn(
            "BLIND_REPEAT_WITHOUT_SOURCE_RATING",
            assignment.validate_design(broken),
        )


if __name__ == "__main__":
    unittest.main()
