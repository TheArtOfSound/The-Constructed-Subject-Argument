from __future__ import annotations

import unittest

import calibrate_multiway_power as power
import simulate_crossed_item_rater as sim


class MultiwayPowerCalibrationTest(unittest.TestCase):
    def test_profile_has_requested_contrast(self) -> None:
        profile = power.truth_profile(0.20)
        contrast = profile["exact_anchor"] - (
            profile["structural_transfer"] + profile["novel"]
        ) / 2.0
        self.assertAlmostEqual(contrast, 0.20)

    def test_common_data_seed_preserves_early_scores(self) -> None:
        smaller = power.simulate_effect(0.10, 77)
        larger = power.simulate_effect(0.30, 77)
        self.assertEqual(
            [row["early"] for row in smaller["rows"]],
            [row["early"] for row in larger["rows"]],
        )

    def test_temporary_truth_is_removed(self) -> None:
        power.simulate_effect(0.20, 1)
        self.assertFalse(any(key.startswith("power_") for key in sim.TRUTH))

    def test_cell_is_deterministic_except_runtime(self) -> None:
        first = power.run_cell(0.20, "item", 3, 20, 9)
        second = power.run_cell(0.20, "item", 3, 20, 9)
        for key in first:
            if key != "runtime_seconds":
                self.assertEqual(first[key], second[key])

    def test_invalid_effect_fails(self) -> None:
        with self.assertRaises(ValueError):
            power.truth_profile(0.0)

    def test_invalid_method_fails(self) -> None:
        with self.assertRaises(ValueError):
            power.run_cell(0.20, "not-a-method", 1, 1, 9)


if __name__ == "__main__":
    unittest.main()
