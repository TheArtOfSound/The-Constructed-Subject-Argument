import json
import unittest
from pathlib import Path

from evaluate_structural_validity import apply_dropout, evaluate

SPEC = json.loads((Path(__file__).parent / "structural_validity_gates.v0.1.json").read_text())
CLASSES = ("exact_anchor", "surface_variant", "structural_transfer", "novel")
DOMAINS = ("autobiographical", "conceptual", "position", "heldout")


def planned_rows():
    rows=[]
    for ci,c in enumerate(CLASSES):
        for i in range(24):
            d=DOMAINS[i%4]
            item=f"{c}:{i}"
            start=((ci*24+i)*5)%12
            for j in range(6):
                r=(start+j)%12
                rows.append({"item":item,"rater":r,"class":c,"domain":d,"early":4.0,"late":4.0})
    return rows


class StructuralGateTests(unittest.TestCase):
    def setUp(self):
        self.rows=planned_rows()

    def ev(self, rows, var=0.2, undefined=0.0):
        return evaluate(rows,SPEC,observed_variance=var,undefined_pattern_fraction=undefined,planned_rows=self.rows)

    def test_complete_design_passes_all_gates(self):
        result=self.ev(self.rows)
        self.assertEqual(result["status"],"structurally_valid_inference_defined")
        self.assertTrue(all(g["passed"] for g in result["gates"]))

    def test_g0_duplicate_and_unknown_fail(self):
        rows=self.rows+[dict(self.rows[0])]
        rows.append({"item":"unknown","rater":99,"class":"novel","domain":"heldout"})
        self.assertIn("G0_SCHEMA_IDENTITY",self.ev(rows)["failed_gate_ids"])

    def test_g1_item_replication_fails(self):
        target=self.rows[0]["item"]
        rows=[r for r in self.rows if r["item"]!=target or r["rater"] in {0,1,2}]
        self.assertIn("G1_ITEM_REPLICATION",self.ev(rows)["failed_gate_ids"])

    def test_g2_whole_rater_loss_fails_at_three(self):
        rows=[r for r in self.rows if r["rater"] not in {0,1,2}]
        self.assertIn("G2_ACTIVE_RATER_COVERAGE",self.ev(rows)["failed_gate_ids"])

    def test_g3_class_balance_fails(self):
        rows=[r for i,r in enumerate(self.rows) if not (r["class"]=="novel" and i%3==0)]
        self.assertIn("G3_CLASS_BALANCE",self.ev(rows)["failed_gate_ids"])

    def test_g4_domain_balance_fails(self):
        rows=[r for i,r in enumerate(self.rows) if not (r["domain"]=="heldout" and i%2==0)]
        self.assertIn("G4_DOMAIN_BALANCE",self.ev(rows)["failed_gate_ids"])

    def test_g5_disconnected_class_graph_fails(self):
        rows=[]
        for r in self.rows:
            if r["class"]!="novel": rows.append(r)
            elif (int(r["item"].split(':')[1])<12 and r["rater"]<6) or (int(r["item"].split(':')[1])>=12 and r["rater"]>=6):
                rows.append(r)
        self.assertIn("G5_GRAPH_IDENTIFIABILITY",self.ev(rows)["failed_gate_ids"])

    def test_g6_noncomputable_has_distinct_status(self):
        result=self.ev(self.rows,var=-1.0,undefined=0.2)
        self.assertEqual(result["status"],"indeterminate_due_to_inferential_noncomputability")
        self.assertFalse(result["report_confirmatory_p_value"])

    def test_structural_failure_precedes_g6(self):
        rows=[r for r in self.rows if r["rater"] not in {0,1,2}]
        result=self.ev(rows,var=-1.0,undefined=0.2)
        self.assertEqual(result["status"],"indeterminate_due_to_structural_invalidity")

    def test_dropout_is_deterministic(self):
        a=apply_dropout(self.rows,"domain_row",seed=7,domain="heldout",fraction=.30)
        b=apply_dropout(self.rows,"domain_row",seed=7,domain="heldout",fraction=.30)
        self.assertEqual(a,b)

    def test_two_whole_rater_losses_preserve_active_gate_but_fail_replication_95pct(self):
        dropped=apply_dropout(self.rows,"random_whole_rater",seed=1,rater_count=2)
        result=self.ev(dropped["rows"])
        g2=next(g for g in result["gates"] if g["id"]=="G2_ACTIVE_RATER_COVERAGE")
        self.assertTrue(g2["passed"])
        self.assertIn("G1_ITEM_REPLICATION",result["failed_gate_ids"])

    def test_combined_attack_records_removed_raters(self):
        scores={str(i):float(i) for i in range(12)}
        out=apply_dropout(self.rows,"combined_attack",seed=5,domain="heldout",fraction=.5,rater_scores=scores,rater_count=2)
        self.assertEqual(out["removed_raters"],["11","10"])
        self.assertLess(out["retained_rows"],len(self.rows))


if __name__=='__main__': unittest.main()
