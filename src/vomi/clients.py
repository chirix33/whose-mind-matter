"""Minimal model-client interface: an OpenAI-compatible HTTP client (stdlib only) and a mock.

Usage accounting rules (AGENTS.md §7): reasoning tokens are recorded only when the server
reports them; an unavailable count is ``None``, never 0. Latency uses a monotonic clock.
"""

from __future__ import annotations

import json
import os
import threading
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


REPO_DOTENV = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")


def load_dotenv(path: str) -> list[str]:
    """Minimal KEY=value loader for the gitignored repo .env. Sets only variables not already set;
    returns the NAMES it set (never values)."""
    if not os.path.exists(path):
        return []
    names = []
    for line in open(path, encoding="utf-8-sig"):
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        key, val = s.removeprefix("export ").split("=", 1)
        key, val = key.strip(), val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
            val = val[1:-1]
        if key and key not in os.environ:
            os.environ[key] = val
            names.append(key)
    return names


class BudgetExceeded(RuntimeError):
    pass


class SpendLedger:
    """Persistent USD spend ledger with a hard cap (estimated from reported usage x configured prices).

    One authoritative file shared by every process: each operation takes an exclusive file lock (``<path>.lock``,
    fcntl) and re-reads the file, so concurrent local processes and threads see each other's reservations.
    Before each call it refuses if spent + unresolved + all in-flight reservations + the call's worst case would
    exceed the cap. Outcomes: ``record`` (usage reported), ``release`` (the server answered with an error status,
    so nothing was billed), ``unresolve`` (ambiguous transport failure: the worst case stays charged as
    ``unresolved_usd``, never assumed free). A reservation left by a crashed process also stays counted."""

    def __init__(self, path: str, cap_usd: float, price_in: float, price_out: float):
        self.path, self.cap = path, cap_usd
        self.price_in, self.price_out = price_in / 1e6, price_out / 1e6
        self._tlock = threading.Lock()

    @staticmethod
    def _defaults(state: dict) -> dict:
        state.setdefault("spent_usd", 0.0)
        state.setdefault("calls", 0)
        state.setdefault("reserved", {})
        state.setdefault("unresolved_usd", 0.0)
        state.setdefault("unresolved_calls", 0)
        return state

    def _locked(self, fn):
        import fcntl
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with self._tlock, open(self.path + ".lock", "a") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            try:
                state = self._defaults(json.loads(open(self.path).read()) if os.path.exists(self.path) else {})
                result = fn(state)
                tmp = f"{self.path}.{os.getpid()}.tmp"
                with open(tmp, "w") as f:
                    json.dump(state, f)
                os.replace(tmp, self.path)
                return result
            finally:
                fcntl.flock(lk, fcntl.LOCK_UN)

    @property
    def state(self) -> dict:
        return self._locked(lambda s: dict(s))

    @property
    def reserved(self) -> float:
        return sum(self.state["reserved"].values())

    def check(self, est_in: int, max_out: int) -> str:
        """Reserve the call's worst-case cost; returns a reservation id for record()/release()/unresolve()."""
        worst = est_in * self.price_in + max_out * self.price_out
        rid = f"{os.getpid()}-{threading.get_ident()}-{time.monotonic_ns()}"

        def op(s):
            committed = s["spent_usd"] + s["unresolved_usd"] + sum(s["reserved"].values())
            if committed + worst > self.cap:
                raise BudgetExceeded(f"cap {self.cap} USD: spent {s['spent_usd']:.4f} + unresolved {s['unresolved_usd']:.4f}"
                                     f" + in-flight {sum(s['reserved'].values()):.4f} + worst-case {worst:.4f}")
            s["reserved"][rid] = worst
        self._locked(op)
        return rid

    def release(self, rid: str) -> None:
        self._locked(lambda s: s["reserved"].pop(rid, None))

    def unresolve(self, rid: str) -> None:
        def op(s):
            s["unresolved_usd"] += s["reserved"].pop(rid, 0.0)
            s["unresolved_calls"] += 1
        self._locked(op)

    def record(self, tokens_in: int | None, tokens_out: int | None, rid: str | None = None) -> float:
        cost = (tokens_in or 0) * self.price_in + (tokens_out or 0) * self.price_out

        def op(s):
            if rid is not None:
                s["reserved"].pop(rid, None)
            s["spent_usd"] += cost
            s["calls"] += 1
        self._locked(op)
        return cost


