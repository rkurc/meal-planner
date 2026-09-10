"""Ollama HTTP client (native /api/chat). No SDK."""

import json
import os
import socket
import urllib.error
import urllib.request
from typing import Any, Dict

DEFAULT_MODEL = "qwen2.5:1.5b"
DEFAULT_TIMEOUT = 90.0


class LlmError(Exception):
    """Base class for LLM transport failures."""


class LlmUnavailableError(LlmError):
    """Ollama missing, unreachable, or model not pulled."""


class LlmTimeoutError(LlmError):
    """LLM call exceeded LLM_TIMEOUT_SECONDS."""


class OllamaClient:
    """POST {base}/api/chat with format=json."""

    def __init__(self, base_url: str, model: str, timeout: float):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    @classmethod
    def from_env(cls) -> "OllamaClient":
        base = (os.environ.get("LLM_BASE_URL") or "").strip()
        if not base:
            raise LlmUnavailableError("LLM_BASE_URL is not set")
        model = (os.environ.get("LLM_MODEL") or DEFAULT_MODEL).strip() or DEFAULT_MODEL
        raw_timeout = os.environ.get("LLM_TIMEOUT_SECONDS") or str(DEFAULT_TIMEOUT)
        try:
            timeout = float(raw_timeout)
        except ValueError:
            timeout = DEFAULT_TIMEOUT
        return cls(base, model, timeout)

    def complete_json(self, system: str, user: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except socket.timeout as exc:
            raise LlmTimeoutError("LLM request timed out") from exc
        except TimeoutError as exc:
            raise LlmTimeoutError("LLM request timed out") from exc
        except urllib.error.HTTPError as exc:
            raise LlmUnavailableError(f"LLM HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            reason = exc.reason
            if isinstance(reason, (socket.timeout, TimeoutError)):
                raise LlmTimeoutError("LLM request timed out") from exc
            if "timed out" in str(exc).lower():
                raise LlmTimeoutError("LLM request timed out") from exc
            raise LlmUnavailableError(f"LLM unreachable: {exc}") from exc

        content = (body.get("message") or {}).get("content")
        if content is None:
            content = body.get("response")
        if isinstance(content, dict):
            return content
        if not content:
            raise LlmUnavailableError("LLM returned empty content")
        try:
            parsed = json.loads(content)
        except (TypeError, json.JSONDecodeError) as exc:
            raise LlmUnavailableError("LLM did not return JSON") from exc
        if not isinstance(parsed, dict):
            raise LlmUnavailableError("LLM JSON was not an object")
        return parsed
