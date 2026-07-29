#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name(
    "simulate_capability_adequacy_operating_characteristics.py"
)
spec = importlib.util.spec_from_file_location("adequacy_oc", MODULE_PATH)
assert spec and spec.loader
oc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oc)

POLICY = Path(__file__).with_name("capability_adequacy_policy.v0.1.json")


class OperatingCharacteristicTests(unittest.TestCase):
    def test_deterministic_output(self) -> None:
        first = oc.run_simulation(POLICY, 200, 20260729)
        second = oc.run_simulation(POLICY, 200, 20260729)
        self.assertEqual(first, second)

    def test_rejects_too_few_replicates(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least 100"):
            oc.run_simulation(POLICY, 99, 1)

    def test_obvious_invalid_regimes_do_not_pass(self) -> None:
        result = oc.run_simulation(POLICY, 300, 20260729)
        by_id = {item["regime"]["regime_id"]: item for item in result["regimes"]}
        self.assertEqual(by_id["small_n_8"]["gate_pass_count"], 0)
        self.assertEqual(by_id["narrow_domain_24"]["gate_pass_count"], 0)
        self.assertEqual(by_id["invalid_controls"]["gate_pass_count"], 0)

    def test_midrange_regime_passes_more_often_than_floor(self) -> None:
        result = oc.run_simulation(POLICY, 500, 20260729)
        by_id = {item["regime"]["regime_id"]: item for item in result["regimes"]}
        self.assertGreater(
            by_id["adequate_mid_24"]["gate_pass_rate"],
            by_id["floor_10pct"]["gate_pass_rate"],
        )

    def test_boundary_uncertainty_is_preserved(self) -> None:
        result = oc.run_simulation(POLICY, 500, 20260729)
        by_id = {item["regime"]["regime_id"]: item for item in result["regimes"]}
        self.assertGreater(by_id["floor_boundary_20pct"]["false_inadequacy_rate"], 0.0)
        self.assertGreater(by_id["ceiling_boundary_90pct"]["false_inadequacy_rate"], 0.0)

    def test_policy_digest_and_claim_boundary_present(self) -> None:
        result = oc.run_simulation(POLICY, 100, 20260729)
        self.assertEqual(len(result["policy_sha256"]), 64)
        boundary = " ".join(result["interpretation_boundary"]).lower()
        self.assertIn("not scientific ground truth", boundary)
        self.assertIn("consciousness", boundary)


if __name__ == "__main__":
    unittest.main()
