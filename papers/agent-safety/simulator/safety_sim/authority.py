"""Two protected permission stores with equivalent tested semantics.

The harness authenticates sessions; callers cannot choose their principal in an
Action. Python attribute privacy is not an isolation boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from secrets import token_hex
from threading import RLock
from typing import Callable

from .model import Action, ControlEvent, Scope, integer, text


@dataclass(frozen=True)
class Access:
    grant_id: str
    root_id: str
    budget: int
    chain: tuple[str, ...]


@dataclass(frozen=True)
class Grant:
    identifier: str
    principal: str
    scope: Scope
    expires: int
    budget: int
    root: str
    parent: str | None
    delegable: bool
    revoked: bool = False


class ControlPlane:
    def __init__(self, now: Callable[[], int]):
        self.lock = RLock()
        self.now = now
        self._sessions: dict[str, str] = {}
        self._events: list[ControlEvent] = []
        self._sequence = 0

    def open_session(self, principal: str) -> str:
        """Trusted harness operation, never exposed as an agent tool."""
        text(principal, "principal")
        with self.lock:
            handle = token_hex(24)
            self._sessions[handle] = principal
            return handle

    def principal(self, session: str) -> str:
        if type(session) is not str or session not in self._sessions:
            raise PermissionError("unknown authenticated session")
        return self._sessions[session]

    def event(self, kind: str, grant_id: str, chain=(), effect_id="") -> int:
        with self.lock:
            self._sequence += 1
            self._events.append(ControlEvent(self._sequence, kind, grant_id,
                                             tuple(chain), effect_id))
            return self._sequence

    def events(self) -> tuple[ControlEvent, ...]:
        with self.lock:
            return tuple(self._events)


class CapabilityAuthority(ControlPlane):
    """Opaque handles bind immutable, issuer-owned scoped leases."""
    label = "C: scoped capability contracts"

    def __init__(self, now):
        super().__init__(now)
        self._handles: dict[str, str] = {}
        self._grants: dict[str, Grant] = {}

    def _store(self, principal, scope, expires, budget, parent, delegable):
        identifier = f"lease-{len(self._grants) + 1}"
        root = self._grants[parent].root if parent else identifier
        self._grants[identifier] = Grant(identifier, principal, scope, expires,
                                         budget, root, parent, delegable)
        handle = token_hex(24)
        self._handles[handle] = identifier
        return handle

    def _lookup(self, handle):
        if type(handle) is not str or handle not in self._handles:
            raise PermissionError("unknown capability handle")
        return self._grants[self._handles[handle]]

    def _chain(self, grant):
        chain = []
        while grant:
            if grant.revoked or self.now() >= grant.expires:
                raise PermissionError("lease or ancestor expired/revoked")
            chain.append(grant.identifier)
            grant = self._grants[grant.parent] if grant.parent else None
        return tuple(chain)

    def issue_root(self, principal, scope, *, expires=100, budget=5,
                   delegable=True):
        with self.lock:
            text(principal, "principal")
            integer(expires, "expiry", self.now() + 1)
            integer(budget, "budget")
            if type(scope) is not Scope or type(delegable) is not bool:
                raise ValueError("invalid root grant")
            return self._store(principal, scope, expires, budget, None, delegable)

    def delegate(self, parent_handle, principal, scope, *, expires=100,
                 delegable=False):
        with self.lock:
            parent = self._lookup(parent_handle)
            self._chain(parent)
            text(principal, "principal")
            integer(expires, "expiry", self.now() + 1)
            if type(scope) is not Scope or type(delegable) is not bool:
                raise ValueError("invalid child grant")
            if not parent.delegable or not scope.within(parent.scope):
                raise PermissionError("delegation would enlarge authority")
            if expires > parent.expires:
                raise PermissionError("child outlives parent")
            return self._store(principal, scope, expires, parent.budget,
                               parent.identifier, delegable)

    def authorize(self, handle, principal, action: Action) -> Access:
        with self.lock:
            grant = self._lookup(handle)
            chain = self._chain(grant)
            if principal != grant.principal:
                raise PermissionError("capability bound to another principal")
            if action.operation not in grant.scope.operations:
                raise PermissionError("operation outside grant")
            if action.object_id not in grant.scope.objects:
                raise PermissionError("object outside grant")
            if (action.recipient is not None
                    and action.recipient not in grant.scope.recipients):
                raise PermissionError("recipient outside grant")
            return Access(grant.identifier, grant.root, grant.budget, chain)

    def revoke(self, handle):
        with self.lock:
            grant = self._lookup(handle)
            self._grants[grant.identifier] = replace(grant, revoked=True)
            return self.event("REVOKE", grant.identifier)


class ConventionalACL(ControlPlane):
    """Separate implementation of issuer-owned ACL rows and ancestry.

    Public row identifiers confer no authority without the authenticated
    principal. Evidence, adapters, accounting, and broker are deliberately shared.
    """
    label = "D: conventional protected ACLs"

    def __init__(self, now):
        super().__init__(now)
        self._rows: dict[str, dict] = {}

    def _active_path(self, row_id):
        path = []
        while row_id is not None:
            if type(row_id) is not str or row_id not in self._rows:
                raise PermissionError("unknown ACL row")
            row = self._rows[row_id]
            if row["disabled"] or row["until"] <= self.now():
                raise PermissionError("ACL row or ancestor expired/revoked")
            path.append(row_id)
            row_id = row["parent"]
        return tuple(path)

    def issue_root(self, principal, scope, *, expires=100, budget=5,
                   delegable=True):
        with self.lock:
            text(principal, "principal")
            integer(expires, "expiry", self.now() + 1)
            integer(budget, "budget")
            if type(scope) is not Scope or type(delegable) is not bool:
                raise ValueError("invalid ACL grant")
            identifier = f"entry-{len(self._rows) + 1}"
            self._rows[identifier] = dict(user=principal, scope=scope, until=expires,
                limit=budget, root=identifier, parent=None, forward=delegable,
                disabled=False)
            return identifier

    def delegate(self, parent_handle, principal, scope, *, expires=100,
                 delegable=False):
        with self.lock:
            self._active_path(parent_handle)
            parent = self._rows[parent_handle]
            text(principal, "principal")
            integer(expires, "expiry", self.now() + 1)
            if type(scope) is not Scope or type(delegable) is not bool:
                raise ValueError("invalid child ACL")
            old = parent["scope"]
            subset = (scope.operations <= old.operations
                      and scope.objects <= old.objects
                      and scope.recipients <= old.recipients
                      and scope.purpose == old.purpose)
            if not parent["forward"] or not subset or expires > parent["until"]:
                raise PermissionError("ACL propagation enlarges authority")
            identifier = f"entry-{len(self._rows) + 1}"
            self._rows[identifier] = dict(user=principal, scope=scope, until=expires,
                limit=parent["limit"], root=parent["root"], parent=parent_handle,
                forward=delegable, disabled=False)
            return identifier

    def authorize(self, handle, principal, action):
        with self.lock:
            chain = self._active_path(handle)
            row = self._rows[handle]
            if row["user"] != principal:
                raise PermissionError("principal absent from ACL")
            scope = row["scope"]
            if action.operation not in scope.operations:
                raise PermissionError("ACL denies operation")
            if action.object_id not in scope.objects:
                raise PermissionError("ACL denies object")
            if action.recipient is not None and action.recipient not in scope.recipients:
                raise PermissionError("ACL denies recipient")
            return Access(handle, row["root"], row["limit"], chain)

    def revoke(self, handle):
        with self.lock:
            if type(handle) is not str or handle not in self._rows:
                raise PermissionError("unknown ACL row")
            self._rows[handle]["disabled"] = True
            return self.event("REVOKE", handle)
