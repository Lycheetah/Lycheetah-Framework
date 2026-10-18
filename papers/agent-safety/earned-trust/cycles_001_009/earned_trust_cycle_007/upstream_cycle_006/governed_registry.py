"""Earned Trust C006: experimental, authenticated provenance-governance control.

LAB ONLY. Authorities, their organizations, source links, signatures and current
revision readback are supplied by trusted fixture configuration. HMAC proves
shared-key possession, not real-world independence or correctness.
"""
from __future__ import annotations

from dataclasses import dataclass
import copy
from hashlib import sha256
import hmac
from threading import RLock
from typing import Any, Mapping, Sequence

from provenance_gate import Source, TrustedRegistry, ProvenanceGate, Verdict, canonical, object_sha


class GovernanceError(ValueError):
    pass


@dataclass(frozen=True)
class Authority:
    name: str
    organization: str
    role: str  # REVIEWER or AUDITOR
    key: bytes

    def __post_init__(self):
        if not self.name or not self.organization or self.role not in {"REVIEWER", "AUDITOR"}:
            raise GovernanceError("invalid authority identity or role")
        if not isinstance(self.key, bytes) or len(self.key) < 32:
            raise GovernanceError("authority key must have at least 32 bytes")


def source_record(s: Source) -> dict[str, Any]:
    return {"source_id": s.source_id, "controller": s.controller,
            "upstream": list(s.upstream), "witness_signer": s.witness_signer}


