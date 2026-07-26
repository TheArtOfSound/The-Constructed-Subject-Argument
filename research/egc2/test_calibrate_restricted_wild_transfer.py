import unittest

import calibrate_restricted_wild_transfer as transfer


class RestrictedWildTransferTest(unittest.TestCase):
    def test_candidate_designs_preserve_fixed_budget(self):
        for design_id in transfer.DESIGN_IDS:
            self.assertEqual(transfer.design(design_id).planned_ratings, 576)

    def test_nonzero_truth_does_not_leak_into_global_state(self):
        key = "transfer_power_0.2"
        self.assertNotIn(key, transfer.sim.TRUTH)
        data = transfer.simulate_cell_data(
            "complete_8x18_r8", "N2", 0.20, seed=11
        )
        self.assertEqual(len(data["rows"]), 576)
        self.assertNotIn(key, transfer.sim.TRUTH)

    def test_exact_test_is_deterministic(self):
        rows = transfer.simulate_cell_data(
            "complete_8x18_r8", "N2", 0.0, seed=12
        )["rows"]
        self.assertEqual(transfer.exact_test(rows), transfer.exact_test(rows))

    def test_incomplete_design_enumerates_all_rater_patterns(self):
        rows = transfer.simulate_cell_data(
            "incomplete_12x24_r6", "N2", 0.0, seed=13
        )["rows"]
        result = transfer.exact_test(rows)
        self.assertEqual(result["enumerated_patterns"], 4096)

    def test_zero_tolerance_fails_closed_when_any_pattern_is_undefined(self):
        rows = transfer.simulate_cell_data(
            "complete_8x18_r8", "N3", 0.0, seed=14
        )["rows"]
        result = transfer.exact_test(rows, max_undefined_pattern_rate=0.0)
        if result.get("undefined_patterns", 0) > 0:
            self.assertEqual(result["status"], "indeterminate")
            self.assertFalse(result["defined"])

    def test_invalid_inputs_fail_clearly(self):
        with self.assertRaises(ValueError):
            transfer.design("missing")
        with self.assertRaises(ValueError):
            transfer.simulate_cell_data("complete_8x18_r8", "missing", 0.0, 1)
        with self.assertRaises(ValueError):
            transfer.exact_test([], max_undefined_pattern_rate=1.0)
        with self.assertRaises(ValueError):
            transfer.run_cell("complete_8x18_r8", "N2", 0.0, 0, 1)


if __name__ == "__main__":
    unittest.main()
