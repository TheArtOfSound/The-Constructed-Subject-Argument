from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("evaluate_v0_3_structural_balance.py")
SPEC = importlib.util.spec_from_file_location("evaluate_v0_3_structural_balance", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class StructuralBalanceOracleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.grid = MODULE.load_grid(
            Path(__file__).with_name("capability_adequacy_v0.3_candidate_grid.json")
        )
        self.strict, self.moderate = self.grid["structural_balance_candidates"]

    def test_balanced_allocation_passes_both_candidates(self) -> None:
        for candidate in (self.strict, self.moderate):
            result = MODULE.evaluate_structural_balance([24] * 6, candidate, 6)
            self.assertTrue(result.structurally_valid)
            self.assertEqual(result.failure_reasons, ())
            self.assertAlmostEqual(result.effective_domain_count, 6.0)

    def test_single_domain_80_percent_fails_all_three_criteria(self) -> None:
        result = MODULE.evaluate_structural_balance([116, 6, 6, 6, 5, 5], self.moderate, 6)
        self.assertFalse(result.structurally_valid)
        self.assertEqual(
            set(result.failure_reasons),
            {"minimum_domain_share", "maximum_domain_share", "effective_domain_count"},
        )

    def test_two_domain_80_percent_is_rejected(self) -> None:
        result = MODULE.evaluate_structural_balance([58, 58, 7, 7, 7, 7], self.moderate, 6)
        self.assertFalse(result.structurally_valid)
        self.assertIn("maximum_domain_share", result.failure_reasons)
        self.assertIn("effective_domain_count", result.failure_reasons)

    def test_missing_domain_is_deterministically_rejected(self) -> None:
        result = MODULE.evaluate_structural_balance([30, 30, 30, 30, 24, 0], self.moderate, 6)
        self.assertFalse(result.structurally_valid)
        self.assertIn("minimum_domain_share", result.failure_reasons)

    def test_moderately_unbalanced_profile_can_pass_moderate_but_not_strict(self) -> None:
        counts = [36, 24, 21, 21, 21, 21]
        moderate = MODULE.evaluate_structural_balance(counts, self.moderate, 6)
        strict = MODULE.evaluate_structural_balance(counts, self.strict, 6)
        self.assertTrue(moderate.structurally_valid)
        self.assertFalse(strict.structurally_valid)
        self.assertIn("maximum_domain_share", strict.failure_reasons)

    def test_structure_is_independent_of_outcomes(self) -> None:
        counts = [116, 6, 6, 6, 5, 5]
        first = MODULE.evaluate_structural_balance(counts, self.moderate, 6)
        second = MODULE.evaluate_structural_balance(counts, self.moderate, 6)
        self.assertEqual(first, second)

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.evaluate_structural_balance([1, 2], self.strict, 6)
        with self.assertRaises(ValueError):
            MODULE.evaluate_structural_balance([0, 0, 0, 0, 0, 0], self.strict, 6)
        with self.assertRaises(ValueError):
            MODULE.evaluate_structural_balance([1, 1, 1, 1, 1, -1], self.strict, 6)
        with self.assertRaises(TypeError):
            MODULE.evaluate_structural_balance([1, 1, 1, 1, 1, 1.0], self.strict, 6)


if __name__ == "__main__":
    unittest.main()
