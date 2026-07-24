#!/usr/bin/env python3
"""Collect exact model and runtime provenance for a QEIB genuine-model run.

The QEIB first-genuine-model preregistration (sections 2 and 12) requires that
each run artifact store the exact local model digest, the Ollama version, model
metadata, and the runtime configuration. Tag names alone are not accepted as
version identifiers because a tag can be repulled or reassigned to a different
digest over time.

This helper queries a running Ollama server for the authoritative per-model
digest and server version, records the repository commit, and writes a single
provenance JSON object alongside the raw run log. It uses only the standard
library and fails clearly rather than silently emitting an unverified artifact.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "qeib-provenance-0.1"


class ProvenanceError(RuntimeError):
    """Raised when authoritative provenance cannot be established."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _http_get_json(url: str, timeout: float) -> Any:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "QEIB-provenance/0.1"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise ProvenanceError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ProvenanceError(f"Could not reach {url}: {exc}") from exc
    except TimeoutError as exc:
        raise ProvenanceError(f"Timed out contacting {url}: {exc}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProvenanceError(f"Response from {url} is not valid JSON: {exc}") from exc


def fetch_ollama_version(host: str, timeout: float) -> str | None:
    payload = _http_get_json(f"{host}/api/version", timeout)
    if isinstance(payload, dict):
        version = payload.get("version")
        if isinstance(version, str) and version:
            return version
    return None


def fetch_model_record(host: str, model: str, timeout: float) -> dict[str, Any]:
    payload = _http_get_json(f"{host}/api/tags", timeout)
    if not isinstance(payload, dict) or not isinstance(payload.get("models"), list):
        raise ProvenanceError(f"{host}/api/tags did not return a models list")
    for entry in payload["models"]:
        if isinstance(entry, dict) and entry.get("name") == model:
            return entry
    available = sorted(
        e.get("name", "?") for e in payload["models"] if isinstance(e, dict)
    )
    raise ProvenanceError(
        f"Model {model!r} is not present on the Ollama server. "
        f"Available models: {available}"
    )


def git_commit(repo_root: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            shell=False,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    commit = completed.stdout.strip()
    return commit or None


def _parse_run_config(value: str | None) -> dict[str, Any]:
    if value is None:
        return {}
    text = value
    if value.startswith("@"):
        path = Path(value[1:])
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ProvenanceError(f"Could not read run-config file {path}: {exc}") from exc
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProvenanceError(f"--run-config is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ProvenanceError("--run-config must decode to a JSON object")
    return parsed


def build_provenance(
    *,
    host: str,
    model: str,
    timeout: float,
    repo_root: Path,
    run_config: dict[str, Any],
) -> dict[str, Any]:
    record = fetch_model_record(host, model, timeout)
    digest = record.get("digest")
    if not isinstance(digest, str) or not digest:
        raise ProvenanceError(
            f"Ollama did not report a digest for {model!r}; cannot certify provenance"
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "collected_at_utc": utc_now(),
        "ollama_host": host,
        "ollama_version": fetch_ollama_version(host, timeout),
        "git_commit": git_commit(repo_root),
        "model": {
            "tag": model,
            "digest": digest,
            "size_bytes": record.get("size"),
            "modified_at": record.get("modified_at"),
            "details": record.get("details"),
            "capabilities": record.get("capabilities"),
        },
        "run_config": run_config,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Exact Ollama model tag used for the run")
    parser.add_argument("--output", required=True, type=Path, help="Where to write provenance JSON")
    parser.add_argument("--host", default=None, help="Ollama host; defaults to OLLAMA_HOST or localhost")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--run-config",
        default=None,
        help="Inline JSON object, or @path to a JSON file, embedded under run_config",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    import os

    args = build_parser().parse_args(argv)
    host = (args.host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
    if args.timeout <= 0:
        print("--timeout must be positive", file=sys.stderr)
        return 2
    try:
        run_config = _parse_run_config(args.run_config)
        provenance = build_provenance(
            host=host,
            model=args.model,
            timeout=args.timeout,
            repo_root=args.repo_root,
            run_config=run_config,
        )
    except ProvenanceError as exc:
        print(f"QEIB provenance error: {exc}", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote provenance for {args.model} (digest {provenance['model']['digest'][:12]}…) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
