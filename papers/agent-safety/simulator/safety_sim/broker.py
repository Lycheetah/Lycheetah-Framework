"""Protected admission, shared reservations, reconciliation, and effect binding.

This module is trusted by the experiment. It cannot isolate hostile Python code.
"""
from dataclasses import dataclass, replace
from typing import Callable

from .authority import ControlPlane
from .evidence import EvidenceGate
from .model import Action, Outcome, State, Verdict, digest
from .world import FakeService, NoEffect


@dataclass(frozen=True)
class Account:
    limit: int
    spent: int = 0
    reserved: int = 0


class Ledger:
    def __init__(self, lock):
        self._lock = lock
        self._accounts: dict[str, Account] = {}
        self._reservations: dict[str, tuple[str, int]] = {}

    def reserve(self, root_id, limit, effect_id, amount) -> bool:
        with self._lock:
            account = self._accounts.setdefault(root_id, Account(limit))
            if account.limit != limit or effect_id in self._reservations:
                raise RuntimeError("inconsistent protected account")
            if account.spent + account.reserved + amount > limit:
                return False
            self._accounts[root_id] = replace(account, reserved=account.reserved + amount)
            self._reservations[effect_id] = (root_id, amount)
            return True

    def settle(self, effect_id, charge):
        with self._lock:
            root, amount = self._reservations[effect_id]
            if type(charge) is not int or not 0 <= charge <= amount:
                raise RuntimeError("adapter charge exceeds reserved bound")
            account = self._accounts[root]
            self._accounts[root] = replace(account, spent=account.spent + charge,
                                           reserved=account.reserved - amount)
            del self._reservations[effect_id]

    def release_certified_unused(self, effect_id):
        self.settle(effect_id, 0)

    def accounts(self) -> dict[str, Account]:
        with self._lock:
            return dict(self._accounts)


@dataclass(frozen=True)
class Operation:
    actor: str
    request_digest: str
    outcome: Outcome


