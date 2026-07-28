#!/usr/bin/env python3
"""Fail-closed closure validation for public EGC synthetic dry-run evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from validate_public_dry_run_artifacts import ALLOWED_SUFFIXES, canonical_digest, scan_file

SCHEMA_VERSION = "egc2-public-evidence-closure-report-0.1.0"
CONFIG_SCHEMA = "egc2-expert-reviewer-dry-run-configuration-evidence-0.1.0"
RESULT_SCHEMA = "egc2-expert-reviewer-synthetic-dry-run-result-0.1.0"


class ClosureValidationError(ValueError):
    pass


def _manifest_digest(value: dict[str, Any], field: str) -> str:
    return canonical_digest({key: child for key, child in value.items() if key != field})


def _collect_evidence_refs(value: Any, path: str = "$") -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in {"evidence_refs", "preserved_evidence_refs"}:
                if not isinstance(child, list):
                    raise ClosureValidationError(f"{child_path} must be a list")
                for index, ref in enumerate(child):
                    if not isinstance(ref, str):
                        raise ClosureValidationError(f"{child_path}[{index}] must be a string")
                    refs.append((ref, f"{child_path}[{index}]"))
            else:
                refs.extend(_collect_evidence_refs(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            refs.extend(_collect_evidence_refs(child, f"{path}[{index}]"))
    return refs


def _safe_target(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ClosureValidationError(f"unsafe evidence path: {relative}")
    root_resolved = root.resolve()
    target = (root_resolved / candidate).resolve()
    if target == root_resolved or root_resolved not in target.parents:
        raise ClosureValidationError(f"evidence path escapes root: {relative}")
    return target


def _discover_public_evidence(root: Path) -> set[str]:
    evidence_root = root / "evidence"
    if not evidence_root.exists():
        raise ClosureValidationError("evidence directory does not exist")
    return {
        item.relative_to(root).as_posix()
        for item in evidence_root.rglob("*")
        if item.is_file() and item.suffix.lower() in ALLOWED_SUFFIXES
    }


def validate_evidence_closure(
    configuration: dict[str, Any],
    result: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    errors: list[str] = []

    if configuration.get("schema_version") != CONFIG_SCHEMA:
        errors.append("invalid configuration schema_version")
    if result.get("schema_version") != RESULT_SCHEMA:
        errors.append("invalid result schema_version")
    if configuration.get("dry_run_id") != result.get("dry_run_id"):
        errors.append("dry_run_id mismatch")
    if configuration.get("repository_commit") != result.get("repository_commit"):
        errors.append("repository_commit mismatch")
    if configuration.get("synthetic_only") is not True or result.get("synthetic_only") is not True:
        errors.append("both manifests must declare synthetic_only=true")

    declared_config_digest = configuration.get("manifest_digest_sha256")
    actual_config_digest = _manifest_digest(configuration, "manifest_digest_sha256")
    if declared_config_digest != actual_config_digest:
        errors.append("configuration manifest digest mismatch")
    linked_digest = (result.get("configuration") or {}).get(
        "configuration_evidence_digest_sha256"
    )
    if linked_digest != declared_config_digest:
        errors.append("result does not bind the configuration manifest digest")

    evidence_entries = configuration.get("evidence_files")
    if not isinstance(evidence_entries, list) or not evidence_entries:
        errors.append("configuration evidence_files must be a non-empty list")
        evidence_entries = []

    paths = [entry.get("path") for entry in evidence_entries if isinstance(entry, dict)]
    digests = [entry.get("sha256") for entry in evidence_entries if isinstance(entry, dict)]
    duplicate_paths = sorted(path for path, count in Counter(paths).items() if count > 1)
    duplicate_digests = sorted(digest for digest, count in Counter(digests).items() if count > 1)
    if duplicate_paths:
        errors.append(f"duplicate declared evidence paths: {duplicate_paths}")
    if duplicate_digests:
        errors.append(f"duplicate declared evidence digests: {duplicate_digests}")
    if len(paths) != len(evidence_entries) or any(not isinstance(path, str) for path in paths):
        errors.append("every evidence entry requires a string path")
    if any(not isinstance(digest, str) or len(digest) != 64 for digest in digests):
        errors.append("every evidence entry requires a 64-character sha256")

    try:
        references = _collect_evidence_refs(configuration) + _collect_evidence_refs(result)
    except ClosureValidationError as exc:
        errors.append(str(exc))
        references = []
    declared_set = {path for path in paths if isinstance(path, str)}
    referenced_set = {ref for ref, _ in references}
    missing_declarations = sorted(referenced_set - declared_set)
    unreferenced_declarations = sorted(declared_set - referenced_set)
    if missing_declarations:
        errors.append(f"referenced but undeclared evidence files: {missing_declarations}")
    if unreferenced_declarations:
        errors.append(f"declared but unreferenced evidence files: {unreferenced_declarations}")

    try:
        discovered_set = _discover_public_evidence(root)
    except ClosureValidationError as exc:
        errors.append(str(exc))
        discovered_set = set()
    missing_files = sorted(declared_set - discovered_set)
    extra_files = sorted(discovered_set - declared_set)
    if missing_files:
        errors.append(f"declared evidence files missing from disk: {missing_files}")
    if extra_files:
        errors.append(f"undeclared public evidence files present: {extra_files}")

    file_results: list[dict[str, Any]] = []
    by_path = {
        entry.get("path"): entry for entry in evidence_entries if isinstance(entry, dict)
    }
    for relative in sorted(declared_set & discovered_set):
        try:
            target = _safe_target(root, relative)
            observed_digest = hashlib.sha256(target.read_bytes()).hexdigest()
            expected_digest = by_path[relative].get("sha256")
            scan = scan_file(target)
            if observed_digest != expected_digest:
                errors.append(f"digest mismatch for {relative}")
            if scan["findings"]:
                errors.append(f"leakage findings for {relative}: {len(scan['findings'])}")
            file_results.append(
                {
                    "path": relative,
                    "expected_sha256": expected_digest,
                    "observed_sha256": observed_digest,
                    "digest_matched": observed_digest == expected_digest,
                    "leakage_finding_count": len(scan["findings"]),
                }
            )
        except (OSError, ClosureValidationError) as exc:
            errors.append(str(exc))

    report = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "passed_evidence_reference_closure"
            if not errors
            else "blocked_evidence_reference_closure"
        ),
        "dry_run_id": result.get("dry_run_id"),
        "declared_file_count": len(declared_set),
        "referenced_file_count": len(referenced_set),
        "discovered_file_count": len(discovered_set),
        "files": file_results,
        "errors": errors,
        "claim_limit": (
            "Closure, digest, and pattern-scan validation only; this does not "
            "authenticate cloud configuration or scientific results."
        ),
    }
    report["report_digest_sha256"] = canonical_digest(report)
    if errors:
        raise ClosureValidationError(json.dumps(report, indent=2))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("configuration", type=Path)
    parser.add_argument("result", type=Path)
    parser.add_argument("evidence_root", type=Path)
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args(argv)
    try:
        configuration = json.loads(args.configuration.read_text(encoding="utf-8"))
        result = json.loads(args.result.read_text(encoding="utf-8"))
        report = validate_evidence_closure(configuration, result, args.evidence_root)
    except (OSError, json.JSONDecodeError, ClosureValidationError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
