from __future__ import annotations

import math
import unittest

import calibrate_multiway_power as power
import calibrate_two_way_crve as crve
import simulate_crossed_item_rater as sim


class TwoWayCRVETest(unittest.TestCase):
    def test_truth_profile_has_requested_estimand(self):
        for effect in (0.10, 0.20, 0.30):
            profile = power.truth_profile(effect)
            estimand = profile["exact_anchor"] - 0.5 * (
                profile["structural_transfer"] + profile["novel"]
            )
            self.assertAlmostEqual(estimand, effect, places=12)

    def test_null_and_power_share_data_seed_contract(self):
        seed = power.stable_seed(20260726, "complete_8x18_r8", "N1", 3, "data")
        null_rows = sim.simulate(power.design(), "global_stability", seed, **power.REGIME)["rows"]
        effect_rows = power.simulate_effect(0.20, seed)["rows"]
        self.assertEqual(len(null_rows), len(effect_rows))
        for null_row, effect_row in zip(null_rows, effect_rows):
            self.assertEqual(
                (null_row["class"], null_row["item"], null_row["rater"], null_row["early"]),
                (effect_row["class"], effect_row["item"], effect_row["rater"], effect_row["early"]),
            )

    def test_crve_is_deterministic(self):
        data = power.simulate_effect(0.20, 12345)
        self.assertEqual(crve.two_way_crve(data["rows"]), crve.two_way_crve(data["rows"]))

    def test_cluster_counts_and_reference_df(self):
        data = power.simulate_effect(0.20, 12345)
        result = crve.two_way_crve(data["rows"])
        self.assertEqual(result["clusters"]["item"], 72)
        self.assertEqual(result["clusters"]["rater"], 8)
        self.assertEqual(result["degrees_of_freedom"], 7)
        self.assertAlmostEqual(result["critical_value"], 2.3646, places=4)

    def test_interval_contains_point_and_has_finite_components(self):
        data = power.simulate_effect(0.20, 54321)
        result = crve.two_way_crve(data["rows"])
        lower, upper = result["ci95"]
        self.assertLessEqual(lower, result["point"])
        self.assertGreaterEqual(upper, result["point"])
        for value in result["components"].values():
            self.assertTrue(math.isfinite(value))

    def test_empty_rows_fail_clearly(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            crve.two_way_crve([])

    def test_invalid_effect_and_trial_count_fail(self):
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            crve.run_cell(-0.1, 1, 1)
        with self.assertRaisesRegex(ValueError, "positive"):
            crve.run_cell(0.1, 0, 1)


if __name__ == "__main__":
    unittest.main()
