"""Independent SQL bitemporal query comparator for already-admitted gateway events.

Does not call the gateway's query, _visible, _by_key or suppression functions.
Competes on query-time reasoning, NOT fact-extraction accuracy. SQL (SQLite 3)
implements half-open valid-time, knowledge-time, withdrawals, exact scope,
transitive supersession and explicit conflict abstention.

Trusted event inputs only: this is not a verifier; callers must verify/anchor
source event history before constructing the SQL snapshot. In-memory database.
"""
from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from typing import Iterable, Mapping
from .core import utc


@dataclass(frozen=True)
class SQLAnswer:
    disposition: str
    value: str | None
    claim_ids: tuple[str, ...]


class SQLTemporalBaseline:
    def __init__(self, events: Iterable[Mapping]):
        self.db = sqlite3.connect(':memory:')
        self.db.executescript('''
          CREATE TABLE claims (
            id TEXT PRIMARY KEY, tenant TEXT NOT NULL, subject TEXT NOT NULL,
            predicate TEXT NOT NULL, scope TEXT NOT NULL, value TEXT NOT NULL,
            valid_from TEXT NOT NULL, valid_until TEXT, recorded_at TEXT NOT NULL
          );
          CREATE TABLE supersession (child TEXT NOT NULL, parent TEXT NOT NULL,
            PRIMARY KEY(child,parent));
          CREATE TABLE withdrawals (claim_id TEXT NOT NULL, effective_from TEXT NOT NULL,
            recorded_at TEXT NOT NULL);
          CREATE INDEX i_scope ON claims(tenant,subject,predicate,scope);
          CREATE INDEX i_sups ON supersession(child,parent);
          CREATE INDEX i_withdrawals ON withdrawals(claim_id,recorded_at,effective_from);
        ''')
        for event in events:
            kind, at = event['kind'], utc(event['at'])
            if kind == 'ADMIT':
                rows = [event['payload']['claim']]
            elif kind == 'BATCH_ADMIT':
                rows = [r['claim'] for r in event['payload']['claims']]
            elif kind == 'WITHDRAW':
                p = event['payload']
                self.db.execute('INSERT INTO withdrawals VALUES(?,?,?)',
                                (p['claim_id'], utc(p['effective_from']), at))
                continue
            else:
                raise ValueError('unsupported event kind')
            for p in rows:
                self.db.execute('INSERT INTO claims VALUES(?,?,?,?,?,?,?,?,?)',
                                (p['claim_id'], p['tenant'], p['subject'], p['predicate'],
                                 p['scope'], p['value'], utc(p['valid_from']),
                                 utc(p['valid_until']) if p['valid_until'] is not None else None, at))
                for parent in p['supersedes']:
                    self.db.execute('INSERT INTO supersession VALUES (?,?)', (p['claim_id'], parent))
        self.db.commit()

    def query(self, *, tenant: str, subject: str, predicate: str, scope: str,
              effective_at: str, known_at: str) -> SQLAnswer:
        eff, known = utc(effective_at), utc(known_at)
        # Recursion follows transitive ancestors even when intervening claims
        # are withdrawn, no longer effective or not yet known.
        sql = '''
            WITH RECURSIVE
            visible(id, value) AS (
              SELECT c.id,c.value FROM claims c WHERE c.tenant=? AND c.subject=?
                AND c.predicate=? AND c.scope=? AND c.recorded_at<=?
                AND c.valid_from<=? AND (c.valid_until IS NULL OR ?<c.valid_until)
                AND NOT EXISTS (
                  SELECT 1 FROM withdrawals w WHERE w.claim_id=c.id
                    AND w.recorded_at<=? AND w.effective_from<=?
                )
            ),
            ancestors(origin, parent) AS (
              SELECT v.id,s.parent FROM visible v
                JOIN supersession s ON s.child=v.id
              UNION
              SELECT a.origin,s.parent FROM ancestors a
                JOIN supersession s ON s.child=a.parent
            )
            SELECT v.id,v.value FROM visible v
            WHERE NOT EXISTS(SELECT 1 FROM ancestors a WHERE a.parent=v.id)
            ORDER BY v.id
        '''
        rows = self.db.execute(sql, (tenant, subject, predicate, scope, known, eff,
                                    eff, known, eff)).fetchall()
        if not rows:
            return SQLAnswer('ABSTAIN_NO_EVIDENCE', None, ())
        values = {r[1] for r in rows}
        if len(values) > 1:
            return SQLAnswer('ABSTAIN_CONFLICT', None, tuple(r[0] for r in rows))
        return SQLAnswer('ANSWER', rows[0][1], tuple(r[0] for r in rows))

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
