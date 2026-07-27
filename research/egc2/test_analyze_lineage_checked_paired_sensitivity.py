#!/usr/bin/env python3
from __future__ import annotations

import unittest
from copy import deepcopy

from analyze_lineage_checked_paired_sensitivity import (
    LineageCheckedAnalysisError,
    analyze_locked_input,
)
from validate_paired_analysis_input import compute_dataset_digest, compute_record_digest


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


def _fixture():
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


class LineageCheckedPairedSensitivityTests(unittest.TestCase):
    def test_echoes_frozen_digest_and_counts(self):
        dataset = _fixture()
        report = analyze_locked_input(
            dataset,
            expected_input_digest_sha256=dataset["analysis_input_digest_sha256"],
        )
        self.assertEqual(
            report["analysis_input_digest_sha256"],
            dataset["analysis_input_digest_sha256"],
        )
        self.assertEqual(report["input_validation"]["participant_count"], 2)

    def test_expected_digest_substitution_fails(self):
        with self.assertRaises(LineageCheckedAnalysisError):
            analyze_locked_input(
                _fixture(), expected_input_digest_sha256=_hex("f")
            )

    def test_redigested_record_change_still_fails_expected_commitment(self):
        dataset = _fixture()
        expected = dataset["analysis_input_digest_sha256"]
        dataset["records"][0]["retained_score"] = 3
        dataset["records"][0]["record_digest_sha256"] = compute_record_digest(
            dataset["records"][0]
        )
        dataset["analysis_input_digest_sha256"] = compute_dataset_digest(dataset)
        with self.assertRaises(LineageCheckedAnalysisError):
            analyze_locked_input(
                dataset, expected_input_digest_sha256=expected
            )

    def test_unresolved_decision_blocks_analysis(self):
        dataset = _fixture()
        dataset["records"][3]["adequacy_disposition"] = (
            "blind_adjudication_required"
        )
        dataset["records"][3]["record_digest_sha256"] = compute_record_digest(
            dataset["records"][3]
        )
        dataset["analysis_input_digest_sha256"] = compute_dataset_digest(dataset)
        with self.assertRaises(LineageCheckedAnalysisError):
            analyze_locked_input(dataset)

    def test_report_digest_is_deterministic(self):
        dataset = _fixture()
        first = analyze_locked_input(dataset)
        second = analyze_locked_input(deepcopy(dataset))
        self.assertEqual(
            first["analysis_report_digest_sha256"],
            second["analysis_report_digest_sha256"],
        )

    def test_engine_digest_is_preserved(self):
        report = analyze_locked_input(_fixture())
        self.assertEqual(len(report["sensitivity_engine_digest_sha256"]), 64)

    def test_source_and_plan_identity_are_preserved(self):
        report = analyze_locked_input(_fixture())
        self.assertEqual(report["study_id"], "synthetic-lineage-test")
        self.assertEqual(report["analysis_plan_id"], "paired-sensitivity-v0.1")

    def test_input_tamper_without_redigest_fails(self):
        dataset = _fixture()
        dataset["records"][0]["retained_score"] = 2
        with self.assertRaises(Exception):
            analyze_locked_input(dataset)


if __name__ == "__main__":
    unittest.main(verbosity=2)
