"""Unified Sovereign Execution Harness (`lycheetah.sovereign_harness`).

Integrates three bounded control mechanisms into a local execution harness:
1. `ConsensusArena` (`lycheetah.consensus`): multi-agent Psi-Consensus gossip,
   connectivity/local-consistency checks and Grey Mode quarantine.
2. `CompactionShield` (`lycheetah.compaction`): 10-field constitutional state
   compaction and semantic collapse detection (`LAMAGUE-SEMANTIC-PACKET-1`).
3. `ActionGateway` (`lycheetah.assurance`): evidence-capped policy evaluation,
   human checkpoint enforcement, and monotonic Ed25519-anchored receipts.

Why Two Hashes Alone Are Insufficient
-------------------------------------
Holding a valid `consensus_digest` and `compaction_critical_hash` does not by
itself establish permission to execute an action. Without explicit binding,
those two digests could be replayed across turns, attached to a mutated action
payload, invoked outside the approved scope, applied after the underlying world
state has changed, or used after expiry.

`SovereignExecutionPermit` and `SovereignExecutionHarness` bind consensus and
preserved context to:
- the exact canonical action digest (`action_hash`),
- the proposing actor and explicit human/checkpoint authority (`authority_id`),
- the authorized scope set and bound target scope (`allowed_scopes`, `bound_scope`),
- the issuing reference packet's declared risk (`bound_risk`),
- the pinned environment/state version (`state_version`),
- the validity window (`issued_at`, `expires_at`), and
- a persistent SQLite single-use replay ledger (`PermitNonceStore`).

Epistemic & Scientific Boundaries
---------------------------------
- `obstruction_free=True` reports connectivity and pairwise vector consistency
  under configured thresholds. It does not compute H^1 or establish truth.
- The digest is recomputed at permit issuance and execution. Its v2 payload binds
  the anchor and complete outcome without authenticating an external issuer.
- `CompactionShield` verification establishes preservation of the 10 schema
  accountability fields (`CRITICAL_FIELDS`); it does NOT prove lossless general
  reasoning.
- `SovereignWitnessReceipt` proves local enforcement across the configured
  harness and SQLite ledgers; it is not an OS-kernel sandbox.
- `authority_id` and `packet.authority` validate declared packet grant metadata
  and exact scope binding; identity strings alone do not establish externally
  authenticated human approval.
"""

from __future__ import annotations

import json
import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal

from .assurance import (
    ActionGateway,
    AssurancePolicy,
    Disposition,
    ExecutionResult,
    action_digest,
)
from .compaction import (
    VALID_RISKS,
    AgentStatePacket,
    CodecError,
    CompactionShield,
)
from .consensus import (
    ConsensusArena,
    DeliberationVerdict,
)

HARNESS_SCHEMA_VERSION = "lycheetah.sovereign_harness.v1"
PERMIT_SCHEMA_VERSION = "lycheetah.sovereign_permit.v2"

EPISTEMIC_BOUNDARIES: tuple[str, ...] = (
    "zero_h1_proves_pairwise_vector_agreement_not_factual_correctness",
    "compaction_shield_proves_10_accountability_fields_not_lossless_reasoning",
    "sovereign_permit_binds_local_gateway_and_nonce_ledger_not_os_kernel",
    "declared_authority_grants_validate_packet_scope_binding_not_external_identity_auth",
)

