"""Three reference approval layers for the suite. Read these before trusting the scorecard.

naive         The minimum interrupt-and-approve loop: approval is a boolean on a pending
              call; on resume the call runs as it is now stored.
conventional  What a careful engineer writes without Lycheetah: a single-use token bound to
              the SHA-256 of the exact action, a TTL, per-actor revocation, and a lock around
              consume-and-run. It is meant to be a fair, strong baseline, not a strawman.
lycheetah     A thin translation onto lycheetah.assurance.ActionGateway.open_local.
"""

from __future__ import annotations

import copy
import tempfile
import threading
import time
import uuid
from typing import Any

from suite import digest, render_bound


class NaiveLayer:
    name = "naive"

    def __init__(self) -> None:
        self.pending: dict[str, dict[str, Any]] = {}

    def request(self, action, actor):
        tid = uuid.uuid4().hex
        self.pending[tid] = {"action": copy.deepcopy(action), "approved": False}
        return tid

    def approve(self, ticket, approver, ttl_seconds=300):
        self.pending[ticket]["approved"] = True

    def execute(self, ticket, live_action, tool):
        p = self.pending[ticket]
        if not p["approved"]:
            return "REFUSED"
        p["action"] = live_action  # resume runs the call as currently stored
        try:
            tool(p["action"])
            return "EXECUTED"
        except TimeoutError:
            return "FAILED"

    def revoke(self, actor):
        pass  # this pattern has no revocation of a pending approval

    def summary(self, ticket):
        p = self.pending[ticket]["action"]  # the screen shows the agent's explanation
        return p.get("description") or p.get("tool", "")


class ConventionalLayer:
    name = "conventional"

    def __init__(self) -> None:
        self.requests: dict[str, tuple[dict[str, Any], str]] = {}
        self.tokens: dict[str, dict[str, Any]] = {}
        self.epochs: dict[str, int] = {}
        self.lock = threading.Lock()

    def request(self, action, actor):
        tid = uuid.uuid4().hex
        self.requests[tid] = (copy.deepcopy(action), actor)
        return tid

    def approve(self, ticket, approver, ttl_seconds=300):
        action, actor = self.requests[ticket]
        self.tokens[ticket] = {"digest": digest(action), "actor": actor, "approver": approver,
                               "expires": time.monotonic() + ttl_seconds,
                               "epoch": self.epochs.get(actor, 0), "used": False}

    def execute(self, ticket, live_action, tool):
        with self.lock:
            tok = self.tokens.get(ticket)
            if (tok is None or tok["used"] or time.monotonic() > tok["expires"]
                    or tok["epoch"] != self.epochs.get(tok["actor"], 0)
                    or digest(live_action) != tok["digest"]):
                return "REFUSED"
            tok["used"] = True
            try:
                tool(live_action)
                return "EXECUTED"
            except TimeoutError:
                return "FAILED"

    def revoke(self, actor):
        with self.lock:
            self.epochs[actor] = self.epochs.get(actor, 0) + 1


class ConventionalPlusLayer(ConventionalLayer):
    """Added AFTER the pre-registered run (see RESULTS.md): the conventional baseline plus
    the one idea C6 tests. A timeout is not a failure; the action stays unresolved, and no
    new approval for the same exact action is honoured until someone reconciles it."""

    name = "conventional+"

    def __init__(self) -> None:
        super().__init__()
        self.unresolved: set[str] = set()

    def approve(self, ticket, approver, ttl_seconds=300):
        if digest(self.requests[ticket][0]) in self.unresolved:
            return  # refuse to issue a token until reconciled
        super().approve(ticket, approver, ttl_seconds)

    def execute(self, ticket, live_action, tool):
        out = super().execute(ticket, live_action, tool)
        if out == "FAILED":  # the provider may have acted; we do not know
            self.unresolved.add(digest(live_action))
            return "UNKNOWN"
        return out

    def reconcile(self, action, happened: bool):
        self.unresolved.discard(digest(action))

    def summary(self, ticket):
        # Added after the C10 run (PREDICTIONS_C10.md): render the bound action itself.
        return render_bound(self.requests[ticket][0])


class LycheetahGatewayLayer:
    name = "lycheetah"
    _MAP = {"SUCCEEDED": "EXECUTED", "UNKNOWN": "UNKNOWN", "FAILED": "FAILED"}

    def __init__(self, workspace: str | None = None) -> None:
        from lycheetah.assurance import ActionGateway

        self.gateway = ActionGateway.open_local(workspace or tempfile.mkdtemp(prefix="ais-"))
        self.requests: dict[str, tuple[dict[str, Any], str]] = {}
        self.effects: dict[str, str] = {}

    def request(self, action, actor):
        tid = uuid.uuid4().hex
        self.requests[tid] = (copy.deepcopy(action), actor)
        return tid

    def approve(self, ticket, approver, ttl_seconds=300):
        action, actor = self.requests[ticket]
        d = self.gateway.propose(action, actor=actor, scope="tools:write",
                                 approver_id=approver, ttl_seconds=ttl_seconds)
        if d.allowed and d.effect_id:
            self.effects[ticket] = d.effect_id

    def execute(self, ticket, live_action, tool):
        eid = self.effects.get(ticket)
        if eid is None:  # no recorded approval: ask the gateway, with no approver
            action, actor = self.requests[ticket]
            d = self.gateway.propose(action, actor=actor, scope="tools:write")
            if not (d.allowed and d.effect_id):
                return "REFUSED"
            eid = d.effect_id

        def run():
            try:
                tool(live_action)
                return {"status": "success"}
            except TimeoutError:
                return {"status": "timeout"}  # neither success nor failure: UNKNOWN

        r = self.gateway.dispatch(eid, run, current_action=live_action)
        return self._MAP.get(r.status, "REFUSED")

    def revoke(self, actor):
        self.gateway.workflow.revoke_all(actor, int(time.time()))


def available() -> dict[str, Any]:
    out: dict[str, Any] = {"naive": NaiveLayer, "conventional": ConventionalLayer,
                           "conventional+": ConventionalPlusLayer}
    try:
        import lycheetah.assurance  # noqa: F401
        out["lycheetah"] = LycheetahGatewayLayer
    except ImportError:
        pass
    return out
