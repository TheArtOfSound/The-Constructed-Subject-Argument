#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from build_public_evidence_ci_fixture import build_fixture
from validate_evidence_reference_closure import (
    ClosureValidationError,
    validate_evidence_closure,
)
from validate_public_dry_run_artifacts import scan_paths


class PublicEvidenceCIIntegrationTest(unittest.TestCase):
    def test_clean_fixture_passes_leakage_and_closure_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = build_fixture(Path(tmp) / "fixture")
            configuration = json.loads(paths["configuration"].read_text(encoding="utf-8"))
            result = json.loads(paths["result"].read_text(encoding="utf-8"))

            leakage = scan_paths([paths["evidence"]])
            self.assertEqual(leakage["status"], "passed_no_detected_leakage")
            self.assertEqual(leakage["finding_count"], 0)
            self.assertEqual(leakage["file_count"], 2)

            closure = validate_evidence_closure(configuration, result, paths["root"])
            self.assertEqual(
                closure["status"], "passed_evidence_reference_closure"
            )
            self.assertEqual(closure["declared_file_count"], 2)
            self.assertEqual(closure["referenced_file_count"], 2)
            self.assertEqual(closure["discovered_file_count"], 2)
            self.assertEqual(closure["errors"], [])

    def test_extra_public_file_blocks_closure_even_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = build_fixture(Path(tmp) / "fixture")
            extra = paths["evidence"] / "unreferenced_clean.txt"
            extra.write_text(
                "synthetic_only=true\nstatus=unreferenced_fixture\n",
                encoding="utf-8",
            )
            configuration = json.loads(paths["configuration"].read_text(encoding="utf-8"))
            result = json.loads(paths["result"].read_text(encoding="utf-8"))

            leakage = scan_paths([paths["evidence"]])
            self.assertEqual(leakage["status"], "passed_no_detected_leakage")

            with self.assertRaises(ClosureValidationError) as caught:
                validate_evidence_closure(configuration, result, paths["root"])
            report = json.loads(str(caught.exception))
            self.assertEqual(
                report["status"], "blocked_evidence_reference_closure"
            )
            self.assertTrue(
                any(
                    "undeclared public evidence files present" in error
                    for error in report["errors"]
                )
            )

    def test_redigested_leakage_still_blocks_closure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = build_fixture(Path(tmp) / "fixture")
            configuration = json.loads(paths["configuration"].read_text(encoding="utf-8"))
            result = json.loads(paths["result"].read_text(encoding="utf-8"))
            target = paths["evidence"] / "delivery_control.json"
            target.write_text(
                json.dumps(
                    {
                        "synthetic_only": True,
                        "reviewer_email": "fixture@example.com",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            import hashlib
            from build_public_evidence_ci_fixture import canonical_digest

            new_digest = hashlib.sha256(target.read_bytes()).hexdigest()
            configuration["evidence_files"][0]["sha256"] = new_digest
            configuration["manifest_digest_sha256"] = canonical_digest(
                {
                    key: value
                    for key, value in configuration.items()
                    if key != "manifest_digest_sha256"
                }
            )
            result["configuration"][
                "configuration_evidence_digest_sha256"
            ] = configuration["manifest_digest_sha256"]

            leakage = scan_paths([paths["evidence"]])
            self.assertEqual(leakage["status"], "blocked_leakage_detected")
            self.assertGreater(leakage["finding_count"], 0)

            with self.assertRaises(ClosureValidationError) as caught:
                validate_evidence_closure(configuration, result, paths["root"])
            report = json.loads(str(caught.exception))
            self.assertTrue(
                any("leakage findings" in error for error in report["errors"])
            )


if __name__ == "__main__":
    unittest.main()
