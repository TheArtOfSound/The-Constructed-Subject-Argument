#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from validate_public_dry_run_artifacts import scan_paths


class LeakageScannerTests(unittest.TestCase):
    def write(self, root: Path, name: str, content: str) -> Path:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_clean_public_manifest_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(Path(directory), "clean.json", json.dumps({
                "schema_version": "fixture-0.1",
                "synthetic_only": True,
                "evidence_files": [{"path": "logs/test.log", "sha256": "a" * 64}],
                "secret_exclusion_attestation": True,
            }))
            report = scan_paths([path])
            self.assertEqual(report["status"], "passed_no_detected_leakage")
            self.assertEqual(report["finding_count"], 0)

    def test_nested_forbidden_key_fails_even_when_outer_artifact_is_redigested(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(Path(directory), "bad.json", json.dumps({
                "payload": {"protected_mapping": {"P-1": "A001"}},
                "outer_digest": "b" * 64,
            }))
            report = scan_paths([path])
            self.assertIn("forbidden_key", {item["kind"] for item in report["findings"]})

    def test_aws_presigned_url_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(Path(directory), "url.txt", "https://bucket.s3.amazonaws.com/x?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Signature=abcd")
            self.assertIn("aws_presigned_url", {item["kind"] for item in scan_paths([path])["findings"]})

    def test_aws_access_key_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(Path(directory), "key.log", "AKIAABCDEFGHIJKLMNOP")
            self.assertIn("aws_access_key", {item["kind"] for item in scan_paths([path])["findings"]})

    def test_real_email_fails_but_example_email_is_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real = self.write(root, "real.txt", "reviewer@university.edu")
            example = self.write(root, "example.txt", "reviewer@example.com")
            self.assertIn("email_address", {item["kind"] for item in scan_paths([real])["findings"]})
            self.assertEqual(scan_paths([example])["finding_count"], 0)

    def test_constructor_target_text_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(Path(directory), "notes.md", "The constructor target was region six.")
            self.assertIn("constructor_target_text", {item["kind"] for item in scan_paths([path])["findings"]})

    def test_invalid_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(Path(directory), "broken.json", '{"x":')
            self.assertIn("invalid_json", {item["kind"] for item in scan_paths([path])["findings"]})

    def test_directory_scan_includes_nested_supported_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "nested/clean.json", '{"synthetic_only": true}')
            self.assertEqual(scan_paths([root])["file_count"], 1)

    def test_report_digest_is_deterministic_for_same_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(Path(directory), "clean.json", '{"synthetic_only": true}')
            first = scan_paths([path])
            second = scan_paths([path])
            self.assertEqual(first["report_digest_sha256"], second["report_digest_sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
