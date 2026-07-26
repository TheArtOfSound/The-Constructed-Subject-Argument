import json
import tempfile
import unittest
from pathlib import Path

import calibrate_multiway_bootstrap_resumable as cal


class CalibrationDriverTests(unittest.TestCase):
    def test_seed_is_stable_and_partitioned(self):
        self.assertEqual(cal.stable_seed(7, "a", 1), cal.stable_seed(7, "a", 1))
        self.assertNotEqual(cal.stable_seed(7, "a", 1), cal.stable_seed(7, "a", 2))

    def test_nested_draw_prefixes_are_identical(self):
        design = cal._design("complete_8x18_r8")
        data = cal.sim.simulate(design, "global_stability", 123, **cal.REGIMES["N1"])
        short = cal._draws(data, "pigeonhole_multinomial", 20, 456)
        long = cal._draws(data, "pigeonhole_multinomial", 50, 456)
        self.assertEqual(short, long[:20])

    def test_resume_loads_completed_cell(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "cells.jsonl"
            row = cal.run_cell("complete_8x18_r8", "N1", "item", 2, 20, 7, (10, 20))
            cal.append_jsonl(path, row)
            loaded = cal.load_completed(path)
            self.assertIn(cal.cell_key(row), loaded)
            self.assertEqual(loaded[cal.cell_key(row)], json.loads(json.dumps(row)))

    def test_conflicting_duplicate_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "cells.jsonl"
            row = cal.run_cell("complete_8x18_r8", "N1", "item", 1, 10, 7, (10,))
            cal.append_jsonl(path, row)
            changed = json.loads(json.dumps(row))
            changed["runtime_seconds"] += 1
            cal.append_jsonl(path, changed)
            with self.assertRaises(ValueError):
                cal.load_completed(path)

    def test_cell_is_deterministic_except_runtime(self):
        first = cal.run_cell("complete_8x18_r8", "N1", "rater", 3, 20, 99, (10, 20))
        second = cal.run_cell("complete_8x18_r8", "N1", "rater", 3, 20, 99, (10, 20))
        first.pop("runtime_seconds")
        second.pop("runtime_seconds")
        self.assertEqual(first, second)

    def test_clopper_pearson_boundaries(self):
        lo, hi = cal.clopper_pearson(0, 100)
        self.assertEqual(lo, 0.0)
        self.assertGreater(hi, 0.0)
        lo, hi = cal.clopper_pearson(100, 100)
        self.assertLess(lo, 1.0)
        self.assertEqual(hi, 1.0)


if __name__ == "__main__":
    unittest.main()
