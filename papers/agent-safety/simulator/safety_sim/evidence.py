"""Exact structured qualification checks, not a learned semantic oracle."""
from dataclasses import dataclass
from secrets import token_hex
from threading import RLock

from .model import Artifact, Context, Packet, Verdict, digest, render


@dataclass(frozen=True)
class Review:
    verdict: Verdict
    checks: tuple[tuple[str, bool], ...]
    reason: str
    handle: str | None = None


@dataclass(frozen=True)
class Witness:
    source_digest: str
    target_digest: str
    context_digest: str
    contract: str
    validator: str
    checks: tuple[tuple[str, bool], ...]


class EvidenceGate:
    def __init__(self, source: Packet, context: Context):
        if type(source) is not Packet or type(context) is not Context:
            raise ValueError("invalid trusted source or context")
        self._source = source
        self._context = context
        self._witnesses: dict[str, Witness] = {}
        self._lock = RLock()
        self.contract = "structured-translation/1"
        self.validator = "exact-fields-and-controlled-renderer/1"

    def update_context(self, context: Context):
        """Trusted harness operation; invalidates earlier witness uses."""
        if type(context) is not Context:
            raise ValueError("invalid context")
        with self._lock:
            self._context = context

    def update_source(self, source: Packet):
        """Trusted revision; source digest makes previous witnesses unusable."""
        if type(source) is not Packet:
            raise ValueError("invalid source")
        with self._lock:
            self._source = source

    def review(self, target: Artifact, context: Context | None) -> Review:
        with self._lock:
            if type(target) is not Artifact or context is None or target.display is None:
                return Review(Verdict.UNRESOLVED, (), "missing representation/context")
            if type(context) is not Context or context != self._context:
                return Review(Verdict.REJECT, (), "context changed")
            source, packet = self._source, target.packet
            checks = (
                ("useful_statement", bool(packet.statement)),
                ("statement_retained", packet.statement == source.statement),
                ("population_retained", packet.population == source.population),
                ("setting_retained", packet.setting == source.setting),
                ("support_retained", packet.support == source.support),
                # Extra uncontrolled strings could themselves add instructions.
                ("qualifiers_retained", source.qualifiers == packet.qualifiers),
                ("recommendation_not_expanded", packet.recommendation in
                 (None, source.recommendation)),
                ("consumer_matches_controlled_render", target.display == render(packet)),
            )
            if not all(value for _, value in checks):
                failed = ", ".join(name for name, value in checks if not value)
                return Review(Verdict.REJECT, checks, failed)
            handle = token_hex(24)
            self._witnesses[handle] = Witness(digest(source), digest(target),
                digest(context), self.contract, self.validator, checks)
            return Review(Verdict.ACCEPT, checks, "selected obligations pass", handle)

    def check(self, handle, target: Artifact | None) -> Review:
        with self._lock:
            if target is None or handle is None:
                return Review(Verdict.UNRESOLVED, (), "required evidence missing")
            if type(handle) is not str or handle not in self._witnesses:
                return Review(Verdict.REJECT, (), "unknown witness")
            witness = self._witnesses[handle]
            matches = (
                witness.source_digest == digest(self._source)
                and witness.target_digest == digest(target)
                and witness.context_digest == digest(self._context)
                and witness.contract == self.contract
                and witness.validator == self.validator
                and len(witness.checks) == 8
                and all(passed for _, passed in witness.checks)
            )
            if not matches:
                return Review(Verdict.REJECT, witness.checks, "witness binding changed")
            return Review(Verdict.ACCEPT, witness.checks, "protected witness matched", handle)
