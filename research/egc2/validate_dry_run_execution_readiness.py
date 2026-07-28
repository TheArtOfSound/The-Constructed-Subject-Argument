#!/usr/bin/env python3
"""Fail-closed validator for the EGC2 synthetic dry-run readiness record."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "egc2-expert-reviewer-dry-run-readiness-0.1.0"
REPORT_SCHEMA_VERSION = "egc2-dry-run-readiness-validation-0.1.0"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_GATES = {
    "P01": "operator_assigned_and_accepted",
    "P02": "all_ownership_roles_assigned",
    "P03": "isolated_proton_resources_named",
    "P04": "isolated_aws_resources_named",
    "P05": "object_lock_and_versioning_configuration_evidenced",
    "P06": "cloudtrail_data_events_and_log_validation_evidenced",
    "P07": "role_and_kms_separation_evidenced",
    "P08": "synthetic_artifacts_generated_and_digest_frozen",
    "P09": "public_artifact_leakage_scan_passed",
    "P10": "evidence_reference_closure_passed",
    "P11": "rollback_and_incident_contacts_verified",
    "P12": "operator_attests_no_live_data_or_private_holdout",
}
OWNERSHIP_ROLES = (
    "delivery_owner",
    "submission_lock_owner",
    "audit_evidence_owner",
    "private_store_owner",
    "incident_authority",
    "target_reveal_authorizer",
)
RESOURCE_ALIASES = (
    "proton_test_account_alias",
    "proton_queue_folder_alias",
    "aws_test_account_alias",
    "aws_region",
    "submission_bucket_alias",
    "audit_bucket_alias",
    "private_admin_store_alias",
    "protected_mapping_store_alias",
    "cloudtrail_alias",
)


def canonical_digest(record: dict[str, Any]) -> str:
    payload = copy.deepcopy(record)
    payload.pop("record_digest_sha256", None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _evidence_list_valid(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_nonempty_string(item) for item in value)


def validate_record(record: Any, *, expected_repository_head: str | None = None) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    def error(code: str, message: str) -> None:
        errors.append({"code": code, "message": message})

    def warning(code: str, message: str) -> None:
        warnings.append({"code": code, "message": message})

    if not isinstance(record, dict):
        error("record_not_object", "Readiness record must be a JSON object.")
        return _report(None, None, errors, warnings, {})

    declared_digest = record.get("record_digest_sha256")
    recomputed_digest = canonical_digest(record)
    if not isinstance(declared_digest, str) or not SHA256_RE.fullmatch(declared_digest):
        error("record_digest_invalid", "record_digest_sha256 must be a lowercase 64-character SHA-256 digest.")
    elif declared_digest != recomputed_digest:
        error("record_digest_mismatch", "Declared readiness-record digest does not match canonical recomputation.")

    if record.get("schema_version") != SCHEMA_VERSION:
        error("schema_version_mismatch", f"schema_version must equal {SCHEMA_VERSION}.")
    if record.get("synthetic_only") is not True:
        error("synthetic_only_required", "synthetic_only must be true.")
    if record.get("live_data_prohibited") is not True:
        error("live_data_prohibition_required", "live_data_prohibited must be true.")

    repository_head = record.get("repository_head_required")
    if not isinstance(repository_head, str) or not COMMIT_RE.fullmatch(repository_head):
        error("repository_head_invalid", "repository_head_required must be a full lowercase 40-character commit SHA.")
    if expected_repository_head is not None:
        if not COMMIT_RE.fullmatch(expected_repository_head):
            error("expected_repository_head_invalid", "Expected repository head is not a full lowercase commit SHA.")
        elif repository_head != expected_repository_head:
            error("repository_head_mismatch", "Readiness record is not frozen to the independently expected repository head.")

    operator = record.get("operator_assignment")
    if not isinstance(operator, dict):
        error("operator_assignment_invalid", "operator_assignment must be an object.")
        operator = {}
    acceptance = operator.get("acceptance_status")
    if acceptance not in {"not_assigned", "pending", "accepted", "declined", "revoked"}:
        error("operator_acceptance_status_invalid", "operator acceptance_status is outside the frozen vocabulary.")
    accepted_operator = (
        acceptance == "accepted"
        and _nonempty_string(operator.get("operator_pseudonym"))
        and _nonempty_string(operator.get("accepted_at_utc"))
    )
    if acceptance == "accepted" and not accepted_operator:
        error("accepted_operator_incomplete", "Accepted operator requires a non-empty pseudonym and acceptance timestamp.")
    if acceptance != "accepted" and (operator.get("operator_pseudonym") is not None or operator.get("accepted_at_utc") is not None):
        error("unaccepted_operator_has_acceptance_data", "Unaccepted operator must not carry pseudonym or acceptance timestamp data.")

    ownership = record.get("ownership_assignments")
    if not isinstance(ownership, dict):
        error("ownership_assignments_invalid", "ownership_assignments must be an object.")
        ownership = {}
    missing_roles = [role for role in OWNERSHIP_ROLES if not _nonempty_string(ownership.get(role))]
    extra_roles = sorted(set(ownership) - set(OWNERSHIP_ROLES))
    if extra_roles:
        warning("unrecognized_ownership_roles", f"Unrecognized ownership roles: {', '.join(extra_roles)}")
    all_roles_assigned = not missing_roles

    resources = record.get("resource_inventory")
    if not isinstance(resources, dict):
        error("resource_inventory_invalid", "resource_inventory must be an object.")
        resources = {}
    missing_aliases = [field for field in RESOURCE_ALIASES if not _nonempty_string(resources.get(field))]
    kms_aliases = resources.get("kms_key_aliases")
    resource_evidence = resources.get("resource_creation_evidence_paths")
    resources_complete = (
        not missing_aliases
        and isinstance(kms_aliases, list)
        and len(kms_aliases) >= 2
        and all(_nonempty_string(item) for item in kms_aliases)
        and _evidence_list_valid(resource_evidence)
    )
    if isinstance(kms_aliases, list) and len(set(kms_aliases)) != len(kms_aliases):
        error("duplicate_kms_alias", "kms_key_aliases must not contain duplicates.")

    gates = record.get("preflight_gates")
    gate_map: dict[str, dict[str, Any]] = {}
    if not isinstance(gates, list):
        error("preflight_gates_invalid", "preflight_gates must be a list.")
        gates = []
    for gate in gates:
        if not isinstance(gate, dict):
            error("preflight_gate_not_object", "Every preflight gate must be an object.")
            continue
        gate_id = gate.get("id")
        if gate_id in gate_map:
            error("duplicate_preflight_gate", f"Duplicate preflight gate id: {gate_id}")
            continue
        if gate_id not in EXPECTED_GATES:
            error("unknown_preflight_gate", f"Unknown preflight gate id: {gate_id}")
            continue
        gate_map[gate_id] = gate
        if gate.get("name") != EXPECTED_GATES[gate_id]:
            error("preflight_gate_name_mismatch", f"{gate_id} has an unexpected name.")
        if gate.get("status") not in {"not_verified", "verified", "failed", "waived"}:
            error("preflight_gate_status_invalid", f"{gate_id} has an invalid status.")
        if gate.get("status") == "verified" and not _evidence_list_valid(gate.get("evidence")):
            error("verified_gate_without_evidence", f"{gate_id} is verified but lacks non-empty evidence references.")
        if gate.get("status") != "verified" and gate.get("status") != "failed" and gate.get("evidence") not in ([], None):
            warning("unverified_gate_has_evidence", f"{gate_id} is not verified but contains evidence references.")
        if gate.get("status") == "waived":
            error("preflight_gate_waiver_prohibited", f"{gate_id} cannot be waived for execution readiness.")
    missing_gate_ids = sorted(set(EXPECTED_GATES) - set(gate_map))
    if missing_gate_ids:
        error("missing_preflight_gates", f"Missing required preflight gates: {', '.join(missing_gate_ids)}")
    if len(gates) != len(EXPECTED_GATES):
        error("preflight_gate_count_mismatch", f"Exactly {len(EXPECTED_GATES)} preflight gates are required.")
    all_gates_verified = len(gate_map) == len(EXPECTED_GATES) and all(
        gate_map[g]["status"] == "verified" and _evidence_list_valid(gate_map[g].get("evidence"))
        for g in EXPECTED_GATES
    )

    unlock_rule = record.get("execution_unlock_rule")
    if not isinstance(unlock_rule, dict):
        error("execution_unlock_rule_invalid", "execution_unlock_rule must be an object.")
        unlock_rule = {}
    expected_unlock = {
        "all_preflight_gates_must_equal": "verified",
        "operator_acceptance_must_equal": "accepted",
        "all_ownership_roles_must_be_non_null": True,
        "resource_aliases_must_be_non_null": True,
        "execution_allowed_must_be_set_only_after_independent_review": True,
    }
    for key, value in expected_unlock.items():
        if unlock_rule.get(key) != value:
            error("unlock_rule_drift", f"execution_unlock_rule.{key} differs from the frozen requirement.")

    status = record.get("status")
    execution_allowed = record.get("execution_allowed")
    if status not in {"blocked", "ready"}:
        error("readiness_status_invalid", "status must be blocked or ready.")
    if not isinstance(execution_allowed, bool):
        error("execution_allowed_not_boolean", "execution_allowed must be boolean.")
        execution_allowed = False

    independent_review = record.get("independent_review")
    independent_review_verified = (
        isinstance(independent_review, dict)
        and independent_review.get("status") == "verified"
        and _nonempty_string(independent_review.get("reviewer_pseudonym"))
        and _nonempty_string(independent_review.get("reviewed_at_utc"))
        and _evidence_list_valid(independent_review.get("evidence"))
    )

    blockers = record.get("current_blockers")
    blockers_present = isinstance(blockers, list) and bool(blockers) and all(_nonempty_string(item) for item in blockers)
    prerequisites_complete = accepted_operator and all_roles_assigned and resources_complete and all_gates_verified

    if execution_allowed:
        if status != "ready":
            error("execution_allowed_while_not_ready", "execution_allowed=true requires status=ready.")
        if not prerequisites_complete:
            error("execution_allowed_without_prerequisites", "Execution is allowed although one or more frozen prerequisites are incomplete.")
        if not independent_review_verified:
            error("execution_allowed_without_independent_review", "Execution is allowed without a complete independent-review attestation.")
        if blockers not in ([], None):
            error("ready_record_has_blockers", "A ready record must not retain current blockers.")
    else:
        if status != "blocked":
            error("blocked_flag_status_mismatch", "execution_allowed=false requires status=blocked.")
        if prerequisites_complete and independent_review_verified:
            warning("fully_prepared_but_still_blocked", "All modeled prerequisites are complete but execution remains blocked.")
        if not blockers_present:
            error("blocked_record_without_blockers", "A blocked record must preserve at least one explicit blocker.")

    semantic_checks = {
        "P01": accepted_operator,
        "P02": all_roles_assigned,
        "P03": all(_nonempty_string(resources.get(k)) for k in ("proton_test_account_alias", "proton_queue_folder_alias")),
        "P04": all(_nonempty_string(resources.get(k)) for k in ("aws_test_account_alias", "aws_region", "submission_bucket_alias", "audit_bucket_alias", "private_admin_store_alias", "protected_mapping_store_alias", "cloudtrail_alias")),
        "P05": _evidence_list_valid(resource_evidence),
        "P06": _evidence_list_valid(resource_evidence),
        "P07": isinstance(kms_aliases, list) and len(kms_aliases) >= 2 and all_roles_assigned and _evidence_list_valid(resource_evidence),
        "P11": _nonempty_string(ownership.get("incident_authority")),
        "P12": record.get("synthetic_only") is True and record.get("live_data_prohibited") is True and accepted_operator,
    }
    for gate_id, condition in semantic_checks.items():
        gate = gate_map.get(gate_id)
        if gate and gate.get("status") == "verified" and not condition:
            error("verified_gate_contradicts_record", f"{gate_id} is verified but its underlying record fields are incomplete.")

    state = {
        "accepted_operator": accepted_operator,
        "all_ownership_roles_assigned": all_roles_assigned,
        "missing_ownership_roles": missing_roles,
        "resources_complete": resources_complete,
        "missing_resource_aliases": missing_aliases,
        "all_preflight_gates_verified": all_gates_verified,
        "independent_review_verified": independent_review_verified,
        "prerequisites_complete": prerequisites_complete,
        "execution_allowed": execution_allowed,
        "status": status,
    }
    return _report(declared_digest, recomputed_digest, errors, warnings, state)


def _report(
    declared_digest: str | None,
    recomputed_digest: str | None,
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
    state: dict[str, Any],
) -> dict[str, Any]:
    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": "passed_readiness_consistency" if not errors else "blocked_readiness_inconsistent",
        "valid": not errors,
        "declared_record_digest_sha256": declared_digest,
        "recomputed_record_digest_sha256": recomputed_digest,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "derived_state": state,
    }
    encoded = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    report["validation_report_digest_sha256"] = hashlib.sha256(encoded).hexdigest()
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--expected-repository-head")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        report = validate_record(record, expected_repository_head=args.expected_repository_head)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        report = _report(None, None, [{"code": "record_read_error", "message": str(exc)}], [], {})
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
