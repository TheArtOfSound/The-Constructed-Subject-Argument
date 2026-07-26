import unittest
import compare_monitoring_workload as m


class WorkloadComparisonTests(unittest.TestCase):
    def test_unknown_design_fails(self):
        with self.assertRaises(ValueError):
            m.generate_trial(1, "bad", "reference")

    def test_design_workloads(self):
        for name, d in m.DESIGNS.items():
            rows = m.generate_trial(2, name, "null_generalized_learning")
            self.assertLessEqual(len(rows), d["raters"] * d["items_per_rater_per_class"] * 4)
            self.assertGreater(len(rows), 0)

    def test_deterministic(self):
        self.assertEqual(
            m.generate_trial(3, "complete_8x18", "reference"),
            m.generate_trial(3, "complete_8x18", "reference"),
        )

    def test_adversarial_signal_direction(self):
        summary = m.summarize(m.generate_trial(4, "incomplete_12x36", "reference"), 0.2)
        self.assertGreater(summary["shifts"]["exact_anchor"], summary["shifts"]["novel"])

    def test_null_not_systematically_false_reassuring(self):
        cell = m.run_cell("incomplete_12x36", "null_generalized_learning", 40, 5, 0.2)
        self.assertLess(cell["support_rate"], 0.20)

    def test_informative_dropout_reduces_completion(self):
        reference = m.run_cell("incomplete_12x36", "reference", 30, 6, 0.2)
        dropout = m.run_cell("incomplete_12x36", "informative_dropout", 30, 6, 0.2)
        self.assertLess(dropout["mean_completed_ratings"], reference["mean_completed_ratings"])


if __name__ == "__main__":
    unittest.main()
