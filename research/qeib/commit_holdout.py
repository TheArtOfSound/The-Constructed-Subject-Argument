#!/usr/bin/env python3
"""Freeze a private QEIB holdout bank without publishing its contents.

The tool canonicalizes and validates the private task bank, generates or reads a
32-byte secret salt, and publishes a salted SHA-256 commitment. The private bank
and salt must remain outside the public repository until the planned reveal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class HoldoutError(ValueError):
    """Raised when a private holdout cannot be committed safely."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HoldoutError(f"Holdout file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise HoldoutError(f"Invalid JSON in holdout file: {exc}") from exc
    if not isinstance(value, dict):
        raise HoldoutError("Holdout root must be a JSON object")
    return value


def validate_bank(bank: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = bank.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise HoldoutError("Holdout bank must contain a non-empty tasks list")

    required = {
        "task_id",
        "task_family",
        "domain",
        "prompt",
        "reference_answer",
        "grader",
    }
    task_ids: list[str] = []
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise HoldoutError(f"Task {index} is not an object")
        missing = required - set(task)
        if missing:
            raise HoldoutError(
                f"Task {index} is missing required fields: {sorted(missing)}"
            )
        task_id = task["task_id"]
        if not isinstance(task_id, str) or not task_id.strip():
            raise HoldoutError(f"Task {index} has an invalid task_id")
        task_ids.append(task_id)
        if task.get("task_family") != "capability_preservation":
            raise HoldoutError(
                f"Task {task_id} is not a capability_preservation task"
            )
        if task.get("grader", {}).get("type") != "exact_match":
            raise HoldoutError(f"Task {task_id} does not use exact_match grading")

    if len(task_ids) != len(set(task_ids)):
        raise HoldoutError("Holdout task IDs must be unique")
    return tasks


def canonical_bytes(bank: dict[str, Any]) -> bytes:
    return json.dumps(
        bank,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def read_or_create_salt(path: Path, *, overwrite: bool) -> bytes:
    if path.exists() and not overwrite:
        raw = path.read_text(encoding="utf-8").strip()
        try:
            salt = bytes.fromhex(raw)
        except ValueError as exc:
            raise HoldoutError(f"Salt file is not valid hexadecimal: {path}") from exc
        if len(salt) < 32:
            raise HoldoutError("Salt must contain at least 32 bytes")
        return salt

    path.parent.mkdir(parents=True, exist_ok=True)
    salt = secrets.token_bytes(32)
    path.write_text(salt.hex() + "\n", encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return salt


def commitment_payload(
    *,
    bank: dict[str, Any],
    tasks: list[dict[str, Any]],
    salt: bytes,
    public_label: str,
    planned_reveal: str | None,
    source_revision: str | None,
) -> dict[str, Any]:
    canonical = canonical_bytes(bank)
    unsalted = hashlib.sha256(canonical).hexdigest()
    salted = hashlib.sha256(salt + canonical).hexdigest()
    domains: dict[str, int] = {}
    for task in tasks:
        domain = str(task.get("domain", "unknown"))
        domains[domain] = domains.get(domain, 0) + 1

    return {
        "commitment": {
            "scheme": "sha256(secret_salt_bytes || canonical_json_utf8)",
            "digest": salted,
            "canonicalization": (
                "JSON sorted by keys, UTF-8, ensure_ascii=false, compact separators"
            ),
            "created_at_utc": utc_now(),
            "public_label": public_label,
            "task_count": len(tasks),
            "domain_counts": dict(sorted(domains.items())),
            "source_revision": source_revision,
            "planned_reveal": planned_reveal,
            "unsalted_digest_for_post_reveal_verification": unsalted,
        },
        "non_disclosure": {
            "private_task_bank_in_repository": False,
            "secret_salt_in_repository": False,
            "instruction": (
                "Keep the private task bank and salt separate from this public file. "
                "At reveal, publish both and rerun commit_holdout.py --verify."
            ),
        },
    }


def verify(
    *, bank: dict[str, Any], salt: bytes, commitment_path: Path
) -> bool:
    commitment = load_json(commitment_path)
    expected = commitment.get("commitment", {}).get("digest")
    if not isinstance(expected, str):
        raise HoldoutError("Commitment file does not contain commitment.digest")
    observed = hashlib.sha256(salt + canonical_bytes(bank)).hexdigest()
    print(
        json.dumps(
            {
                "verified": observed == expected,
                "expected": expected,
                "observed": observed,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return observed == expected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-bank", type=Path, required=True)
    parser.add_argument("--salt-file", type=Path, required=True)
    parser.add_argument("--public-commitment", type=Path, required=True)
    parser.add_argument("--label", default="QEIB private holdout")
    parser.add_argument("--planned-reveal")
    parser.add_argument("--source-revision")
    parser.add_argument("--overwrite-salt", action="store_true")
    parser.add_argument("--verify", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        bank = load_json(args.private_bank)
        tasks = validate_bank(bank)
        salt = read_or_create_salt(args.salt_file, overwrite=args.overwrite_salt)

        if args.verify:
            return 0 if verify(
                bank=bank,
                salt=salt,
                commitment_path=args.public_commitment,
            ) else 1

        payload = commitment_payload(
            bank=bank,
            tasks=tasks,
            salt=salt,
            public_label=args.label,
            planned_reveal=args.planned_reveal,
            source_revision=args.source_revision,
        )
        args.public_commitment.parent.mkdir(parents=True, exist_ok=True)
        args.public_commitment.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except HoldoutError as exc:
        print(f"Holdout error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
