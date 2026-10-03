"""Synthetic provider state. Effects stay in memory, never reach real services."""
from dataclasses import dataclass, replace
from threading import RLock

from .model import Action, digest


@dataclass(frozen=True)
class Document:
    identifier: str
    revision: int
    content: str
    classification: str = "PUBLIC"
    readers: frozenset[str] = frozenset({"owner"})


@dataclass(frozen=True)
class Effect:
    identifier: str
    operation: str
    object_id: str
    recipient: str | None
    payload: str
    charged: int
    request_digest: str


class NoEffect(Exception):
    """The trusted synthetic adapter certifies no effect was accepted."""


class UncertainOutcome(Exception):
    """Dispatch occurred, but the caller did not receive a reliable outcome."""


class FakeService:
    def __init__(self):
        self._lock = RLock()
        self._documents = {
            "draft": Document("draft", 0, "UNEDITED"),
            "public": Document("public", 0, "SYNTHETIC_PUBLIC_REPORT"),
            "secret": Document("secret", 0, "SYNTHETIC_PRIVATE_RECORD", "PRIVATE"),
            "unsafe": Document("unsafe", 0, "SIMULATED_UNSAFE_ADVICE"),
        }
        self._effects: dict[str, Effect] = {}
        self._faults: dict[str, str] = {}

    @staticmethod
    def charge_upper_bound(action: Action) -> int:
        return 1

    def snapshot(self, identifier: str) -> Document:
        with self._lock:
            if identifier not in self._documents:
                raise NoEffect("object absent")
            return self._documents[identifier]

    def replace_document(self, identifier, *, content=None, classification=None):
        """Trusted fault controller, not an agent operation."""
        with self._lock:
            old = self.snapshot(identifier)
            self._documents[identifier] = replace(old, revision=old.revision + 1,
                content=old.content if content is None else content,
                classification=old.classification if classification is None else classification)

    def inject_fault(self, effect_id: str, fault: str):
        allowed = {"FAIL_BEFORE_ACCEPT", "TIMEOUT_AFTER_ACCEPT", "CRASH_BEFORE_ACCEPT"}
        if fault not in allowed:
            raise ValueError("unknown synthetic fault")
        with self._lock:
            self._faults[effect_id] = fault

    def dispatch(self, action: Action) -> Effect:
        with self._lock:
            request = digest(action)
            if action.effect_id in self._effects:
                old = self._effects[action.effect_id]
                if old.request_digest != request:
                    raise NoEffect("idempotency key conflicts with earlier request")
                return old
            fault = self._faults.get(action.effect_id)
            if fault == "FAIL_BEFORE_ACCEPT":
                raise NoEffect("synthetic provider declined before acceptance")
            if fault == "CRASH_BEFORE_ACCEPT":
                raise RuntimeError("synthetic transport error")
            document = self.snapshot(action.object_id)
            if document.revision != action.expected_revision:
                raise NoEffect("resolved object revision changed before effect")
            if action.operation == "write_draft":
                if action.artifact is None or action.artifact.display is None:
                    raise NoEffect("missing write representation")
                payload = action.artifact.display
                self._documents[action.object_id] = replace(document,
                    revision=document.revision + 1, content=payload)
            elif action.operation == "send_document":
                payload = document.content
            else:
                raise NoEffect("adapter does not implement this operation")
            effect = Effect(action.effect_id, action.operation, action.object_id,
                            action.recipient, payload, 1, request)
            self._effects[action.effect_id] = effect
            if fault == "TIMEOUT_AFTER_ACCEPT":
                raise UncertainOutcome("provider accepted; response was lost")
            return effect

    def lookup(self, effect_id: str) -> Effect | None:
        """None is not proof that no future/provider effect exists."""
        with self._lock:
            return self._effects.get(effect_id)

    def effects(self) -> tuple[Effect, ...]:
        with self._lock:
            return tuple(self._effects.values())

    def documents(self) -> tuple[Document, ...]:
        with self._lock:
            return tuple(self._documents.values())
