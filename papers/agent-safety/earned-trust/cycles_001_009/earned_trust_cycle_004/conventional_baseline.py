"""Matched conventional same-controls reconciliation baseline.

Uses the SAME cryptographic checks, two separate source IDs, fresh observations,
SQLite integrity checks and status contract. It is written independently as a
plain control checklist: no AURA/CASCADE/LAMAGUE semantics are invoked. Agreement
shows no measured advantage from naming/structuring the checks as Lycheetah.
"""
from __future__ import annotations
import sqlite3
from typing import Any
from authenticated_provider import SignedSQLiteProvider, valid_action
from independent_witness import IndependentObserver


def conventional_reconcile(provider: SignedSQLiteProvider, observer: IndependentObserver,
                           effect_id: str, token: dict[str, Any], action: dict[str, Any],
                           observed: dict[str, Any] | None = None) -> str:
    if not effect_id or not valid_action(action):
        return "REVIEW"
    try:
        receipt = provider.lookup(effect_id)
    except (TypeError, ValueError, UnicodeError, sqlite3.DatabaseError):
        return "REVIEW"
    if receipt is None:
        return "UNKNOWN"
    try:
        if not provider.verify_proof(receipt,token=token,action=action):
            return "REVIEW"
        if not provider.verify_stored_effect(effect_id,token=token):
            return "REVIEW"
        if provider.verify_audit().get('valid') is not True:
            return "REVIEW"
        current=observer.current(effect_id)
    except (TypeError, ValueError, UnicodeError, sqlite3.DatabaseError):
        return "REVIEW"
    if current is None or not observer.verify(current):
        return "REVIEW"
    witness=current if observed is None else observed
    if not observer.verify(witness) or current != witness:
        return "REVIEW"
    a,b=receipt['body'],witness['body']
    if (b['effect_id'] != effect_id or b['action_sha256'] != a['action_sha256']
            or b['token_sha256'] != a['token_sha256']):
        return "CONFLICT"
    if b['status'] == 'NOT_COMMITTED' or b['correctness'] == 'FALSE':
        return "CONFLICT"
    if b['status'] != 'COMMITTED' or b['correctness'] != 'TRUE':
        return "REVIEW"
    return "CONFIRMED"
