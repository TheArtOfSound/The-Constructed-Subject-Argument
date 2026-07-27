#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from analyze_lineage_checked_paired_sensitivity import RunContractViolation
from run_preregistered_paired_analysis import (
    RepositoryAttestationError,
    attest_repository,
    resolve_output_target,
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


class OutputTargetBindingTests(unittest.TestCase):
    FROZEN = "research/egc2/results/preregistered-run.json"

    def test_exact_resolved_repository_target_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            requested = root / self.FROZEN
            target, runtime_value = resolve_output_target(root, self.FROZEN, requested)
            self.assertEqual(target, requested.resolve(strict=False))
            self.assertEqual(runtime_value, self.FROZEN)

    def test_same_relative_string_from_other_working_directory_fails(self):
        with tempfile.TemporaryDirectory() as repository_directory, tempfile.TemporaryDirectory() as other_directory:
            root = Path(repository_directory).resolve()
            requested = Path(other_directory) / self.FROZEN
            with self.assertRaisesRegex(RunContractViolation, "does not resolve"):
                resolve_output_target(root, self.FROZEN, requested)

    def test_absolute_frozen_path_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with self.assertRaisesRegex(RunContractViolation, "repository-relative"):
                resolve_output_target(root, "/tmp/result.json", root / "result.json")

    def test_traversing_frozen_path_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with self.assertRaisesRegex(RunContractViolation, "non-traversing"):
                resolve_output_target(root, "research/../outside.json", root / "outside.json")

    def test_existing_parent_symlink_escape_fails(self):
        with tempfile.TemporaryDirectory() as repository_directory, tempfile.TemporaryDirectory() as outside_directory:
            root = Path(repository_directory).resolve()
            results_parent = root / "research" / "egc2"
            results_parent.mkdir(parents=True)
            (results_parent / "results").symlink_to(Path(outside_directory), target_is_directory=True)
            requested = results_parent / "results" / "preregistered-run.json"
            with self.assertRaisesRegex(RunContractViolation, "outside the attested repository"):
                resolve_output_target(root, self.FROZEN, requested)


if __name__ == "__main__":
    unittest.main(verbosity=2)
