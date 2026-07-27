#!/usr/bin/env python3
import unittest

from analyze_paired_adequacy_sensitivity import (
    PairedOutcome,
    PairedSensitivityInputError,
    analyze,
    gamma_sensitivity,
    leave_one_participant_out,
    mean_difference_bounds,
    participant_difference_bounds,
)


class ParticipantBoundsTests(unittest.TestCase):
    def test_complete_pair_is_point_identified(self):
        result = participant_difference_bounds(PairedOutcome("P1", 3, 6))
        self.assertEqual(result["pattern"], "complete_pair")
        self.assertEqual(
            (result["difference_lower"], result["difference_upper"]),
            (3.0, 3.0),
        )

    def test_condition_b_suppressed_bounds(self):
        result = participant_difference_bounds(PairedOutcome("P1", 4, None))
        self.assertEqual(result["pattern"], "condition_b_suppressed")
        self.assertEqual(
            (result["difference_lower"], result["difference_upper"]),
            (-3.0, 3.0),
        )

    def test_condition_a_suppressed_bounds(self):
        result = participant_difference_bounds(PairedOutcome("P1", None, 5))
        self.assertEqual(result["pattern"], "condition_a_suppressed")
        self.assertEqual(
            (result["difference_lower"], result["difference_upper"]),
            (-2.0, 4.0),
        )

    def test_both_suppressed_bounds(self):
        result = participant_difference_bounds(PairedOutcome("P1", None, None))
        self.assertEqual(
            (result["difference_lower"], result["difference_upper"]),
            (-6.0, 6.0),
        )


class MeanBoundsTests(unittest.TestCase):
    def setUp(self):
        self.pairs = [
            PairedOutcome("P1", 3, 5),
            PairedOutcome("P2", 4, None),
            PairedOutcome("P3", None, 6),
            PairedOutcome("P4", None, None),
        ]

    def test_manual_mean_bounds(self):
        result = mean_difference_bounds(self.pairs)
        # Participant intervals: [2,2], [-3,3], [-1,5], [-6,6].
        self.assertAlmostEqual(result["mean_difference_lower"], -2.0)
        self.assertAlmostEqual(result["mean_difference_upper"], 4.0)
        self.assertEqual(result["complete_pair_mean_difference"], 2.0)
        self.assertEqual(result["pattern_counts"]["complete_pair"], 1)
        self.assertEqual(result["sign_status"], "sign_not_robust")

    def test_gamma_zero_uses_observed_condition_means(self):
        result = gamma_sensitivity(self.pairs, [0.0])[0]
        self.assertAlmostEqual(result["mean_difference_lower"], 2.0)
        self.assertAlmostEqual(result["mean_difference_upper"], 2.0)
        self.assertEqual(result["sign_status"], "positive_sign_robust")

    def test_gamma_intervals_expand_monotonically(self):
        results = gamma_sensitivity(self.pairs, [0.0, 0.5, 1.0, 2.0])
        widths = [
            result["mean_difference_upper"] - result["mean_difference_lower"]
            for result in results
        ]
        self.assertEqual(widths, sorted(widths))

    def test_duplicate_participant_rejected(self):
        with self.assertRaises(PairedSensitivityInputError):
            mean_difference_bounds(
                [PairedOutcome("P1", 3, 4), PairedOutcome("P1", 4, 5)]
            )

    def test_out_of_range_score_rejected(self):
        with self.assertRaises(PairedSensitivityInputError):
            mean_difference_bounds([PairedOutcome("P1", 0, 5)])

    def test_gamma_requires_observation_in_both_conditions(self):
        with self.assertRaises(PairedSensitivityInputError):
            gamma_sensitivity(
                [PairedOutcome("P1", 4, None), PairedOutcome("P2", 5, None)],
                [0.0],
            )


class DiagnosticTests(unittest.TestCase):
    def test_leave_one_out_detects_sign_dependency(self):
        pairs = [
            PairedOutcome("P1", 1, 7),
            PairedOutcome("P2", 5, 5),
            PairedOutcome("P3", 5, 5),
        ]
        result = leave_one_participant_out(
            pairs,
            a_missing_bounds=(4, 4),
            b_missing_bounds=(4, 4),
        )
        self.assertGreaterEqual(result["sign_status_change_count"], 1)

    def test_analysis_digest_is_deterministic(self):
        pairs = [
            PairedOutcome("P1", 3, 5),
            PairedOutcome("P2", 4, None),
            PairedOutcome("P3", None, 6),
        ]
        self.assertEqual(analyze(pairs), analyze(pairs))

    def test_single_participant_leave_one_out_rejected(self):
        with self.assertRaises(PairedSensitivityInputError):
            leave_one_participant_out([PairedOutcome("P1", 3, 4)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
