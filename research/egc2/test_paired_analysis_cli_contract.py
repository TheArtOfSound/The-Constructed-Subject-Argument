#!/usr/bin/env python3
"""Repository-native subprocess tests for the preregistered paired-analysis CLI.

These tests exercise the actual command-line boundary, filesystem behavior, output
creation, non-overwrite rule, and machine-readable fail-closed artifacts. Synthetic
fixtures are used only to validate software behavior; they are not EGC results.
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
import tempfile
import unittest
import uuid
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
ENTRYPOINT = HERE / "analyze_lineage_checked_paired_sensitivity.py"

if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from analyze_lineage_checked_paired_sensitivity import OUTPUT_SCHEMA  # noqa: E402
from validate_paired_analysis_input import (  # noqa: E402
    compute_dataset_digest,
    compute_record_digest,
)
from validate_paired_analysis_run_manifest import compute_manifest_digest  # noqa: E402


def _hex(char: str, length: int = 64) -> str:
    return char * length


def _record(participant_id: str, condition: str, disposition: str, score, index: int):
    row = {
        "participant_id": participant_id,
        "condition": condition,
        "adequacy_disposition": disposition,
        "retained_score": score,
        "source_record_digest_sha256": _hex(str(index % 10)),
        "adequacy_decision_digest_sha256": _hex(str((index + 1) % 10)),
        "decision_version": "0.1.0",
        "decision_locked_at_utc": "2026-07-27T15:00:00Z",
    }
    row["record_digest_sha256"] = compute_record_digest(row)
    return row


def _dataset():
    value = {
        "schema_version": "egc2-paired-analysis-input-0.1.0",
        "study_id": "synthetic-cli-contract-test",
        "analysis_plan_id": "paired-sensitivity-v0.1",
        "source_export_digest_sha256": _hex("a"),
        "condition_order": ["A", "B"],
        "locked_for_analysis": True,
        "analysis_locked_at_utc": "2026-07-27T15:01:00Z",
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
    value["analysis_input_digest_sha256"] = compute_dataset_digest(value)
    return value


def _manifest(dataset: dict, report_path: str):
    value = {
        "schema_version": "egc2-paired-analysis-run-manifest-0.1.0",
        "status": "preregistered_not_run",
        "run_id": "synthetic-cli-run",
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
        "output": {"report_path": report_path, "overwrite_existing": False},
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
            "locked_at_utc": "2026-07-27T15:02:00Z",
            "locked_by": "synthetic-cli-test",
        },
    }
    value["manifest_digest_sha256"] = compute_manifest_digest(value)
    return value


class PairedAnalysisCliContractTests(unittest.TestCase):
    def setUp(self):
        self.dataset = _dataset()
        unique = uuid.uuid4().hex
        self.relative_output = f"research/egc2/results/.cli-contract-{unique}.json"
        self.output_path = REPO_ROOT / self.relative_output
        self.manifest = _manifest(self.dataset, self.relative_output)
        self.tempdir = tempfile.TemporaryDirectory(prefix="egc2-cli-contract-")
        self.tmp = Path(self.tempdir.name)
        self.input_path = self.tmp / "input.json"
        self.manifest_path = self.tmp / "manifest.json"
        self._write_fixtures()

    def tearDown(self):
        self.output_path.unlink(missing_ok=True)
        self.tempdir.cleanup()

    def _write_fixtures(self):
        self.input_path.write_text(json.dumps(self.dataset, indent=2) + "\n", encoding="utf-8")
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8")

    def _run(self, *, commit: str = "b" * 40, expected_manifest_digest: str | None = None):
        command = [
            sys.executable,
            str(ENTRYPOINT),
            str(self.input_path),
            str(self.manifest_path),
            "--expected-run-manifest-digest",
            expected_manifest_digest or self.manifest["manifest_digest_sha256"],
            "--runtime-repository-commit",
            commit,
            "--output",
            self.relative_output,
        ]
        return subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    @staticmethod
    def _stdout_json(result: subprocess.CompletedProcess[str]):
        return json.loads(result.stdout)

    def test_cli_success_writes_digest_bound_report(self):
        result = self._run()
        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        summary = self._stdout_json(result)
        self.assertEqual(summary["status"], "completed")
        report = json.loads(self.output_path.read_text(encoding="utf-8"))
        self.assertEqual(
            report["analysis_input_digest_sha256"],
            self.dataset["analysis_input_digest_sha256"],
        )
        self.assertEqual(
            report["run_contract"]["run_manifest_digest_sha256"],
            self.manifest["manifest_digest_sha256"],
        )
        self.assertEqual(summary["report_digest_sha256"], report["analysis_report_digest_sha256"])

    def test_preexisting_output_fails_without_overwrite(self):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        sentinel = "do-not-overwrite\n"
        self.output_path.write_text(sentinel, encoding="utf-8")
        result = self._run()
        self.assertEqual(result.returncode, 2)
        failure = self._stdout_json(result)
        self.assertEqual(failure["status"], "output_path_mismatch")
        self.assertFalse(failure["analysis_performed"])
        self.assertEqual(self.output_path.read_text(encoding="utf-8"), sentinel)
        self.assertEqual(len(failure["failure_digest_sha256"]), 64)

    def test_commit_mismatch_returns_declared_failure_artifact(self):
        result = self._run(commit="c" * 40)
        self.assertEqual(result.returncode, 2)
        failure = self._stdout_json(result)
        self.assertEqual(failure["status"], "software_commit_mismatch")
        self.assertFalse(failure["analysis_performed"])
        self.assertFalse(self.output_path.exists())

    def test_external_manifest_commitment_mismatch_fails(self):
        result = self._run(expected_manifest_digest="d" * 64)
        self.assertEqual(result.returncode, 2)
        failure = self._stdout_json(result)
        self.assertEqual(failure["status"], "input_lineage_invalid")
        self.assertFalse(self.output_path.exists())

    def test_redigested_input_substitution_fails_against_manifest(self):
        altered = deepcopy(self.dataset)
        altered["records"][0]["retained_score"] = 3
        altered["records"][0]["record_digest_sha256"] = compute_record_digest(altered["records"][0])
        altered["analysis_input_digest_sha256"] = compute_dataset_digest(altered)
        self.dataset = altered
        self._write_fixtures()
        result = self._run()
        self.assertEqual(result.returncode, 2)
        failure = self._stdout_json(result)
        self.assertEqual(failure["status"], "input_digest_mismatch")
        self.assertFalse(self.output_path.exists())

    def test_malformed_input_returns_lineage_failure(self):
        self.input_path.write_text("{not-json", encoding="utf-8")
        result = self._run()
        self.assertEqual(result.returncode, 2)
        failure = self._stdout_json(result)
        self.assertEqual(failure["status"], "input_lineage_invalid")
        self.assertFalse(failure["analysis_performed"])
        self.assertFalse(self.output_path.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
