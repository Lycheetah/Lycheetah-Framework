"""Explicit recovery decision function for ambiguous provider outcomes.

This module refuses to infer guarantees from a provider's name or a boolean feature flag.
Profiles must be filled from the exact API action's authoritative contract.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class LookupState(str, Enum):
    COMMITTED = "COMMITTED"
    DEFINITIVE_NOT_FOUND = "DEFINITIVE_NOT_FOUND"
    UNKNOWN = "UNKNOWN"

class RecoveryDecision(str, Enum):
    ACCEPT_STORED_RESULT = "ACCEPT_STORED_RESULT"
    RETRY_SAME_KEY = "RETRY_SAME_KEY"
    RECONCILE = "RECONCILE"

@dataclass(frozen=True)
class ProviderContractProfile:
    provider: str
    api_action: str
    durable_idempotency: bool
    payload_mismatch_conflicts: bool
    key_retention_seconds: int | None
    lookup_is_authoritative: bool
    condition_checked_at_effect_commit: bool | None

    def __post_init__(self):
        if not isinstance(self.provider, str) or not self.provider.strip() or not isinstance(self.api_action, str) or not self.api_action.strip():
            raise ValueError("provider and api_action must be explicit")
        for name in ("durable_idempotency", "payload_mismatch_conflicts", "lookup_is_authoritative"):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"{name} must be a boolean")
        if self.condition_checked_at_effect_commit is not None and type(self.condition_checked_at_effect_commit) is not bool:
            raise ValueError("condition_checked_at_effect_commit must be true, false, or unknown")
        if self.key_retention_seconds is not None and (isinstance(self.key_retention_seconds, bool) or not isinstance(self.key_retention_seconds, int) or self.key_retention_seconds < 1):
            raise ValueError("key_retention_seconds must be a positive integer or None")


def classify_ambiguous_recovery(*, profile: ProviderContractProfile,
                                lookup_state: LookupState,
                                elapsed_seconds: float,
                                condition_sensitive: bool = True,
                                lookup_operation_id_matches: bool | None = None,
                                lookup_payload_sha256_matches: bool | None = None) -> RecoveryDecision:
    """Return the only permissible action following an ambiguous provider response.

    COMMITTED is accepted only when the adapter says lookup is authoritative and
    has verified the returned result is bound to the same operation+payload.
    Unknown lookup never becomes permission to replay.
    """
    if elapsed_seconds < 0:
        raise ValueError("elapsed_seconds cannot be negative")
    if lookup_state == LookupState.COMMITTED:
        bound = lookup_operation_id_matches is True and lookup_payload_sha256_matches is True
        return (RecoveryDecision.ACCEPT_STORED_RESULT
                if profile.lookup_is_authoritative and bound
                else RecoveryDecision.RECONCILE)
    if lookup_state == LookupState.UNKNOWN:
        return RecoveryDecision.RECONCILE
    if not profile.lookup_is_authoritative:
        return RecoveryDecision.RECONCILE
    # A retry after definitive not-found is safe only while its dedupe window remains.
    if not profile.durable_idempotency or not profile.payload_mismatch_conflicts:
        return RecoveryDecision.RECONCILE
    if profile.key_retention_seconds is None or elapsed_seconds >= profile.key_retention_seconds:
        return RecoveryDecision.RECONCILE
    if condition_sensitive and profile.condition_checked_at_effect_commit is not True:
        return RecoveryDecision.RECONCILE
    return RecoveryDecision.RETRY_SAME_KEY