HarnessStatus = Literal["SUCCEEDED", "FAILED", "UNKNOWN", "DENIED", "BLOCKED"]


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_hex(value: Any) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SovereignExecutionPermit:
    """Single-use local permit binding consensus, context and admission risk.

    ``bound_risk=None`` represents a legacy v1 permit for inspection only. Its
    original payload/digest can still be reproduced, but registration, claiming
    and execution refuse it. New issuance requires an explicit reference risk.
    """

    permit_id: str
    actor: str
    authority_id: str | None
    allowed_scopes: tuple[str, ...]
    bound_scope: str
    state_version: str
    issued_at: int
    expires_at: int
    action_hash: str
    consensus_digest: str
    compaction_critical_hash: str
    bound_packet_id: str
    permit_digest: str
    bound_risk: str | None = None

    def _payload_without_digest(self) -> dict[str, Any]:
        payload = {
            "schema": HARNESS_SCHEMA_VERSION if self.bound_risk is None else PERMIT_SCHEMA_VERSION,
            "permit_id": self.permit_id,
            "actor": self.actor,
            "authority_id": self.authority_id,
            "allowed_scopes": list(self.allowed_scopes),
            "bound_scope": self.bound_scope,
            "state_version": self.state_version,
            "issued_at": int(self.issued_at),
            "expires_at": int(self.expires_at),
            "action_hash": self.action_hash,
            "consensus_digest": self.consensus_digest,
            "compaction_critical_hash": self.compaction_critical_hash,
            "bound_packet_id": self.bound_packet_id,
        }
        if self.bound_risk is not None:
            payload["bound_risk"] = self.bound_risk
        return payload

    def risk_binding_error(self) -> str | None:
        """Return an admission error for missing or invalid risk bindings."""
        if self.bound_risk is None:
            return "PERMIT_RISK_UNBOUND"
        if not isinstance(self.bound_risk, str) or self.bound_risk not in VALID_RISKS:
            return "PERMIT_RISK_INVALID"
        return None

    def compute_digest(self) -> str:
        """Compute canonical SHA-256 digest over all bound permit fields."""
        return _sha256_hex(self._payload_without_digest())

    @classmethod
    def issue(
        cls,
        *,
        permit_id: str,
        actor: str,
        authority_id: str | None,
        allowed_scopes: tuple[str, ...] | list[str],
        bound_scope: str,
        state_version: str,
        action: dict[str, Any],
        consensus_digest: str,
        compaction_critical_hash: str,
        bound_packet_id: str,
        bound_risk: str,
        issued_at: int | None = None,
        ttl_seconds: int = 300,
    ) -> SovereignExecutionPermit:
        """Create and canonically hash a new `SovereignExecutionPermit`."""
        if not permit_id or not isinstance(permit_id, str):
            raise ValueError("permit_id must be a non-empty string")
        if not actor or not isinstance(actor, str):
            raise ValueError("actor must be a non-empty string")
        if not bound_scope or not isinstance(bound_scope, str):
            raise ValueError("bound_scope must be a non-empty string")
        if not state_version or not isinstance(state_version, str):
            raise ValueError("state_version must be a non-empty string")
        if not bound_packet_id or not isinstance(bound_packet_id, str):
            raise ValueError("bound_packet_id must be a non-empty string")
        if not isinstance(bound_risk, str) or bound_risk not in VALID_RISKS:
            raise ValueError(f"bound_risk must be one of {sorted(VALID_RISKS)}")
        if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be a positive integer")

        scopes_tuple = tuple(str(s) for s in allowed_scopes if str(s))
        if not scopes_tuple:
            raise ValueError("allowed_scopes must contain at least one scope")

        now_ts = int(time.time()) if issued_at is None else int(issued_at)
        act_hash = action_digest(action)

        temp = cls(
            permit_id=permit_id,
            actor=actor,
            authority_id=authority_id,
            allowed_scopes=scopes_tuple,
            bound_scope=bound_scope,
            state_version=state_version,
            issued_at=now_ts,
            expires_at=now_ts + ttl_seconds,
            action_hash=act_hash,
            consensus_digest=consensus_digest,
            compaction_critical_hash=compaction_critical_hash,
            bound_packet_id=bound_packet_id,
            permit_digest="",
            bound_risk=bound_risk,
        )
        return cls(
            permit_id=temp.permit_id,
            actor=temp.actor,
            authority_id=temp.authority_id,
            allowed_scopes=temp.allowed_scopes,
            bound_scope=temp.bound_scope,
            state_version=temp.state_version,
            issued_at=temp.issued_at,
            expires_at=temp.expires_at,
            action_hash=temp.action_hash,
            consensus_digest=temp.consensus_digest,
            compaction_critical_hash=temp.compaction_critical_hash,
            bound_packet_id=temp.bound_packet_id,
            permit_digest=temp.compute_digest(),
            bound_risk=temp.bound_risk,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize permit to a JSON-compatible dictionary."""
        out = self._payload_without_digest()
        out["permit_digest"] = self.permit_digest
        return out


@dataclass(frozen=True)
class SovereignWitnessReceipt:
    """Bound witness receipt emitted by `SovereignExecutionHarness`."""

    accepted: bool
    status: HarnessStatus
    stop_reason: str
    provider_called: bool
    permit: SovereignExecutionPermit
    live_action_hash: str
    live_scope: str
    live_state_version: str
    evaluated_at: int
    consensus_summary: dict[str, Any]
    compaction_summary: dict[str, Any]
    gateway_result: ExecutionResult | None
    witness_digest: str
    epistemic_boundaries: tuple[str, ...] = EPISTEMIC_BOUNDARIES

    def to_dict(self) -> dict[str, Any]:
        """Serialize receipt to a canonical JSON-compatible dictionary."""
        gw_dict: dict[str, Any] | None = None
        if self.gateway_result is not None:
            gw_dict = {
                "status": self.gateway_result.status,
                "reason": self.gateway_result.reason,
                "effect_id": self.gateway_result.effect_id,
                "action_hash": self.gateway_result.action_hash,
                "provider_called": self.gateway_result.provider_called,
                "checkpoint_generation": self.gateway_result.checkpoint_generation,
                "result": self.gateway_result.result,
                "assurance_receipt_digest": (
                    self.gateway_result.receipt.integrity["digest"]
                    if self.gateway_result.receipt is not None
                    else None
                ),
            }
        return {
            "schema": HARNESS_SCHEMA_VERSION,
            "accepted": self.accepted,
            "status": self.status,
            "stop_reason": self.stop_reason,
            "provider_called": self.provider_called,
            "permit": self.permit.to_dict(),
            "live_action_hash": self.live_action_hash,
            "live_scope": self.live_scope,
            "live_state_version": self.live_state_version,
            "evaluated_at": self.evaluated_at,
            "consensus_summary": self.consensus_summary,
            "compaction_summary": self.compaction_summary,
            "gateway_result": gw_dict,
            "epistemic_boundaries": list(self.epistemic_boundaries),
            "witness_digest": self.witness_digest,
        }


class PermitNonceStore:
    """SQLite-backed single-use permit ledger enforcing replay protection across runs."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sovereign_permits (
                    permit_id TEXT PRIMARY KEY,
                    permit_digest TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    authority_id TEXT,
                    bound_scope TEXT NOT NULL,
                    state_version TEXT NOT NULL,
                    action_hash TEXT NOT NULL,
                    issued_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    consumed_at INTEGER
                );
                """
            )
            conn.commit()

    def register_permit(self, permit: SovereignExecutionPermit) -> None:
        """Record a newly issued permit. Raises ValueError if `permit_id` already exists."""
        risk_error = permit.risk_binding_error()
        if risk_error is not None:
            raise ValueError(f"Cannot register permit: {risk_error}; reissue from reference packet")
        if permit.permit_digest != permit.compute_digest():
            raise ValueError("Cannot register permit with invalid permit_digest")
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT permit_id FROM sovereign_permits WHERE permit_id = ?",
                (permit.permit_id,),
            ).fetchone()
            if existing is not None:
                raise ValueError(f"Permit ID already registered: {permit.permit_id}")
            conn.execute(
                """
                INSERT INTO sovereign_permits (
                    permit_id, permit_digest, actor, authority_id,
                    bound_scope, state_version, action_hash,
                    issued_at, expires_at, status, consumed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ISSUED', NULL)
                """,
                (
                    permit.permit_id,
                    permit.permit_digest,
                    permit.actor,
                    permit.authority_id,
                    permit.bound_scope,
                    permit.state_version,
                    permit.action_hash,
                    permit.issued_at,
                    permit.expires_at,
                ),
            )
            conn.commit()

    def claim_single_use(self, permit: SovereignExecutionPermit, now: int) -> tuple[bool, str]:
        """Atomically mark a permit as CONSUMED. Rejects unknown, tampered, or replayed permits."""
        risk_error = permit.risk_binding_error()
        if risk_error is not None:
            return False, risk_error
        if permit.permit_digest != permit.compute_digest():
            return False, "PERMIT_DIGEST_TAMPERED"
        with self._connect() as conn:
            row = conn.execute(
                "SELECT permit_digest, status FROM sovereign_permits WHERE permit_id = ?",
                (permit.permit_id,),
            ).fetchone()
            if row is None:
                return False, "PERMIT_UNREGISTERED"
            if row["permit_digest"] != permit.permit_digest:
                return False, "PERMIT_LEDGER_DIGEST_MISMATCH"
            if row["status"] != "ISSUED":
                return False, "PERMIT_REPLAYED"

            cursor = conn.execute(
                """
                UPDATE sovereign_permits
                SET status = 'CONSUMED', consumed_at = ?
                WHERE permit_id = ? AND status = 'ISSUED'
                """,
                (int(now), permit.permit_id),
            )
            conn.commit()
            if cursor.rowcount != 1:
                return False, "PERMIT_REPLAYED"
            return True, "CONSUMED"

    def get_permit_record(self, permit_id: str) -> dict[str, Any] | None:
        """Inspect the stored ledger status for a permit ID."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM sovereign_permits WHERE permit_id = ?",
                (permit_id,),
            ).fetchone()
            return dict(row) if row is not None else None