class GovernedRegistry:
    """Revisioned source graph and reproducible decision to suspend contested paths.

    The replay anchor MUST be held independently from this mutable object. A
    self-reported checkpoint cannot detect legitimate-looking history truncation.
    """
    def __init__(self, sources: Sequence[Source], witness_keys: Mapping[str, bytes],
                 authorities: Sequence[Authority]):
        self._lock = RLock()
        self._initial_sources = tuple(sources)
        self._keys = dict(witness_keys)
        self._authorities = {a.name: a for a in authorities}
        if not authorities or len(self._authorities) != len(authorities):
            raise GovernanceError("authorities must be unique and nonempty")
        if not any(a.role == "AUDITOR" for a in authorities):
            raise GovernanceError("at least one independent challenge role required")
        reviewer_orgs = {a.organization for a in authorities if a.role == "REVIEWER"}
        if len(reviewer_orgs) < 2:
            raise GovernanceError("two separate reviewer organizations required")
        self._registry = TrustedRegistry(sources, self._keys)
        self._sources = {s.source_id: s for s in sources}
        self._challenges: dict[str, dict[str, Any]] = {}
        self._last_patch: dict[str, int] = {}
        self.events: list[dict[str, Any]] = []
        self.genesis = object_sha({
            "schema": "earned-trust.governance-genesis.v1",
            "sources": sorted((source_record(s) for s in sources), key=lambda r: r["source_id"]),
            "signers": {k: sha256(v).hexdigest() for k, v in sorted(self._keys.items())},
            "authorities": {a.name: {"org": a.organization, "role": a.role,
                                     "key_fingerprint": sha256(a.key).hexdigest()}
                            for a in sorted(authorities, key=lambda a: a.name)},
        })
        self.head = self.genesis

    @property
    def revision(self) -> int:
        return len(self.events)

    def checkpoint(self) -> dict[str, Any]:
        with self._lock:
            return {"genesis": self.genesis, "revision": self.revision, "head": self.head}

    def prepare(self, kind: str, target: str, **fields) -> dict[str, Any]:
        with self._lock:
            if kind not in {"PATCH", "CHALLENGE", "RESOLVE"}:
                raise GovernanceError("unsupported operation")
            if not isinstance(target, str) or target not in self._sources:
                raise GovernanceError("unknown target")
            expected = {"PATCH": {"controller", "upstream"},
                        "CHALLENGE": {"reason"},
                        "RESOLVE": {"resolution", "reason"}}[kind]
            if set(fields) != expected:
                raise GovernanceError("missing or extra operation fields")
            return {"schema": "earned-trust.registry-operation.v1", "seq": self.revision + 1,
                    "previous": self.head, "kind": kind, "target": target, "fields": fields}

    def sign(self, operation: dict[str, Any], authority_name: str) -> dict[str, str]:
        """TEST FIXTURE UTILITY: a real application must not hold review secrets here."""
        authority = self._authorities[authority_name]
        return {"signer": authority_name,
                "mac": hmac.new(authority.key, canonical(operation), sha256).hexdigest()}

    def _verify_signatures(self, body: dict, signatures: Sequence[dict]) -> None:
        if not isinstance(signatures, (tuple, list)) or not signatures:
            raise GovernanceError("missing signatures")
        if any(not isinstance(s, dict) or set(s) != {"signer", "mac"} for s in signatures):
            raise GovernanceError("invalid signature schema")
        names = [s["signer"] for s in signatures]
        if any(not isinstance(x, str) for x in names) or len(set(names)) != len(names):
            raise GovernanceError("duplicate or malformed signer")
        kind = body["kind"]
        roles = {"PATCH": "REVIEWER", "RESOLVE": "REVIEWER", "CHALLENGE": "AUDITOR"}
        required = 1 if kind == "CHALLENGE" else 2
        if len(signatures) < required:
            raise GovernanceError("insufficient cosigners")
        organizations = set()
        for signature in signatures:
            signer = self._authorities.get(signature["signer"])
            if signer is None or signer.role != roles[kind]:
                raise GovernanceError("unregistered or incorrectly privileged signer")
            expected = hmac.new(signer.key, canonical(body), sha256).hexdigest()
            if not isinstance(signature["mac"], str) or not hmac.compare_digest(expected, signature["mac"]):
                raise GovernanceError("invalid or substituted signature")
            organizations.add(signer.organization)
        if len(organizations) < required:
            raise GovernanceError("reviewer organizations are not independent")
        # A source controller cannot adjudicate its own provenance patch/dispute.
        if kind != "CHALLENGE":
            owners = {self._sources[body["target"]].controller}
            if kind == "PATCH":
                owners.add(body["fields"]["controller"])
            if organizations & owners:
                raise GovernanceError("conflicted controller cannot adjudicate itself")

    def apply(self, body: dict, signatures: Sequence[dict]) -> dict[str, Any]:
        with self._lock:
            if not isinstance(body, dict) or set(body) != {"schema", "seq", "previous", "kind", "target", "fields"}:
                raise GovernanceError("malformed operation")
            if body["schema"] != "earned-trust.registry-operation.v1" or type(body["seq"]) is not int:
                raise GovernanceError("invalid schema or sequence")
            if body["previous"] != self.head or body["seq"] != self.revision + 1:
                raise GovernanceError("stale checkpoint, gap or replay")
            # Validate exact operation fields while preserving explicit parent/sequence.
            candidate = self.prepare(body["kind"], body["target"], **body["fields"])
            if candidate != body:
                raise GovernanceError("operation mismatch")
            self._verify_signatures(body, signatures)
            target, fields, kind = body["target"], body["fields"], body["kind"]
            if kind == "PATCH":
                if not isinstance(fields["controller"], str) or not fields["controller"]:
                    raise GovernanceError("invalid controller")
                if not isinstance(fields["upstream"], (list, tuple)) or any(not isinstance(x, str) for x in fields["upstream"]):
                    raise GovernanceError("invalid dependencies")
                old = self._sources[target]
                updated = Source(target, fields["controller"], tuple(fields["upstream"]), old.witness_signer)
                new = {**self._sources, target: updated}
                # Builds and validates full acyclic graph before changing any state.
                next_registry = TrustedRegistry(list(new.values()), self._keys)
            elif kind == "CHALLENGE":
                if not isinstance(fields["reason"], str) or not 8 <= len(fields["reason"]) <= 300:
                    raise GovernanceError("reason must be meaningful and bounded")
                if target in self._challenges:
                    raise GovernanceError("target already challenged")
            elif kind == "RESOLVE":
                if fields["resolution"] not in {"DISMISSED", "REMEDIATED"}:
                    raise GovernanceError("invalid resolution")
                if not isinstance(fields["reason"], str) or not 8 <= len(fields["reason"]) <= 300:
                    raise GovernanceError("reason required")
                if target not in self._challenges:
                    raise GovernanceError("no open challenge")
                if fields["resolution"] == "REMEDIATED" and self._last_patch.get(target, 0) <= self._challenges[target]["opened_seq"]:
                    raise GovernanceError("remediation needs a post-challenge source patch")
            # Event ownership is internal: caller-side mutation after acceptance must
            # not rewrite history or silently poison replay verification.
            signatures_sorted = sorted(copy.deepcopy(signatures), key=lambda s: s["signer"])
            entry = {"operation": copy.deepcopy(body), "signatures": signatures_sorted}
            entry["hash"] = object_sha(entry)
            if kind == "PATCH":
                self._sources = new
                self._registry = next_registry
                self._last_patch[target] = body["seq"]
            elif kind == "CHALLENGE":
                self._challenges[target] = {"opened_seq": body["seq"], "reason": fields["reason"]}
            else:
                del self._challenges[target]
            self.events.append(entry)
            self.head = entry["hash"]
            return self.checkpoint()

    def verify_history(self, *, trusted_checkpoint: Mapping[str, Any] | None) -> tuple[bool, str]:
        with self._lock:
            if trusted_checkpoint is None:
                return False, "trusted-checkpoint-required"
            if dict(trusted_checkpoint) != self.checkpoint():
                return False, "external-checkpoint-disagrees"
            try:
                clone = GovernedRegistry(self._initial_sources, self._keys, tuple(self._authorities.values()))
                for entry in self.events:
                    if not isinstance(entry, dict) or set(entry) != {"operation", "signatures", "hash"}:
                        return False, "event-corrupted"
                    if entry["hash"] != object_sha({"operation": entry["operation"], "signatures": entry["signatures"]}):
                        return False, "hash-chain-corrupted"
                    clone.apply(entry["operation"], entry["signatures"])
                if (clone.head != self.head or clone._sources != self._sources
                        or clone._challenges != self._challenges or clone._last_patch != self._last_patch):
                    return False, "materialized-state-inconsistent"
                return True, "ok"
            except (ValueError, KeyError, TypeError, RecursionError, AttributeError):
                return False, "event-replay-invalid"

    def _depends_on(self, source_id: str, target: str) -> bool:
        if source_id == target:
            return True
        return any(self._depends_on(parent, target) for parent in self._sources[source_id].upstream)

    def sign_bound_witness(self, statement: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            """LAB convenience. Bind C005 witness to exact registry head."""
            signer = statement["body"]["source_id"]
            if signer not in self._keys:
                raise GovernanceError("unknown witness signer")
            binding = {"registry_head": self.head, "statement_sha256": object_sha(statement)}
            mac = hmac.new(self._keys[signer], canonical(binding), sha256).hexdigest()
            return {"statement": statement, "binding": binding, "binding_mac": mac}

    def evaluate(self, bound_witnesses: Sequence[dict], *, trusted_checkpoint: dict | None,
                 effect_id: str, action_sha256: str, token_sha256: str,
                 now: int, current_revisions: Mapping[str, int] | None,
                 provider_receipt_valid: bool = True) -> Verdict:
        with self._lock:
            ok, why = self.verify_history(trusted_checkpoint=trusted_checkpoint)
            if not ok:
                return Verdict("REVIEW", "governance-" + why, 0, 0)
            if not isinstance(bound_witnesses, (tuple, list)) or not bound_witnesses:
                return Verdict("REVIEW", "missing-governed-witnesses", 0, 0)
            plain: list[dict] = []
            for item in bound_witnesses:
                if not isinstance(item, dict) or set(item) != {"statement", "binding", "binding_mac"}:
                    return Verdict("REVIEW", "bad-witness-binding-format", 0, 0)
                statement, binding, mac = item["statement"], item["binding"], item["binding_mac"]
                if (not isinstance(statement, dict) or not isinstance(statement.get("body"), dict)
                        or not isinstance(binding, dict) or set(binding) != {"registry_head", "statement_sha256"}):
                    return Verdict("REVIEW", "bad-witness-binding-schema", 0, 0)
                sid = statement["body"].get("source_id")
                if not isinstance(sid, str) or sid not in self._keys:
                    return Verdict("REVIEW", "unregistered-witness", 0, 0)
                expected = hmac.new(self._keys[sid], canonical(binding), sha256).hexdigest()
                if not isinstance(mac, str) or not hmac.compare_digest(expected, mac):
                    return Verdict("REVIEW", "witness-binding-invalid", 0, 0)
                if binding["registry_head"] != self.head or binding["statement_sha256"] != object_sha(statement):
                    return Verdict("REVIEW", "witness-bound-to-obsolete-or-wrong-registry", 0, 0)
                if any(self._depends_on(sid, challenged) for challenged in self._challenges):
                    return Verdict("REVIEW", "source-provenance-under-challenge", 0, 0)
                plain.append(statement)
            gate = ProvenanceGate(self._registry)
            return gate.evaluate(plain, effect_id=effect_id, action_sha256=action_sha256,
                                 token_sha256=token_sha256, now=now,
                                 current_revisions=current_revisions,
                                 provider_receipt_valid=provider_receipt_valid)
