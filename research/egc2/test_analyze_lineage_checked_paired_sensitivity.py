#!/usr/bin/env python3
from __future__ import annotations

import platform
import unittest
from copy import deepcopy

from analyze_lineage_checked_paired_sensitivity import (
    OUTPUT_SCHEMA,
    RunContractViolation,
    execute_preregistered_run,
    validate_runtime_contract,
)
from validate_paired_analysis_input import compute_dataset_digest, compute_record_digest
from validate_paired_analysis_run_manifest import compute_manifest_digest


def _hex(char: str) -> str:
    return char * 64


def _record(participant_id, condition, disposition, score, index):
    row = {
        "participant_id": participant_id,
        "condition": condition,
        "adequacy_disposition": disposition,
        "retained_score": score,
        "source_record_digest_sha256": _hex(str(index % 10)),
        "adequacy_decision_digest_sha256": _hex(str((index + 1) % 10)),
        "decision_version": "0.1.0",
        "decision_locked_at_utc": "2026-07-27T11:00:00Z",
    }
    row["record_digest_sha256"] = compute_record_digest(row)
    return row


def _dataset():
    dataset = {
        "schema_version": "egc2-paired-analysis-input-0.1.0",
        "study_id": "synthetic-lineage-test",
        "analysis_plan_id": "paired-sensitivity-v0.1",
        "source_export_digest_sha256": _hex("a"),
        "condition_order": ["A", "B"],
        "locked_for_analysis": True,
        "analysis_locked_at_utc": "2026-07-27T11:01:00Z",
        "records": [
            _record("P1", "A", "retain_numeric_score", 4, 1),
            _record("P1", "B", "retain_numeric_score", 6, 2),
            _record("P2", "A", "retain_numeric_score", 5, 3),
            _record(
                "P2",
                "B",
                "suppress_numeric_score_reference_inadequate",
                None,
                4,
            ),
        ],
    }
    dataset["analysis_input_digest_sha256"] = compute_dataset_digest(dataset)
    return dataset


def _run_manifest(dataset):
    manifest = {
        "schema_version": "egc2-paired-analysis-run-manifest-0.1.0",
        "status": "preregistered_not_run",
        "run_id": "synthetic-run-001",
        "study_id": dataset["study_id"],
        "analysis_plan_id": dataset["analysis_plan_id"],
        "expected_input_digest_sha256": dataset["analysis_input_digest_sha256"],
        "gamma_grid": [0.0, 0.5, 1.0, 2.0, 3.0, 6.0],
        "software": {
            "repository_commit_sha": "b" * 40,
            "python_version": platform.python_version(),
            "entrypoint_schema": OUTPUT_SCHEMA,
            "entrypoint_path": "research/egc2/analyze_lineage_checked_paired_sensitivity.py",
        },
        "output": {
            "report_path": "research/egc2/results/synthetic-run-001.json",
            "overwrite_existing": False,
        },
        "permitted_failure_statuses": [
            "input_digest_mismatch",
            "input_lineage_invalid",
            "unresolved_adequacy_decision",
            "participant_count_mismatch",
            "record_count_mismatch",
            "gamma_grid_mismatch",
            "software_commit_mismatch",
            "python_version_mismatch",
            "entrypoint_schema_mismatch",
            "output_path_mismatch",
            "analysis_engine_failure",
            "report_digest_failure",
        ],
        "preregistration_lock": {
            "locked_before_input_access": True,
            "parameters_mutable_after_lock": False,
            "locked_at_utc": "2026-07-27T12:00:00Z",
            "locked_by": "synthetic-test",
        },
    }
    manifest["manifest_digest_sha256"] = compute_manifest_digest(manifest)
    return manifest


