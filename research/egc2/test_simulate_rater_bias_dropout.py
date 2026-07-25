import importlib.util
import pathlib
import unittest

P = pathlib.Path(__file__).with_name("simulate_rater_bias_dropout.py")
S = importlib.util.spec_from_file_location("sim", P)
M = importlib.util.module_from_spec(S)
S.loader.exec_module(M)


class SimulatorTests(unittest.TestCase):
    def test_assignment_is_balanced(self):
        rows = M.balanced_assignments(7)
        self.assertEqual(len(rows), 240)
        for rater in {x["rater_id"] for x in rows}:
            ratings = [x for x in rows if x["rater_id"] == rater]
            self.assertEqual(sum(x["condition"] == "private" for x in ratings), 15)
            self.assertEqual(sum(x["condition"] == "evaluated" for x in ratings), 15)

    def test_no_rater_sees_both_responses(self):
        rows = M.balanced_assignments(7)
        seen = {}
        for row in rows:
            seen.setdefault((row["participant_id"], row["rater_id"]), set()).add(row["condition"])
        self.assertTrue(all(len(values) == 1 for values in seen.values()))

    def test_true_zero_generation_has_no_structural_condition_shift(self):
        rows, _ = M.generate_trial(99, severity_sd=0, interaction_sd=0, fatigue_slope=0)
        self.assertLess(abs(M.naive_effect(rows)), 0.75)

    def test_severe_dropout_removes_correct_rater(self):
        rows, severity = M.generate_trial(2)
        kept, dropped = M.apply_dropout(rows, severity, "most_severe", 2)
        self.assertEqual(dropped, [max(severity, key=severity.get)])
        self.assertNotIn(dropped[0], {x["rater_id"] for x in kept})

    def test_compact_run_is_deterministic(self):
        first = M.compact_run(10, 123, 50)
        second = M.compact_run(10, 123, 50)
        for payload in (first, second):
            payload.pop("runtime_seconds")
            payload.pop("content_sha256")
        self.assertEqual(first, second)

    def test_rater_centering_removes_constant_rater_offset(self):
        rows = M.balanced_assignments(1)
        for row in rows:
            row["score"] = 5 if row["rater_id"] == "R01" else 3
        self.assertAlmostEqual(M.rater_centered_effect(rows), 0)

    def test_partial_dropout_preserves_some_ratings(self):
        rows, severity = M.generate_trial(3)
        kept, _ = M.apply_dropout(rows, severity, "late_severity", 3)
        self.assertGreater(len(kept), 0)
        self.assertLess(len(kept), len(rows))


if __name__ == "__main__":
    unittest.main()
