"""Adversarial tests for the frozen QEIB v0.3 beta-binomial PPC evaluator."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("evaluate_v0_3_beta_binomial_ppc.py")
SPEC = importlib.util.spec_from_file_location("evaluate_v0_3_beta_binomial_ppc", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

GRID_PATH = Path(__file__).with_name("capability_adequacy_v0.3_candidate_grid.json")


class BetaBinomialPPCEvaluatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grid = MODULE.load_grid(GRID_PATH)

    def test_grid_dimensions_match_frozen_method(self) -> None:
        definition = MODULE.grid_definition()
        self.assertEqual(definition["mu"]["point_count"], 199)
        self.assertEqual(definition["kappa"]["point_count"], 19)
        self.assertEqual(definition["total_cell_count"], 3781)
        mu = MODULE.build_mu_grid()
        kappa = MODULE.build_kappa_grid()
        self.assertEqual(len(mu), 199)
        self.assertEqual(len(kappa), 19)
        self.assertAlmostEqual(mu[0], 0.005)
        self.assertAlmostEqual(mu[-1], 0.995)
        self.assertAlmostEqual(kappa[0], 1.0)
        self.assertAlmostEqual(kappa[-1], 512.0)

    def test_probabilities_remain_finite_and_in_unit_interval(self) -> None:
        y = [12, 12, 12, 12, 12, 12]
        n = [24, 24, 24, 24, 24, 24]
        result = MODULE.evaluate_beta_binomial_ppc(
            y, n, candidate_id="beta_binomial_ppc_90", grid=self.grid
        )
        for key in ("primary_prior", "alternative_prior"):
            tail = result[key]["posterior_predictive_tail_probability"]
            self.assertTrue(math.isfinite(tail))
            self.assertGreaterEqual(tail, 0.0)
            self.assertLessEqual(tail, 1.0)
            self.assertEqual(result[key]["rejected_non_finite_cells"], 0)
            for bound in result[key]["mu_central_interval_90"]:
                self.assertTrue(0.0 < bound < 1.0)
            for bound in result[key]["rho_central_interval_90"]:
                self.assertTrue(0.0 < bound <= 1.0)

    def test_deterministic_reproduction_is_byte_identical(self) -> None:
        y = [10, 11, 12, 13, 14, 15]
        n = [20, 20, 24, 24, 28, 28]
        first = MODULE.evaluate_beta_binomial_ppc(
            y, n, candidate_id="beta_binomial_ppc_95", grid=self.grid
        )
        second = MODULE.evaluate_beta_binomial_ppc(
            y, n, candidate_id="beta_binomial_ppc_95", grid=self.grid
        )
        self.assertEqual(
            json.dumps(first, sort_keys=True, separators=(",", ":")),
            json.dumps(second, sort_keys=True, separators=(",", ":")),
        )
        self.assertEqual(first["artifact_digest"], second["artifact_digest"])
        self.assertEqual(
            first["artifact_digest"],
            MODULE.artifact_digest(first),
        )

    def test_balanced_equal_rate_domains_do_not_fail_from_labels_alone(self) -> None:
        # Same counts in every domain; only allocation labels change under
        # permutation, so the diagnostic must be permutation-invariant and
        # should not fail solely from domain labels.
        y = [18, 18, 18, 18, 18, 18]
        n = [30, 30, 30, 30, 30, 30]
        base = MODULE.evaluate_beta_binomial_ppc(
            y, n, candidate_id="beta_binomial_ppc_90", grid=self.grid
        )
        permuted = MODULE.evaluate_beta_binomial_ppc(
            list(reversed(y)),
            list(reversed(n)),
            candidate_id="beta_binomial_ppc_90",
            grid=self.grid,
        )
        self.assertEqual(
            base["primary_prior"]["posterior_predictive_tail_probability"],
            permuted["primary_prior"]["posterior_predictive_tail_probability"],
        )
        # Balanced equal-rate vectors should receive a high tail probability
        # under the operating model, so they pass the more permissive threshold.
        self.assertEqual(base["primary_decision"], "pass")
        self.assertGreaterEqual(
            base["primary_prior"]["posterior_predictive_tail_probability"],
            0.10,
        )

    def test_floor_ceiling_mixture_has_lower_tail_than_low_dispersion(self) -> None:
        # Low-dispersion: all domains near mid-rate.
        low_y = [12, 13, 12, 13, 12, 13]
        low_n = [24, 24, 24, 24, 24, 24]
        # Floor/ceiling mixture with similar pooled accuracy (~0.5).
        mix_y = [2, 2, 2, 22, 22, 22]
        mix_n = [24, 24, 24, 24, 24, 24]
        low = MODULE.evaluate_beta_binomial_ppc(
            low_y, low_n, candidate_id="beta_binomial_ppc_90", grid=self.grid
        )
        mix = MODULE.evaluate_beta_binomial_ppc(
            mix_y, mix_n, candidate_id="beta_binomial_ppc_90", grid=self.grid
        )
        self.assertLess(
            mix["primary_prior"]["posterior_predictive_tail_probability"],
            low["primary_prior"]["posterior_predictive_tail_probability"],
        )

    def test_primary_and_alternative_both_emitted_primary_authoritative(self) -> None:
        y = [8, 10, 12, 14, 16, 18]
        n = [24, 24, 24, 24, 24, 24]
        result = MODULE.evaluate_beta_binomial_ppc(
            y, n, candidate_id="beta_binomial_ppc_90", grid=self.grid
        )
        self.assertIn("primary_prior", result)
        self.assertIn("alternative_prior", result)
        self.assertEqual(result["qualification_prior"], "primary_only")
        primary_pass = (
            result["primary_prior"]["posterior_predictive_tail_probability"]
            >= result["candidate_threshold"]
        )
        self.assertEqual(result["primary_decision"], "pass" if primary_pass else "fail")
        # Alternative cannot change primary decision field even if it disagrees.
        alt_pass = (
            result["alternative_prior"]["posterior_predictive_tail_probability"]
            >= result["candidate_threshold"]
        )
        self.assertEqual(
            result["prior_sensitivity_disagreement"],
            primary_pass != alt_pass,
        )
        if result["prior_sensitivity_disagreement"]:
            self.assertEqual(
                result["primary_decision"],
                "pass" if primary_pass else "fail",
            )

    def test_boundary_thresholds(self) -> None:
        y = [12] * 6
        n = [24] * 6
        r90 = MODULE.evaluate_beta_binomial_ppc(
            y, n, candidate_id="beta_binomial_ppc_90", grid=self.grid
        )
        r95 = MODULE.evaluate_beta_binomial_ppc(
            y, n, candidate_id="beta_binomial_ppc_95", grid=self.grid
        )
        self.assertAlmostEqual(r90["candidate_threshold"], 0.10)
        self.assertAlmostEqual(r95["candidate_threshold"], 0.05)
        # Same primary tail; decision may differ only via threshold.
        self.assertEqual(
            r90["primary_prior"]["posterior_predictive_tail_probability"],
            r95["primary_prior"]["posterior_predictive_tail_probability"],
        )

    def test_malformed_inputs_fail_closed(self) -> None:
        good_y = [10, 10, 10, 10, 10, 10]
        good_n = [20, 20, 20, 20, 20, 20]
        with self.assertRaises(MODULE.BetaBinomialPPCError):
            MODULE.evaluate_beta_binomial_ppc(
                [10, 10, 10, 10, 10], good_n, candidate_id="beta_binomial_ppc_90"
            )
        with self.assertRaises(MODULE.BetaBinomialPPCError):
            MODULE.evaluate_beta_binomial_ppc(
                [10, 10, 10, 10, 10, 25],
                good_n,
                candidate_id="beta_binomial_ppc_90",
            )
        with self.assertRaises(MODULE.BetaBinomialPPCError):
            MODULE.evaluate_beta_binomial_ppc(
                good_y,
                [20, 20, 20, 20, 20, 0],
                candidate_id="beta_binomial_ppc_90",
            )
        with self.assertRaises(MODULE.BetaBinomialPPCError):
            MODULE.evaluate_beta_binomial_ppc(
                good_y,
                good_n,
                candidate_id="beta_binomial_ppc_90",
                upstream_eligible=False,
            )
        with self.assertRaises(MODULE.BetaBinomialPPCError):
            MODULE.evaluate_beta_binomial_ppc(
                good_y,
                [20, 20, 20, 20, 20, 20.0],  # type: ignore[list-item]
                candidate_id="beta_binomial_ppc_90",
            )
        with self.assertRaises(MODULE.BetaBinomialPPCError):
            MODULE.evaluate_beta_binomial_ppc(
                good_y,
                good_n,
                candidate_id="beta_binomial_ppc_90",
                extra_payload={"model_id": "should-reject", "private_holdout": True},
            )
        with self.assertRaises(MODULE.BetaBinomialPPCError):
            MODULE.evaluate_beta_binomial_ppc(
                good_y,
                good_n,
                candidate_id="not_a_real_candidate",
            )

    def test_beta_binomial_pmf_sums_near_one(self) -> None:
        n = 12
        mu = 0.4
        kappa = 8.0
        total = sum(MODULE.beta_binomial_pmf(y, n, mu, kappa) for y in range(n + 1))
        self.assertTrue(math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-9))

    def test_t_obs_zero_assigns_unit_tail_probability_at_cell(self) -> None:
        # Perfect agreement of all domain rates with a mu on the grid that
        # equals that common rate makes T_obs=0 and interior empty, so the
        # cell-level tail is 1 by the frozen equality-in-tail rule.
        y = [5, 5, 5, 5, 5, 5]
        n = [10, 10, 10, 10, 10, 10]
        p_cell = MODULE.cell_tail_probability(y, n, mu=0.5, kappa=4.0)
        self.assertAlmostEqual(p_cell, 1.0)

    def test_cli_all_candidates(self) -> None:
        import io
        from contextlib import redirect_stdout

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = MODULE.main(
                [
                    "--grid",
                    str(GRID_PATH),
                    "--y",
                    "12,12,12,12,12,12",
                    "--n",
                    "24,24,24,24,24,24",
                    "--candidate-id",
                    "all",
                ]
            )
        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(len(payload["results"]), 2)


if __name__ == "__main__":
    unittest.main()
