"""Lycheetah Hybrid Gateway v0.2: reversible, evidence-carrying BITEMPORAL probe.

A source-anchored claim ledger; NOT an LLM, semantic contradiction detector,
identity provider, durable datastore, authorized effect executor or neural editor.
Records are immutable after admission by public API; the in-memory ledger is not
secure against a hostile process. Reviewer approval is injected by a trusted
caller and is NOT authenticated by this prototype.

All datetimes must be ISO8601 with explicit timezone. Internally UTC.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
import copy
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Optional, Protocol, Callable


def json_bytes(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf8")


def canonical_digest(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def utc(t: str) -> str:
    if not isinstance(t, str):
        raise ValueError("timestamps must be timezone-aware ISO8601 strings")
    dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("timestamp must include timezone")
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def in_interval(t: str, start: str, end: Optional[str]) -> bool:
    return start <= t and (end is None or t < end)


def key(c: "ClaimProposal") -> tuple[str, str, str, str]:
    return (c.tenant, c.subject, c.predicate, c.scope)


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    tenant: str
    uri: str
    body: str
    # Operator-controlled registry field, not supplied by a model. No semantics of trust inferred.
    label: str = "registered"
    digest: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "digest", canonical_digest(self.body))


@dataclass(frozen=True)
class ClaimProposal:
    claim_id: str
    tenant: str
    subject: str
    predicate: str
    scope: str
    value: str
    valid_from: str
    source_id: str
    evidence_quote: str
    valid_until: Optional[str] = None
    supersedes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Decision:
    disposition: str  # ALLOW / REVIEW / BLOCK
    reason: str
    event_hash: Optional[str] = None


@dataclass(frozen=True)
class QueryResult:
    disposition: str  # ANSWER / ABSTAIN_CONFLICT / ABSTAIN_NO_EVIDENCE
    value: Optional[str]
    citations: tuple[dict, ...]
    effective_at: str
    known_at: str
    reason: str

    def render(self) -> str:
        if self.disposition != "ANSWER":
            return f"Cannot establish a supported answer ({self.disposition}): {self.reason}."
        refs = ", ".join(f"{c['source_id']} [{c['digest']}]" for c in self.citations)
        return (f"{self.value} (effective {self.effective_at}; known as of {self.known_at}). "
                f"Evidence: {refs}.")


class CandidateAdapter(Protocol):
    def extract(self, source: SourceDocument) -> list[ClaimProposal]: ...


class ScriptedNeuralAdapter:
    """Deterministic stand-in. The output represents untrusted LLM-proposed claims."""
    def __init__(self, name: str, candidates: dict[str, list[ClaimProposal]]) -> None:
        self.name = name
        self.candidates = candidates

    def extract(self, source: SourceDocument) -> list[ClaimProposal]:
        return list(self.candidates.get(source.source_id, []))


class SourceRegistrationError(ValueError):
    pass


def refund_window_quote_validator(p: ClaimProposal) -> bool:
    """Narrow deterministic schema for fictional refund-window cases ONLY.

    Other policies require their own domain validator; no generic NLI is claimed.
    """
    if (p.subject, p.predicate) != ("refunds", "window_days"):
        return False
    match = re.fullmatch(r"Refunds allowed within ([0-9]+) days\.", p.evidence_quote)
    return bool(match and match.group(1) == p.value)


class HybridGateway:
    def __init__(self, *, semantic_validator: Optional[Callable[[ClaimProposal], bool]] = None) -> None:
        self.semantic_validator = semantic_validator
        self.sources: dict[str, SourceDocument] = {}
        self.claims: dict[str, ClaimProposal] = {}
        self.admitted_at: dict[str, str] = {}
        self.events: list[dict] = []
        self._latest_at: Optional[str] = None
        self._by_key: dict[tuple[str, str, str, str], set[str]] = {}
        self._withdrawals: list[dict] = []

    def register_source(self, source: SourceDocument) -> None:
        """Trusted/operator path: source documents are immutable per source_id."""
        if not all([source.source_id, source.tenant, source.uri, source.body]):
            raise SourceRegistrationError("source metadata and body are required")
        old = self.sources.get(source.source_id)
        if old is not None and old != source:
            raise SourceRegistrationError("source ID cannot be rebound")
        self.sources[source.source_id] = source

    def _record(self, kind: str, payload: dict, at: str) -> str:
        record = {"seq": len(self.events) + 1, "kind": kind,
                  "at": at, "payload": payload,
                  "prev_hash": self.events[-1]["hash"] if self.events else None}
        record["hash"] = canonical_digest(json_bytes(record))
        self.events.append(record)
        self._latest_at = at
        return record["hash"]

    def _record_time(self, at: str) -> str:
        at = utc(at)
        if self._latest_at is not None and at < self._latest_at:
            raise ValueError("trusted record clock cannot move backwards")
        return at

    def ingest(self, p: ClaimProposal, *, recorded_at: str,
               reviewer_approved: bool = False) -> Decision:
        """An LLM never grants its own approval; caller passes explicit review state.

        REVIEW/BLOCK do not change the ledger. `recorded_at` is the trusted caller's
        clock; a model-provided observation time is never accepted.
        """
        at = self._record_time(recorded_at)
        if not reviewer_approved:
            return Decision("REVIEW", "explicit trusted reviewer approval required")
        try:
            start = utc(p.valid_from)
            end = utc(p.valid_until) if p.valid_until is not None else None
        except (ValueError, TypeError, OverflowError):
            return Decision("BLOCK", "invalid or timezone-naive effective interval")
        if end is not None and end <= start:
            return Decision("BLOCK", "effective interval is empty or reversed")
        s = self.sources.get(p.source_id)
        if s is None:
            return Decision("BLOCK", "unregistered source")
        if s.tenant != p.tenant:
            return Decision("BLOCK", "cross-tenant source")
        if not all([p.claim_id, p.tenant, p.subject, p.predicate, p.scope, p.value, p.evidence_quote]):
            return Decision("BLOCK", "missing required claim field")
        if p.claim_id in self.claims:
            return Decision("BLOCK", "duplicate claim ID (append-only)")
        if p.evidence_quote not in s.body:
            return Decision("BLOCK", "quote not found in registered source")
        if p.value not in p.evidence_quote:
            return Decision("REVIEW", "proposed value is not textually supported by quote")
        if self.semantic_validator is not None and not self.semantic_validator(p):
            return Decision("REVIEW", "domain-specific semantic rule could not substantiate claim")
        for old_id in p.supersedes:
            old = self.claims.get(old_id)
            if old is None or key(old) != key(p):
                return Decision("BLOCK", "supersession target unknown or wrong key")
            if utc(old.valid_from) > start:
                return Decision("BLOCK", "supersession cannot start earlier than target")
        if p.claim_id in p.supersedes or len(set(p.supersedes)) != len(p.supersedes):
            return Decision("BLOCK", "invalid supersession graph")
        normalized = ClaimProposal(**{**asdict(p), "valid_from": start,
                                      "valid_until": end, "supersedes": tuple(p.supersedes)})
        self.claims[p.claim_id] = normalized
        self.admitted_at[p.claim_id] = at
        self._by_key.setdefault(key(normalized), set()).add(p.claim_id)
        digest = self._record("ADMIT", {"claim_id": p.claim_id, "source_id": p.source_id,
                                        "source_digest": s.digest,
                                        "claim": asdict(normalized)}, at)
        return Decision("ALLOW", "admitted, subject to query-time conflict resolution", digest)

    def ingest_batch(self, proposals: tuple[ClaimProposal, ...] | list[ClaimProposal], *,
                     recorded_at: str, reviewer_approved: bool = False) -> Decision:
        """Atomic *in-memory* admission with one chain event and deterministic replay.

        Preflight applies every candidate to a shadow ledger; no real state changes
        until every check passes. Dependencies on members of the same batch are
        resolved topologically. This is not concurrency protection or durable storage.
        A trusted caller must independently attest approval.
        """
        at = self._record_time(recorded_at)
        if not reviewer_approved:
            return Decision("REVIEW", "explicit trusted reviewer approval required")
        if not isinstance(proposals, (tuple, list)) or not proposals:
            return Decision("BLOCK", "batch must contain at least one typed claim")
        if any(not isinstance(p, ClaimProposal) for p in proposals):
            return Decision("BLOCK", "batch contains non-claim item")
        if (any(not isinstance(p.claim_id, str) or not p.claim_id for p in proposals)
                or len({p.claim_id for p in proposals}) != len(proposals)):
            return Decision("BLOCK", "duplicate or empty batch claim ID")
        if any(not isinstance(p.supersedes, (tuple, list)) for p in proposals):
            return Decision("BLOCK", "invalid batch dependency list")

        shadow = copy.copy(self)
        shadow.claims = dict(self.claims)
        shadow.admitted_at = dict(self.admitted_at)
        shadow._by_key = {k: set(v) for k, v in self._by_key.items()}
        shadow.events = list(self.events)
        shadow._withdrawals = list(self._withdrawals)
        pending = {p.claim_id: p for p in proposals}
        accepted: list[ClaimProposal] = []
        while pending:
            eligible = sorted((p for p in pending.values()
                               if all(dep in shadow.claims for dep in p.supersedes)),
                              key=lambda p: p.claim_id)
            if not eligible:
                return Decision("BLOCK", "batch has missing, cyclic or unresolved supersession dependencies")
            for p in eligible:
                try:
                    decision = shadow.ingest(p, recorded_at=at, reviewer_approved=True)
                except (ValueError, TypeError, AttributeError, OverflowError, KeyError):
                    return Decision("BLOCK", "invalid batch claim representation")
                if decision.disposition != "ALLOW":
                    return decision
                accepted.append(shadow.claims[p.claim_id])
                del pending[p.claim_id]
        payload = {"size": len(accepted), "claims": [
            {"claim_id": p.claim_id, "source_id": p.source_id,
             "source_digest": self.sources[p.source_id].digest, "claim": asdict(p)}
            for p in accepted]}
        record = {"seq": len(self.events) + 1, "kind": "BATCH_ADMIT",
                  "at": at, "payload": payload, "prev_hash": self.head_digest}
        record["hash"] = canonical_digest(json_bytes(record))
        self.claims = shadow.claims
        self.admitted_at = shadow.admitted_at
        self._by_key = shadow._by_key
        self.events = [*self.events, record]
        self._latest_at = at
        return Decision("ALLOW", f"atomically admitted {len(accepted)} claims in one event", record["hash"])

    def withdraw(self, claim_id: str, *, effective_from: str, recorded_at: str,
                 reviewer_approved: bool = False) -> Decision:
        at = self._record_time(recorded_at)
        if not reviewer_approved:
            return Decision("REVIEW", "withdrawal requires explicit trusted review")
        if claim_id not in self.claims:
            return Decision("BLOCK", "cannot withdraw unknown claim")
        try:
            when = utc(effective_from)
        except (ValueError, TypeError, OverflowError):
            return Decision("BLOCK", "invalid withdrawal effective time")
        self._withdrawals.append({"claim_id": claim_id, "effective_from": when, "recorded_at": at})
        digest = self._record("WITHDRAW", {"claim_id": claim_id, "effective_from": when}, at)
        return Decision("ALLOW", "withdrawal accepted; prior knowledge remains reconstructable", digest)

    def _visible(self, c: ClaimProposal, effective_at: str, known_at: str) -> bool:
        if self.admitted_at[c.claim_id] > known_at or not in_interval(effective_at, c.valid_from, c.valid_until):
            return False
        return not any(w["claim_id"] == c.claim_id and w["recorded_at"] <= known_at
                       and effective_at >= w["effective_from"] for w in self._withdrawals)

    def query(self, *, tenant: str, subject: str, predicate: str, scope: str,
              effective_at: str, known_at: str) -> QueryResult:
        effective_at, known_at = utc(effective_at), utc(known_at)
        ids = self._by_key.get((tenant, subject, predicate, scope), set())
        active = {i: self.claims[i] for i in ids if self._visible(self.claims[i], effective_at, known_at)}
        # Explicit accepted supersessions dominate ONLY while the newer claim is
        # effective AND visible at this knowledge-time. Withdrawal restores a prior
        # eligible claim unless its own validity interval has ended.
        # Traverse links through intermediate withdrawn/out-of-interval ancestors.
        # A later active revision can dominate the original even if the
        # intermediate revision is no longer independently visible.
        suppressed: set[str] = set()
        for c in active.values():
            pending = list(c.supersedes)
            seen: set[str] = set()
            while pending:
                ancestor = pending.pop()
                if ancestor in seen:
                    continue
                seen.add(ancestor)
                if ancestor in active:
                    suppressed.add(ancestor)
                if ancestor in self.claims:
                    pending.extend(self.claims[ancestor].supersedes)
        survivors = [c for i, c in sorted(active.items()) if i not in suppressed]
        values = {c.value for c in survivors}
        if not survivors:
            return QueryResult("ABSTAIN_NO_EVIDENCE", None, (), effective_at, known_at,
                               "no admitted, currently visible claim in exact tenant/scope")
        if len(values) > 1:
            return QueryResult("ABSTAIN_CONFLICT", None, self._cite(survivors), effective_at, known_at,
                               "multiple admitted claims disagree; no override inferred")
        return QueryResult("ANSWER", survivors[0].value, self._cite(survivors), effective_at, known_at,
                           "unique supported value for requested time and scope")

    def _cite(self, claims: list[ClaimProposal]) -> tuple[dict, ...]:
        return tuple({"claim_id": c.claim_id, "source_id": c.source_id,
                      "uri": self.sources[c.source_id].uri,
                      "digest": self.sources[c.source_id].digest,
                      "evidence_quote": c.evidence_quote,
                      "valid_from": c.valid_from, "valid_until": c.valid_until,
                      "recorded_at": self.admitted_at[c.claim_id]}
                     for c in sorted(claims, key=lambda x: x.claim_id))

    def propose_effect(self, *, tool: str, args: dict) -> Decision:
        """No execute API exists. Deliberately stops at the effect boundary."""
        return Decision("REVIEW", "no effect executor; external Action Guard and authorization required")

    def verify_chain(self, *, anchored_head: Optional[str] = None) -> bool:
        prev = None
        for idx, e in enumerate(self.events, 1):
            if e.get("seq") != idx or e.get("prev_hash") != prev:
                return False
            clean = {k: v for k, v in e.items() if k != "hash"}
            if canonical_digest(json_bytes(clean)) != e.get("hash"):
                return False
            prev = e["hash"]
        return anchored_head is None or prev == anchored_head

    def export_events(self) -> str:
        return "\n".join(json.dumps(e, sort_keys=True, ensure_ascii=False) for e in self.events) + ("\n" if self.events else "")

    @property
    def head_digest(self) -> Optional[str]:
        return self.events[-1]["hash"] if self.events else None

    @classmethod
    def restore(cls, *, sources: list[SourceDocument], event_jsonl: str,
                pinned_head: Optional[str],
                semantic_validator: Optional[Callable[[ClaimProposal], bool]] = None) -> "HybridGateway":
        """Replay a ledger, requiring its externally retained head hash.

        This is tamper EVIDENCE (against an anchored head), not authentication;
        there is no trustworthy key store or trusted clock in this prototype.
        """
        if not pinned_head:
            raise ValueError("restore requires independent anchored head digest")
        imported = [json.loads(line) for line in event_jsonl.splitlines() if line.strip()]
        witness = cls(semantic_validator=semantic_validator)
        witness.events = imported
        if not witness.verify_chain(anchored_head=pinned_head):
            raise ValueError("ledger chain does not match anchored head")
        witness.events = []
        for s in sources:
            witness.register_source(s)
        for event in imported:
            kind, at, payload = event["kind"], event["at"], event["payload"]
            if kind == "ADMIT":
                s = witness.sources.get(payload["source_id"])
                if s is None or s.digest != payload["source_digest"]:
                    raise ValueError("source is missing or changed")
                candidate = ClaimProposal(**payload["claim"])
                d = witness.ingest(candidate, recorded_at=at, reviewer_approved=True)
            elif kind == "BATCH_ADMIT":
                rows = payload.get("claims")
                if not isinstance(rows, list) or not rows or payload.get("size") != len(rows):
                    raise ValueError("malformed batch event")
                for row in rows:
                    s = witness.sources.get(row["source_id"])
                    if s is None or s.digest != row["source_digest"] or row["claim_id"] != row["claim"]["claim_id"]:
                        raise ValueError("batch source missing, changed or mismatched")
                candidates = [ClaimProposal(**row["claim"]) for row in rows]
                d = witness.ingest_batch(candidates, recorded_at=at, reviewer_approved=True)
            elif kind == "WITHDRAW":
                d = witness.withdraw(payload["claim_id"], effective_from=payload["effective_from"],
                                     recorded_at=at, reviewer_approved=True)
            else:
                raise ValueError("unknown event type")
            if d.disposition != "ALLOW" or d.event_hash != event["hash"]:
                raise ValueError("ledger event failed deterministic replay")
        return witness
