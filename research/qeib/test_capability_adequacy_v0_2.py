#!/usr/bin/env python3
import importlib.util
import json
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "simulate_capability_adequacy_v0_2.py"
SPEC = importlib.util.spec_from_file_location("qeib_v02_sim", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class V02SimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = json.loads(
            (ROOT / "capability_adequacy_v0.2_candidate_grid.json").read_text()
        )

    def test_candidate_grid_expands_to_18_unique_candidates(self):
        rows = MODULE.candidates(self.grid)
        self.assertEqual(len(rows), 18)
        self.assertEqual(len({x["candidate_id"] for x in rows}), 18)

    def test_regime_suite_covers_every_frozen_value(self):
        ids = {r.regime_id for r in MODULE.build_regimes(self.grid)}
        for value in [0.05, 0.10, 0.15, 0.95, 0.98]:
            self.assertIn(f"inadequate_accuracy_{value}", ids)
        self.assertIn("structural_three_domains", ids)
        self.assertIn("structural_invalid_controls", ids)
        self.assertIn("structural_severe_domain_imbalance", ids)
        self.assertIn("inadequate_domain_floor_ceiling_mixture", ids)

    def test_structural_invalidity_fails_closed(self):
        candidate = {
            "candidate_id": "x",
            "family_count": 24,
            "rule_family": "point_threshold",
            "max_domain_accuracy_deviation": 0.30,
        }
        rng = random.Random(1)
        for regime in [
            MODULE.Regime("bad-domains", "structural_invalidity", domains=3),
            MODULE.Regime(
                "bad-controls", "structural_invalidity", controls_valid=False
            ),
        ]:
            obs = MODULE.simulate_observation(regime, 24, rng)
            self.assertFalse(MODULE.evaluate(obs, candidate, self.grid)[1])

    def test_deterministic_reproduction(self):
        first = MODULE.compare(self.grid, replicates=100, seed=123)
        second = MODULE.compare(self.grid, replicates=100, seed=123)
        self.assertEqual(first, second)

    def test_result_is_fail_closed_when_none_qualify(self):
        result = MODULE.compare(self.grid, replicates=100, seed=20260729)
        qualified = [x for x in result["candidates"] if x["qualifies"]]
        expected = qualified[0]["candidate_id"] if qualified else "select_none"
        self.assertEqual(result["selection"], expected)

    def test_no_prohibited_target_fields_are_emitted(self):
        rendered = json.dumps(MODULE.compare(self.grid, replicates=100, seed=7))
        for forbidden in self.grid["prohibited_inputs_for_selection"]:
            self.assertNotIn(forbidden, rendered)


if __name__ == "__main__":
    unittest.main()
