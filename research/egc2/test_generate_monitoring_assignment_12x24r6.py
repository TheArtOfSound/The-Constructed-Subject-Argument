import importlib.util, pathlib, unittest
P=pathlib.Path(__file__).with_name('generate_monitoring_assignment_12x24r6.py')
s=importlib.util.spec_from_file_location('gen',P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
class T(unittest.TestCase):
 def test_valid(self): self.assertEqual(m.generate()['validation_errors'],[])
 def test_budget(self):
  p=m.generate(); self.assertEqual(len(p['items']),96); self.assertEqual(len(p['assignments']),576)
 def test_exact_balance(self):
  p=m.generate()
  for r in p['design']['rater_ids']:
   rows=[x for x in p['assignments'] if x['rater_id']==r]; self.assertEqual(len(rows),48)
   for c in m.CLASSES:
    for d in m.DOMAINS:self.assertEqual(sum(x['item_class']==c and x['domain']==d for x in rows),3)
 def test_concealment(self):
  p=m.generate(); self.assertTrue(all(set(x)=={'position','presentation_id','item_id'} for q in p['rater_queues'].values() for x in q))
 def test_cycles(self):
  p=m.generate()
  for q in p['audit_schedule'].values():
   for i in range(0,48,4):
    self.assertEqual(set(x['item_class'] for x in q[i:i+4]),set(m.CLASSES)); self.assertEqual(set(x['domain'] for x in q[i:i+4]),set(m.DOMAINS))
 def test_dropout(self):
  p=m.generate(); self.assertEqual(p['dropout_audit']['1']['failure_count'],0); self.assertEqual(p['dropout_audit']['2']['failure_count'],0); self.assertEqual(p['dropout_audit']['1']['minimum_remaining_ratings_per_item'],5); self.assertEqual(p['dropout_audit']['2']['minimum_remaining_ratings_per_item'],4)
 def test_determinism(self): self.assertEqual(m.generate()['content_sha256'],m.generate()['content_sha256'])
 def test_tamper_detected(self):
  p=m.generate(); p['assignments'].pop(); self.assertIn('ASSIGNMENT_COUNT',m.validate(p))
if __name__=='__main__':unittest.main()