class RuntimeContractTests(unittest.TestCase):
    def setUp(self):
        self.dataset = _dataset()
        self.manifest = _run_manifest(self.dataset)
        self.output = self.manifest["output"]["report_path"]

    def _validate(self, **overrides):
        kwargs = {
            "expected_manifest_digest_sha256": self.manifest["manifest_digest_sha256"],
            "runtime_repository_commit_sha": "b" * 40,
            "runtime_output_path": self.output,
        }
        kwargs.update(overrides)
        return validate_runtime_contract(self.manifest, **kwargs)

    def test_valid_frozen_runtime_passes(self):
        self.assertTrue(self._validate()["valid"])

    def test_repository_commit_mismatch_fails_closed(self):
        with self.assertRaises(RunContractViolation) as caught:
            self._validate(runtime_repository_commit_sha="c" * 40)
        self.assertEqual(caught.exception.status, "software_commit_mismatch")

    def test_python_version_mismatch_fails_closed(self):
        with self.assertRaises(RunContractViolation) as caught:
            self._validate(runtime_python_version="0.0.1")
        self.assertEqual(caught.exception.status, "python_version_mismatch")

    def test_gamma_grid_mismatch_fails_closed(self):
        with self.assertRaises(RunContractViolation) as caught:
            self._validate(runtime_gamma_grid=[0.0, 1.0, 6.0])
        self.assertEqual(caught.exception.status, "gamma_grid_mismatch")

    def test_output_path_mismatch_fails_closed(self):
        with self.assertRaises(RunContractViolation) as caught:
            self._validate(runtime_output_path="research/egc2/results/other.json")
        self.assertEqual(caught.exception.status, "output_path_mismatch")

    def test_redigested_manifest_substitution_fails_external_commitment(self):
        expected = self.manifest["manifest_digest_sha256"]
        self.manifest["gamma_grid"] = [0.0, 1.0, 2.0, 6.0]
        self.manifest["manifest_digest_sha256"] = compute_manifest_digest(self.manifest)
        with self.assertRaises(RunContractViolation) as caught:
            validate_runtime_contract(
                self.manifest,
                expected_manifest_digest_sha256=expected,
                runtime_repository_commit_sha="b" * 40,
                runtime_output_path=self.output,
            )
        self.assertEqual(caught.exception.status, "input_lineage_invalid")

    def test_successful_report_echoes_run_contract(self):
        report = execute_preregistered_run(
            self.dataset,
            self.manifest,
            expected_manifest_digest_sha256=self.manifest["manifest_digest_sha256"],
            runtime_repository_commit_sha="b" * 40,
            runtime_output_path=self.output,
        )
        self.assertEqual(report["run_contract"]["run_id"], "synthetic-run-001")
        self.assertEqual(report["analysis_input_digest_sha256"], self.dataset["analysis_input_digest_sha256"])

    def test_input_digest_substitution_fails_closed(self):
        altered = deepcopy(self.dataset)
        altered["records"][0]["retained_score"] = 3
        altered["records"][0]["record_digest_sha256"] = compute_record_digest(altered["records"][0])
        altered["analysis_input_digest_sha256"] = compute_dataset_digest(altered)
        with self.assertRaises(RunContractViolation) as caught:
            execute_preregistered_run(
                altered,
                self.manifest,
                expected_manifest_digest_sha256=self.manifest["manifest_digest_sha256"],
                runtime_repository_commit_sha="b" * 40,
                runtime_output_path=self.output,
            )
        self.assertEqual(caught.exception.status, "input_digest_mismatch")

    def test_study_identity_mismatch_fails_closed(self):
        altered = deepcopy(self.dataset)
        altered["study_id"] = "other-study"
        altered["analysis_input_digest_sha256"] = compute_dataset_digest(altered)
        self.manifest["expected_input_digest_sha256"] = altered["analysis_input_digest_sha256"]
        self.manifest["manifest_digest_sha256"] = compute_manifest_digest(self.manifest)
        with self.assertRaises(RunContractViolation) as caught:
            execute_preregistered_run(
                altered,
                self.manifest,
                expected_manifest_digest_sha256=self.manifest["manifest_digest_sha256"],
                runtime_repository_commit_sha="b" * 40,
                runtime_output_path=self.output,
            )
        self.assertEqual(caught.exception.status, "input_lineage_invalid")


if __name__ == "__main__":
    unittest.main(verbosity=2)
