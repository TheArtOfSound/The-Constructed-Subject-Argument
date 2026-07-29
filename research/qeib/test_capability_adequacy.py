import json
import tempfile
import unittest
from pathlib import Path

from research.qeib.evaluate_capability_adequacy import (
    AdequacyInputError,
    evaluate,
    load_policy,
)


class CapabilityAdequacyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_policy()

    def adequate_summary(self):
        return {
            "scheduled_neutral_observations": 24,
            "eligible_neutral_families": 24,
            "correct_eligible_families": 15,
            "incorrect_eligible_families": 9,
            "transport_failures": 0,
            "empty_format_ungradable_observations": 1,
            "eligible_families_by_domain": {
                "arithmetic": 4,
                "constraint_reasoning": 4,
                "document_extraction": 4,
                "code_reasoning": 4,
                "planning": 4,
                "calibrated_abstention": 4,
            },
            "negative_control_pass": True,
            "positive_control_pass": True,
        }

    def test_adequate_run_passes(self):
        result = evaluate(self.adequate_summary(), self.policy)
        self.assertTrue(result["adequate_for_context_inference"])
        self.assertEqual(result["summary_label"], "adequate_for_context_inference")
        self.assertEqual(result["all_failure_labels"], [])

    def test_floor_run_is_noninterpretable(self):
        summary = self.adequate_summary()
        summary["correct_eligible_families"] = 3
        summary["incorrect_eligible_families"] = 21
        result = evaluate(summary, self.policy)
        self.assertFalse(result["adequate_for_context_inference"])
        self.assertEqual(result["summary_label"], "inadequate_floor")
        self.assertIn("inadequate_floor", result["all_failure_labels"])
        self.assertIn("descriptive engineering output only", result["interpretation"])

    def test_concurrent_failures_are_preserved_with_precedence(self):
        summary = self.adequate_summary()
        summary.update(
            {
                "scheduled_neutral_observations": 20,
                "eligible_neutral_families": 10,
                "correct_eligible_families": 9,
                "incorrect_eligible_families": 1,
                "transport_failures": 4,
                "empty_format_ungradable_observations": 1,
                "eligible_families_by_domain": {"arithmetic": 5, "planning": 5},
                "negative_control_pass": False,
            }
        )
        result = evaluate(summary, self.policy)
        self.assertEqual(result["summary_label"], "invalid_controls")
        self.assertIn("inadequate_operational", result["all_failure_labels"])
        self.assertIn("indeterminate_small_n", result["all_failure_labels"])
        self.assertIn("indeterminate_narrow_domain", result["all_failure_labels"])
        self.assertIn("indeterminate_low_variation", result["all_failure_labels"])

    def test_context_contrast_input_is_rejected(self):
        summary = self.adequate_summary()
        summary["paired_mean_delta"] = -0.08
        with self.assertRaisesRegex(AdequacyInputError, "neutral-context-only"):
            evaluate(summary, self.policy)

    def test_inconsistent_denominators_are_rejected(self):
        summary = self.adequate_summary()
        summary["correct_eligible_families"] = 16
        with self.assertRaisesRegex(AdequacyInputError, "must equal"):
            evaluate(summary, self.policy)

    def test_policy_is_valid_json_and_expected_version(self):
        policy_path = Path(__file__).with_name("capability_adequacy_policy.v0.1.json")
        parsed = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertEqual(parsed["schema_version"], "qeib-capability-adequacy-policy-0.1.0")
        self.assertEqual(parsed["thresholds"]["minimum_neutral_accuracy"], 0.20)
        self.assertEqual(parsed["thresholds"]["maximum_neutral_accuracy"], 0.90)


if __name__ == "__main__":
    unittest.main()
