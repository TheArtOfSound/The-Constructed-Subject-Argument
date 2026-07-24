#!/usr/bin/env python3
"""Local tests for QEIB HTTP adapters using an in-process mock server."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class MockHandler(BaseHTTPRequestHandler):
    server_version = "QEIBMock/0.1"

    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def do_POST(self) -> None:  # noqa: N802 - standard library callback
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        request = json.loads(raw or b"{}")

        if self.path == "/v1/chat/completions":
            assert request["model"] == "mock-openai"
            assert request["messages"][-1]["role"] == "user"
            payload = {
                "id": "chatcmpl-qeib-test",
                "model": "mock-openai-reported",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "42"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 11,
                    "completion_tokens": 1,
                    "total_tokens": 12,
                },
                "system_fingerprint": "mock-fingerprint",
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("x-request-id", "req-qeib-test")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        if self.path == "/api/chat":
            assert request["model"] == "mock-ollama"
            assert request["stream"] is False
            payload = {
                "model": "mock-ollama",
                "created_at": "2026-07-24T00:00:00Z",
                "message": {"role": "assistant", "content": "42"},
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 9,
                "eval_count": 1,
                "total_duration": 1000,
                "load_duration": 100,
                "prompt_eval_duration": 200,
                "eval_duration": 300,
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


class AdapterTests(unittest.TestCase):
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

    def request(self) -> str:
        return json.dumps(
            {
                "prompt": "Return only 42.",
                "system_prompt": "Be exact.",
                "seed": 7,
                "temperature": 0,
                "max_tokens": 8,
                "task_id": "mock-task",
                "task_family": "capability_preservation",
                "context_id": "neutral",
                "replicate": 0,
            }
        )

    def test_openai_compatible_adapter(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "QEIB_BASE_URL": f"{self.base_url}/v1",
                "QEIB_MODEL": "mock-openai",
                "QEIB_API_KEY": "not-a-real-secret",
            }
        )
        result = subprocess.run(
            [sys.executable, str(ROOT / "adapters" / "openai_compatible_adapter.py")],
            input=self.request(),
            text=True,
            capture_output=True,
            env=env,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["response_text"], "42")
        self.assertEqual(payload["input_tokens"], 11)
        self.assertEqual(payload["output_tokens"], 1)
        self.assertEqual(payload["provider_request_id"], "req-qeib-test")
        self.assertNotIn("not-a-real-secret", result.stdout)

    def test_ollama_adapter(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "OLLAMA_HOST": self.base_url,
                "QEIB_MODEL": "mock-ollama",
            }
        )
        result = subprocess.run(
            [sys.executable, str(ROOT / "adapters" / "ollama_adapter.py")],
            input=self.request(),
            text=True,
            capture_output=True,
            env=env,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["response_text"], "42")
        self.assertEqual(payload["input_tokens"], 9)
        self.assertEqual(payload["output_tokens"], 1)
        self.assertEqual(payload["metadata"]["done_reason"], "stop")


if __name__ == "__main__":
    unittest.main()
