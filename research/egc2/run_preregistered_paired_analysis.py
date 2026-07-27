#!/usr/bin/env python3
"""Execute the preregistered paired EGC analysis with repository-derived attestation.

This is the production command-line boundary. It derives the current Git commit and
working-tree state from Git rather than trusting a caller-supplied commit string.
A dirty or non-repository execution fails closed before scientific analysis.
The report target is resolved against the attested repository root so a matching
path string cannot redirect output through another working directory or symlink.
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


def resolve_output_target(
    repository_root: Path,
    frozen_report_path: str,
    requested_output: Path,
) -> tuple[Path, str]:
    """Bind the requested output to the frozen repository-relative report path.

    String equality is insufficient because a relative path is interpreted against
    the process working directory and an existing parent symlink can redirect the
    write outside the attested repository. Both paths are therefore resolved before
    comparison, and the canonical runtime value remains the frozen POSIX path.
    """
    root = repository_root.resolve()
    frozen = Path(frozen_report_path)
    if frozen.is_absolute() or ".." in frozen.parts:
        raise RunContractViolation(
            "output_path_mismatch",
            "frozen report path must be repository-relative and non-traversing",
        )

    expected_target = (root / frozen).resolve(strict=False)
    requested_target = requested_output.resolve(strict=False)

    try:
        expected_target.relative_to(root)
    except ValueError as exc:
        raise RunContractViolation(
            "output_path_mismatch",
            "frozen report path resolves outside the attested repository",
        ) from exc

    if requested_target != expected_target:
        raise RunContractViolation(
            "output_path_mismatch",
            "requested output does not resolve to the frozen repository report target",
        )

    return expected_target, frozen.as_posix()


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

        output_section = run_manifest.get("output")
        frozen_report_path = (
            output_section.get("report_path") if isinstance(output_section, dict) else None
        )
        if not isinstance(frozen_report_path, str):
            raise RunManifestError("run manifest output.report_path is required")

        output_target, runtime_output = resolve_output_target(
            Path(attestation["repository_root"]),
            frozen_report_path,
            args.output,
        )
        if output_target.exists():
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
        report["repository_attestation"] = {
            **attestation,
            "resolved_output_target": output_target.as_posix(),
            "frozen_output_path": runtime_output,
        }
        report.pop("analysis_report_digest_sha256", None)
        from analyze_lineage_checked_paired_sensitivity import _canonical_digest

        report["analysis_report_digest_sha256"] = _canonical_digest(report)
        output_target.parent.mkdir(parents=True, exist_ok=True)
        output_target.write_text(
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
                    "resolved_output_target": output_target.as_posix(),
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
