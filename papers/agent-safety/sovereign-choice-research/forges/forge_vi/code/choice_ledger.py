"""Forge V: atomic intention versions over Lycheetah's *existing* CommitFence database.

Single trust boundary: the protected SQLite finality sink. Instead of a second
journal database, keep choice versions in the *same transaction* that fences
old generations. Reuse upstream CommitFence.issue_handle and .commit intact.

Research software: trusted-host-only API, not identity authentication, a
consent verifier, provider cancellation, general OS sandbox, or a free-will
measurement system. The operator MUST deny agents direct fence DB/port access.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from research_support import Action


@dataclass(frozen=True)
class ChoiceState:
    principal: str
    scope_key: str
    version: int
    generation: int
    purpose: str
    action_hash: str
    active: bool


@dataclass(frozen=True)
class ChoiceVerdict:
    allowed: bool
    reason: str
    handle: Any = None


class AtomicChoiceLedger:
    """Small extension of upstream CommitFence; protected writes share its DB.

    The trusted host must use this API to issue/revise/revoke human grants;
    do not let an LLM reach ``fence.activate``, ``fence.issue_handle`` or SQL.
    No method asserts that the person understood the preview or was uncoerced.
    """

    def __init__(self, fence: Any):
        self.fence = fence
        # We deliberately need the SQLite adapter from the EXACT upstream fence.
        if not callable(getattr(fence, 'connect', None)):
            raise TypeError('expected upstream CommitFence with connect()')
        self.db_path = Path(fence.db_path)
        with closing(self.fence.connect()) as con:
            names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not {'authorities', 'handles', 'effects', 'audit'} <= names:
                raise RuntimeError('upstream CommitFence schema missing')
            con.executescript('''
                CREATE TABLE IF NOT EXISTS choice_intents (
                    principal TEXT NOT NULL,
                    scope_key TEXT NOT NULL,
                    version INTEGER NOT NULL CHECK(version > 0),
                    generation INTEGER NOT NULL CHECK(generation > 0),
                    purpose TEXT NOT NULL,
                    action_hash TEXT NOT NULL,
                    active INTEGER NOT NULL CHECK(active IN (0,1)),
                    PRIMARY KEY(principal,scope_key));
                CREATE TABLE IF NOT EXISTS choice_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    principal TEXT NOT NULL,
                    scope_key TEXT NOT NULL,
                    event TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    generation INTEGER NOT NULL,
                    action_hash TEXT NOT NULL,
                    reason_class TEXT NOT NULL);
            ''')

    @staticmethod
    def _text(v: str, label: str, maxlen: int = 256) -> str:
        if not isinstance(v, str) or not v.strip() or len(v) > maxlen:
            raise ValueError(f'invalid {label}')
        return v

    def _check_action(self, principal: str, scope_key: str, action: Action) -> str:
        if type(action) is not Action:
            raise TypeError('action must be trusted-host research_support.Action')
        if action.principal != principal or action.tool != scope_key:
            raise ValueError('action principal/tool do not match the intended grant')
        if not self._text(action.effect_id, 'effect ID'):
            raise ValueError('missing effect ID')
        ah = action.action_hash
        if not re.fullmatch('[0-9a-f]{64}', ah):
            raise ValueError('invalid action digest')
        return ah

    @staticmethod
    def _as_state(row: Any) -> ChoiceState | None:
        if row is None:
            return None
        return ChoiceState(row['principal'], row['scope_key'], row['version'],
                           row['generation'], row['purpose'], row['action_hash'],
                           bool(row['active']))

    def _write(self, con, principal, scope_key, version, generation,
               purpose, action_hash, active, event, reason_class):
        con.execute('''INSERT INTO choice_intents
            VALUES(?,?,?,?,?,?,?) ON CONFLICT(principal,scope_key) DO UPDATE SET
            version=excluded.version,generation=excluded.generation,
            purpose=excluded.purpose,action_hash=excluded.action_hash,
            active=excluded.active''',
            (principal, scope_key, version, generation, purpose, action_hash, int(active)))
        con.execute('''INSERT INTO choice_events
            (principal,scope_key,event,version,generation,action_hash,reason_class)
            VALUES(?,?,?,?,?,?,?)''',
            (principal, scope_key, event, version, generation, action_hash, reason_class))
        # We add an event to the upstream audit stream, but do not change its code.
        con.execute('''INSERT INTO audit(kind,principal,scope_key,generation,detail)
            VALUES(?,?,?,?,?)''',
            ('CHOICE_'+event, principal, scope_key, generation, f'intent_version={version};reason={reason_class}'))

    def grant(self, principal: str, scope_key: str, purpose: str, action: Action,
              *, reason_class: str = 'endorsed', inject_failure: bool = False) -> ChoiceState:
        """Atomic versioning + generation fence; failure rolls both back.

        ``inject_failure`` is for controlled crash-window testing only. Never
        expose this method directly to an untrusted AI or network request.
        """
        self._text(principal, 'principal')
        self._text(scope_key, 'scope')
        self._text(purpose, 'purpose', 1000)
        self._text(reason_class, 'reason class', 64)
        action_hash = self._check_action(principal, scope_key, action)
        with closing(self.fence.connect()) as con:
            con.execute('BEGIN IMMEDIATE')
            try:
                prior = con.execute('''SELECT * FROM choice_intents
                    WHERE principal=? AND scope_key=?''', (principal,scope_key)).fetchone()
                auth = con.execute('''SELECT generation FROM authorities
                    WHERE principal=? AND scope_key=?''', (principal, scope_key)).fetchone()
                version = 1 if prior is None else prior['version'] + 1
                generation = 1 if auth is None else auth['generation'] + 1
                # Update authoritative generation and the human intention in
                # ONE transaction. Old handles now have stale generations.
                con.execute('''INSERT INTO authorities(principal,scope_key,generation,active)
                    VALUES(?,?,?,1) ON CONFLICT(principal,scope_key) DO UPDATE SET
                    generation=excluded.generation,active=1''',
                    (principal,scope_key,generation))
                self._write(con, principal,scope_key,version,generation,purpose,
                            action_hash,True,'GRANT',reason_class)
                if inject_failure:
                    raise RuntimeError('injected pre-commit failure')
                con.execute('COMMIT')
            except BaseException:
                con.execute('ROLLBACK')
                raise
        return ChoiceState(principal,scope_key,version,generation,purpose,action_hash,True)

    def withdraw(self, principal: str, scope_key: str,
                 *, inject_failure: bool = False) -> ChoiceState | None:
        """Atomic revocation; no human explanation required."""
        self._text(principal, 'principal')
        self._text(scope_key, 'scope')
        with closing(self.fence.connect()) as con:
            con.execute('BEGIN IMMEDIATE')
            try:
                prior = con.execute('''SELECT * FROM choice_intents
                    WHERE principal=? AND scope_key=?''',(principal,scope_key)).fetchone()
                auth = con.execute('''SELECT generation FROM authorities
                    WHERE principal=? AND scope_key=?''', (principal,scope_key)).fetchone()
                generation = 1 if auth is None else auth['generation'] + 1
                con.execute('''INSERT INTO authorities(principal,scope_key,generation,active)
                    VALUES(?,?,?,0) ON CONFLICT(principal,scope_key) DO UPDATE SET
                    generation=excluded.generation,active=0''',
                    (principal,scope_key,generation))
                if prior is not None:
                    version = prior['version'] + 1
                    self._write(con,principal,scope_key,version,generation,prior['purpose'],
                                prior['action_hash'],False,'WITHDRAW','not_required')
                else:
                    con.execute('''INSERT INTO audit(kind,principal,scope_key,generation,detail)
                        VALUES(?,?,?,?,?)''',
                        ('CHOICE_WITHDRAW_UNKNOWN',principal,scope_key,generation,'no prior endorsed intent'))
                if inject_failure:
                    raise RuntimeError('injected pre-commit failure')
                con.execute('COMMIT')
            except BaseException:
                con.execute('ROLLBACK')
                raise
        return None if prior is None else ChoiceState(principal,scope_key,version,generation,
            prior['purpose'],prior['action_hash'],False)

    def current(self, principal: str, scope_key: str) -> ChoiceState | None:
        with closing(self.fence.connect()) as con:
            row=con.execute('''SELECT * FROM choice_intents
                WHERE principal=? AND scope_key=?''',(principal,scope_key)).fetchone()
            return self._as_state(row)

    def _matches(self, principal, scope_key, action):
        ah=self._check_action(principal,scope_key,action)
        with closing(self.fence.connect()) as con:
            row=con.execute('''SELECT i.*,a.generation AS live_generation,
                a.active AS live_active FROM choice_intents i
                LEFT JOIN authorities a ON a.principal=i.principal AND a.scope_key=i.scope_key
                WHERE i.principal=? AND i.scope_key=?''', (principal,scope_key)).fetchone()
            if row is None or not row['active']:
                return None,'no_active_endorsement'
            if not row['live_active'] or row['generation']!=row['live_generation']:
                return None,'stale_authority_generation'
            if ah!=row['action_hash']:
                return None,'action_not_endorsed'
            return self._as_state(row),'matched'

    def issue(self, principal: str, scope_key: str, action: Action) -> ChoiceVerdict:
        """Call unchanged upstream issue_handle and verify generation after issue.

        Any handle issued concurrently with revocation becomes stale at commit.
        """
        prior,reason=self._matches(principal,scope_key,action)
        if prior is None:
            return ChoiceVerdict(False,reason)
        handle,decision=self.fence.issue_handle(principal,scope_key,action)
        if handle is None:
            return ChoiceVerdict(False,getattr(decision,'reason','upstream_denied'))
        latest,reason=self._matches(principal,scope_key,action)
        if latest is None or latest.generation!=prior.generation or handle.generation!=prior.generation:
            return ChoiceVerdict(False,'changed_during_issue')
        return ChoiceVerdict(True,'issued',handle)

    def commit(self, handle: Any, action: Action) -> Any:
        """Delegate the finality boundary to the original CommitFence."""
        return self.fence.commit(handle.handle_id,action)

    def events(self) -> list[dict]:
        with closing(self.fence.connect()) as con:
            return [dict(r) for r in con.execute('SELECT * FROM choice_events ORDER BY sequence')]
