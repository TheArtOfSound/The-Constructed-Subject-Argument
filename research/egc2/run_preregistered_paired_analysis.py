#!/usr/bin/env python3
"""Execute the preregistered paired EGC analysis with repository-derived attestation.

This is the production command-line boundary. It derives the current Git commit and
working-tree state from Git rather than trusting a caller-supplied commit string.
A dirty or non-repository execution fails closed before scientific analysis.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Sequence

from analyze_lineage_checked_paired_sensitivity import (
    AnalysisInputError,
    RunContractViolation,
    RunManifestError,
    _failure_payload,
    execute_preregistered_run,
)


class RepositoryAttestationError(ValueError):
    """Raised when the runtime repository state cannot satisfy the frozen contract."""


def _run_git(arguments: Sequence[str], *, repository_root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=repository_root,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise RepositoryAttestationError(f"unable to execute git: {exc}") from exc
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise RepositoryAttestationError(
            f"git {' '.join(arguments)} failed with exit {completed.returncode}: {detail}"
        )
    return completed.stdout.strip()


def attest_repository(repository_root: Path) -> dict[str, Any]:
    """Return a fail-closed attestation of HEAD and working-tree cleanliness."""
    root = repository_root.resolve()
    inside = _run_git(["rev-parse", "--is-inside-work-tree"], repository_root=root)
    if inside != "true":
        raise RepositoryAttestationError("runtime path is not inside a Git work tree")

    top_level = Path(
        _run_git(["rev-parse", "--show-toplevel"], repository_root=root)
    ).resolve()
    if top_level != root:
        raise RepositoryAttestationError(
            f"repository root mismatch: expected {root}, Git reports {top_level}"
        )

    head = _run_git(["rev-parse", "--verify", "HEAD"], repository_root=root)
    if len(head) != 40 or any(char not in "0123456789abcdef" for char in head.lower()):
        raise RepositoryAttestationError("Git HEAD is not a full 40-character commit SHA")

    status = _run_git(
        ["status", "--porcelain=v1", "--untracked-files=all"],
        repository_root=root,
    )
    if status:
        changed = [line for line in status.splitlines() if line.strip()]
        raise RepositoryAttestationError(
            "working tree is not clean; preregistered analysis refuses modified or "
            f"untracked files ({len(changed)} entries)"
        )

    return {
        "repository_root": root.as_posix(),
        "repository_commit_sha": head.lower(),
        "working_tree_clean": True,
        "attestation_method": "git-rev-parse-and-porcelain-v1",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("locked_input", type=Path)
    parser.add_argument("run_manifest", type=Path)
    parser.add_argument("--expected-run-manifest-digest", required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    run_manifest: dict[str, Any] | None = None
    try:
        locked_input = json.loads(args.locked_input.read_text(encoding="utf-8"))
        run_manifest = json.loads(args.run_manifest.read_text(encoding="utf-8"))
        attestation = attest_repository(args.repository_root)
        runtime_output = args.output.as_posix()
        if args.output.exists():
            raise RunContractViolation(
                "output_path_mismatch",
                "frozen output path already exists and overwrite is prohibited",
            )
        report = execute_preregistered_run(
            locked_input,
            run_manifest,
            expected_manifest_digest_sha256=args.expected_run_manifest_digest,
            runtime_repository_commit_sha=attestation["repository_commit_sha"],
            runtime_output_path=runtime_output,
        )
        report["repository_attestation"] = attestation
        report.pop("analysis_report_digest_sha256", None)
        from analyze_lineage_checked_paired_sensitivity import _canonical_digest

        report["analysis_report_digest_sha256"] = _canonical_digest(report)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "status": "completed",
                    "report_digest_sha256": report["analysis_report_digest_sha256"],
                    "repository_commit_sha": attestation["repository_commit_sha"],
                    "working_tree_clean": True,
                },
                indent=2,
            )
        )
        return 0
    except RepositoryAttestationError as exc:
        print(
            json.dumps(
                _failure_payload(run_manifest, "software_commit_mismatch", str(exc)),
                indent=2,
            )
        )
        return 2
    except RunContractViolation as exc:
        print(json.dumps(_failure_payload(run_manifest, exc.status, exc.message), indent=2))
        return 2
    except (OSError, json.JSONDecodeError, AnalysisInputError, RunManifestError) as exc:
        print(
            json.dumps(
                _failure_payload(run_manifest, "input_lineage_invalid", str(exc)),
                indent=2,
            )
        )
        return 2
    except Exception as exc:
        print(
            json.dumps(
                _failure_payload(run_manifest, "analysis_engine_failure", str(exc)),
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
