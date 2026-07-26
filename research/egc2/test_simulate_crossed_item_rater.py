import unittest
from research.egc2 import simulate_crossed_item_rater as m

class CrossedSimulationTests(unittest.TestCase):
    def test_fixed_budgets(self):
        self.assertTrue(all(d.planned_ratings == 576 for d in m.DESIGNS))

    def test_counts_without_dropout(self):
        for d in m.DESIGNS:
            self.assertEqual(len(m.simulate(d,"global_stability",1)["rows"]),576)

    def test_deterministic(self):
        d=m.DESIGNS[0]
        self.assertEqual(m.simulate(d,"false_reassurance",9),m.simulate(d,"false_reassurance",9))

    def test_truths(self):
        self.assertTrue(all(v==0 for v in m.TRUTH["global_stability"].values()))
        t=m.TRUTH["false_reassurance"]
        self.assertGreater(t["exact_anchor"],0)
        self.assertLess(t["novel"],0)
        self.assertLess(t["structural_transfer"],0)

    def test_ordinal_clipping(self):
        x=m.simulate(m.DESIGNS[0],"false_reassurance",2,ceiling_limited=True)
        self.assertTrue(all(1<=r["early"]<=7 and 1<=r["late"]<=7 for r in x["rows"]))

    def test_dropout_reduces_or_preserves_rows(self):
        d=m.DESIGNS[1]
        self.assertLessEqual(len(m.simulate(d,"global_stability",3,dropout="severity")["rows"]),576)

    def test_generalization_metrics_exist(self):
        e=m.estimate(m.simulate(m.DESIGNS[2],"false_reassurance",4))
        self.assertIn("item_population_error",e)
        self.assertIn("heldout_domain_gap",e)
        self.assertIn("leave_one_domain_out",e)

    def test_cluster_bootstrap_is_deterministic(self):
        x=m.simulate(m.DESIGNS[1],"false_reassurance",5)
        self.assertEqual(m.cluster_bootstrap_intervals(x,25,9),m.cluster_bootstrap_intervals(x,25,9))

    def test_cluster_bootstrap_axes_differ(self):
        x=m.simulate(m.DESIGNS[1],"false_reassurance",5,item_sd=1.0)
        b=m.cluster_bootstrap_intervals(x,100,9)
        self.assertNotEqual(b["item"]["ci95"],b["rater"]["ci95"])

    def test_lodo_reports_all_domains(self):
        x=m.leave_one_domain_out(m.simulate(m.DESIGNS[0],"false_reassurance",6))
        self.assertEqual(set(x["omitted_domain_contrasts"]),set(m.DOMAINS))
        self.assertGreaterEqual(x["range"],0)

    def test_bootstrap_diagnostic_shape(self):
        x=m.run_bootstrap_diagnostic(2,10,10)
        self.assertEqual(len(x["cells"]),len(m.DESIGNS)*2)
        self.assertTrue(all("item_bootstrap_coverage" in c for c in x["cells"]))

    def test_grid_shape(self):
        self.assertEqual(len(m.run_grid(2,10)["cells"]),5*2*2*2)

if __name__=="__main__": unittest.main()
