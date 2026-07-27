#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "validate_anchor_development_manifest.py"
MANIFEST_PATH = HERE / "anchor_development_manifest.v0.1.json"

spec = importlib.util.spec_from_file_location("anchor_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class AnchorDevelopmentManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_committed_manifest_passes(self) -> None:
        summary = validator.validate_manifest(copy.deepcopy(self.manifest))
        self.assertTrue(summary["valid"])
        self.assertEqual(summary["packet_count"], 24)
        self.assertEqual(summary["contrast_group_count"], 12)
        self.assertEqual(set(summary["score_region_counts"]), {str(i) for i in range(1, 8)})

    def test_digest_tampering_fails(self) -> None:
        broken = copy.deepcopy(self.manifest)
        broken["packets"][0]["candidate_response"] += " altered"
        with self.assertRaises(validator.ManifestValidationError):
            validator.validate_manifest(broken)

    def test_missing_contrast_family_fails(self) -> None:
        broken = copy.deepcopy(self.manifest)
        for packet in broken["packets"]:
            if packet["contrast_family"] == "agreement_decoy":
                packet["contrast_family"] = "polish_decoy"
        broken["content_digest_sha256"] = validator.canonical_packets_digest(broken["packets"])
        with self.assertRaises(validator.ManifestValidationError):
            validator.validate_manifest(broken)

    def test_pair_map_mismatch_fails(self) -> None:
        broken = copy.deepcopy(self.manifest)
        broken["packets"][1]["private_intention_map"]["central_meaning"] = "Changed target"
        broken["content_digest_sha256"] = validator.canonical_packets_digest(broken["packets"])
        with self.assertRaises(validator.ManifestValidationError):
            validator.validate_manifest(broken)

    def test_blind_export_contains_no_target_leakage(self) -> None:
        export = validator.build_blind_review_export(copy.deepcopy(self.manifest))
        self.assertEqual(len(export["items"]), 24)
        for item in export["items"]:
            self.assertFalse(validator.LEAKAGE_KEYS & set(item))
            self.assertIsNone(item["review_form"]["semantic_fidelity_score"])
            self.assertFalse(item["review_form"]["locked_before_target_reveal"])

    def test_blind_export_preserves_source_digest(self) -> None:
        export = validator.build_blind_review_export(copy.deepcopy(self.manifest))
        self.assertEqual(
            export["source_content_digest_sha256"],
            self.manifest["content_digest_sha256"],
        )

    def test_inadequate_map_requires_reason_code(self) -> None:
        broken = copy.deepcopy(self.manifest)
        target = next(p for p in broken["packets"] if p["anchor_id"] == "A007")
        target["provisional_reason_codes"] = ["NO_MATERIAL_LOSS"]
        broken["content_digest_sha256"] = validator.canonical_packets_digest(broken["packets"])
        with self.assertRaises(validator.ManifestValidationError):
            validator.validate_manifest(broken)

    def test_cli_writes_summary_and_blind_export(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            summary_path = Path(td) / "summary.json"
            export_path = Path(td) / "blind.json"
            rc = validator.main([
                str(MANIFEST_PATH),
                "--summary-out", str(summary_path),
                "--blind-export-out", str(export_path),
            ])
            self.assertEqual(rc, 0)
            self.assertTrue(summary_path.exists())
            self.assertTrue(export_path.exists())
            export = json.loads(export_path.read_text(encoding="utf-8"))
            self.assertEqual(export["schema_version"], "egc2-anchor-blind-review-export-0.1.0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
