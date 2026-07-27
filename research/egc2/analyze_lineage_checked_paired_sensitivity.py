#!/usr/bin/env python3
"""Run paired adequacy sensitivity only under a frozen, validated run contract.

Production execution requires both a lineage-checked participant artifact and a
preregistered run manifest. Any mismatch terminates with a declared fail-closed
status rather than silently changing the analysis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any, Iterable

from analyze_paired_adequacy_sensitivity import PairedOutcome, analyze
from validate_paired_analysis_input import (
    AnalysisInputError,
    build_analysis_pairs,
    validate_analysis_input,
)
from validate_paired_analysis_run_manifest import RunManifestError, validate_manifest

OUTPUT_SCHEMA = "egc2-lineage-checked-paired-sensitivity-0.1.0"


class LineageCheckedAnalysisError(ValueError):
    """Raised when the locked analysis artifact and computed report diverge."""


class RunContractViolation(LineageCheckedAnalysisError):
    """A preregistered, machine-readable fail-closed termination."""

    def __init__(self, status: str, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _violate(summary: dict[str, Any], status: str, message: str) -> None:
    permitted = set(summary.get("permitted_failure_statuses", []))
    if status not in permitted:
        status = "analysis_engine_failure"
    raise RunContractViolation(status, message)


def validate_runtime_contract(
    run_manifest: dict[str, Any],
    *,
    expected_manifest_digest_sha256: str | None,
    runtime_repository_commit_sha: str,
    runtime_output_path: str,
    runtime_python_version: str | None = None,
    runtime_entrypoint_schema: str = OUTPUT_SCHEMA,
    runtime_gamma_grid: Iterable[float] | None = None,
) -> dict[str, Any]:
    """Validate the frozen run manifest and every runtime-controlled invariant."""
    try:
        summary = validate_manifest(
            run_manifest,
            expected_manifest_digest=expected_manifest_digest_sha256,
        )
    except RunManifestError as exc:
        raise RunContractViolation("input_lineage_invalid", str(exc)) from exc

    python_version = runtime_python_version or platform.python_version()
    gamma_grid = [
        float(value)
        for value in (
            runtime_gamma_grid
            if runtime_gamma_grid is not None
            else summary["gamma_grid"]
        )
    ]

    if runtime_repository_commit_sha != summary["repository_commit_sha"]:
        _violate(
            summary,
            "software_commit_mismatch",
            "runtime repository commit differs from the frozen run contract",
        )
    if python_version != summary["python_version"]:
        _violate(
            summary,
            "python_version_mismatch",
            "runtime Python version differs from the frozen run contract",
        )
    if runtime_entrypoint_schema != summary["entrypoint_schema"]:
        _violate(
            summary,
            "entrypoint_schema_mismatch",
            "runtime entrypoint schema differs from the frozen run contract",
        )
    if gamma_grid != summary["gamma_grid"]:
        _violate(
            summary,
            "gamma_grid_mismatch",
            "runtime gamma grid differs from the frozen run contract",
        )
    if runtime_output_path != summary["report_path"]:
        _violate(
            summary,
            "output_path_mismatch",
            "runtime output path differs from the frozen run contract",
        )

    return {
        "valid": True,
        **summary,
        "runtime_python_version": python_version,
        "runtime_output_path": runtime_output_path,
        "runtime_entrypoint_schema": runtime_entrypoint_schema,
        "runtime_gamma_grid": gamma_grid,
    }


def analyze_locked_input(
    locked_input: dict[str, Any],
    *,
    gammas: Iterable[float],
    expected_input_digest_sha256: str,
) -> dict[str, Any]:
    """Validate, convert, analyze, and bind one frozen paired-analysis input."""
    validation = validate_analysis_input(locked_input)
    if not validation.get("analysis_ready"):
        raise RunContractViolation(
            "unresolved_adequacy_decision",
            "paired analysis is blocked while adequacy decisions remain unresolved",
        )

    frozen_digest = validation["analysis_input_digest_sha256"]
    declared_digest = locked_input.get("analysis_input_digest_sha256")
    if declared_digest != frozen_digest:
        raise RunContractViolation(
            "input_lineage_invalid",
            "declared analysis input digest does not match validated digest",
        )
    if frozen_digest != expected_input_digest_sha256:
        raise RunContractViolation(
            "input_digest_mismatch",
            "validated analysis input digest does not match the frozen run contract",
        )

    conversion = build_analysis_pairs(locked_input)
    if conversion.get("analysis_input_digest_sha256") != frozen_digest:
        raise RunContractViolation(
            "input_lineage_invalid",
            "pair conversion artifact is not bound to the validated input digest",
        )

    raw_pairs = conversion.get("pairs")
    if not isinstance(raw_pairs, list):
        raise RunContractViolation(
            "input_lineage_invalid", "pair conversion artifact must contain a pair list"
        )
    if conversion.get("participant_count") != validation.get("participant_count"):
        raise RunContractViolation(
            "participant_count_mismatch",
            "participant count differs between validation and pair conversion",
        )
    if len(raw_pairs) != validation.get("participant_count"):
        raise RunContractViolation(
            "participant_count_mismatch",
            "converted pair count differs from the validated participant count",
        )

    seen: set[str] = set()
    pairs: list[PairedOutcome] = []
    for index, row in enumerate(raw_pairs):
        if not isinstance(row, dict):
            raise RunContractViolation(
                "input_lineage_invalid", f"pairs[{index}] must be an object"
            )
        participant_id = row.get("participant_id")
        if not isinstance(participant_id, str) or not participant_id.strip():
            raise RunContractViolation(
                "input_lineage_invalid", f"pairs[{index}].participant_id is invalid"
            )
        if participant_id in seen:
            raise RunContractViolation(
                "input_lineage_invalid",
                f"duplicate participant in pair conversion: {participant_id}",
            )
        seen.add(participant_id)
        pairs.append(
            PairedOutcome(
                participant_id=participant_id,
                condition_a_score=row.get("condition_a_score"),
                condition_b_score=row.get("condition_b_score"),
            )
        )

    sensitivity = analyze(pairs, gammas=tuple(gammas))
    worst_case = sensitivity.get("worst_case_bounds") or {}
    if worst_case.get("participant_count") != validation.get("participant_count"):
        raise RunContractViolation(
            "participant_count_mismatch",
            "sensitivity report participant count does not match the frozen input",
        )

    engine_digest = sensitivity.get("analysis_digest_sha256")
    if not isinstance(engine_digest, str) or len(engine_digest) != 64:
        raise RunContractViolation(
            "report_digest_failure",
            "sensitivity engine did not return a valid analysis digest",
        )

    report = {
        "schema_version": OUTPUT_SCHEMA,
        "study_id": locked_input["study_id"],
        "analysis_plan_id": locked_input["analysis_plan_id"],
        "source_export_digest_sha256": locked_input["source_export_digest_sha256"],
        "analysis_input_digest_sha256": frozen_digest,
        "input_lock": {
            "locked_for_analysis": locked_input["locked_for_analysis"],
            "analysis_locked_at_utc": locked_input["analysis_locked_at_utc"],
            "condition_order": locked_input["condition_order"],
        },
        "input_validation": {
            "participant_count": validation["participant_count"],
            "record_count": validation["record_count"],
            "retained_record_count": validation["retained_record_count"],
            "suppressed_record_count": validation["suppressed_record_count"],
            "unresolved_record_count": validation["unresolved_record_count"],
            "analysis_ready": validation["analysis_ready"],
        },
        "pair_conversion_schema_version": conversion.get("schema_version"),
        "sensitivity_engine_schema_version": sensitivity.get("schema_version"),
        "sensitivity_engine_digest_sha256": engine_digest,
        "sensitivity_analysis": sensitivity,
        "claim_limit": (
            "This report proves only that the paired sensitivity analysis consumed "
            "the exact internally validated frozen input and runtime contract. It "
            "does not authenticate source records, identify suppressed scores, "
            "establish reviewer reliability, validate semantic fidelity, or validate EGC."
        ),
    }
    report["analysis_report_digest_sha256"] = _canonical_digest(report)
    return report


def execute_preregistered_run(
    locked_input: dict[str, Any],
    run_manifest: dict[str, Any],
    *,
    expected_manifest_digest_sha256: str | None,
    runtime_repository_commit_sha: str,
    runtime_output_path: str,
    runtime_python_version: str | None = None,
) -> dict[str, Any]:
    runtime = validate_runtime_contract(
        run_manifest,
        expected_manifest_digest_sha256=expected_manifest_digest_sha256,
        runtime_repository_commit_sha=runtime_repository_commit_sha,
        runtime_output_path=runtime_output_path,
        runtime_python_version=runtime_python_version,
    )
    if locked_input.get("study_id") != run_manifest.get("study_id"):
        _violate(runtime, "input_lineage_invalid", "study_id differs from run manifest")
    if locked_input.get("analysis_plan_id") != run_manifest.get("analysis_plan_id"):
        _violate(
            runtime,
            "input_lineage_invalid",
            "analysis_plan_id differs from run manifest",
        )

    report = analyze_locked_input(
        locked_input,
        gammas=runtime["gamma_grid"],
        expected_input_digest_sha256=runtime["expected_input_digest_sha256"],
    )
    report["run_contract"] = {
        "run_id": runtime["run_id"],
        "run_manifest_digest_sha256": runtime["manifest_digest_sha256"],
        "repository_commit_sha": runtime["repository_commit_sha"],
        "python_version": runtime["python_version"],
        "entrypoint_schema": runtime["entrypoint_schema"],
        "gamma_grid": runtime["gamma_grid"],
        "report_path": runtime["report_path"],
    }
    report.pop("analysis_report_digest_sha256", None)
    report["analysis_report_digest_sha256"] = _canonical_digest(report)
    return report


def _failure_payload(
    run_manifest: dict[str, Any] | None,
    status: str,
    message: str,
) -> dict[str, Any]:
    payload = {
        "schema_version": "egc2-paired-analysis-run-failure-0.1.0",
        "run_id": run_manifest.get("run_id") if isinstance(run_manifest, dict) else None,
        "status": status,
        "message": message,
        "analysis_performed": False,
    }
    payload["failure_digest_sha256"] = _canonical_digest(payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("locked_input", type=Path)
    parser.add_argument("run_manifest", type=Path)
    parser.add_argument("--expected-run-manifest-digest", required=True)
    parser.add_argument("--runtime-repository-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    run_manifest: dict[str, Any] | None = None
    try:
        locked_input = json.loads(args.locked_input.read_text(encoding="utf-8"))
        run_manifest = json.loads(args.run_manifest.read_text(encoding="utf-8"))
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
            runtime_repository_commit_sha=args.runtime_repository_commit,
            runtime_output_path=runtime_output,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({"status": "completed", "report_digest_sha256": report["analysis_report_digest_sha256"]}, indent=2))
        return 0
    except RunContractViolation as exc:
        print(json.dumps(_failure_payload(run_manifest, exc.status, exc.message), indent=2))
        return 2
    except (OSError, json.JSONDecodeError, AnalysisInputError, RunManifestError) as exc:
        print(json.dumps(_failure_payload(run_manifest, "input_lineage_invalid", str(exc)), indent=2))
        return 2
    except Exception as exc:  # preserve unexpected failures without producing a result
        print(json.dumps(_failure_payload(run_manifest, "analysis_engine_failure", str(exc)), indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
