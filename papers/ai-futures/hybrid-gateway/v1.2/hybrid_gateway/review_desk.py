"""Cycle 10: loopback-only, password-gated reference review desk.

A neural adapter cannot reach this service via the gateway API. The service is
constructed only with a trusted operator plan and candidate batch, never arbitrary
HTTP-submitted claims. Successful human interface interaction proves knowledge
of a local password and possession of a CSRF-protected session, NOT real-world
identity, attentive reading, or protected signing-key custody.

NOT for deployment on a public host. No TLS, SSO, durable rejected-decision journal,
process sandbox, key-management system or external event anchor is provided.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from contextlib import closing
from datetime import datetime, timezone
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import html
import json
import re
import secrets
import sqlite3
import threading
import time
from typing import Mapping
from urllib.parse import parse_qs, urlsplit

from .authorization import ReviewKeyring, batch_digest, issue_approval
from .core import Decision, canonical_digest, json_bytes, utc
from .coverage import AuditedBatch, ExtractionPlan, _fingerprint_candidate
from .contracts import TrustedContractRegistry
from .durable import SQLiteLedger
from .review_journal import ReviewJournalAuthority


@dataclass(frozen=True)
class ReviewOutcome:
    disposition: str
    reason: str
    at: str
    elapsed_seconds: float | None
    event_hash: str | None


class ReviewDesk:
    """One immutable operator-staged batch + one local browser review decision."""

    SESSION_SECONDS = 900
    MAX_PASSWORD_TRIES = 5

    def __init__(self, *, ledger: SQLiteLedger, registry: TrustedContractRegistry,
                 plan: ExtractionPlan, batch: AuditedBatch, recorded_at: str,
                 key_id: str, signing_secret: bytes, password: str):
        if not isinstance(ledger, SQLiteLedger) or not isinstance(registry, TrustedContractRegistry):
            raise TypeError('trusted ledger and registry required')
        if not isinstance(plan, ExtractionPlan) or not isinstance(batch, AuditedBatch):
            raise TypeError('trusted extraction plan and audited batch required')
        if not isinstance(password, str) or len(password) < 16:
            raise ValueError('local reviewer password must have at least 16 characters')
        if batch.receipt.disposition != 'READY_FOR_REVIEW' or not batch.stages:
            raise ValueError('only complete, nonempty, reviewed-plan batches can be shown')
        if (batch.receipt.plan_fingerprint != plan.fingerprint or
            batch.receipt.registry_fingerprint != registry.fingerprint or
            batch.receipt.source_digest != plan.source_digest or
            batch.receipt.source_id != plan.source_id):
            raise ValueError('staged batch and operator plan disagree')
        source = registry.registered_source(plan.source_id)
        if source is None or source.digest != plan.source_digest:
            raise ValueError('unregistered review source')
        # Do not leave the service's authorization ambiguous on legacy databases.
        with closing(ledger._connect()) as conn:
            row = conn.execute("SELECT value FROM gateway_settings WHERE name='approval_policy'").fetchone()
            journal_policy = conn.execute("SELECT value FROM gateway_settings WHERE name='review_policy'").fetchone()
        if journal_policy is not None and journal_policy['value']!='journal_v1':
            raise ValueError('unknown local review journal policy')
        self.__journal_enabled = journal_policy is not None
        if row is None or row['value'] != 'signed_v1':
            raise ValueError('review desk requires a strict signed-approval SQLite ledger')
        ReviewKeyring({key_id: signing_secret})
        self.ledger = ledger
        self.registry = registry
        self.plan = plan
        self.batch = batch
        self.source = source
        self.recorded_at = utc(recorded_at)
        self.key_id = key_id
        self.__secret = signing_secret
        self.__password_salt = secrets.token_bytes(16)
        self.__password_digest = hashlib.scrypt(password.encode('utf-8'), salt=self.__password_salt,
                                                n=2**14, r=8, p=1, dklen=32)
        self.__sessions: dict[str, dict] = {}
        self.__failures: list[float] = []
        self.__lock = threading.RLock()
        self.__decision: ReviewOutcome | None = None
        self.__ledger_id = ledger.ledger_id
        self.__fingerprint = batch_digest(batch)
        self.__view = self._snapshot()
        self.view_digest = canonical_digest(json_bytes(self.__view))

    def _snapshot(self) -> dict:
        return {
            'source': asdict(self.source),
            'plan': asdict(self.plan),
            'receipt': asdict(self.batch.receipt),
            'candidates': [asdict(stage.staged.candidate) for stage in self.batch.stages],
            'contracts': [asdict(self.registry.matched_contract(stage.staged.candidate))
                          for stage in self.batch.stages],
            'ledger_id': self.__ledger_id,
            'recorded_at': self.recorded_at,
        }

    def _invariant(self) -> bool:
        with closing(self.ledger._connect()) as conn:
            row=conn.execute("SELECT value FROM gateway_settings WHERE name='review_policy'").fetchone()
            current_journal = row is not None and row['value']=='journal_v1'
        return (current_journal == self.__journal_enabled and
                self.__ledger_id == self.ledger.ledger_id and
                self.__fingerprint == batch_digest(self.batch) and
                self.view_digest == canonical_digest(json_bytes(self._snapshot())) and
                self.registry.fingerprint == self.plan.registry_fingerprint and
                self.registry.registered_source(self.plan.source_id) == self.source and
                self.plan.fingerprint == self.batch.receipt.plan_fingerprint)

    def login(self, password: str, *, now: float | None = None) -> tuple[str, str] | None:
        """Return (unpredictable cookie, csrf) only after local-password validation."""
        now = time.monotonic() if now is None else now
        with self.__lock:
            self.__failures = [t for t in self.__failures if now - t < 60]
            if len(self.__failures) >= self.MAX_PASSWORD_TRIES:
                return None
            # Hash candidate even when incorrect. Never retain submitted password.
            if not isinstance(password, str) or len(password) > 1024:
                self.__failures.append(now)
                return None
            calculated = hashlib.scrypt(password.encode('utf-8'), salt=self.__password_salt,
                                        n=2**14, r=8, p=1, dklen=32)
            if not secrets.compare_digest(self.__password_digest, calculated):
                self.__failures.append(now)
                return None
            self.__failures.clear()
            token = secrets.token_urlsafe(32)
            csrf = secrets.token_urlsafe(32)
            self.__sessions[hashlib.sha256(token.encode()).hexdigest()] = {
                'csrf': csrf, 'expires': now + self.SESSION_SECONDS,
                'started': None,
            }
            return token, csrf

    def session(self, token: str, *, now: float | None = None) -> dict | None:
        now = time.monotonic() if now is None else now
        if not isinstance(token, str) or len(token) > 128:
            return None
        with self.__lock:
            k = hashlib.sha256(token.encode()).hexdigest()
            entry = self.__sessions.get(k)
            if entry is None:
                return None
            if now >= entry['expires']:
                self.__sessions.pop(k, None)
                return None
            return entry.copy()

    def start_review(self, token: str, *, now: float | None = None) -> dict | None:
        now = time.monotonic() if now is None else now
        with self.__lock:
            session = self.session(token, now=now)
            if session is None:
                return None
            key = hashlib.sha256(token.encode()).hexdigest()
            if self.__sessions[key]['started'] is None:
                self.__sessions[key]['started'] = now
            return self.__sessions[key].copy()

    def logout(self, token: str) -> None:
        with self.__lock:
            self.__sessions.pop(hashlib.sha256(token.encode()).hexdigest(), None)

    @property
    def outcome(self) -> ReviewOutcome | None:
        with self.__lock:
            return self.__decision

    def submit(self, token: str, *, csrf: str, presented_digest: str,
               decision: str, confirmation: str = '', now: float | None = None) -> ReviewOutcome:
        now = time.monotonic() if now is None else now
        with self.__lock:
            session = self.session(token, now=now)
            if session is None or session['started'] is None:
                return ReviewOutcome('REVIEW', 'authenticated review session required', self._now(), None, None)
            if (not isinstance(csrf, str) or
                    not secrets.compare_digest(session['csrf'], csrf)):
                return ReviewOutcome('BLOCK', 'invalid CSRF token', self._now(), None, None)
            if (not isinstance(presented_digest, str) or
                    not secrets.compare_digest(self.view_digest, presented_digest)):
                return ReviewOutcome('BLOCK', 'review presentation changed', self._now(), None, None)
            if self.__decision is not None:
                return ReviewOutcome('BLOCK', 'this review has already been decided', self._now(), None, None)
            if not self._invariant():
                return ReviewOutcome('REVIEW', 'operator batch or ledger identity changed', self._now(), None, None)
            elapsed = max(0.0, now - session['started'])
            if decision == 'reject':
                if self.__journal_enabled:
                    try:
                        self.ledger.record_rejection(self.batch,registry=self.registry,plan=self.plan,
                            authority=self._journal_authority(),
                            trusted_keys=ReviewKeyring({self.key_id:self.__secret}))
                    except sqlite3.DatabaseError:
                        return ReviewOutcome('BLOCK','batch already decided',self._now(),None,None)
                    except ValueError:
                        return ReviewOutcome('REVIEW','rejection could not be durably recorded',self._now(),None,None)
                self.__decision = ReviewOutcome('REJECTED', 'operator rejected all claims',
                                                self._now(), elapsed, None)
                return self.__decision
            if decision != 'approve' or confirmation != 'YES_REVIEWED_EXACT_BATCH':
                return ReviewOutcome('REVIEW', 'explicit full-batch approval required', self._now(), None, None)
            # The model and browser cannot choose nonce, TTL, key, ledger ID or timestamp.
            permit = issue_approval(self.batch, self.plan, key_id=self.key_id,
                                    secret=self.__secret, recorded_at=self.recorded_at,
                                    ledger_id=self.__ledger_id)
            try:
                result = self.ledger.commit_batch(self.batch, registry=self.registry,
                    plan=self.plan, recorded_at=self.recorded_at, authorization=permit,
                    trusted_keys=ReviewKeyring({self.key_id: self.__secret}),
                    review_journal_authority=self._journal_authority() if self.__journal_enabled else None)
            except sqlite3.DatabaseError:
                return ReviewOutcome('BLOCK','batch was already decided or database rejected the write',self._now(),None,None)
            except ValueError:
                return ReviewOutcome('REVIEW','approval could not be durably recorded',self._now(),None,None)
            if result.disposition == 'ALLOW':
                self.__decision = ReviewOutcome('APPROVED',
                    'signed permit committed with complete knowledge batch', self._now(),
                    elapsed, result.event_hash)
                return self.__decision
            return ReviewOutcome(result.disposition, result.reason,
                                 self._now(), elapsed, result.event_hash)

    def _journal_authority(self) -> ReviewJournalAuthority:
        return ReviewJournalAuthority(key_id=self.key_id,secret=self.__secret,
            ledger_id=self.__ledger_id,presentation_digest=self.view_digest,
            batch_fingerprint=self.__fingerprint)

    def observation(self) -> dict:
        """Privacy-minimized optional experiment record, not evidence of attention.

        The report omits source prose, proposed values, passwords, keys and cookies.
        A completed event may later be correlated using the persisted event hash.
        """
        with self.__lock:
            outcome = self.__decision
            return {
                'schema': 'lycheetah.local-review-observation.v1',
                'status': 'UNDECIDED' if outcome is None else outcome.disposition,
                'source_digest': self.source.digest,
                'presentation_digest': self.view_digest,
                'batch_digest': self.__fingerprint,
                'claims_in_batch': len(self.batch.stages),
                'session_elapsed_seconds': None if outcome is None else outcome.elapsed_seconds,
                'decision_timestamp': None if outcome is None else outcome.at,
                'committed_event_hash': None if outcome is None else outcome.event_hash,
                'measurement_limit': 'local session wall-time; cannot prove attention or human identity',
            }

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

    def review_html(self, csrf: str) -> str:
        """All document and claim strings are escaped, never rendered as trusted HTML."""
        e = lambda x: html.escape(str(x), quote=True)
        stages = []
        for i, stage in enumerate(self.batch.stages, 1):
            c = stage.staged.candidate
            fields = asdict(c)
            stage_fields = ''.join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v in fields.items())
            contract = self.registry.matched_contract(c)
            if contract is None:
                raise ValueError('review contract no longer matches candidate')
            contract_fields = ''.join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>'
                                      for k,v in asdict(contract).items())
            stages.append(f'<section class="claim"><h3>Candidate {i}</h3>'
                          f'<p>Effective from: {e(c.valid_from)}; effective until: {e(c.valid_until)}</p>'
                          f'<h4>Extracted candidate</h4><dl>{stage_fields}</dl>'
                          f'<h4>Operator-authorized clause contract</h4><dl>{contract_fields}</dl>'
                          f'<p>Contract fingerprint: <code>{e(stage.contract_fingerprint)}</code></p></section>')
        status = self.outcome
        status_html = (f'<p class="notice">Decision: {e(status.disposition)}. {e(status.reason)}</p>'
                       if status else '')
        actions = '' if status else f'''<form method="post" action="/approve">
          <input type="hidden" name="csrf" value="{e(csrf)}">
          <input type="hidden" name="digest" value="{e(self.view_digest)}">
          <label><input type="checkbox" name="confirmation" value="YES_REVIEWED_EXACT_BATCH" required>
          I have reviewed the source, scope, dates, all candidates and the full batch.</label>
          <button type="submit">Approve and atomically admit entire batch</button>
          </form><form method="post" action="/reject">
          <input type="hidden" name="csrf" value="{e(csrf)}">
          <input type="hidden" name="digest" value="{e(self.view_digest)}">
          <button type="submit" class="reject">Reject entire batch</button></form>'''
        return self._shell('Review evidence',f'''<h1>Lycheetah Review Desk</h1>
          <p class="warning">Local reference workflow. Password possession is not proof of a person's identity.
          The source text may be inaccurate or malicious; verify it independently before approving.</p>
          <p>Ledger identity: <code>{e(self.__ledger_id)}</code></p>
          <p>Recorded knowledge timestamp: <code>{e(self.recorded_at)}</code></p>
          <p>Source: <code>{e(self.source.source_id)}</code> · Tenant: {e(self.source.tenant)} ·
          Source digest: <code>{e(self.source.digest)}</code></p>
          <p>Coverage: {e(self.batch.receipt.supported_unique)} / {e(self.batch.receipt.expected)} clauses;
          state: {e(self.batch.receipt.disposition)}</p>
          <h2>Complete registered source</h2><pre class="source">{e(self.source.body)}</pre>
          <h2>Every candidate & its evidence</h2>{''.join(stages)}
          <h2>Review commitment</h2>
          <p>Exact presentation digest: <code>{e(self.view_digest)}</code></p>{status_html}{actions}
          <form method="post" action="/logout"><input type="hidden" name="csrf" value="{e(csrf)}">
          <button type="submit">Log out</button></form>''')

    @staticmethod
    def _shell(title: str, body: str) -> str:
        return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
          <meta name="viewport" content="width=device-width,initial-scale=1">
          <title>'''+html.escape(title)+'''</title><style>
          body{font-family:system-ui,sans-serif;line-height:1.5;max-width:850px;
          padding:2rem;margin:auto;color:#172035;background:#f7f8fa}
          h1{font-size:1.7rem} h2{margin-top:2rem} code,pre{overflow-wrap:anywhere}
          pre{white-space:pre-wrap;border:1px solid #ccd3dc;padding:1rem;background:white}
          button{padding:.75rem 1rem;margin:.5rem 0;cursor:pointer;background:#162c57;
          color:white;border:0;border-radius:5px} button.reject{background:#7f2233}
          form{margin:1.2rem 0}label{display:block}.warning{border-left:4px solid #b78226;
          padding:.7rem;background:#fff3db}.notice{padding:.8rem;background:#e4f0e6}
          .claim{padding:1rem;background:white;border:1px solid #ccd3dc;margin:1rem 0}
          dl{display:grid;grid-template-columns:150px 1fr;gap:.25rem 1rem}
          dt{font-weight:600}dd{margin:0;overflow-wrap:anywhere}
          input[type=password]{padding:.6rem;width:min(95%,360px)}
          </style></head><body>'''+body+'''</body></html>'''


def make_review_server(desk: ReviewDesk, *, port: int = 0) -> ThreadingHTTPServer:
    """Binds exclusively to 127.0.0.1; never expose this on a public network."""
    if not isinstance(desk, ReviewDesk):
        raise TypeError('review desk required')
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError('invalid loopback port')

    class Handler(BaseHTTPRequestHandler):
        server_version = 'LycheetahLocalReview/0.1'
        sys_version = ''
        def log_message(self, fmt, *args):
            # Never log submitted password, cookies, query strings, or evidence.
            return

        def _send(self, status, body, *, cookie=None):
            data = body.encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Content-Security-Policy',
                "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('X-Frame-Options','DENY')
            self.send_header('Referrer-Policy','no-referrer')
            if cookie:
                self.send_header('Set-Cookie',cookie)
            self.end_headers()
            self.wfile.write(data)

        def _origin(self):
            addr = f'127.0.0.1:{self.server.server_port}'
            return (self.headers.get('Host') == addr and
                    self.headers.get('Origin') == 'http://' + addr)

        def _token(self):
            header = self.headers.get('Cookie','')
            jar = cookies.SimpleCookie()
            try:jar.load(header)
            except cookies.CookieError:return ''
            morsel = jar.get('review_session')
            return morsel.value if morsel else ''

        def _post(self):
            try: n = int(self.headers.get('Content-Length','-1'))
            except ValueError: return None
            if n < 0 or n > 8192 or self.headers.get('Content-Type') != 'application/x-www-form-urlencoded':
                return None
            raw=self.rfile.read(n)
            try:
                pairs=parse_qs(raw.decode('utf-8'),keep_blank_values=True,strict_parsing=True,
                               max_num_fields=10)
                if any(len(v)!=1 for v in pairs.values()):return None
                return {k:v[0] for k,v in pairs.items()}
            except (ValueError,UnicodeError):return None

        def do_GET(self):
            if self.headers.get('Host') != f'127.0.0.1:{self.server.server_port}':
                return self._send(400,'Invalid host')
            if urlsplit(self.path).query:
                return self._send(400,'No query strings accepted')
            if self.path not in ('/','/review'):
                return self._send(404,'Not found')
            token=self._token()
            session=desk.start_review(token) if self.path=='/review' else desk.session(token)
            if session:
                return self._send(200,desk.review_html(session['csrf']))
            login=desk._shell('Local login','''<h1>Lycheetah local review</h1>
                <p>Operator password required. Loopback-only reference prototype.</p>
                <form method="post" action="/login"><label>Password <input type="password" name="password" autocomplete="current-password" required></label>
                <button type="submit">Open evidence review</button></form>''')
            return self._send(200,login)

        def do_POST(self):
            if not self._origin():return self._send(403,'Origin or host refused')
            if self.path not in ('/login','/approve','/reject','/logout'):
                return self._send(404,'Not found')
            form=self._post()
            if form is None:return self._send(400,'Invalid form')
            if self.path=='/login':
                if set(form) != {'password'}:return self._send(400,'Invalid login fields')
                auth=desk.login(form['password'])
                if auth is None:return self._send(403,'Invalid login')
                token, csrf=auth
                cookie=f'review_session={token}; HttpOnly; SameSite=Strict; Path=/'
                session=desk.start_review(token)
                return self._send(200,desk.review_html(session['csrf']),cookie=cookie)
            token=self._token()
            session=desk.session(token)
            if session is None:return self._send(401,'Session required')
            if (not isinstance(form.get('csrf'), str) or
                    not secrets.compare_digest(form['csrf'],session['csrf'])):
                return self._send(403,'Invalid CSRF')
            if self.path=='/logout':
                if set(form) != {'csrf'}:return self._send(400,'Invalid logout fields')
                desk.logout(token)
                return self._send(200,'Logged out',cookie='review_session=; Max-Age=0; HttpOnly; SameSite=Strict; Path=/')
            allowed = {'csrf','digest'} | ({'confirmation'} if self.path=='/approve' else set())
            if set(form) != allowed:return self._send(400,'Invalid decision fields')
            decision = 'approve' if self.path == '/approve' else 'reject'
            outcome=desk.submit(token,csrf=form['csrf'],presented_digest=form['digest'],
                                decision=decision,confirmation=form.get('confirmation',''))
            code = (200 if outcome.disposition in ('APPROVED','REJECTED') else
                    409 if outcome.disposition in ('BLOCK','REVIEW') else 500)
            content=desk._shell('Review decision',
                f'<h1>{html.escape(outcome.disposition)}</h1><p>{html.escape(outcome.reason)}</p>'
                f'<p>Event hash: {html.escape(str(outcome.event_hash))}</p>'
                '<p><a href="/review">View review</a></p>')
            return self._send(code,content)

    return ThreadingHTTPServer(('127.0.0.1',port),Handler)
