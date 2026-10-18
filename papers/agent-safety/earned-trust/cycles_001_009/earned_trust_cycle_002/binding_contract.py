"""Narrow data-contract bridge across tool/approval/provider action representations.

It checks exact canonical payload equality; it is not authorization, provenance,
or proof that either caller is genuine. Authenticated identities must be external.
"""
from __future__ import annotations
from collections.abc import Mapping
from dataclasses import dataclass
from transactional_provider import Intent, canonical, digest

REQUIRED = frozenset({"actor", "subject", "amount_cents", "scope"})


@dataclass(frozen=True)
class BindingCheck:
    valid: bool
    reason: str
    action_sha256: str | None = None


def verify_action_binding(event_arguments: Mapping, guard_action: Mapping, intent: Intent) -> BindingCheck:
    def valid_action(value) -> bool:
        return (isinstance(value, Mapping) and set(value) == REQUIRED
                and all(isinstance(value[k], str) and value[k] for k in ("actor", "subject", "scope"))
                and type(value["amount_cents"]) is int and value["amount_cents"] > 0)
    if not valid_action(event_arguments) or not valid_action(guard_action):
        return BindingCheck(False, "invalid-schema")
    expected = intent.payload()
    if not valid_action(expected):
        return BindingCheck(False, "invalid-provider-intent")
    if canonical(dict(event_arguments)) != canonical(dict(guard_action)):
        return BindingCheck(False, "event-vs-guard-action-mismatch")
    if canonical(dict(guard_action)) != canonical(expected):
        return BindingCheck(False, "guard-vs-provider-action-mismatch")
    return BindingCheck(True, "exact-payload-match", digest(expected))
