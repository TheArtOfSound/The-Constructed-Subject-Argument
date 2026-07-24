#!/usr/bin/env python3
"""QEIB adapter for OpenAI-compatible chat-completions endpoints.

Configuration:
  QEIB_BASE_URL       default: https://api.openai.com/v1
  QEIB_API_KEY        required for authenticated endpoints
  QEIB_MODEL          required unless the input request contains model
  QEIB_TIMEOUT        seconds, default 120
  QEIB_SEND_SEED      1 or 0, default 1
  QEIB_EXTRA_HEADERS  optional JSON object
  QEIB_EXTRA_BODY     optional JSON object merged into request body

The adapter reads one QEIB JSON request from stdin and writes one QEIB JSON
response to stdout. Secrets are never included in output metadata.
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


def read_json_env(name: str) -> dict[str, Any]:
    raw = os.environ.get(name)
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"{name} is not valid JSON", detail=str(exc))
    if not isinstance(value, dict):
        fail(f"{name} must decode to a JSON object")
    return value


def extract_content(message: dict[str, Any]) -> str:
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        pieces: list[str] = []
        for block in content:
            if isinstance(block, str):
                pieces.append(block)
            elif isinstance(block, dict):
                text = block.get("text")
                if isinstance(text, str):
                    pieces.append(text)
        return "".join(pieces)
    return str(content)


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

    base_url = os.environ.get("QEIB_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    url = f"{base_url}/chat/completions"
    timeout = float(os.environ.get("QEIB_TIMEOUT", "120"))

    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": float(request_data.get("temperature", 0.0)),
        "max_tokens": int(request_data.get("max_tokens", 64)),
        "stream": False,
    }
    if os.environ.get("QEIB_SEND_SEED", "1") != "0":
        body["seed"] = int(request_data.get("seed", 0))
    body.update(read_json_env("QEIB_EXTRA_BODY"))

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "QEIB/0.1",
    }
    api_key = os.environ.get("QEIB_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    headers.update({str(k): str(v) for k, v in read_json_env("QEIB_EXTRA_HEADERS").items()})

    http_request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(http_request, timeout=timeout) as response:
            response_bytes = response.read()
            response_headers = dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:4000]
        fail(f"HTTP {exc.code} from model endpoint", detail=detail, code=1)
    except urllib.error.URLError as exc:
        fail("Could not reach model endpoint", detail=str(exc), code=1)
    except TimeoutError as exc:
        fail("Model endpoint timed out", detail=str(exc), code=1)

    try:
        payload = json.loads(response_bytes)
    except json.JSONDecodeError as exc:
        fail("Endpoint response is not valid JSON", detail=str(exc), code=1)

    try:
        choice = payload["choices"][0]
        message = choice["message"]
        response_text = extract_content(message)
    except (KeyError, IndexError, TypeError) as exc:
        fail("Endpoint response lacks choices[0].message.content", detail=str(exc), code=1)

    usage = payload.get("usage") or {}
    output = {
        "response_text": response_text,
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "provider_request_id": (
            response_headers.get("x-request-id")
            or response_headers.get("X-Request-Id")
            or payload.get("id")
        ),
        "metadata": {
            "finish_reason": choice.get("finish_reason"),
            "system_fingerprint": payload.get("system_fingerprint"),
            "reported_model": payload.get("model"),
        },
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
