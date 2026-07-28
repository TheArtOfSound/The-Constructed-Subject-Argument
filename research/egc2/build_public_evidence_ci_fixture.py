#!/usr/bin/env python3
"""Build a deterministic, public-safe synthetic fixture for evidence-gate CI.

This fixture tests repository plumbing only. It contains no real cloud events,
reviewer data, protected mappings, anchor content, or scientific observations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CONFIG_SCHEMA = "egc2-expert-reviewer-dry-run-configuration-evidence-0.1.0"
RESULT_SCHEMA = "egc2-expert-reviewer-synthetic-dry-run-result-0.1.0"
FIXTURE_ID = "public-evidence-ci-fixture-v0.1"
FIXTURE_COMMIT = "0" * 40


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_json(path: Path, value: Any) -> str:
    payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_fixture(root: Path) -> dict[str, Path]:
    root.mkdir(parents=True, exist_ok=True)
    evidence_root = root / "evidence"

    delivery_path = evidence_root / "delivery_control.json"
    audit_path = evidence_root / "audit_control.log"

    delivery_digest = write_json(
        delivery_path,
        {
            "schema_version": "egc2-public-safe-ci-evidence-0.1.0",
            "synthetic_only": True,
            "control": "recipient_specific_delivery",
            "status": "passed_synthetic_fixture",
            "observation_limit": "Repository integration fixture only; no service was contacted.",
        },
    )
    audit_payload = (
        "synthetic_only=true\n"
        "control=audit_inventory\n"
        "status=passed_synthetic_fixture\n"
        "observation_limit=no external event or timestamp observed\n"
    )
    audit_path.write_text(audit_payload, encoding="utf-8")
    audit_digest = hashlib.sha256(audit_payload.encode("utf-8")).hexdigest()

    configuration = {
        "schema_version": CONFIG_SCHEMA,
        "dry_run_id": FIXTURE_ID,
        "repository_commit": FIXTURE_COMMIT,
        "synthetic_only": True,
        "evidence_files": [
            {
                "path": "evidence/delivery_control.json",
                "sha256": delivery_digest,
                "classification": "public_synthetic_fixture",
            },
            {
                "path": "evidence/audit_control.log",
                "sha256": audit_digest,
                "classification": "public_synthetic_fixture",
            },
        ],
        "controls": {
            "delivery": {"evidence_refs": ["evidence/delivery_control.json"]},
        },
        "claim_limit": "Configuration fixture only; no operational control was observed.",
    }
    configuration["manifest_digest_sha256"] = canonical_digest(configuration)

    result = {
        "schema_version": RESULT_SCHEMA,
        "dry_run_id": FIXTURE_ID,
        "repository_commit": FIXTURE_COMMIT,
        "synthetic_only": True,
        "configuration": {
            "configuration_evidence_digest_sha256": configuration[
                "manifest_digest_sha256"
            ]
        },
        "controls": {
            "audit": {"evidence_refs": ["evidence/audit_control.log"]},
        },
        "execution_status": "synthetic_repository_fixture_only",
        "scientific_claim_limit": (
            "No cloud, reviewer, anchor, semantic-fidelity, EGC, or consciousness "
            "result is represented."
        ),
    }

    configuration_path = root / "configuration.json"
    result_path = root / "result.json"
    write_json(configuration_path, configuration)
    write_json(result_path, result)
    return {
        "root": root,
        "configuration": configuration_path,
        "result": result_path,
        "evidence": evidence_root,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_root", type=Path)
    args = parser.parse_args()
    paths = build_fixture(args.output_root)
    print(json.dumps({key: str(value) for key, value in paths.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
