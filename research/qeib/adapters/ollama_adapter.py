#!/usr/bin/env python3
"""QEIB adapter for a local or remote Ollama chat endpoint.

Configuration:
  OLLAMA_HOST        default: http://localhost:11434
  QEIB_MODEL         required, for example qwen2.5:0.5b-instruct
  QEIB_TIMEOUT       seconds, default 300
  QEIB_KEEP_ALIVE    default: 15m
  QEIB_OLLAMA_BODY   optional JSON object merged into the request body

The adapter reads one QEIB JSON request from stdin and writes one QEIB JSON
response to stdout. Ollama keeps the model loaded between adapter invocations
when keep_alive is enabled, so the provider-neutral QEIB runner can call this
script repeatedly without reloading model weights every time.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any


def fail(message: str, *, detail: Any = None, code: int = 2) -> None:
    payload: dict[str, Any] = {"error": message}
    if detail is not None:
        payload["detail"] = detail
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(code)


def read_extra_body() -> dict[str, Any]:
    raw = os.environ.get("QEIB_OLLAMA_BODY")
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail("QEIB_OLLAMA_BODY is not valid JSON", detail=str(exc))
    if not isinstance(value, dict):
        fail("QEIB_OLLAMA_BODY must decode to an object")
    return value


def main() -> int:
    try:
        request_data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        fail("stdin is not valid JSON", detail=str(exc))

    if not isinstance(request_data, dict):
        fail("stdin JSON must be an object")

    prompt = request_data.get("prompt")
    if not isinstance(prompt, str) or not prompt:
        fail("request.prompt must be a non-empty string")

    model = request_data.get("model") or os.environ.get("QEIB_MODEL")
    if not model:
        fail("Set QEIB_MODEL or provide request.model")

    system_prompt = request_data.get("system_prompt") or ""
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": str(system_prompt)})
    messages.append({"role": "user", "content": prompt})

    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    url = f"{host}/api/chat"
    timeout = float(os.environ.get("QEIB_TIMEOUT", "300"))

    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
        "keep_alive": os.environ.get("QEIB_KEEP_ALIVE", "15m"),
        "options": {
            "temperature": float(request_data.get("temperature", 0.0)),
            "seed": int(request_data.get("seed", 0)),
            "num_predict": int(request_data.get("max_tokens", 64)),
        },
    }
    body.update(read_extra_body())

    http_request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "QEIB/0.1",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(http_request, timeout=timeout) as response:
            response_bytes = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:4000]
        fail(f"HTTP {exc.code} from Ollama", detail=detail, code=1)
    except urllib.error.URLError as exc:
        fail("Could not reach Ollama", detail=str(exc), code=1)
    except TimeoutError as exc:
        fail("Ollama request timed out", detail=str(exc), code=1)

    try:
        payload = json.loads(response_bytes)
    except json.JSONDecodeError as exc:
        fail("Ollama response is not valid JSON", detail=str(exc), code=1)

    message = payload.get("message")
    if not isinstance(message, dict) or not isinstance(message.get("content"), str):
        fail("Ollama response lacks message.content", detail=payload, code=1)

    output = {
        "response_text": message["content"],
        "input_tokens": payload.get("prompt_eval_count"),
        "output_tokens": payload.get("eval_count"),
        "provider_request_id": None,
        "metadata": {
            "reported_model": payload.get("model"),
            "created_at": payload.get("created_at"),
            "done_reason": payload.get("done_reason"),
            "total_duration_ns": payload.get("total_duration"),
            "load_duration_ns": payload.get("load_duration"),
            "prompt_eval_duration_ns": payload.get("prompt_eval_duration"),
            "eval_duration_ns": payload.get("eval_duration"),
        },
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
