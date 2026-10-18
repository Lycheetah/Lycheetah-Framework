"""Unseen-corpus evaluation infrastructure, NOT a published external benchmark.

A frozen, independently labelled JSONL corpus may be supplied by other humans.
The sample fixtures shipped here are SELF-AUTHORED and cannot establish external
validity. This parser never sends documents to an LLM or guesses reference labels.

Each corpus line:
 {"case_id":"case-1", "source_digest":"sha256:<64-hex>",
  "gold":[{"subject":"refunds", "predicate":"window_days", "scope":"store",
           "value":"14", "valid_from":"2026-10-01T00:00:00Z",
           "valid_until":null}], "answerable":true}
Each prediction line:
 {"case_id":"case-1", "claims":[<same fields>], "review_minutes":0.5}

Gold and predictions are read from *separate* files. Raw text must not be
embedded in published aggregate reports. An independent annotator is required
for actual independent validation but cannot be authenticated by this program.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .core import json_bytes, utc

_FIELDS = {'subject', 'predicate', 'scope', 'value', 'valid_from', 'valid_until'}


def _positive_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and 0 <= x <= 1e7


def _claims(items: Any) -> list[tuple[str, str, str, str, str, str | None]]:
    if not isinstance(items, list):
        raise ValueError('claims must be a list')
    normalized = []
    for item in items:
        if not isinstance(item, dict) or set(item) != _FIELDS:
            raise ValueError('claim has missing or unexpected fields')
        if any(not isinstance(item[f], str) or not item[f] for f in
               ('subject', 'predicate', 'scope', 'value', 'valid_from')):
            raise ValueError('claim has missing identity or value')
        if item['valid_until'] is not None and not isinstance(item['valid_until'], str):
            raise ValueError('invalid interval end')
        start = utc(item['valid_from'])
        end = utc(item['valid_until']) if item['valid_until'] is not None else None
        if end is not None and end <= start:
            raise ValueError('claim interval reversed')
        normalized.append((item['subject'], item['predicate'], item['scope'],
                           item['value'], start, end))
    return normalized


def _unique_pairs(pairs):
    d = {}
    for key, value in pairs:
        if key in d:
            raise ValueError('duplicate JSON property')
        d[key] = value
    return d


def _read_jsonl(path: str | Path, *, kind: str) -> tuple[list[dict], str]:
    raw = Path(path).read_bytes()
    if not raw.strip():
        raise ValueError('empty evaluation file')
    rows = []
    ids = set()
    for n, line in enumerate(raw.decode('utf8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line, object_pairs_hook=_unique_pairs,
                             parse_constant=lambda _: (_ for _ in ()).throw(ValueError('non-finite number')))
        except (ValueError, json.JSONDecodeError) as e:
            raise ValueError(f'invalid JSON on line {n}: {e}') from e
        required = ({'case_id', 'source_digest', 'gold', 'answerable'} if kind == 'gold'
                    else {'case_id', 'claims', 'review_minutes'})
        if not isinstance(obj, dict) or set(obj) != required:
            raise ValueError(f'line {n} has missing or unexpected keys')
        ident = obj['case_id']
        if not isinstance(ident, str) or not ident or ident in ids:
            raise ValueError('empty or duplicate case ID')
        ids.add(ident)
        if kind == 'gold':
            dig = obj['source_digest']
            if not isinstance(dig, str) or not dig.startswith('sha256:') or len(dig) != 71:
                raise ValueError('invalid reference source digest')
            try:
                bytes.fromhex(dig[7:])
            except ValueError as e:
                raise ValueError('malformed source SHA256') from e
            gold = _claims(obj['gold'])
            if len(set(gold)) != len(gold):
                raise ValueError('duplicated gold claim')
            if not isinstance(obj['answerable'], bool) or obj['answerable'] != bool(gold):
                raise ValueError('answerable must match nonempty gold')
        else:
            _claims(obj['claims'])  # predictions may duplicate; duplicates count as FP
            if not _positive_num(obj['review_minutes']):
                raise ValueError('invalid review time')
        rows.append(obj)
    if not rows:
        raise ValueError('no evaluation cases')
    return rows, 'sha256:' + hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class EvaluationReport:
    corpus_digest: str
    predictions_digest: str
    cases: int
    positive_cases: int
    negative_cases: int
    true_positive: int
    false_positive: int
    false_negative: int
    wrong_field_or_scope_candidates: int
    exact_document_matches: int
    correct_negative_abstentions: int
    missed_positive_documents: int
    precision: float
    recall: float
    f1: float
    positive_document_coverage: float
    negative_abstention_rate: float
    exact_match_rate: float
    total_review_minutes: float
    note: str = 'Only externally sourced, independently frozen labels yield an external benchmark.'

    def public_dict(self) -> dict:
        return asdict(self)


def evaluate(corpus_file: str | Path, predictions_file: str | Path,
             *, expected_corpus_digest: str | None = None) -> EvaluationReport:
    corpus, corpus_hash = _read_jsonl(corpus_file, kind='gold')
    predicted, prediction_hash = _read_jsonl(predictions_file, kind='predictions')
    if expected_corpus_digest is not None and corpus_hash != expected_corpus_digest:
        raise ValueError('frozen corpus content has changed')
    candidates = {row['case_id']: row for row in predicted}
    if set(candidates) != {row['case_id'] for row in corpus}:
        raise ValueError('prediction IDs must match all corpus IDs exactly')
    tp = fp = fn = exact = neg_ok = pos_missed = wrong_field = 0
    positive = negative = 0
    positive_answered = 0
    review_minutes = 0.0
    for row in corpus:
        gold = set(_claims(row['gold']))
        predictions = _claims(candidates[row['case_id']]['claims'])
        unpaired = list(predictions)
        correct = 0
        for fact in gold:
            if fact in unpaired:
                unpaired.remove(fact)
                correct += 1
        tp += correct
        fp += len(unpaired)
        wrong_field += sum(1 for p in unpaired if any(
            p[3] == g[3] and p[:3] != g[:3] for g in gold))
        fn += len(gold) - correct
        if len(predictions) == len(gold) and correct == len(gold):
            exact += 1
        if gold:
            positive += 1
            if correct:
                positive_answered += 1
            if not predictions:
                pos_missed += 1
        else:
            negative += 1
            if not predictions:
                neg_ok += 1
        review_minutes += candidates[row['case_id']]['review_minutes']
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return EvaluationReport(corpus_hash, prediction_hash, len(corpus), positive,
        negative, tp, fp, fn, wrong_field, exact, neg_ok, pos_missed, precision, recall, f1,
        positive_answered / positive if positive else 0.0,
        neg_ok / negative if negative else 0.0, exact / len(corpus), review_minutes)
