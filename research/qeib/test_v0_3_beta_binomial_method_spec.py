"""Integrity tests for the prospectively frozen QEIB v0.3 PPC method."""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path


GRID_PATH = Path(__file__).with_name("capability_adequacy_v0.3_candidate_grid.json")
SPEC_PATH = Path(__file__).with_name("QEIB_V0_3_BETA_BINOMIAL_PPC_METHOD.md")


class BetaBinomialMethodSpecificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grid = json.loads(GRID_PATH.read_text(encoding="utf-8"))
        cls.method = cls.grid["beta_binomial_numerical_method"]

    def test_grid_dimensions_are_exact(self) -> None:
        mu = self.method["grid"]["mu"]
        kappa = self.method["grid"]["kappa"]
        self.assertEqual(mu["point_count"], 199)
        self.assertAlmostEqual(mu["minimum"], 0.005)
        self.assertAlmostEqual(mu["maximum"], 0.995)
        self.assertAlmostEqual(mu["step"], 0.005)
        self.assertEqual(kappa["point_count"], 19)
        self.assertEqual(kappa["j_min"], 0)
        self.assertEqual(kappa["j_max"], 18)
        self.assertEqual(self.method["grid"]["total_cell_count"], 199 * 19)

    def test_kappa_formula_has_frozen_endpoints(self) -> None:
        values = [2 ** (j / 2) for j in range(19)]
        self.assertEqual(len(values), 19)
        self.assertAlmostEqual(values[0], 1.0)
        self.assertAlmostEqual(values[-1], 512.0)
        self.assertTrue(all(math.isfinite(value) and value > 0 for value in values))

    def test_primary_prior_controls_qualification(self) -> None:
        self.assertEqual(self.method["qualification_prior"], "primary_only")
        self.assertIn("primary_tail_probability", self.method["candidate_decision"])
        self.assertIn("without_changing_primary_decision", self.method["sensitivity_rule"])

    def test_tail_and_discreteness_are_frozen(self) -> None:
        discreteness = self.method["discreteness"]
        self.assertEqual(discreteness["tail_event"], "T_rep_greater_than_or_equal_to_T_obs")
        self.assertIn("strictly_less_than", discreteness["interior_event"])
        self.assertFalse(discreteness["mid_p"])
        self.assertFalse(discreteness["randomized_p"])

    def test_candidate_thresholds_match_design(self) -> None:
        candidates = {
            item["id"]: item["tail_probability"]
            for item in self.grid["hierarchical_heterogeneity_candidates"]
        }
        self.assertEqual(candidates, {
            "beta_binomial_ppc_90": 0.10,
            "beta_binomial_ppc_95": 0.05,
        })

    def test_specification_file_exists_and_preserves_limits(self) -> None:
        text = SPEC_PATH.read_text(encoding="utf-8")
        self.assertIn("no v0.3 candidate result inspected", text)
        self.assertIn("private-holdout outcomes", text)
        self.assertIn("Posterior-predictive p-values are generally conservative", text)
        self.assertIn("not a test of consciousness", text)


if __name__ == "__main__":
    unittest.main()
