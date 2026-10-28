"""Minimal model-client interface: an OpenAI-compatible HTTP client (stdlib only) and a mock.

Usage accounting rules (AGENTS.md §7): reasoning tokens are recorded only when the server
reports them; an unavailable count is ``None``, never 0. Latency uses a monotonic clock.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class ChatResult:
    text: str
    reasoning: str | None
    model: str
    finish_reason: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    reasoning_tokens: int | None
    latency_s: float
    error: str | None = None
    raw_usage: dict = field(default_factory=dict)


class ChatClient(Protocol):
    def chat(self, messages: list[dict], **params) -> ChatResult: ...


class OpenAICompatClient:
    """Talks to any OpenAI-compatible /v1/chat/completions endpoint (local vLLM first)."""

    def __init__(self, base_url: str, model: str, api_key_env: str | None = None, timeout_s: float = 300.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = os.environ.get(api_key_env, "") if api_key_env else ""
        self.timeout_s = timeout_s

    def _request(self, path: str, payload: dict | None = None) -> dict:
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(self.base_url + path, data=data, method="POST" if data else "GET")
        req.add_header("Content-Type", "application/json")
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            return json.loads(resp.read())

    def list_models(self) -> list[str]:
        return [m["id"] for m in self._request("/v1/models")["data"]]

    def chat(self, messages: list[dict], **params) -> ChatResult:
        payload = {"model": self.model, "messages": messages, **params}
        start = time.monotonic()
        try:
            body = self._request("/v1/chat/completions", payload)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            detail = e.read().decode(errors="replace")[:500] if isinstance(e, urllib.error.HTTPError) else ""
            return ChatResult("", None, self.model, None, None, None, None, time.monotonic() - start,
                              error=f"{type(e).__name__}: {e} {detail}".strip())
        latency = time.monotonic() - start
        choice = body["choices"][0]
        msg = choice.get("message", {})
        usage = body.get("usage") or {}
        details = usage.get("completion_tokens_details") or {}
        return ChatResult(
            text=msg.get("content") or "",
            reasoning=msg.get("reasoning_content") or msg.get("reasoning"),
            model=body.get("model", self.model),
            finish_reason=choice.get("finish_reason"),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            reasoning_tokens=details.get("reasoning_tokens"),  # None when not reported
            latency_s=latency,
            raw_usage=usage,
        )


class MockClient:
    """Scripted responses for tests; never used for real evaluations."""

    def __init__(self, responses: list[str], model: str = "mock"):
        self.responses = list(responses)
        self.model = model
        self.calls: list[list[dict]] = []

    def chat(self, messages: list[dict], **params) -> ChatResult:
        self.calls.append(messages)
        text = self.responses.pop(0)
        return ChatResult(text, None, self.model, "stop", None, None, None, 0.0)


def make_client(cfg: dict) -> ChatClient:
    if cfg["provider"] == "openai_compat":
        return OpenAICompatClient(cfg["base_url"], cfg["model"], cfg.get("api_key_env"), cfg.get("timeout_s", 300.0))
    raise ValueError(f"unknown provider {cfg['provider']}")
