import unittest
from validate_paired_analysis_run_manifest import compute_manifest_digest, validate_manifest, RunManifestError

def fixture():
    m={"schema_version":"egc2-paired-analysis-run-manifest-0.1.0","status":"preregistered_not_run","run_id":"egc2-paired-primary-v0.1.0","study_id":"egc2-rater-pilot","analysis_plan_id":"egc2-paired-plan-v0.1.0","expected_input_digest_sha256":"a"*64,"gamma_grid":[0.0,0.5,1.0,2.0,3.0,6.0],"software":{"repository_commit_sha":"b"*40,"python_version":"3.12.4","entrypoint_schema":"egc2-lineage-checked-paired-sensitivity-0.1.0","entrypoint_path":"research/egc2/analyze_lineage_checked_paired_sensitivity.py"},"output":{"report_path":"research/egc2/results/egc2-paired-primary-v0.1.0.json","overwrite_existing":False},"permitted_failure_statuses":["input_digest_mismatch","input_lineage_invalid","unresolved_adequacy_decision","participant_count_mismatch","record_count_mismatch","gamma_grid_mismatch","software_commit_mismatch","python_version_mismatch","entrypoint_schema_mismatch","output_path_mismatch","analysis_engine_failure","report_digest_failure"],"preregistration_lock":{"locked_before_input_access":True,"parameters_mutable_after_lock":False,"locked_at_utc":"2026-07-27T13:00:00Z","locked_by":"GPT-5.6 Thinking"}}
    m["manifest_digest_sha256"]=compute_manifest_digest(m); return m

class Tests(unittest.TestCase):
    def test_valid(self): self.assertTrue(validate_manifest(fixture())["valid"])
    def test_expected_digest(self):
        m=fixture(); self.assertTrue(validate_manifest(m,expected_manifest_digest=m["manifest_digest_sha256"])["valid"])
    def test_redigested_gamma_drift_rejected_by_external_commitment(self):
        m=fixture(); expected=m["manifest_digest_sha256"]; m["gamma_grid"]=[0.0,1.0,6.0]; m["manifest_digest_sha256"]=compute_manifest_digest(m)
        with self.assertRaises(RunManifestError): validate_manifest(m,expected_manifest_digest=expected)
    def test_duplicate_gamma_rejected(self):
        m=fixture(); m["gamma_grid"]=[0,1,1,6]; m["manifest_digest_sha256"]=compute_manifest_digest(m)
        with self.assertRaises(RunManifestError): validate_manifest(m)
    def test_missing_extremes_rejected(self):
        m=fixture(); m["gamma_grid"]=[0,1,2]; m["manifest_digest_sha256"]=compute_manifest_digest(m)
        with self.assertRaises(RunManifestError): validate_manifest(m)
    def test_commit_mismatch_rejected(self):
        m=fixture(); m["software"]["repository_commit_sha"]="bad"; m["manifest_digest_sha256"]=compute_manifest_digest(m)
        with self.assertRaises(RunManifestError): validate_manifest(m)
    def test_output_traversal_rejected(self):
        m=fixture(); m["output"]["report_path"]="research/egc2/results/../x.json"; m["manifest_digest_sha256"]=compute_manifest_digest(m)
        with self.assertRaises(RunManifestError): validate_manifest(m)
    def test_overwrite_rejected(self):
        m=fixture(); m["output"]["overwrite_existing"]=True; m["manifest_digest_sha256"]=compute_manifest_digest(m)
        with self.assertRaises(RunManifestError): validate_manifest(m)
    def test_unknown_failure_rejected(self):
        m=fixture(); m["permitted_failure_statuses"].append("silently_continue"); m["manifest_digest_sha256"]=compute_manifest_digest(m)
        with self.assertRaises(RunManifestError): validate_manifest(m)
    def test_unlockable_parameters_rejected(self):
        m=fixture(); m["preregistration_lock"]["parameters_mutable_after_lock"]=True; m["manifest_digest_sha256"]=compute_manifest_digest(m)
        with self.assertRaises(RunManifestError): validate_manifest(m)

if __name__=='__main__': unittest.main(verbosity=2)