class OpenAIResponsesClient:
    """Official OpenAI Responses API adapter (stdlib HTTP). Request mapping, checked against the official
    docs on 2026-10-28: response_format json_schema -> text.format {type json_schema, name, schema, strict};
    reasoning_effort -> reasoning.effort; max_tokens -> max_output_tokens; `temperature` is not sent
    (reasoning models). Incomplete (status incomplete, e.g. max_output_tokens) and refusal content items
    are returned as errors, never parsed. Billed output tokens include reasoning tokens."""

    URL = "https://api.openai.com/v1/responses"

    def __init__(self, model: str, api_key_env: str, ledger: SpendLedger, timeout_s: float = 600.0):
        self.model, self.ledger, self.timeout_s = model, ledger, timeout_s
        self.api_key = os.environ.get(api_key_env, "")
        if not self.api_key:
            raise RuntimeError(f"environment variable {api_key_env} is not set (configure it locally; never commit it)")

    def list_models(self) -> list[str]:
        return [self.model]

    @staticmethod
    def request_body(model: str, messages: list[dict], params: dict) -> dict:
        body = {"model": model, "input": [{"role": m["role"] if m["role"] != "system" else "developer",
                                           "content": m["content"]} for m in messages]}
        if "reasoning_effort" in params:
            body["reasoning"] = {"effort": params["reasoning_effort"]}
        if "max_tokens" in params:
            body["max_output_tokens"] = params["max_tokens"]
        rf = params.get("response_format")
        if rf and rf.get("type") == "json_schema":
            body["text"] = {"format": {"type": "json_schema", "name": rf["json_schema"]["name"],
                                       "schema": rf["json_schema"]["schema"], "strict": True}}
        return body

    def chat(self, messages: list[dict], **params) -> ChatResult:
        body = self.request_body(self.model, messages, params)
        est_in = sum(len(m["content"]) for m in messages) // 3 + 200  # conservative chars->tokens
        reservation = self.ledger.check(est_in, params.get("max_tokens", 4096))
        req = urllib.request.Request(self.URL, data=json.dumps(body).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {self.api_key}")
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                out = json.loads(resp.read())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if isinstance(e, urllib.error.HTTPError):  # the server answered with an error status: not billed
                self.ledger.release(reservation)
            else:  # no usable answer (timeout, dropped connection, unreadable body): billing unknown
                self.ledger.unresolve(reservation)
            detail = e.read().decode(errors="replace")[:500] if isinstance(e, urllib.error.HTTPError) else ""
            return ChatResult("", None, self.model, None, None, None, None, time.monotonic() - start,
                              error=f"{type(e).__name__}: {e} {detail}".strip())
        latency = time.monotonic() - start
        usage = out.get("usage") or {}
        rin, rout = usage.get("input_tokens"), usage.get("output_tokens")
        self.ledger.record(rin, rout, reservation)
        text, refusal = "", None
        for item in out.get("output", []):
            if item.get("type") == "message":
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        text += c.get("text", "")
                    elif c.get("type") == "refusal":
                        refusal = c.get("refusal", "refused")
        status = out.get("status")
        error = None
        if status == "incomplete":
            error = f"incomplete: {(out.get('incomplete_details') or {}).get('reason')}"
        elif refusal is not None:
            error = f"refusal: {refusal[:200]}"
        return ChatResult(text if error is None else "", None, out.get("model", self.model), status, rin, rout,
                          (usage.get("output_tokens_details") or {}).get("reasoning_tokens"), latency,
                          error=error, raw_usage=usage)


def make_client(cfg: dict) -> ChatClient:
    if cfg["provider"] == "openai_compat":
        return OpenAICompatClient(cfg["base_url"], cfg["model"], cfg.get("api_key_env"), cfg.get("timeout_s", 300.0))
    if cfg["provider"] == "openai_responses":
        if not os.environ.get(cfg["api_key_env"]):
            load_dotenv(REPO_DOTENV)
        b = cfg["budget"]
        ledger = SpendLedger(os.path.expanduser(b["ledger_path"]), float(os.environ.get(b.get("cap_env", ""), b["cap_usd"])),
                             cfg["price_per_mtok"]["input"], cfg["price_per_mtok"]["output"])
        return OpenAIResponsesClient(cfg["model"], cfg["api_key_env"], ledger, cfg.get("timeout_s", 600.0))
    raise ValueError(f"unknown provider {cfg['provider']}")
