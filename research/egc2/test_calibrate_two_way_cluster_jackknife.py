from __future__ import annotations

import unittest

import calibrate_multiway_power as power
import calibrate_two_way_cluster_jackknife as mod
import simulate_crossed_item_rater as sim


class TwoWayClusterJackknifeTest(unittest.TestCase):
    def rows(self):
        return sim.simulate(power.design(), "global_stability", 123, **power.REGIME)["rows"]

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            mod.two_way_cluster_jackknife([])

    def test_invalid_repair_rejected(self):
        with self.assertRaises(ValueError):
            mod.two_way_cluster_jackknife(self.rows(), "invented")

    def test_components_match_direct_deletion(self):
        rows = self.rows()
        result = mod.two_way_cluster_jackknife(rows)
        item_ids = sorted({row["item"] for row in rows})
        direct = [
            sim._point_metrics([row for row in rows if row["item"] != item])["contrast"]
            for item in item_ids
        ]
        center = sum(direct) / len(direct)
        expected = (len(direct) - 1) / len(direct) * sum(
            (estimate - center) ** 2 for estimate in direct
        )
        self.assertAlmostEqual(result["components"]["item"], expected, 12)
        self.assertEqual(result["influence"]["item"]["count"], len(item_ids))

    def test_max_repair_is_psd_and_at_least_one_way(self):
        result = mod.two_way_cluster_jackknife(self.rows())
        self.assertGreaterEqual(result["variance"], 0.0)
        self.assertGreaterEqual(result["variance"], result["components"]["item"])
        self.assertGreaterEqual(result["variance"], result["components"]["rater"])

    def test_deletion_estimates_are_preserved(self):
        result = mod.two_way_cluster_jackknife(self.rows())
        self.assertEqual(len(result["influence"]["rater"]["deleted_estimates"]), 8)
        self.assertEqual(len(result["influence"]["item"]["deleted_estimates"]), 72)
        self.assertEqual(len(result["influence"]["intersection"]["deleted_estimates"]), 576)

    def test_fixed_seed_is_deterministic(self):
        first = mod.run_cell(0.20, 3, 20260726)
        second = mod.run_cell(0.20, 3, 20260726)
        for key in first:
            if key != "runtime_seconds":
                self.assertEqual(first[key], second[key])

    def test_truth_profile_matches_requested_effect(self):
        for effect in (0.1, 0.2, 0.3):
            profile = power.truth_profile(effect)
            contrast = (
                profile["exact_anchor"]
                - 0.5 * profile["structural_transfer"]
                - 0.5 * profile["novel"]
            )
            self.assertAlmostEqual(contrast, effect)

    def test_invalid_trials_and_effect_rejected(self):
        with self.assertRaises(ValueError):
            mod.run_cell(-0.1, 1, 1)
        with self.assertRaises(ValueError):
            mod.run_cell(0.0, 0, 1)


if __name__ == "__main__":
    unittest.main()
