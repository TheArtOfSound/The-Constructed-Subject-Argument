import itertools
import unittest

import calibrate_multiway_power as power
import calibrate_restricted_wild_cluster as wild
import calibrate_two_way_crve as crve
import simulate_crossed_item_rater as sim


class RestrictedWildClusterTests(unittest.TestCase):
    def rows(self, effect=0.0, seed=42):
        if effect:
            return power.simulate_effect(effect, seed)["rows"]
        return sim.simulate(power.design(), "global_stability", seed, **power.REGIME)["rows"]

    def reference_draws(self, rows):
        restricted, residuals = wild._restricted_components(rows)
        raters = sorted({row["rater"] for row in rows})
        draws = []
        for pattern in itertools.product((-1, 1), repeat=len(raters)):
            signs = dict(zip(raters, pattern))
            draws.append(crve.two_way_crve(wild._bootstrap_rows(rows, restricted, residuals, signs)))
        return draws

    def test_null_projection_is_exact(self):
        restricted, _ = wild._restricted_components(self.rows(effect=0.2))
        contrast = sum(wild.COEFFICIENTS[c] * restricted[c] for c in sim.CLASSES)
        self.assertAlmostEqual(contrast, 0.0, places=12)

    def test_bootstrap_preserves_row_structure(self):
        rows = self.rows()
        restricted, residuals = wild._restricted_components(rows)
        signs = {r: 1 for r in range(power.design().raters)}
        boot = wild._bootstrap_rows(rows, restricted, residuals, signs)
        self.assertEqual(len(boot), len(rows))
        self.assertEqual({r["item"] for r in boot}, {r["item"] for r in rows})
        self.assertEqual({r["rater"] for r in boot}, {r["rater"] for r in rows})

    def test_quadratic_draw_matches_reference_row_reconstruction(self):
        rows = self.rows(seed=404)
        prepared = wild._prepare_quadratic_form(rows)
        reference = self.reference_draws(rows)
        patterns = list(itertools.product((-1, 1), repeat=len(prepared["raters"])))
        self.assertEqual(len(reference), len(patterns))
        for pattern, expected in zip(patterns, reference):
            actual = wild._quadratic_draw(prepared, pattern)
            self.assertAlmostEqual(actual["point"], expected["point"], places=12)
            self.assertAlmostEqual(actual["variance_raw"], expected["variance_raw"], places=12)
            self.assertEqual(
                actual["negative_variance_truncated"],
                expected["negative_variance_truncated"],
            )

    def test_exact_test_matches_reference_p_value(self):
        rows = self.rows(seed=505)
        observed = crve.two_way_crve(rows)
        observed_t = observed["point"] / observed["standard_error"]
        defined = []
        for draw in self.reference_draws(rows):
            if draw["standard_error"] > 0.0 and not draw["negative_variance_truncated"]:
                defined.append(draw["point"] / draw["standard_error"])
        expected = sum(abs(value) >= abs(observed_t) for value in defined) / len(defined)
        actual = wild.exact_restricted_rater_wild_test(rows)
        self.assertTrue(actual["defined"])
        self.assertAlmostEqual(actual["p_value_two_sided"], expected, places=15)
        self.assertEqual(actual["defined_patterns"], len(defined))

    def test_exact_enumeration_count(self):
        result = wild.exact_restricted_rater_wild_test(self.rows(seed=101))
        self.assertEqual(result["enumerated_patterns"], 256)
        self.assertEqual(result["defined_patterns"] + result["undefined_patterns"], 256)

    def test_p_value_bounds_when_defined(self):
        result = wild.exact_restricted_rater_wild_test(self.rows(seed=202))
        if result["defined"]:
            self.assertGreaterEqual(result["p_value_two_sided"], 0.0)
            self.assertLessEqual(result["p_value_two_sided"], 1.0)

    def test_deterministic(self):
        a = wild.exact_restricted_rater_wild_test(self.rows(seed=303))
        b = wild.exact_restricted_rater_wild_test(self.rows(seed=303))
        self.assertEqual(a, b)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            wild._restricted_components([])
        with self.assertRaises(ValueError):
            wild.run_cell(-0.1, 1, 1)
        with self.assertRaises(ValueError):
            wild.run_cell(0.0, 0, 1)


if __name__ == "__main__":
    unittest.main()
