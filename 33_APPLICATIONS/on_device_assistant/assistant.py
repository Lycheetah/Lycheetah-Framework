#!/usr/bin/env python3
"""Lycheetah on-device assistant — a runnable skeleton.  [SCAFFOLD]

The model thinks; Lycheetah decides what may leave the device and keeps a receipt.

- The model runs locally (Ollama on the user's machine) or is a scripted stand-in for tests.
- Anything that leaves the device (a web fetch) is a gated action: the person sees the exact
  bound action rendered from the bytes that are hashed, approves or refuses, and the
  ActionGateway binds that approval to that action.
- The approval layer below IS an Approval Integrity Suite adapter, so the suite's score
  applies to the code path this app uses (tests/test_on_device_assistant.py).

Run:  python3 assistant.py --stand-in "What is the weather in Dunedin?"
      python3 assistant.py --model qwen3.5:4b "..."    # needs Ollama running locally (UNVERIFIED here)

Nothing here trains, benchmarks or ships a model.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SUITE = Path(__file__).resolve().parents[2] / "papers" / "agent-safety" / "approval-integrity-suite"
sys.path.insert(0, str(SUITE))

from adapters import LycheetahGatewayLayer  # noqa: E402  one implementation, shared with the suite
from suite import render_bound  # noqa: E402

SYSTEM = (
    "You are a careful assistant running on the user's own device. If you need something from "
    "the internet, reply with ONLY one JSON line: {\"tool\": \"web.fetch\", \"arguments\": "
    "{\"url\": \"https://...\"}, \"description\": \"why\"}. Otherwise answer plainly, and say "
    "when you are unsure."
)


class ApprovalLayer(LycheetahGatewayLayer):
    """The gateway adapter plus a screen built from the bound action (the suite's C10)."""

    name = "on-device-assistant"

    def summary(self, ticket: str) -> str:
        return render_bound(self.requests[ticket][0])


# -- models -----------------------------------------------------------------------

class StandInModel:
    """Scripted model for tests and demos: asks for one fetch, then answers from it."""

    def __init__(self, url: str = "https://example.org/") -> None:
        self.url = url

    def chat(self, messages: list[dict[str, str]]) -> str:
        if not any(m["role"] == "tool" for m in messages):
            return json.dumps({"tool": "web.fetch", "arguments": {"url": self.url},
                               "description": "look this up"})
        tool_text = [m["content"] for m in messages if m["role"] == "tool"][-1]
        return f"Based on what I fetched ({len(tool_text)} characters): {tool_text[:120]}"


class OllamaModel:
    """A model served by Ollama on this machine. Nothing leaves the device for thinking."""

    def __init__(self, model: str, host: str = "http://127.0.0.1:11434") -> None:
        self.model, self.host = model, host

    def chat(self, messages: list[dict[str, str]]) -> str:
        body = json.dumps({"model": self.model, "messages": messages, "stream": False}).encode()
        req = urllib.request.Request(f"{self.host}/api/chat", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read())["message"]["content"]


# -- tools --------------------------------------------------------------------------

def web_fetch(arguments: dict[str, Any], limit: int = 4000) -> str:
    url = str(arguments.get("url", ""))
    if not url.startswith("https://"):
        raise ValueError("only https URLs are fetched")
    with urllib.request.urlopen(url, timeout=20) as resp:
        return resp.read(limit).decode("utf-8", errors="replace")


@dataclass
class Assistant:
    model: Any
    approve: Callable[[str], bool]                  # shown the bound action; returns the decision
    fetch: Callable[[dict[str, Any]], str] = web_fetch
    workspace: str = field(default_factory=lambda: tempfile.mkdtemp(prefix="lycheetah-assistant-"))
    max_steps: int = 4
    log: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.layer = ApprovalLayer(self.workspace)

    def ask(self, question: str) -> str:
        messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
        for _ in range(self.max_steps):
            reply = self.model.chat(messages).strip()
            call = _tool_call(reply)
            if call is None:
                return reply
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "tool", "content": self._gated(call)})
        return "Stopped: step budget reached without an answer."

    def _gated(self, call: dict[str, Any]) -> str:
        action = {"tool": call["tool"], "side_effect": True,  # leaving the device is gated
                  "arguments": call.get("arguments", {}), "description": call.get("description", "")}
        ticket = self.layer.request(action, "assistant")
        if not self.approve(self.layer.summary(ticket)):
            self.log.append({"action": action, "outcome": "REFUSED_BY_PERSON"})
            return "The person declined this request. Answer without it, or ask them."
        self.layer.approve(ticket, "device-owner")
        result: dict[str, str] = {}

        def tool(live: dict[str, Any]) -> dict[str, Any]:
            if live["tool"] != "web.fetch":
                raise ValueError(f"unknown tool {live['tool']}")
            result["text"] = self.fetch(live["arguments"])
            return {"ok": True}

        outcome = self.layer.execute(ticket, action, tool)
        self.log.append({"action": action, "outcome": outcome})
        if outcome == "EXECUTED":
            return result.get("text", "")
        return f"The request was not completed ({outcome}). Do not assume it happened."


def _tool_call(reply: str) -> dict[str, Any] | None:
    if not reply.startswith("{"):
        return None
    try:
        obj = json.loads(reply.splitlines()[0])
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) and "tool" in obj else None


def _terminal_approve(screen: str) -> bool:
    print("\n--- The assistant wants to leave your device ---")
    print(screen)
    return input("Allow this? [y/N] ").strip().lower() == "y"


def main() -> int:
    ap = argparse.ArgumentParser(description="Lycheetah on-device assistant (skeleton)")
    ap.add_argument("question")
    ap.add_argument("--model", help="Ollama model name, e.g. qwen3.5:4b")
    ap.add_argument("--stand-in", action="store_true", help="use the scripted stand-in model")
    args = ap.parse_args()
    model = StandInModel() if args.stand_in or not args.model else OllamaModel(args.model)
    bot = Assistant(model=model, approve=_terminal_approve)
    print("\n" + bot.ask(args.question))
    print(f"\nReceipts and ledger: {bot.workspace}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
