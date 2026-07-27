import copy, hashlib, json, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from validate_paired_analysis_input import *

def h(x): return hashlib.sha256(x.encode()).hexdigest()
def rec(pid,c,disp='retain_numeric_score',score=4):
    r={'participant_id':pid,'condition':c,'adequacy_disposition':disp,'retained_score':score if disp=='retain_numeric_score' else None,'source_record_digest_sha256':h(f'source-{pid}-{c}'),'adequacy_decision_digest_sha256':h(f'decision-{pid}-{c}'),'decision_version':'1.0.0','decision_locked_at_utc':'2026-07-27T10:00:00Z'}
    r['record_digest_sha256']=compute_record_digest(r);return r
def ds(records):
    d={'schema_version':SCHEMA_VERSION,'study_id':'pilot-1','analysis_plan_id':'paired-v1','source_export_digest_sha256':h('export'),'condition_order':['A','B'],'locked_for_analysis':True,'analysis_locked_at_utc':'2026-07-27T10:10:00Z','records':records}
    d['analysis_input_digest_sha256']=compute_dataset_digest(d);return d
class T(unittest.TestCase):
    def test_valid(self):
        d=ds([rec('P1','A'),rec('P1','B', 'suppress_numeric_score_reference_inadequate')]);s=validate_analysis_input(d);self.assertTrue(s['analysis_ready']);self.assertEqual(s['suppressed_record_count'],1)
    def test_pairs(self):
        p=build_analysis_pairs(ds([rec('P1','A',score=3),rec('P1','B',score=5)]));self.assertEqual(p['pairs'][0]['condition_b_score'],5.0)
    def test_duplicate(self):
        d=ds([rec('P1','A'),rec('P1','A')]);
        with self.assertRaises(AnalysisInputError):validate_analysis_input(d)
    def test_missing_condition(self):
        d=ds([rec('P1','A')]);
        with self.assertRaises(AnalysisInputError):validate_analysis_input(d)
    def test_score_disposition(self):
        r=rec('P1','A');r['adequacy_disposition']='suppress_numeric_score_reference_inadequate';r['record_digest_sha256']=compute_record_digest(r);d=ds([r,rec('P1','B')])
        with self.assertRaises(AnalysisInputError):validate_analysis_input(d)
    def test_record_tamper_even_redigested_dataset(self):
        d=ds([rec('P1','A'),rec('P1','B')]);d['records'][0]['retained_score']=7;d['analysis_input_digest_sha256']=compute_dataset_digest(d)
        with self.assertRaises(AnalysisInputError):validate_analysis_input(d)
    def test_dataset_digest_tamper(self):
        d=ds([rec('P1','A'),rec('P1','B')]);d['analysis_plan_id']='posthoc'
        with self.assertRaises(AnalysisInputError):validate_analysis_input(d)
    def test_unresolved_blocks_conversion(self):
        d=ds([rec('P1','A','blind_adjudication_required'),rec('P1','B')]);self.assertFalse(validate_analysis_input(d)['analysis_ready'])
        with self.assertRaises(AnalysisInputError):build_analysis_pairs(d)
    def test_source_digest_unique(self):
        a=rec('P1','A');b=rec('P1','B');b['source_record_digest_sha256']=a['source_record_digest_sha256'];b['record_digest_sha256']=compute_record_digest(b);d=ds([a,b])
        with self.assertRaises(AnalysisInputError):validate_analysis_input(d)
    def test_deterministic_order(self):
        a=ds([rec('P2','B'),rec('P1','A'),rec('P2','A'),rec('P1','B')]);b=copy.deepcopy(a);b['records']=list(reversed(b['records']));b['analysis_input_digest_sha256']=compute_dataset_digest(b);self.assertEqual(a['analysis_input_digest_sha256'],b['analysis_input_digest_sha256']);self.assertEqual([x['participant_id'] for x in build_analysis_pairs(b)['pairs']],['P1','P2'])
if __name__=='__main__':unittest.main(verbosity=2)
