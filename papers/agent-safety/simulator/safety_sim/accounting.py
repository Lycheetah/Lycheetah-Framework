"""In-memory resource and operation state owned by one trusted control plane.

Sharing Python objects is not distributed accounting or a persistence guarantee.
"""
from dataclasses import dataclass, replace

from .model import Outcome


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
    adapter: object
    outcome: Outcome
