"""Cycle 12: externally retained journal checkpoint, separate from the SQLite database.

This is an integrity witness, not independent reviewer authentication.
Store the checkpoint in a separately controlled location to detect rollback/truncation.
"""
from __future__ import annotations
import hashlib
import hmac
import json
from dataclasses import dataclass, asdict
from .review_journal import audit_decisions
from .authorization import ReviewKeyring

@dataclass(frozen=True)
class Witness:
    ledger_id: str
    count: int
    head: str | None
    signature: str

def _payload(ledger_id, count, head):
    return json.dumps({"purpose":"lycheetah.external-journal-witness.v1",
                       "ledger_id":ledger_id,"count":count,"head":head},
                      sort_keys=True,separators=(",",":")).encode()

def issue_witness(conn, *, ledger_id: str, journal_keys: ReviewKeyring,
                  witness_secret: bytes) -> Witness:
    if len(witness_secret)<32: raise ValueError("witness key too short")
    audit=audit_decisions(conn,ledger_id=ledger_id,keyring=journal_keys)
    if audit["invalid_entries"]: raise ValueError("journal audit failed")
    rows=conn.execute("SELECT entry_hash FROM review_decisions ORDER BY seq").fetchall()
    count=len(rows)
    head=rows[-1]["entry_hash"] if rows else None
    sig=hmac.new(witness_secret,_payload(ledger_id,count,head),hashlib.sha256).hexdigest()
    return Witness(ledger_id,count,head,sig)

def verify_witness(conn, *, witness: Witness, ledger_id: str,
                   journal_keys: ReviewKeyring, witness_secret: bytes) -> bool:
    if len(witness_secret)<32: return False
    expected=hmac.new(witness_secret,_payload(witness.ledger_id,witness.count,witness.head),
                      hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected,witness.signature) or witness.ledger_id!=ledger_id:
        return False
    audit=audit_decisions(conn,ledger_id=ledger_id,keyring=journal_keys)
    if audit["invalid_entries"]: return False
    rows=conn.execute("SELECT entry_hash FROM review_decisions ORDER BY seq").fetchall()
    if len(rows)<witness.count: return False
    actual=rows[witness.count-1]["entry_hash"] if witness.count else None
    return actual==witness.head
