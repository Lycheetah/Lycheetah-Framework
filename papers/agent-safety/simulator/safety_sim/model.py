"""Immutable requests and observations. No proposal executes Python code."""
from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from hashlib import sha256
import json


def canonical(value) -> bytes:
    def convert(item):
        if is_dataclass(item):
            return {f.name: convert(getattr(item, f.name)) for f in fields(item)}
        if isinstance(item, Enum):
            return item.value
        if isinstance(item, frozenset):
            return sorted(convert(x) for x in item)
        if isinstance(item, (tuple, list)):
            return [convert(x) for x in item]
        if isinstance(item, dict):
            return {k: convert(v) for k, v in item.items()}
        return item
    return json.dumps(convert(value), sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value) -> str:
    return sha256(canonical(value)).hexdigest()


def integer(value, name: str, minimum: int = 0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def text(value, name: str):
    if type(value) is not str or not value:
        raise ValueError(f"{name} must be a nonempty string")


class State(str, Enum):
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"
    ADMITTED = "ADMITTED"
    DISPATCHED = "DISPATCHED"
    CONFIRMED = "EFFECT_CONFIRMED"
    FAILED = "FAILED_NO_EFFECT"
    UNKNOWN = "OUTCOME_UNKNOWN"


class Verdict(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class Packet:
    statement: str
    population: str
    setting: str
    support: str
    qualifiers: frozenset[str]
    recommendation: str | None

    def __post_init__(self):
        for name in ("statement", "population", "setting", "support"):
            if type(getattr(self, name)) is not str:
                raise ValueError(f"{name} must be a string")
        if type(self.qualifiers) is not frozenset:
            raise ValueError("qualifiers must be immutable")
        if any(type(x) is not str or not x for x in self.qualifiers):
            raise ValueError("invalid qualifier")
        if self.recommendation is not None:
            text(self.recommendation, "recommendation")


def render(packet: Packet) -> str:
    """Controlled template only; this is not natural-language entailment."""
    return (f"Claim: {packet.statement}\nPopulation: {packet.population}\n"
            f"Setting: {packet.setting}\nSupport: {packet.support}\n"
            f"Qualifications: {'; '.join(sorted(packet.qualifiers))}\n"
            f"Recommendation: {packet.recommendation or 'NONE'}")


@dataclass(frozen=True)
class Artifact:
    packet: Packet
    display: str | None

    def __post_init__(self):
        if type(self.packet) is not Packet:
            raise ValueError("artifact needs a structured Packet")
        if self.display is not None and type(self.display) is not str:
            raise ValueError("display must be text or missing")


@dataclass(frozen=True)
class Context:
    schema: str
    decoder: str
    reference_revision: str

    def __post_init__(self):
        for name in ("schema", "decoder", "reference_revision"):
            text(getattr(self, name), name)


@dataclass(frozen=True)
class Scope:
    operations: frozenset[str]
    objects: frozenset[str]
    recipients: frozenset[str]
    purpose: str

    def __post_init__(self):
        for name in ("operations", "objects", "recipients"):
            value = getattr(self, name)
            if type(value) is not frozenset:
                raise ValueError("scope sets must be immutable")
            if any(type(x) is not str or not x for x in value):
                raise ValueError("invalid scope member")
        text(self.purpose, "purpose")

    def within(self, parent: Scope) -> bool:
        return (self.operations <= parent.operations
                and self.objects <= parent.objects
                and self.recipients <= parent.recipients
                and self.purpose == parent.purpose)


@dataclass(frozen=True)
class Action:
    operation: str
    object_id: str
    expected_revision: int
    charge_limit: int
    effect_id: str
    recipient: str | None = None
    artifact: Artifact | None = None

    def __post_init__(self):
        for name in ("operation", "object_id", "effect_id"):
            text(getattr(self, name), name)
        integer(self.expected_revision, "expected_revision")
        integer(self.charge_limit, "charge_limit")
        if self.recipient is not None:
            text(self.recipient, "recipient")
        if self.artifact is not None and type(self.artifact) is not Artifact:
            raise ValueError("invalid artifact")


@dataclass(frozen=True)
class Outcome:
    effect_id: str
    state: State
    reason: str
    admission_sequence: int | None = None
    charged: int = 0


@dataclass(frozen=True)
class ControlEvent:
    sequence: int
    kind: str
    grant_id: str
    chain: tuple[str, ...] = ()
    effect_id: str = ""
