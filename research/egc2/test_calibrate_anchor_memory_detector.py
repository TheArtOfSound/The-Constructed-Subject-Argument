#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import unittest

MODULE_PATH=Path(__file__).with_name("calibrate_anchor_memory_detector.py")
spec=importlib.util.spec_from_file_location("calibration",MODULE_PATH)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)

class DetectorCalibrationTests(unittest.TestCase):
    def test_percentile_endpoints(self):
        self.assertEqual(mod.percentile([1,2,3],0),1)
        self.assertEqual(mod.percentile([1,2,3],1),3)

    def test_bootstrap_is_deterministic(self):
        rows=mod.anchor.generate_trial(7,"generalized_learning",items_per_class=8)
        self.assertEqual(mod.cluster_bootstrap_ci(rows,"novel",60,99),mod.cluster_bootstrap_ci(rows,"novel",60,99))

    def test_clear_adversarial_case_supported(self):
        rows=mod.anchor.generate_trial(9,"memorization_plus_novel_drift",items_per_class=36,learning_gain=1.1,novel_drift=1.2,noise_sd=.15)
        result=mod.classify_trial(rows,.2,100,123)
        self.assertEqual(result["status"],"supported")

    def test_generalized_learning_not_false_reassurance(self):
        rows=mod.anchor.generate_trial(11,"generalized_learning",items_per_class=36,learning_gain=.9,novel_drift=.7,noise_sd=.15)
        result=mod.classify_trial(rows,.2,100,456)
        self.assertNotEqual(result["status"],"supported")

    def test_cell_deterministic(self):
        scenario=mod.DEFAULT_SCENARIOS[0]
        a=mod.run_cell("pure_memorization",scenario,.35,20,50,123)
        b=mod.run_cell("pure_memorization",scenario,.35,20,50,123)
        self.assertEqual(a,b)

    def test_grid_contains_floor_and_ceiling(self):
        ids={x["scenario_id"] for x in mod.DEFAULT_SCENARIOS}
        self.assertIn("floor_limited",ids); self.assertIn("ceiling_limited",ids)

if __name__=="__main__": unittest.main()
