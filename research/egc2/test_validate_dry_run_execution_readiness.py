import copy
import json
import unittest
from pathlib import Path

from validate_dry_run_execution_readiness import canonical_digest, validate_record

BASE = json.loads(
    (Path(__file__).parent / "expert_reviewer_dry_run_execution_readiness.v0.1.json").read_text(encoding="utf-8")
)


def redigest(record):
    record["record_digest_sha256"] = canonical_digest(record)
    return record


class ReadinessConsistencyTests(unittest.TestCase):
    def test_committed_blocked_record_passes(self):
        report = validate_record(BASE)
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["status"], "passed_readiness_consistency")
        self.assertFalse(report["derived_state"]["prerequisites_complete"])

    def test_tampering_without_redigest_fails(self):
        record = copy.deepcopy(BASE)
        record["execution_allowed"] = True
        report = validate_record(record)
        self.assertIn("record_digest_mismatch", {e["code"] for e in report["errors"]})

    def test_redigested_false_unlock_fails(self):
        record = copy.deepcopy(BASE)
        record["execution_allowed"] = True
        record["status"] = "ready"
        record["current_blockers"] = []
        redigest(record)
        report = validate_record(record)
        codes = {e["code"] for e in report["errors"]}
        self.assertIn("execution_allowed_without_prerequisites", codes)
        self.assertIn("execution_allowed_without_independent_review", codes)

    def test_verified_gate_requires_evidence(self):
        record = copy.deepcopy(BASE)
        record["preflight_gates"][0]["status"] = "verified"
        redigest(record)
        report = validate_record(record)
        self.assertIn("verified_gate_without_evidence", {e["code"] for e in report["errors"]})

    def test_verified_operator_gate_cannot_contradict_assignment(self):
        record = copy.deepcopy(BASE)
        record["preflight_gates"][0].update(status="verified", evidence=["evidence/operator.json"])
        redigest(record)
        report = validate_record(record)
        self.assertIn("verified_gate_contradicts_record", {e["code"] for e in report["errors"]})

    def test_duplicate_gate_fails(self):
        record = copy.deepcopy(BASE)
        record["preflight_gates"][-1] = copy.deepcopy(record["preflight_gates"][0])
        redigest(record)
        report = validate_record(record)
        self.assertIn("duplicate_preflight_gate", {e["code"] for e in report["errors"]})

    def test_unaccepted_operator_cannot_have_acceptance_data(self):
        record = copy.deepcopy(BASE)
        record["operator_assignment"]["operator_pseudonym"] = "operator-001"
        redigest(record)
        report = validate_record(record)
        self.assertIn("unaccepted_operator_has_acceptance_data", {e["code"] for e in report["errors"]})

    def test_independent_expected_head_blocks_substitution(self):
        report = validate_record(BASE, expected_repository_head="0" * 40)
        self.assertIn("repository_head_mismatch", {e["code"] for e in report["errors"]})

    def test_report_digest_is_deterministic(self):
        one = validate_record(BASE)
        two = validate_record(BASE)
        self.assertEqual(one["validation_report_digest_sha256"], two["validation_report_digest_sha256"])

    def test_complete_ready_fixture_passes(self):
        record = copy.deepcopy(BASE)
        record["status"] = "ready"
        record["execution_allowed"] = True
        record["operator_assignment"].update(
            operator_pseudonym="operator-001",
            acceptance_status="accepted",
            accepted_at_utc="2026-07-28T18:00:00Z",
        )
        for role in record["ownership_assignments"]:
            record["ownership_assignments"][role] = f"{role}-001"
        for key in record["resource_inventory"]:
            if key == "kms_key_aliases":
                record["resource_inventory"][key] = ["alias/synthetic-a", "alias/synthetic-b"]
            elif key == "resource_creation_evidence_paths":
                record["resource_inventory"][key] = ["evidence/resources.json"]
            else:
                record["resource_inventory"][key] = f"synthetic-{key}"
        for gate in record["preflight_gates"]:
            gate["status"] = "verified"
            gate["evidence"] = [f"evidence/{gate['id'].lower()}.json"]
        record["independent_review"] = {
            "status": "verified",
            "reviewer_pseudonym": "reviewer-001",
            "reviewed_at_utc": "2026-07-28T18:30:00Z",
            "evidence": ["evidence/independent-review.json"],
        }
        record["current_blockers"] = []
        redigest(record)
        report = validate_record(record)
        self.assertTrue(report["valid"], report["errors"])
        self.assertTrue(report["derived_state"]["prerequisites_complete"])


if __name__ == "__main__":
    unittest.main()