class SovereignExecutionHarness:
    """End-to-end execution harness binding ConsensusArena, CompactionShield, and ActionGateway."""

    def __init__(
        self,
        base_dir: str | Path,
        *,
        policy: AssurancePolicy | None = None,
        require_human_authority_for_high_risk: bool = True,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.gateway = ActionGateway.open_local(self.base_dir, policy=policy)
        self.nonce_store = PermitNonceStore(self.base_dir / "ledger" / "sovereign_permits.sqlite3")
        self.require_human_authority_for_high_risk = require_human_authority_for_high_risk

    def issue_permit(
        self,
        *,
        permit_id: str,
        actor: str,
        authority_id: str | None,
        allowed_scopes: tuple[str, ...] | list[str],
        bound_scope: str,
        state_version: str,
        action: dict[str, Any],
        consensus_verdict: DeliberationVerdict,
        reference_packet: AgentStatePacket | dict[str, Any],
        issued_at: int | None = None,
        ttl_seconds: int = 300,
    ) -> SovereignExecutionPermit:
        """Issue and register a single-use `SovereignExecutionPermit`."""
        if not consensus_verdict.verify_integrity():
            raise ValueError(
                "Consensus verdict integrity is invalid; re-deliberate before issuance"
            )
        pkt = (
            reference_packet
            if isinstance(reference_packet, AgentStatePacket)
            else AgentStatePacket.from_dict(reference_packet)
        )
        permit = SovereignExecutionPermit.issue(
            permit_id=permit_id,
            actor=actor,
            authority_id=authority_id,
            allowed_scopes=allowed_scopes,
            bound_scope=bound_scope,
            state_version=state_version,
            action=action,
            consensus_digest=consensus_verdict.consensus_digest,
            compaction_critical_hash=pkt.critical_hash,
            bound_packet_id=pkt.id,
            bound_risk=pkt.risk,
            issued_at=issued_at,
            ttl_seconds=ttl_seconds,
        )
        self.nonce_store.register_permit(permit)
        return permit

    @staticmethod
    def _resolve_candidate_packet(
        candidate: AgentStatePacket | dict[str, Any] | str,
        codebook: dict[str, Any] | None = None,
    ) -> tuple[AgentStatePacket | None, str | None]:
        """Resolve an AgentStatePacket, dict, or L1/L1D wire string."""
        try:
            if isinstance(candidate, AgentStatePacket):
                # Validate round-trip schema
                return AgentStatePacket.from_dict(candidate.to_dict()), None
            if isinstance(candidate, str):
                return CompactionShield.decompact(candidate, codebook=codebook), None
            if isinstance(candidate, dict):
                return AgentStatePacket.from_dict(candidate), None
            return None, f"Unsupported candidate packet type: {type(candidate).__name__}"
        except (CodecError, ValueError, KeyError, TypeError) as exc:
            return None, str(exc)

    @staticmethod
    def _extract_authority_grants(packet: AgentStatePacket) -> dict[str, set[str]]:
        """Extract typed `{holder_id: {allowed_scope, ...}}` grants from `packet.authority`.

        Only entries that specify both a non-empty holder identifier (`id`, `holder`,
        `approver`, `authority_id`, or `actor`) and an explicit non-empty `scope` (str)
        or `scopes` / `allowed_scopes` (sequence of str) are usable grants. Malformed or
        scopeless entries grant nothing.
        """
        grants: dict[str, set[str]] = {}
        if not isinstance(packet.authority, list):
            return grants
        for entry in packet.authority:
            if not isinstance(entry, dict):
                continue
            holders: list[str] = []
            for key in ("holder", "id", "approver", "authority_id", "actor"):
                val = entry.get(key)
                if isinstance(val, str) and val.strip():
                    holders.append(val.strip())
            if not holders:
                continue

            entry_scopes: set[str] = set()
            raw_scope = entry.get("scope")
            if isinstance(raw_scope, str) and raw_scope.strip():
                entry_scopes.add(raw_scope.strip())
            for list_key in ("scopes", "allowed_scopes"):
                raw_list = entry.get(list_key)
                if isinstance(raw_list, (list, tuple, set)):
                    for item in raw_list:
                        if isinstance(item, str) and item.strip():
                            entry_scopes.add(item.strip())
            if not entry_scopes:
                continue

            for h in holders:
                grants.setdefault(h, set()).update(entry_scopes)
        return grants

    def _build_receipt(
        self,
        *,
        accepted: bool,
        status: HarnessStatus,
        stop_reason: str,
        provider_called: bool,
        permit: SovereignExecutionPermit,
        live_action_hash: str,
        live_scope: str,
        live_state_version: str,
        evaluated_at: int,
        consensus_summary: dict[str, Any],
        compaction_summary: dict[str, Any],
        gateway_result: ExecutionResult | None,
    ) -> SovereignWitnessReceipt:
        envelope = {
            "schema": HARNESS_SCHEMA_VERSION,
            "accepted": accepted,
            "status": status,
            "stop_reason": stop_reason,
            "provider_called": provider_called,
            "permit_digest": permit.permit_digest,
            "live_action_hash": live_action_hash,
            "live_scope": live_scope,
            "live_state_version": live_state_version,
            "evaluated_at": evaluated_at,
            "consensus_summary": consensus_summary,
            "compaction_summary": compaction_summary,
            "gateway_effect_id": gateway_result.effect_id if gateway_result else None,
            "gateway_status": gateway_result.status if gateway_result else None,
            "epistemic_boundaries": list(EPISTEMIC_BOUNDARIES),
        }
        digest = _sha256_hex(envelope)
        return SovereignWitnessReceipt(
            accepted=accepted,
            status=status,
            stop_reason=stop_reason,
            provider_called=provider_called,
            permit=permit,
            live_action_hash=live_action_hash,
            live_scope=live_scope,
            live_state_version=live_state_version,
            evaluated_at=evaluated_at,
            consensus_summary=consensus_summary,
            compaction_summary=compaction_summary,
            gateway_result=gateway_result,
            witness_digest=digest,
        )

    def evaluate_and_execute(
        self,
        *,
        permit: SovereignExecutionPermit,
        consensus: ConsensusArena | DeliberationVerdict,
        reference_packet: AgentStatePacket | dict[str, Any],
        candidate_packet: AgentStatePacket | dict[str, Any] | str,
        live_action: dict[str, Any],
        live_scope: str,
        current_state_version: str,
        executor: Callable[[], dict[str, Any]],
        codebook: dict[str, Any] | None = None,
        now: int | None = None,
    ) -> SovereignWitnessReceipt:
        """Verify all five safety gates and execute `executor` only if every contract holds."""
        eval_now = int(time.time()) if now is None else int(now)
        live_act_hash = action_digest(live_action)

        verdict = consensus.deliberate() if isinstance(consensus, ConsensusArena) else consensus
        consensus_summary = {
            "converged": verdict.converged,
            "obstruction_free": verdict.obstruction_free,
            "byzantine_safe": verdict.byzantine_safe,
            "healthy_agents": list(verdict.healthy_agents),
            "quarantined_agents": list(verdict.quarantined_agents),
            "consensus_digest": verdict.consensus_digest,
        }

        ref_obj = (
            reference_packet
            if isinstance(reference_packet, AgentStatePacket)
            else AgentStatePacket.from_dict(reference_packet)
        )
        cand_obj, decode_err = self._resolve_candidate_packet(candidate_packet, codebook=codebook)
        if cand_obj is None:
            compaction_summary: dict[str, Any] = {
                "is_safe": False,
                "classification": "UNDECODABLE",
                "reason": decode_err or "Invalid candidate packet",
                "candidate_critical_hash": None,
            }
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="COMPACTION_UNDECODABLE",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )

        integrity = CompactionShield.verify_integrity(ref_obj, cand_obj)
        compaction_summary = {
            "is_safe": bool(integrity.get("is_safe")),
            "classification": integrity.get("classification"),
            "reason": integrity.get("reason"),
            "candidate_critical_hash": integrity.get("candidate_critical_hash"),
            "packet_id": cand_obj.id,
            "risk": cand_obj.risk,
            "reference_risk": ref_obj.risk,
            "bound_risk": permit.bound_risk,
            "has_recovery": bool(cand_obj.recovery),
        }

        # GATE 1: digest-bound gossip/consistency proxy and healthy actor.
        # The legacy stop reason COHOMOLOGY_OBSTRUCTION is retained for callers;
        # this gate does not compute H^1 or prove Byzantine fault tolerance.
        if not verdict.converged:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="CONSENSUS_NOT_CONVERGED",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if not verdict.obstruction_free:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="COHOMOLOGY_OBSTRUCTION",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if not verdict.byzantine_safe:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="BYZANTINE_QUORUM_EXCEEDED",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if permit.actor in verdict.quarantined_agents or permit.actor not in verdict.healthy_agents:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="ACTOR_QUARANTINED",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if verdict.consensus_digest != permit.consensus_digest:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="CONSENSUS_DIGEST_MISMATCH",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if not verdict.verify_integrity():
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="CONSENSUS_INTEGRITY_INVALID",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )

        # ── GATE 2: CONTEXT COMPACTION SHIELD (10 accountability fields + recovery) ──
        if not integrity.get("is_safe"):
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="COMPACTION_UNSAFE_COLLAPSE",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if integrity.get("candidate_critical_hash") != permit.compaction_critical_hash:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="COMPACTION_HASH_MISMATCH",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if cand_obj.id != permit.bound_packet_id:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="COMPACTION_PACKET_ID_MISMATCH",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if bool(live_action.get("side_effect", True)) and not cand_obj.recovery:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="MISSING_RECOVERY_ANCHOR",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )

        # ── GATE 3: PERMIT BINDING (Risk, Action, Scope, State, Expiry, Authority) ──
        risk_error = permit.risk_binding_error()
        if risk_error is None:
            if permit.permit_digest != permit.compute_digest():
                risk_error = "PERMIT_DIGEST_TAMPERED"
            elif ref_obj.risk != permit.bound_risk:
                risk_error = "REFERENCE_RISK_MISMATCH"
            elif cand_obj.risk != permit.bound_risk:
                risk_error = "CANDIDATE_RISK_MISMATCH"
        if risk_error is not None:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason=risk_error,
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if live_act_hash != permit.action_hash:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="ACTION_PAYLOAD_MISMATCH",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if live_scope != permit.bound_scope or live_scope not in permit.allowed_scopes:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="SCOPE_MISMATCH",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if current_state_version != permit.state_version:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="STATE_VERSION_MISMATCH",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if eval_now < permit.issued_at:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="PERMIT_NOT_YET_VALID",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if eval_now >= permit.expires_at:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="PERMIT_EXPIRED",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )

        if (
            self.require_human_authority_for_high_risk
            and permit.bound_risk in ("HIGH", "CRITICAL")
            and permit.authority_id is None
        ):
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="HUMAN_AUTHORITY_REQUIRED",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )

        authority_grants = self._extract_authority_grants(cand_obj)
        if permit.authority_id is not None:
            if permit.authority_id not in authority_grants:
                return self._build_receipt(
                    accepted=False,
                    status="DENIED",
                    stop_reason="AUTHORITY_NOT_IN_PACKET",
                    provider_called=False,
                    permit=permit,
                    live_action_hash=live_act_hash,
                    live_scope=live_scope,
                    live_state_version=current_state_version,
                    evaluated_at=eval_now,
                    consensus_summary=consensus_summary,
                    compaction_summary=compaction_summary,
                    gateway_result=None,
                )
            if live_scope not in authority_grants[permit.authority_id]:
                return self._build_receipt(
                    accepted=False,
                    status="DENIED",
                    stop_reason="AUTHORITY_SCOPE_MISMATCH",
                    provider_called=False,
                    permit=permit,
                    live_action_hash=live_act_hash,
                    live_scope=live_scope,
                    live_state_version=current_state_version,
                    evaluated_at=eval_now,
                    consensus_summary=consensus_summary,
                    compaction_summary=compaction_summary,
                    gateway_result=None,
                )

        # Pre-check gateway policy disposition BEFORE consuming the single-use permit
        disposition, _findings = self.gateway.evaluate_policy(
            live_action,
            live_scope,
            permit.actor,
            approver_id=permit.authority_id,
        )
        if disposition == Disposition.BLOCK:
            return self._build_receipt(
                accepted=False,
                status="BLOCKED",
                stop_reason="GATEWAY_POLICY_BLOCKED",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )
        if disposition == Disposition.REVIEW and permit.authority_id is None:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason="HUMAN_AUTHORITY_REQUIRED",
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )

        # ── GATE 4: SINGLE-USE NONCE / REPLAY PROTECTION ──
        claimed, claim_reason = self.nonce_store.claim_single_use(permit, now=eval_now)
        if not claimed:
            return self._build_receipt(
                accepted=False,
                status="DENIED",
                stop_reason=claim_reason,
                provider_called=False,
                permit=permit,
                live_action_hash=live_act_hash,
                live_scope=live_scope,
                live_state_version=current_state_version,
                evaluated_at=eval_now,
                consensus_summary=consensus_summary,
                compaction_summary=compaction_summary,
                gateway_result=None,
            )

        # ── GATE 5: ACTION GATEWAY LINEARIZED EXECUTION & ED25519 CHECKPOINT ──
        gw_result = self.gateway.execute(
            action=live_action,
            actor=permit.actor,
            scope=live_scope,
            executor=executor,
            approver_id=permit.authority_id,
        )
        accepted = gw_result.status == "SUCCEEDED"
        stop_reason = "EXECUTED" if accepted else f"GATEWAY_{gw_result.status}"
        return self._build_receipt(
            accepted=accepted,
            status=gw_result.status,
            stop_reason=stop_reason,
            provider_called=gw_result.provider_called,
            permit=permit,
            live_action_hash=live_act_hash,
            live_scope=live_scope,
            live_state_version=current_state_version,
            evaluated_at=eval_now,
            consensus_summary=consensus_summary,
            compaction_summary=compaction_summary,
            gateway_result=gw_result,
        )


__all__ = [
    "EPISTEMIC_BOUNDARIES",
    "HARNESS_SCHEMA_VERSION",
    "PERMIT_SCHEMA_VERSION",
    "PermitNonceStore",
    "SovereignExecutionHarness",
    "SovereignExecutionPermit",
    "SovereignWitnessReceipt",
]
