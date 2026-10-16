"""Compose the v3.4 quorum verifier with an external one-use spent-nonce registry.

Safety ordering: validate local persisted challenge, verify signed/current witness
reports, atomically consume nonce in the independently administered registry, then
consume the local challenge. If the process fails after remote consumption but before
local commit, the nonce is burned and the operation fails closed (availability loss).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from checkpoint_witness_quorum import Head, verify_current_chain
from durable_freshness_verifier import (
    ChallengeLifecycleError, DurableFreshnessVerifier, FreshnessChallenge,
)
from spent_nonce_registry import SpentChallengeRegistryClient, RegistryProtocolError


@dataclass(frozen=True)
class RemoteFreshnessChallenge:
    database_id: str
    nonce: str
    issued_at_ms: int
    expires_at_ms: int
    policy_sha256: str


class RemoteMonotonicFreshnessVerifier:
    """Freshness verifier whose one-use marker is consumed by an external registry."""
    def __init__(self, local_verifier: DurableFreshnessVerifier, registry: SpentChallengeRegistryClient):
        if not isinstance(local_verifier, DurableFreshnessVerifier):
            raise TypeError("local_verifier-must-be-DurableFreshnessVerifier")
        if not isinstance(registry, SpentChallengeRegistryClient):
            raise TypeError("registry-must-be-SpentChallengeRegistryClient")
        self.local = local_verifier
        self.registry = registry

    def issue(self, database_id: str) -> RemoteFreshnessChallenge:
        local_challenge = self.local.issue(database_id)
        row = self.local._load_pending(local_challenge.nonce, database_id=database_id)
        challenge = RemoteFreshnessChallenge(
            database_id=row["database_id"], nonce=row["nonce"],
            issued_at_ms=row["issued_at_ms"], expires_at_ms=row["expires_at_ms"],
            policy_sha256=row["policy_sha256"],
        )
        # Do not return a challenge to the caller unless the monotonic service has
        # durably registered it. If this call times out, local state may be orphaned;
        # caller must request a new challenge rather than guessing registration status.
        self.registry.register(challenge)
        return challenge

    def verify_and_consume(
        self,
        certificates: Sequence[Mapping[str, Any]],
        freshness_reports: Sequence[Mapping[str, Any]],
        challenge: RemoteFreshnessChallenge,
    ) -> tuple[Head, ...]:
        if not isinstance(challenge, RemoteFreshnessChallenge):
            raise ChallengeLifecycleError("remote-challenge-envelope-invalid")
        local_challenge = FreshnessChallenge(
            challenge.database_id, challenge.nonce,
            challenge.issued_at_ms, challenge.expires_at_ms,
        )
        row = self.local._load_pending(challenge.nonce, database_id=challenge.database_id)
        # The returned challenge is only a reference. Its policy and time fields must
        # exactly match the HMAC-authenticated local issue row.
        if (challenge.issued_at_ms != row["issued_at_ms"]
                or challenge.expires_at_ms != row["expires_at_ms"]
                or challenge.policy_sha256 != row["policy_sha256"]):
            raise ChallengeLifecycleError("remote-challenge-local-binding-mismatch")
        # Verify expensive cryptographic evidence before irreversibly consuming the
        # external nonce. This mirrors the v3.4 verifier's validation contract.
        heads = verify_current_chain(
            list(certificates), list(freshness_reports),
            self.local._anchor_key_registry, self.local._witness_key_registry,
            database_id=row["database_id"], challenge_nonce=row["nonce"],
            max_byzantine=row["max_byzantine"],
            max_clock_skew_seconds=row["max_clock_skew_seconds"],
        )
        # External CAS is authoritative against primary-ledger-only rollback. Failure,
        # a lost response, or a consumed nonce is fail-closed; never infer success.
        self.registry.consume(challenge)
        # Revalidate/consume the local ledger too. If local state changed or the
        # process fails after external consume, retry cannot pass the remote registry.
        locally_verified_heads = self.local.verify_and_consume(
            list(certificates), list(freshness_reports), local_challenge,
        )
        if tuple(h.record_sha256 for h in locally_verified_heads) != tuple(h.record_sha256 for h in heads):
            raise ChallengeLifecycleError("local-remote-head-result-mismatch")
        return locally_verified_heads
