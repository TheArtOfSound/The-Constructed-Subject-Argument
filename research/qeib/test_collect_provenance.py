#!/usr/bin/env python3
"""Tests for QEIB run provenance collection using an in-process mock Ollama server."""

from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import collect_provenance  # noqa: E402


MODEL_RECORD = {
    "name": "mock-model:tiny",
    "model": "mock-model:tiny",
    "modified_at": "2026-07-24T00:00:00Z",
    "size": 123456,
    "digest": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    "details": {
        "format": "gguf",
        "family": "mock",
        "parameter_size": "0.3B",
        "quantization_level": "Q8_0",
    },
    "capabilities": ["completion"],
}


class MockHandler(BaseHTTPRequestHandler):
    server_version = "QEIBMock/0.1"

    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def do_GET(self) -> None:  # noqa: N802 - standard library callback
        if self.path == "/api/version":
            body = json.dumps({"version": "9.9.9-mock"}).encode("utf-8")
        elif self.path == "/api/tags":
            body = json.dumps({"models": [MODEL_RECORD]}).encode("utf-8")
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)


class ProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), MockHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_collects_digest_version_and_run_config(self) -> None:
        provenance = collect_provenance.build_provenance(
            host=self.base_url,
            model="mock-model:tiny",
            timeout=5.0,
            repo_root=ROOT,
            run_config={"tasks": "dev_math_001", "max_tokens": 16},
        )
        self.assertEqual(provenance["schema_version"], collect_provenance.SCHEMA_VERSION)
        self.assertEqual(provenance["ollama_version"], "9.9.9-mock")
        self.assertEqual(provenance["model"]["tag"], "mock-model:tiny")
        self.assertEqual(provenance["model"]["digest"], MODEL_RECORD["digest"])
        self.assertEqual(provenance["model"]["size_bytes"], 123456)
        self.assertEqual(provenance["model"]["details"]["parameter_size"], "0.3B")
        self.assertEqual(provenance["run_config"]["max_tokens"], 16)

    def test_missing_model_fails_clearly(self) -> None:
        with self.assertRaises(collect_provenance.ProvenanceError):
            collect_provenance.build_provenance(
                host=self.base_url,
                model="not-present:tag",
                timeout=5.0,
                repo_root=ROOT,
                run_config={},
            )

    def test_parse_run_config_rejects_non_object(self) -> None:
        with self.assertRaises(collect_provenance.ProvenanceError):
            collect_provenance._parse_run_config("[1, 2, 3]")

    def test_parse_run_config_accepts_none(self) -> None:
        self.assertEqual(collect_provenance._parse_run_config(None), {})


if __name__ == "__main__":
    unittest.main()
