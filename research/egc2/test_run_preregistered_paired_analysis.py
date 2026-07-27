#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from run_preregistered_paired_analysis import (
    RepositoryAttestationError,
    attest_repository,
)


ROOT = Path("/tmp/egc-repo").resolve()
HEAD = "a" * 40


def completed(stdout: str = "", stderr: str = "", returncode: int = 0):
    return subprocess.CompletedProcess(
        args=["git"], returncode=returncode, stdout=stdout, stderr=stderr
    )


class RepositoryAttestationTests(unittest.TestCase):
    def test_clean_exact_repository_passes(self):
        responses = [
            completed("true\n"),
            completed(f"{ROOT}\n"),
            completed(f"{HEAD}\n"),
            completed(""),
        ]
        with patch("run_preregistered_paired_analysis.subprocess.run", side_effect=responses) as run:
            result = attest_repository(ROOT)
        self.assertEqual(result["repository_commit_sha"], HEAD)
        self.assertTrue(result["working_tree_clean"])
        self.assertEqual(run.call_count, 4)
        for call in run.call_args_list:
            self.assertFalse(call.kwargs["check"])
            self.assertEqual(call.kwargs["cwd"], ROOT)

    def test_dirty_tracked_file_fails(self):
        responses = [
            completed("true\n"),
            completed(f"{ROOT}\n"),
            completed(f"{HEAD}\n"),
            completed(" M research/egc2/file.py\n"),
        ]
        with patch("run_preregistered_paired_analysis.subprocess.run", side_effect=responses):
            with self.assertRaisesRegex(RepositoryAttestationError, "working tree is not clean"):
                attest_repository(ROOT)

    def test_untracked_file_fails(self):
        responses = [
            completed("true\n"),
            completed(f"{ROOT}\n"),
            completed(f"{HEAD}\n"),
            completed("?? private-output.json\n"),
        ]
        with patch("run_preregistered_paired_analysis.subprocess.run", side_effect=responses):
            with self.assertRaises(RepositoryAttestationError):
                attest_repository(ROOT)

    def test_nested_directory_rejected_as_repository_root(self):
        nested = ROOT / "research" / "egc2"
        responses = [completed("true\n"), completed(f"{ROOT}\n")]
        with patch("run_preregistered_paired_analysis.subprocess.run", side_effect=responses):
            with self.assertRaisesRegex(RepositoryAttestationError, "repository root mismatch"):
                attest_repository(nested)

    def test_not_a_repository_fails(self):
        with patch(
            "run_preregistered_paired_analysis.subprocess.run",
            return_value=completed(stderr="fatal: not a git repository", returncode=128),
        ):
            with self.assertRaisesRegex(RepositoryAttestationError, "failed with exit 128"):
                attest_repository(ROOT)

    def test_invalid_head_fails(self):
        responses = [
            completed("true\n"),
            completed(f"{ROOT}\n"),
            completed("abc123\n"),
        ]
        with patch("run_preregistered_paired_analysis.subprocess.run", side_effect=responses):
            with self.assertRaisesRegex(RepositoryAttestationError, "full 40-character"):
                attest_repository(ROOT)

    def test_git_execution_failure_fails_closed(self):
        with patch(
            "run_preregistered_paired_analysis.subprocess.run",
            side_effect=FileNotFoundError("git missing"),
        ):
            with self.assertRaisesRegex(RepositoryAttestationError, "unable to execute git"):
                attest_repository(ROOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
