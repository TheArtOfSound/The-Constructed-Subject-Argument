#!/usr/bin/env python3
"""End-to-end standard-library tests for the QEIB execution pipeline."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUNNER = ROOT / "run_qeib_model.py"
ANALYZER = ROOT / "analyze_qeib.py"
MANIFEST = ROOT / "manifest.v0.1.json"
TASK_BANK = ROOT / "task_bank.v0.1.json"
ADAPTER = ROOT / "adapters" / "example_adapter.py"


class QEIBPipelineTest(unittest.TestCase):
    maxDiff = None

    def run_model(self, temp: Path, mode: str) -> Path:
        output = temp / f"{mode}.jsonl"
        command = " ".join(
            [
                sys.executable,
                str(ADAPTER),
                "--mode",
                mode,
                "--task-bank",
                str(TASK_BANK),
            ]
        )
        subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--manifest",
                str(MANIFEST),
                "--task-bank",
                str(TASK_BANK),
                "--output",
                str(output),
                "--command",
                command,
                "--provider",
                "qeib-test",
                "--model",
                f"{mode}-control",
                "--model-version",
                "0.1",
                "--tasks",
                "dev_math_001,dev_math_002",
                "--contexts",
                "neutral,eval_explicit,replacement,cue_stripped",
                "--replicates",
                "2",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertTrue(output.exists())
        return output

    def test_invariant_and_sensitive_controls(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            invariant = self.run_model(temp, "invariant")
            sensitive = self.run_model(temp, "sensitive")
            json_report = temp / "analysis.json"
            markdown_report = temp / "analysis.md"
            subprocess.run(
                [
                    sys.executable,
                    str(ANALYZER),
                    str(invariant),
                    str(sensitive),
                    "--json-output",
                    str(json_report),
                    "--markdown-output",
                    str(markdown_report),
                    "--bootstrap-samples",
                    "200",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(json_report.read_text(encoding="utf-8"))
            self.assertEqual(report["record_count"], 32)

            invariant_result = report["models"]["qeib-test::invariant-control::0.1"]
            sensitive_result = report["models"]["qeib-test::sensitive-control::0.1"]

            self.assertEqual(
                invariant_result["context_deltas"]["eval_explicit"]["paired_mean_delta"],
                0.0,
            )
            self.assertEqual(
                invariant_result["context_deltas"]["replacement"]["paired_mean_delta"],
                0.0,
            )
            self.assertEqual(
                sensitive_result["context_deltas"]["eval_explicit"]["paired_mean_delta"],
                -1.0,
            )
            self.assertEqual(
                sensitive_result["context_deltas"]["replacement"]["paired_mean_delta"],
                -1.0,
            )
            self.assertEqual(
                sensitive_result["context_deltas"]["cue_stripped"]["paired_mean_delta"],
                0.0,
            )
            self.assertIn("QEIB Analysis Report", markdown_report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