class Broker:
    def __init__(self, authority: ControlPlane, gate: EvidenceGate,
                 service: FakeService, *, before_dispatch: Callable | None = None):
        self.authority = authority
        self.gate = gate
        self.service = service
        self.ledger = Ledger(authority.lock)
        self._operations: dict[str, Operation] = {}
        self._observations: list[Outcome] = []
        # Only the trusted experiment controller can supply fault hooks.
        self.before_dispatch = before_dispatch

    def _observe(self, outcome: Outcome) -> Outcome:
        with self.authority.lock:
            self._observations.append(outcome)
        return outcome

    def _finish(self, effect_id, state, reason, charged=0):
        with self.authority.lock:
            operation = self._operations[effect_id]
            outcome = replace(operation.outcome, state=state, reason=reason, charged=charged)
            self._operations[effect_id] = replace(operation, outcome=outcome)
            return self._observe(outcome)

    def submit(self, session, grant, action: Action, *, witness=None) -> Outcome:
        if type(action) is not Action:
            return self._observe(Outcome("", State.REJECTED, "malformed action"))
        with self.authority.lock:
            try:
                actor = self.authority.principal(session)
            except PermissionError as error:
                return self._observe(Outcome(action.effect_id, State.REJECTED, str(error)))
            request = digest(action)
            existing = self._operations.get(action.effect_id)
            if existing:
                if existing.actor != actor or existing.request_digest != request:
                    return self._observe(Outcome(action.effect_id, State.REJECTED,
                                                "effect identity reused with different request"))
                return self._observe(existing.outcome)  # Observation, no new admission.
            try:
                access = self.authority.authorize(grant, actor, action)
            except PermissionError as error:
                return self._observe(Outcome(action.effect_id, State.REJECTED, str(error)))
            try:
                document = self.service.snapshot(action.object_id)
            except NoEffect as error:
                return self._observe(Outcome(action.effect_id, State.REJECTED, str(error)))
            if document.revision != action.expected_revision:
                return self._observe(Outcome(action.effect_id, State.REJECTED,
                                            "object revision mismatch at admission"))
            if document.classification not in {"PUBLIC", "PRIVATE"}:
                return self._observe(Outcome(action.effect_id, State.UNRESOLVED,
                                            "unknown document classification"))
            if action.charge_limit < self.service.charge_upper_bound(action):
                return self._observe(Outcome(action.effect_id, State.REJECTED,
                                            "requested charge limit below adapter upper bound"))
            if action.operation == "send_document":
                if action.artifact is not None or action.recipient is None:
                    return self._observe(Outcome(action.effect_id, State.REJECTED,
                                                "invalid send parameters"))
                if document.classification == "PRIVATE" and action.recipient not in document.readers:
                    return self._observe(Outcome(action.effect_id, State.REJECTED,
                                                "document policy forbids recipient"))
            elif action.operation == "write_draft":
                if action.recipient is not None or document.classification != "PUBLIC":
                    return self._observe(Outcome(action.effect_id, State.REJECTED,
                                                "invalid draft destination"))
                review = self.gate.check(witness, action.artifact)
                if review.verdict != Verdict.ACCEPT:
                    state = (State.UNRESOLVED if review.verdict == Verdict.UNRESOLVED
                             else State.REJECTED)
                    return self._observe(Outcome(action.effect_id, state, review.reason))
            else:
                return self._observe(Outcome(action.effect_id, State.REJECTED,
                                            "operation lacks a runtime policy"))
            if not self.ledger.reserve(access.root_id, access.budget,
                                       action.effect_id, action.charge_limit):
                return self._observe(Outcome(action.effect_id, State.REJECTED,
                                            "aggregate resource ceiling reached"))
            sequence = self.authority.event("ADMIT", access.grant_id,
                                           access.chain, action.effect_id)
            outcome = Outcome(action.effect_id, State.ADMITTED, "checks passed", sequence)
            self._operations[action.effect_id] = Operation(actor, request, outcome)
            self._observe(outcome)
        # External dispatch is deliberately outside the admission/revocation lock.
        # A revocation now prevents future admissions, not this admitted effect.
        try:
            if self.before_dispatch:
                self.before_dispatch(action)
            self._finish(action.effect_id, State.DISPATCHED, "synthetic adapter invoked")
            receipt = self.service.dispatch(action)
            with self.authority.lock:
                self.ledger.settle(action.effect_id, receipt.charged)
            return self._finish(action.effect_id, State.CONFIRMED,
                                "provider effect confirmed", receipt.charged)
        except NoEffect as error:
            with self.authority.lock:
                self.ledger.release_certified_unused(action.effect_id)
            return self._finish(action.effect_id, State.FAILED, str(error))
        except Exception:
            # Preserve the reservation: transport errors are not proof of no effect.
            return self._finish(action.effect_id, State.UNKNOWN,
                                "dispatch outcome requires reconciliation")

    def reconcile(self, session, effect_id) -> Outcome:
        if type(effect_id) is not str or not effect_id:
            return self._observe(Outcome("", State.REJECTED, "invalid effect identifier"))
        with self.authority.lock:
            try:
                actor = self.authority.principal(session)
            except PermissionError as error:
                return self._observe(Outcome(effect_id, State.REJECTED, str(error)))
            operation = self._operations.get(effect_id)
            if operation is None or operation.actor != actor:
                return self._observe(Outcome(effect_id, State.REJECTED,
                                            "operation absent from authenticated session"))
            if operation.outcome.state != State.UNKNOWN:
                return self._observe(operation.outcome)
            receipt = self.service.lookup(effect_id)
            if receipt is None:
                return self._observe(operation.outcome)
            if receipt.request_digest != operation.request_digest:
                return self._observe(Outcome(effect_id, State.UNRESOLVED,
                                            "provider receipt request mismatch"))
            self.ledger.settle(effect_id, receipt.charged)
            return self._finish(effect_id, State.CONFIRMED,
                                "provider acceptance reconciled", receipt.charged)

    def observations(self) -> tuple[Outcome, ...]:
        with self.authority.lock:
            return tuple(self._observations)
