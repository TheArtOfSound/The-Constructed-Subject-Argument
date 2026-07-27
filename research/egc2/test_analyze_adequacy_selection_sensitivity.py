import unittest
from analyze_adequacy_selection_sensitivity import *
class T(unittest.TestCase):
 def test1(self):
  a=ConditionSummary("a",10,0,40); b=ConditionSummary("b",10,0,50); r=contrast_bounds(a,b); self.assertEqual((r["worst_case_lower"],r["worst_case_upper"]),(1,1))
 def test2(self):
  a=ConditionSummary("a",8,2,32); b=ConditionSummary("b",9,1,45); r=contrast_bounds(a,b); self.assertAlmostEqual(r["worst_case_lower"],0); self.assertAlmostEqual(r["worst_case_upper"],1.8)
 def test3(self):
  a=ConditionSummary("a",5,5,20); b=ConditionSummary("b",5,5,25); self.assertEqual(contrast_bounds(a,b)["sign_status"],"sign_not_robust")
 def test4(self):
  a=ConditionSummary("a",8,2,32); b=ConditionSummary("b",9,1,45); r=gamma_sensitivity(a,b,[0])[0]; self.assertAlmostEqual(r["contrast_lower"],1); self.assertAlmostEqual(r["contrast_upper"],1)
 def test5(self):
  a=ConditionSummary("a",8,2,32); b=ConditionSummary("b",9,1,45); rows=gamma_sensitivity(a,b,[0,.5,1,2]); widths=[x["contrast_upper"]-x["contrast_lower"] for x in rows]; self.assertEqual(widths,sorted(widths))
 def test6(self):
  a=ConditionSummary("a",8,2,32); b=ConditionSummary("b",6,4,30); self.assertAlmostEqual(analyze(a,b,gammas=[0,1])["retention_rate_difference_b_minus_a"],-.2)
 def test7(self):
  a=ConditionSummary("a",8,2,32); b=ConditionSummary("b",9,1,45); self.assertEqual(analyze(a,b,gammas=[0,1])["analysis_digest_sha256"],analyze(a,b,gammas=[0,1])["analysis_digest_sha256"])
 def test8(self):
  with self.assertRaises(SensitivityInputError): condition_mean_bounds(ConditionSummary("a",2,0,15))
 def test9(self):
  a=ConditionSummary("a",8,2,32); b=ConditionSummary("b",9,1,45)
  with self.assertRaises(SensitivityInputError): gamma_sensitivity(a,b,[1,.5])
 def test10(self):
  a=ConditionSummary("x",8,2,32); b=ConditionSummary("x",9,1,45)
  with self.assertRaises(SensitivityInputError): contrast_bounds(a,b)
if __name__=="__main__": unittest.main(verbosity=2)
