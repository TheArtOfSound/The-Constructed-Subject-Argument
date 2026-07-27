#!/usr/bin/env python3
"""Create and validate two-phase commitments for live EGC anchor-review generation.

This module records reproducibility commitments without storing the live secret seed,
protected source mapping, reviewer identities, or reviewer content. It does not
authenticate people, provide trusted timestamps, or validate anchors.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

PRE_SCHEMA = "egc2-anchor-review-generation-precommit-0.1.0"
POST_SCHEMA = "egc2-anchor-review-generation-postcommit-0.1.0"
HEX64 = re.compile(r"^[a-f0-9]{64}$")
HEX40 = re.compile(r"^[a-f0-9]{40}$")
REVIEWER_ID = re.compile(r"^R[0-9]{2,}$")
FORBIDDEN_KEYS = {
    "seed", "secret_seed", "nonce", "protected_mapping", "reviewer_name",
    "reviewer_email", "anchor_id", "contrast_group_id", "constructor_target",
    "candidate_response", "private_intention_map",
}

class CommitmentValidationError(ValueError):
    """Raised when a commitment fails closed."""


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def seed_commitment(secret_seed: str, private_nonce: str, ceremony_id: str) -> str:
    if not secret_seed or not private_nonce or not ceremony_id:
        raise CommitmentValidationError("seed, private nonce, and ceremony ID are required")
    return hashlib.sha256(
        f"egc2-anchor-review-seed-v0.1|{ceremony_id}|{secret_seed}|{private_nonce}".encode("utf-8")
    ).hexdigest()


def _walk_forbidden(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_KEYS:
                errors.append(f"{path}.{key}: forbidden secret or protected field")
            errors.extend(_walk_forbidden(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_walk_forbidden(child, f"{path}[{index}]"))
    return errors


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def build_precommit(*, ceremony_id: str, repository: str, code_commit_sha: str,
                    manifest_id: str, manifest_digest: str, reviewer_ids: list[str],
                    seed_commitment_sha256: str, operator_pseudonym: str,
                    created_at_utc: str) -> dict[str, Any]:
    record = {
        "schema_version": PRE_SCHEMA,
        "ceremony_id": ceremony_id,
        "repository": repository,
        "code_commit_sha": code_commit_sha,
        "source_manifest_id": manifest_id,
        "source_manifest_digest_sha256": manifest_digest,
        "reviewer_ids": sorted(reviewer_ids),
        "seed_commitment_sha256": seed_commitment_sha256,
        "operator_pseudonym": operator_pseudonym,
        "created_at_utc": created_at_utc,
        "claim_limit": "Reproducibility commitment only; no seed, protected mapping, reviewer identity, expert judgment, or anchor validation is recorded.",
    }
    record["precommit_digest_sha256"] = canonical_digest(record)
    validate_precommit(record)
    return record


def validate_precommit(record: dict[str, Any]) -> dict[str, Any]:
    errors = _walk_forbidden(record)
    _require(record.get("schema_version") == PRE_SCHEMA, "invalid precommit schema", errors)
    _require(bool(record.get("ceremony_id")), "ceremony_id is required", errors)
    _require(record.get("repository") == "TheArtOfSound/The-Constructed-Subject-Argument", "unexpected repository", errors)
    _require(bool(HEX40.fullmatch(str(record.get("code_commit_sha", "")))), "code_commit_sha must be 40 lowercase hex characters", errors)
    _require(bool(record.get("source_manifest_id")), "source_manifest_id is required", errors)
    _require(bool(HEX64.fullmatch(str(record.get("source_manifest_digest_sha256", "")))), "manifest digest must be 64 lowercase hex characters", errors)
    reviewer_ids = record.get("reviewer_ids")
    _require(isinstance(reviewer_ids, list) and len(reviewer_ids) >= 3, "at least three reviewer pseudonyms are required", errors)
    if isinstance(reviewer_ids, list):
        _require(reviewer_ids == sorted(set(reviewer_ids)), "reviewer IDs must be unique and sorted", errors)
        _require(all(REVIEWER_ID.fullmatch(str(x)) for x in reviewer_ids), "reviewer IDs must be opaque RNN pseudonyms", errors)
    _require(bool(HEX64.fullmatch(str(record.get("seed_commitment_sha256", "")))), "seed commitment must be 64 lowercase hex characters", errors)
    _require(bool(record.get("operator_pseudonym")), "operator pseudonym is required", errors)
    _require(str(record.get("created_at_utc", "")).endswith("Z"), "created_at_utc must be UTC with Z suffix", errors)
    declared = record.get("precommit_digest_sha256")
    unsigned = {k: v for k, v in record.items() if k != "precommit_digest_sha256"}
    _require(declared == canonical_digest(unsigned), "precommit digest mismatch", errors)
    if errors:
        raise CommitmentValidationError(json.dumps({"valid": False, "errors": errors}, indent=2))
    return {"valid": True, "reviewer_count": len(reviewer_ids), "precommit_digest_sha256": declared}


def build_postcommit(*, precommit: dict[str, Any], public_queue_digests: dict[str, str],
                     protected_bundle_digest: str, generator_version: str,
                     python_version: str, generated_at_utc: str,
                     witness_pseudonyms: list[str]) -> dict[str, Any]:
    validate_precommit(precommit)
    record = {
        "schema_version": POST_SCHEMA,
        "ceremony_id": precommit["ceremony_id"],
        "precommit_digest_sha256": precommit["precommit_digest_sha256"],
        "source_manifest_digest_sha256": precommit["source_manifest_digest_sha256"],
        "code_commit_sha": precommit["code_commit_sha"],
        "reviewer_ids": precommit["reviewer_ids"],
        "public_queue_digests_sha256": dict(sorted(public_queue_digests.items())),
        "protected_bundle_digest_sha256": protected_bundle_digest,
        "generator_version": generator_version,
        "python_version": python_version,
        "generated_at_utc": generated_at_utc,
        "witness_pseudonyms": sorted(witness_pseudonyms),
        "claim_limit": "Artifact-lineage commitment only; digests do not authenticate reviewers, witnesses, timestamps, or scientific validity.",
    }
    run_material = {
        "precommit_digest_sha256": record["precommit_digest_sha256"],
        "public_queue_digests_sha256": record["public_queue_digests_sha256"],
        "protected_bundle_digest_sha256": record["protected_bundle_digest_sha256"],
    }
    record["review_run_commitment_sha256"] = canonical_digest(run_material)
    record["postcommit_digest_sha256"] = canonical_digest(record)
    validate_postcommit(precommit, record)
    return record


def validate_postcommit(precommit: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    validate_precommit(precommit)
    errors = _walk_forbidden(record)
    _require(record.get("schema_version") == POST_SCHEMA, "invalid postcommit schema", errors)
    for key in ("ceremony_id", "precommit_digest_sha256", "source_manifest_digest_sha256", "code_commit_sha", "reviewer_ids"):
        expected_key = "precommit_digest_sha256" if key == "precommit_digest_sha256" else key
        expected = precommit[expected_key]
        _require(record.get(key) == expected, f"{key} does not match precommit", errors)
    queues = record.get("public_queue_digests_sha256")
    _require(isinstance(queues, dict), "public queue digests must be an object", errors)
    if isinstance(queues, dict):
        _require(set(queues) == set(precommit["reviewer_ids"]), "queue digest reviewer set must exactly match precommit", errors)
        _require(all(HEX64.fullmatch(str(v)) for v in queues.values()), "every queue digest must be 64 lowercase hex characters", errors)
    _require(bool(HEX64.fullmatch(str(record.get("protected_bundle_digest_sha256", "")))), "protected bundle digest must be 64 lowercase hex characters", errors)
    _require(bool(record.get("generator_version")), "generator version is required", errors)
    _require(bool(record.get("python_version")), "python version is required", errors)
    _require(str(record.get("generated_at_utc", "")).endswith("Z"), "generated_at_utc must be UTC with Z suffix", errors)
    witnesses = record.get("witness_pseudonyms")
    _require(isinstance(witnesses, list), "witness pseudonyms must be a list", errors)
    if isinstance(witnesses, list):
        _require(witnesses == sorted(set(witnesses)), "witness pseudonyms must be unique and sorted", errors)
    run_material = {
        "precommit_digest_sha256": record.get("precommit_digest_sha256"),
        "public_queue_digests_sha256": record.get("public_queue_digests_sha256"),
        "protected_bundle_digest_sha256": record.get("protected_bundle_digest_sha256"),
    }
    _require(record.get("review_run_commitment_sha256") == canonical_digest(run_material), "review-run commitment mismatch", errors)
    unsigned = {k: v for k, v in record.items() if k != "postcommit_digest_sha256"}
    _require(record.get("postcommit_digest_sha256") == canonical_digest(unsigned), "postcommit digest mismatch", errors)
    if errors:
        raise CommitmentValidationError(json.dumps({"valid": False, "errors": errors}, indent=2))
    return {
        "valid": True,
        "reviewer_count": len(precommit["reviewer_ids"]),
        "review_run_commitment_sha256": record["review_run_commitment_sha256"],
        "witness_count": len(witnesses),
    }
