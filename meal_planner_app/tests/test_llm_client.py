"""Ollama client env + error mapping (no live server)."""

import io
import json
import urllib.error

import pytest

from meal_planner_app.ingest.llm_client import (
    DEFAULT_MODEL,
    LlmTimeoutError,
    LlmUnavailableError,
    OllamaClient,
)


def test_from_env_requires_base_url(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    with pytest.raises(LlmUnavailableError):
        OllamaClient.from_env()


def test_from_env_reads_model_and_timeout(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://ollama:11434")
    monkeypatch.setenv("LLM_MODEL", "qwen2.5:3b")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "12")
    client = OllamaClient.from_env()
    assert client.base_url == "http://ollama:11434"
    assert client.model == "qwen2.5:3b"
    assert client.timeout == 12.0


def test_from_env_defaults_model(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://127.0.0.1:11434/")
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LLM_TIMEOUT_SECONDS", raising=False)
    client = OllamaClient.from_env()
    assert client.base_url == "http://127.0.0.1:11434"
    assert client.model == DEFAULT_MODEL


class _FakeResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_complete_json_parses_message_content(monkeypatch):
    client = OllamaClient("http://ollama:11434", "qwen2.5:1.5b", 5)

    def fake_urlopen(request, timeout=None):
        assert request.full_url == "http://ollama:11434/api/chat"
        assert timeout == 5
        body = json.loads(request.data.decode("utf-8"))
        assert body["format"] == "json"
        assert body["stream"] is False
        return _FakeResponse({"message": {"content": json.dumps({"name": "Zupa"})}})

    monkeypatch.setattr(
        "meal_planner_app.ingest.llm_client.urllib.request.urlopen", fake_urlopen
    )
    assert client.complete_json("sys", "user") == {"name": "Zupa"}


def test_complete_json_http_error_is_unavailable(monkeypatch):
    client = OllamaClient("http://ollama:11434", "qwen2.5:1.5b", 5)

    def fake_urlopen(request, timeout=None):
        raise urllib.error.HTTPError(
            "http://ollama:11434/api/chat",
            404,
            "not found",
            hdrs=None,
            fp=io.BytesIO(b""),
        )

    monkeypatch.setattr(
        "meal_planner_app.ingest.llm_client.urllib.request.urlopen", fake_urlopen
    )
    with pytest.raises(LlmUnavailableError):
        client.complete_json("sys", "user")


def test_complete_json_timeout(monkeypatch):
    client = OllamaClient("http://ollama:11434", "qwen2.5:1.5b", 1)

    def fake_urlopen(request, timeout=None):
        raise TimeoutError("timed out")

    monkeypatch.setattr(
        "meal_planner_app.ingest.llm_client.urllib.request.urlopen", fake_urlopen
    )
    with pytest.raises(LlmTimeoutError):
        client.complete_json("sys", "user")
