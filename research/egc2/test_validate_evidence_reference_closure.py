#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from validate_public_dry_run_artifacts import canonical_digest
from validate_evidence_reference_closure import (
    ClosureValidationError,
    validate_evidence_closure,
)


def _write(root: Path, relative: str, text: str) -> str:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(root: Path):
    digest_a = _write(root, "evidence/a.json", '{"synthetic":true}\n')
    digest_b = _write(root, "evidence/b.log", "synthetic event\n")
    configuration = {
        "schema_version": "egc2-expert-reviewer-dry-run-configuration-evidence-0.1.0",
        "dry_run_id": "EGC2-DRY-TEST01",
        "repository_commit": "a" * 40,
        "synthetic_only": True,
        "delivery": {"evidence_refs": ["evidence/a.json"]},
        "audit": {"evidence_refs": ["evidence/b.log"]},
        "evidence_files": [
            {"path": "evidence/a.json", "sha256": digest_a},
            {"path": "evidence/b.log", "sha256": digest_b},
        ],
    }
    configuration["manifest_digest_sha256"] = canonical_digest(configuration)
    result = {
        "schema_version": "egc2-expert-reviewer-synthetic-dry-run-result-0.1.0",
        "dry_run_id": configuration["dry_run_id"],
        "repository_commit": configuration["repository_commit"],
        "synthetic_only": True,
        "configuration": {
            "configuration_evidence_digest_sha256": configuration[
                "manifest_digest_sha256"
            ]
        },
        "delivery": {"evidence_refs": ["evidence/a.json"]},
        "audit": {"evidence_refs": ["evidence/b.log"]},
    }
    return configuration, result


def _redigest(configuration, result):
    configuration["manifest_digest_sha256"] = canonical_digest(
        {
            key: value
            for key, value in configuration.items()
            if key != "manifest_digest_sha256"
        }
    )
    result["configuration"]["configuration_evidence_digest_sha256"] = configuration[
        "manifest_digest_sha256"
    ]


class EvidenceClosureTests(unittest.TestCase):
    def test_valid_closure_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            configuration, result = _fixture(root)
            report = validate_evidence_closure(configuration, result, root)
            self.assertEqual(report["status"], "passed_evidence_reference_closure")
            self.assertEqual(report["declared_file_count"], 2)

    def test_missing_declared_file_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            configuration, result = _fixture(root)
            (root / "evidence/a.json").unlink()
            with self.assertRaises(ClosureValidationError):
                validate_evidence_closure(configuration, result, root)

    def test_altered_file_fails_digest_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            configuration, result = _fixture(root)
            (root / "evidence/a.json").write_text("changed", encoding="utf-8")
            with self.assertRaises(ClosureValidationError):
                validate_evidence_closure(configuration, result, root)

    def test_undeclared_extra_file_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            configuration, result = _fixture(root)
            _write(root, "evidence/extra.txt", "extra")
            with self.assertRaises(ClosureValidationError):
                validate_evidence_closure(configuration, result, root)

    def test_referenced_but_undeclared_file_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            configuration, result = _fixture(root)
            result["audit"]["evidence_refs"].append("evidence/c.log")
            with self.assertRaises(ClosureValidationError):
                validate_evidence_closure(configuration, result, root)

    def test_declared_but_unreferenced_file_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            configuration, result = _fixture(root)
            configuration["audit"]["evidence_refs"] = []
            result["audit"]["evidence_refs"] = []
            _redigest(configuration, result)
            with self.assertRaises(ClosureValidationError):
                validate_evidence_closure(configuration, result, root)

    def test_duplicate_declared_digest_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            configuration, result = _fixture(root)
            configuration["evidence_files"][1]["sha256"] = configuration[
                "evidence_files"
            ][0]["sha256"]
            _redigest(configuration, result)
            with self.assertRaises(ClosureValidationError):
                validate_evidence_closure(configuration, result, root)

    def test_leakage_finding_fails_even_after_redigest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            configuration, result = _fixture(root)
            path = root / "evidence/a.json"
            path.write_text('{"note":"constructor target"}', encoding="utf-8")
            configuration["evidence_files"][0]["sha256"] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            _redigest(configuration, result)
            with self.assertRaises(ClosureValidationError):
                validate_evidence_closure(configuration, result, root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
