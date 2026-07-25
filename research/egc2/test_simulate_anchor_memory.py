#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import unittest

MODULE_PATH=Path(__file__).with_name("simulate_anchor_memory.py")
spec=importlib.util.spec_from_file_location("anchor_memory",MODULE_PATH)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)

class AnchorMemorySimulatorTests(unittest.TestCase):
    def test_unknown_regime_rejected(self):
        with self.assertRaises(ValueError): mod.class_effect("unknown","novel",1,.6,.7)

    def test_generalized_learning_transfers_to_all_classes(self):
        effects=[mod.class_effect("generalized_learning",c,1,.6,.7) for c in mod.ITEM_CLASSES]
        self.assertTrue(all(abs(x-.6)<1e-12 for x in effects))

    def test_pure_memorization_changes_exact_only(self):
        self.assertEqual(mod.class_effect("pure_memorization","exact_anchor",1,.6,.7),.6)
        self.assertTrue(all(mod.class_effect("pure_memorization",c,1,.6,.7)==0 for c in mod.ITEM_CLASSES if c!="exact_anchor"))

    def test_novel_drift_regime_has_opposing_signs(self):
        self.assertGreater(mod.class_effect("memorization_plus_novel_drift","exact_anchor",1,.6,.7),0)
        self.assertLess(mod.class_effect("memorization_plus_novel_drift","novel",1,.6,.7),0)

    def test_deterministic_fixed_seed(self):
        a=mod.compact_run(20,123); b=mod.compact_run(20,123)
        a.pop("runtime_seconds"); a.pop("content_sha256")
        b.pop("runtime_seconds"); b.pop("content_sha256")
        self.assertEqual(a,b)

    def test_false_reassurance_discriminates_adversarial_regime(self):
        result={x["regime"]:x for x in mod.compact_run(100,20260725)["results"]}
        self.assertLess(result["generalized_learning"]["false_reassurance_rate"],.10)
        self.assertGreater(result["memorization_plus_novel_drift"]["false_reassurance_rate"],.50)

    def test_baseline_score_is_validated(self):
        with self.assertRaises(ValueError): mod.generate_trial(1,"generalized_learning",baseline_score=.9)
        with self.assertRaises(ValueError): mod.generate_trial(1,"generalized_learning",baseline_score=7.1)

    def test_floor_and_ceiling_regimes_remain_bounded(self):
        for baseline in (1.2,6.8):
            rows=mod.generate_trial(2,"memorization_plus_novel_drift",baseline_score=baseline)
            self.assertTrue(all(1 <= row["score"] <= 7 for row in rows))

if __name__=="__main__": unittest.main()
