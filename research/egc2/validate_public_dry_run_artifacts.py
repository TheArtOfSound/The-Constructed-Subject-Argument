#!/usr/bin/env python3
"""Fail-closed leakage scanner for public EGC synthetic dry-run artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "egc2-public-artifact-leakage-report-0.1.0"
FORBIDDEN_EXACT_KEYS = {
    "access_key", "access_key_id", "secret_access_key", "session_token",
    "aws_access_key_id", "aws_secret_access_key", "aws_session_token",
    "presigned_url", "pre_signed_url", "signed_url", "upload_url", "download_url",
    "share_password", "proton_share_password", "encryption_key", "kms_key_material",
    "private_key", "secret_key", "api_key", "token", "bearer_token",
    "reviewer_name", "reviewer_email", "legal_name", "email", "phone",
    "mailing_address", "payment_details", "tax_information", "tax_id",
    "identity_linkage", "reviewer_identity_map", "protected_mapping",
    "source_anchor_id", "anchor_id", "contrast_group_id", "contrast_family",
    "constructor_target", "constructor_target_region", "provisional_score_region",
    "constructor_rationale", "expert_rationale", "admissible_score_range",
    "private_intention_map", "candidate_response", "holdout_prompt",
    "reference_answer", "private_holdout",
}
FORBIDDEN_KEY_FRAGMENTS = (
    "secret", "password", "credential", "private_key", "access_token",
    "identity_link", "payment_account", "protected_map",
)
SAFE_KEY_EXCEPTIONS = {
    "secret_exclusion_attestation", "contains_secrets", "secret_scan_status",
    "private_data_exclusion_attestation", "protected_mapping_excluded",
}
PATTERNS = {
    "aws_access_key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "aws_account_id": re.compile(r"(?<!\d)\d{12}(?!\d)"),
    "aws_secret_candidate": re.compile(r"(?i)\baws.{0,24}(?:secret|credential).{0,12}[=:]\s*[A-Za-z0-9/+=]{32,}\b"),
    "aws_presigned_url": re.compile(r"https?://[^\s\"']+[?&]X-Amz-(?:Algorithm|Credential|Signature|Security-Token)=", re.I),
    "generic_bearer_url": re.compile(r"https?://[^\s\"']+[?&](?:token|signature|sig|key|secret)=[^&\s\"']+", re.I),
    "private_key_block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    "email_address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "proton_share_secret": re.compile(r"https?://drive\.proton\.me/urls/[A-Za-z0-9_-]+#[A-Za-z0-9_-]+", re.I),
}
TEXT_LEAK_MARKERS = {
    "constructor target": "constructor_target_text",
    "admissible score range": "admissible_score_range_text",
    "private intention map": "private_intention_map_text",
    "candidate response": "candidate_response_text",
    "protected mapping": "protected_mapping_text",
    "private holdout": "private_holdout_text",
}
ALLOWED_SUFFIXES = {".json", ".jsonl", ".md", ".txt", ".log", ".csv"}


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def iter_files(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(item for item in path.rglob("*") if item.is_file() and item.suffix.lower() in ALLOWED_SUFFIXES)
        else:
            raise ValueError(f"path does not exist: {path}")
    return sorted(set(item.resolve() for item in files))


def _normalized_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")


def scan_json(value: Any, *, file: str, path: str = "$") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for raw_key, child in value.items():
            normalized = _normalized_key(str(raw_key))
            child_path = f"{path}.{raw_key}"
            if normalized in FORBIDDEN_EXACT_KEYS:
                findings.append({"file": file, "location": child_path, "kind": "forbidden_key", "evidence": normalized})
            elif normalized not in SAFE_KEY_EXCEPTIONS and any(fragment in normalized for fragment in FORBIDDEN_KEY_FRAGMENTS):
                findings.append({"file": file, "location": child_path, "kind": "forbidden_key_fragment", "evidence": normalized})
            findings.extend(scan_json(child, file=file, path=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(scan_json(child, file=file, path=f"{path}[{index}]"))
    return findings


def scan_text(text: str, *, file: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for kind, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            evidence = match.group(0)
            if kind == "email_address" and evidence.lower().endswith("@example.com"):
                continue
            findings.append({
                "file": file,
                "location": f"offset:{match.start()}",
                "kind": kind,
                "evidence_sha256": hashlib.sha256(evidence.encode("utf-8")).hexdigest(),
            })
    lowered = text.lower()
    for marker, kind in TEXT_LEAK_MARKERS.items():
        start = 0
        while True:
            index = lowered.find(marker, start)
            if index < 0:
                break
            findings.append({"file": file, "location": f"offset:{index}", "kind": kind, "evidence": marker})
            start = index + len(marker)
    return findings


def scan_file(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    file_digest = hashlib.sha256(raw).hexdigest()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return {"path": str(path), "sha256": file_digest, "findings": [{"file": str(path), "location": "$", "kind": "non_utf8_public_artifact", "evidence": "decode_failed"}]}
    findings = scan_text(text, file=str(path))
    if path.suffix.lower() == ".json":
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            findings.append({"file": str(path), "location": f"line:{exc.lineno}", "kind": "invalid_json", "evidence": exc.msg})
        else:
            findings.extend(scan_json(value, file=str(path)))
    elif path.suffix.lower() == ".jsonl":
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                findings.append({"file": str(path), "location": f"line:{line_number}", "kind": "invalid_jsonl", "evidence": exc.msg})
            else:
                findings.extend(scan_json(value, file=str(path), path=f"$line[{line_number}]"))
    return {"path": str(path), "sha256": file_digest, "findings": findings}


def scan_paths(paths: Iterable[Path]) -> dict[str, Any]:
    files = iter_files(paths)
    if not files:
        raise ValueError("no supported public artifacts found")
    results = [scan_file(path) for path in files]
    findings = [finding for result in results for finding in result["findings"]]
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "blocked_leakage_detected" if findings else "passed_no_detected_leakage",
        "file_count": len(files),
        "finding_count": len(findings),
        "files": [{"path": result["path"], "sha256": result["sha256"], "finding_count": len(result["findings"])} for result in results],
        "findings": findings,
        "claim_limit": "Pattern and structural scan only; a clean report does not prove absence of all sensitive information.",
    }
    report["report_digest_sha256"] = canonical_digest(report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args(argv)
    try:
        report = scan_paths(args.paths)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "scanner_error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 1 if report["finding_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
