#!/usr/bin/env python3
"""Fail-closed validator for preregistered EGC paired-analysis runs."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "egc2-paired-analysis-run-manifest-0.1.0"
ENTRYPOINT_SCHEMA = "egc2-lineage-checked-paired-sensitivity-0.1.0"
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?$")
COMMIT_RE = re.compile(r"^[a-f0-9]{40}$")
ALLOWED_FAILURES = {"input_digest_mismatch","input_lineage_invalid","unresolved_adequacy_decision","participant_count_mismatch","record_count_mismatch","gamma_grid_mismatch","software_commit_mismatch","python_version_mismatch","entrypoint_schema_mismatch","output_path_mismatch","analysis_engine_failure","report_digest_failure"}
REQUIRED_STATUS = "preregistered_not_run"

class RunManifestError(ValueError): pass

def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def compute_manifest_digest(manifest: dict[str, Any]) -> str:
    body = {k: v for k, v in manifest.items() if k != "manifest_digest_sha256"}
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()

def validate_manifest(manifest: dict[str, Any], *, expected_manifest_digest: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    def req(ok: bool, msg: str) -> None:
        if not ok: errors.append(msg)
    req(manifest.get("schema_version") == SCHEMA_VERSION, "invalid schema_version")
    req(manifest.get("status") == REQUIRED_STATUS, f"status must be {REQUIRED_STATUS}")
    for key in ("run_id", "study_id", "analysis_plan_id"):
        req(isinstance(manifest.get(key), str) and bool(manifest.get(key)), f"{key} required")
    expected_input = manifest.get("expected_input_digest_sha256")
    req(isinstance(expected_input, str) and bool(SHA256_RE.fullmatch(expected_input)), "expected_input_digest_sha256 must be 64 lowercase hex")
    gamma = manifest.get("gamma_grid")
    req(isinstance(gamma, list) and bool(gamma), "gamma_grid must be a nonempty list")
    if isinstance(gamma, list):
        req(all(isinstance(x, (int, float)) and not isinstance(x, bool) and 0 <= float(x) <= 6 for x in gamma), "gamma_grid values must be numeric in [0,6]")
        normalized = [float(x) for x in gamma if isinstance(x, (int, float)) and not isinstance(x, bool)]
        req(normalized == sorted(set(normalized)), "gamma_grid must be strictly increasing and unique")
        req(0.0 in normalized and 6.0 in normalized, "gamma_grid must include 0.0 and 6.0")
    software = manifest.get("software")
    req(isinstance(software, dict), "software object required")
    if isinstance(software, dict):
        req(bool(COMMIT_RE.fullmatch(str(software.get("repository_commit_sha", "")))), "repository_commit_sha must be 40 lowercase hex")
        req(bool(SEMVER_RE.fullmatch(str(software.get("python_version", "")))), "python_version must be semantic version")
        req(software.get("entrypoint_schema") == ENTRYPOINT_SCHEMA, "entrypoint_schema mismatch")
        req(software.get("entrypoint_path") == "research/egc2/analyze_lineage_checked_paired_sensitivity.py", "unexpected entrypoint_path")
    output = manifest.get("output")
    req(isinstance(output, dict), "output object required")
    if isinstance(output, dict):
        path = output.get("report_path")
        req(isinstance(path, str) and path.startswith("research/egc2/results/") and path.endswith(".json"), "report_path must be a JSON path under research/egc2/results/")
        req(".." not in str(path) and not str(path).startswith("/"), "report_path must not traverse or be absolute")
        req(output.get("overwrite_existing") is False, "overwrite_existing must be false")
    failures = manifest.get("permitted_failure_statuses")
    req(isinstance(failures, list) and bool(failures), "permitted_failure_statuses must be nonempty")
    if isinstance(failures, list):
        req(len(failures) == len(set(failures)), "permitted_failure_statuses must be unique")
        req(not (set(failures) - ALLOWED_FAILURES), f"unknown failure statuses: {sorted(set(failures) - ALLOWED_FAILURES)}")
        req({"input_digest_mismatch","input_lineage_invalid","report_digest_failure"}.issubset(set(failures)), "mandatory fail-closed statuses missing")
    lock = manifest.get("preregistration_lock")
    req(isinstance(lock, dict), "preregistration_lock object required")
    if isinstance(lock, dict):
        req(lock.get("locked_before_input_access") is True, "locked_before_input_access must be true")
        req(lock.get("parameters_mutable_after_lock") is False, "parameters_mutable_after_lock must be false")
        req(isinstance(lock.get("locked_at_utc"), str) and str(lock.get("locked_at_utc")).endswith("Z"), "locked_at_utc must be UTC Z timestamp")
        req(isinstance(lock.get("locked_by"), str) and bool(lock.get("locked_by")), "locked_by required")
    actual = compute_manifest_digest(manifest)
    req(manifest.get("manifest_digest_sha256") == actual, "manifest_digest_sha256 mismatch")
    if expected_manifest_digest is not None: req(expected_manifest_digest == actual, "manifest does not match independently frozen expected digest")
    if errors: raise RunManifestError(json.dumps({"valid": False, "errors": errors}, indent=2))
    return {"valid": True,"run_id": manifest["run_id"],"expected_input_digest_sha256": expected_input,"gamma_grid": [float(x) for x in gamma],"repository_commit_sha": software["repository_commit_sha"],"python_version": software["python_version"],"entrypoint_schema": software["entrypoint_schema"],"report_path": output["report_path"],"permitted_failure_statuses": failures,"manifest_digest_sha256": actual,"claim_limit": "Run freeze and lineage control only; this does not validate scores, missingness assumptions, semantic fidelity, or EGC."}

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(); p.add_argument("manifest", type=Path); p.add_argument("--expected-manifest-digest"); p.add_argument("--summary-out", type=Path); args = p.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8")); summary = validate_manifest(manifest, expected_manifest_digest=args.expected_manifest_digest)
    except (OSError, json.JSONDecodeError, RunManifestError) as exc:
        print(str(exc), file=sys.stderr); return 1
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True); args.summary_out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2)); return 0
if __name__ == "__main__": raise SystemExit(main())