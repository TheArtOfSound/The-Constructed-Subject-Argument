#!/usr/bin/env python3
"""Regression tests for the QEIB small-sample calibration harness."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


QEIB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(QEIB_DIR))

spec = importlib.util.spec_from_file_location(
    "calibrate_qeib_inference", QEIB_DIR / "calibrate_qeib_inference.py"
)
assert spec and spec.loader
calibration = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = calibration
spec.loader.exec_module(calibration)


class SyntheticRecordGenerationTest(unittest.TestCase):
    def test_sharp_null_pairs_are_identical(self) -> None:
        records, truth = calibration.generate_records(
            scenario="sharp_null",
            n_families=12,
            baseline_accuracy=0.5,
            effect_size=0.2,
            replicates=3,
            seed=101,
        )
        paired = {}
        for record in records:
            key = (record["task_family_id"], record["replicate"])
            paired.setdefault(key, {})[record["context_id"]] = record["grader_outputs"]["score"]
        self.assertEqual(0.0, truth)
        self.assertTrue(paired)
        self.assertTrue(
            all(values["neutral"] == values["eval_explicit"] for values in paired.values())
        )

    def test_mean_zero_heterogeneous_truth_is_zero(self) -> None:
        _records, truth = calibration.generate_records(
            scenario="mean_zero_heterogeneous",
            n_families=12,
            baseline_accuracy=0.5,
            effect_size=0.2,
            replicates=1,
            seed=202,
        )
        self.assertAlmostEqual(0.0, truth, places=12)

    def test_probability_clipping_is_reflected_in_truth(self) -> None:
        _records, truth = calibration.generate_records(
            scenario="constant_effect",
            n_families=6,
            baseline_accuracy=0.95,
            effect_size=0.20,
            replicates=1,
            seed=303,
        )
        self.assertAlmostEqual(0.05, truth, places=12)


class ProductionEstimatorIntegrationTest(unittest.TestCase):
    def test_sharp_null_is_exactly_zero_and_equivalent(self) -> None:
        cell = calibration.run_cell(
            scenario="sharp_null",
            n_families=12,
            baseline_accuracy=0.5,
            effect_size=0.2,
            replicates=3,
            trials=4,
            equivalence_margin=0.10,
            bootstrap_samples=200,
            seed=404,
        )
        self.assertEqual(1.0, cell.coverage_95)
        self.assertEqual(0.0, cell.false_or_true_detection_rate)
        self.assertEqual(1.0, cell.formal_equivalence_rate)
        self.assertEqual(0.0, cell.mean_estimated_delta)
        self.assertEqual(1.0, cell.degenerate_ci_rate)

    def test_grid_is_deterministic(self) -> None:
        kwargs = dict(
            family_counts=(6,),
            baselines=(0.5,),
            scenarios=("constant_effect",),
            effect_size=0.2,
            replicates=2,
            trials=5,
            equivalence_margin=0.10,
            bootstrap_samples=200,
            seed=505,
        )
        first = calibration.run_grid(**kwargs)
        second = calibration.run_grid(**kwargs)
        self.assertEqual(first, second)

    def test_replicates_do_not_change_family_count(self) -> None:
        records_one, _ = calibration.generate_records(
            scenario="constant_effect",
            n_families=6,
            baseline_accuracy=0.5,
            effect_size=0.2,
            replicates=1,
            seed=606,
        )
        records_ten, _ = calibration.generate_records(
            scenario="constant_effect",
            n_families=6,
            baseline_accuracy=0.5,
            effect_size=0.2,
            replicates=10,
            seed=606,
        )
        infer = calibration.family_level_inference
        one = infer(
            records_one,
            contexts=["neutral", "eval_explicit"],
            equivalence_margin=0.10,
            bootstrap_samples=200,
            seed=607,
        )
        ten = infer(
            records_ten,
            contexts=["neutral", "eval_explicit"],
            equivalence_margin=0.10,
            bootstrap_samples=200,
            seed=607,
        )
        self.assertEqual(6, one["contexts"]["eval_explicit"]["n_families"])
        self.assertEqual(6, ten["contexts"]["eval_explicit"]["n_families"])


if __name__ == "__main__":
    unittest.main()
