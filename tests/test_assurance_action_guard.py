"""Tests for PersistentActionGuard, CheckpointAuthority, and ActionGateway."""
from __future__ import annotations

import json
from pathlib import Path
import secrets
import tempfile
import threading
import time
import unittest

from lycheetah.assurance import (
    AUDIT_GENESIS,
    ActionGateway,
    CheckpointConflict,
    CheckpointError,
    CheckpointHTTPClient,
    CheckpointStore,
    CommandExecutor,
    Decision,
    ExecutionResult,
    GateDecision,
    PersistentActionGuard,
    action_digest,
    canonical_action,
    make_server,
    verify_envelope,
)
from lycheetah.assurance.models import Disposition


class TestPersistentActionGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "ledger.sqlite3"
        self.guard = PersistentActionGuard(self.db_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_approval_and_effect_lifecycle(self):
        action = {"tool": "echo", "args": ["hello"]}
        now = int(time.time())
        app = self.guard.issue_approval(
            approval_id="app-1",
            actor="agent-1",
            approver_id="human-reviewer",
            action=action,
            scope="exec:echo",
            issued_at=now,
            expires_at=now + 60,
        )
        self.assertTrue(app.allowed)

        prep = self.guard.prepare_effect(
            effect_id="eff-1",
            approval_id="app-1",
            actor="agent-1",
            action=action,
            scope="exec:echo",
            now=now,
        )
        self.assertTrue(prep.allowed)
        self.assertEqual(prep.status, "PREPARED")

        # Duplicate preparation with same approval must be rejected
        dup = self.guard.prepare_effect(
            effect_id="eff-dup",
            approval_id="app-1",
            actor="agent-1",
            action=action,
            scope="exec:echo",
            now=now,
        )
        self.assertFalse(dup.allowed)
        self.assertEqual(dup.reason, "approval_already_consumed")

        # Claim dispatch
        anchor = self.guard.audit_anchor()
        claim = self.guard.claim_dispatch(
            effect_id="eff-1",
            now=now,
            current_action=action,
            expected_audit_anchor=anchor,
        )
        self.assertTrue(claim.allowed)
        self.assertEqual(claim.status, "DISPATCHING")

        # Record success
        rec = self.guard.record_result(
            effect_id="eff-1",
            now=now + 1,
            outcome="success",
            details={"output": "hello"},
        )
        self.assertTrue(rec.allowed)
        self.assertEqual(rec.status, "SUCCEEDED")

        eff = self.guard.get_effect("eff-1")
        self.assertIsNotNone(eff)
        self.assertEqual(eff["status"], "SUCCEEDED")
        self.assertEqual(eff["result"]["output"], "hello")

    def test_authority_epoch_revocation_blocks_prepared_work(self):
        action = {"tool": "restart", "target": "service-a"}
        now = int(time.time())
        self.guard.issue_approval(
            approval_id="app-rev",
            actor="agent-untrusted",
            approver_id="admin",
            action=action,
            scope="service:restart",
            issued_at=now,
            expires_at=now + 120,
        )
        self.guard.prepare_effect(
            effect_id="eff-rev",
            approval_id="app-rev",
            actor="agent-untrusted",
            action=action,
            scope="service:restart",
            now=now,
        )
        # Revoke authority for agent
        self.guard.revoke_all("agent-untrusted", now + 1)

        anchor = self.guard.audit_anchor()
        claim = self.guard.claim_dispatch(
            effect_id="eff-rev",
            now=now + 2,
            current_action=action,
            expected_audit_anchor=anchor,
        )
        self.assertFalse(claim.allowed)
        self.assertEqual(claim.reason, "revoked")
        self.assertEqual(self.guard.get_effect("eff-rev")["status"], "CANCELLED")

    def test_audit_chain_integrity_and_tamper_detection(self):
        action = {"tool": "test"}
        now = int(time.time())
        self.guard.issue_approval("a1", "actor1", "human", action, "scope", now, now + 10)
        status = self.guard.verify_audit_chain()
        self.assertTrue(status["valid"])
        self.assertEqual(status["event_count"], 1)

        consistency = self.guard.verify_state_consistency()
        self.assertTrue(consistency["valid"])

        # Directly tamper with SQLite audit table
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        conn.execute("UPDATE audit SET actor='forged_actor' WHERE seq=1")
        conn.commit()
        conn.close()

        tampered_audit = self.guard.verify_audit_chain()
        self.assertFalse(tampered_audit["valid"])
        self.assertEqual(tampered_audit["reason"], "event_hash_mismatch")


class TestCheckpointAuthority(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = self.root / "auth.sqlite3"
        self.key = self.root / "auth.pem"
        self.store = CheckpointStore(self.db, self.key)
        self.token = secrets.token_urlsafe(32)
        self.server = make_server(self.store, self.token, "127.0.0.1", 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        port = self.server.server_address[1]
        self.client = CheckpointHTTPClient(
            f"http://127.0.0.1:{port}", self.token, self.store.public_key_bytes()
        )

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tmp.cleanup()

    def test_checkpoint_store_and_client_roundtrip(self):
        genesis_anchor = {"event_count": 0, "last_seq": None, "root_hash": AUDIT_GENESIS}
        cp = self.client.publish("journal-test", genesis_anchor, [])
        self.assertEqual(cp["generation"], 1)
        self.assertEqual(cp["event_count"], 0)
        self.assertTrue(verify_envelope(cp, self.store.public_key_bytes(), "journal-test"))

        latest = self.client.get_latest("journal-test")
        self.assertIsNotNone(latest)
        self.assertEqual(latest["envelope_hash"], cp["envelope_hash"])

    def test_checkpoint_rollback_rejected(self):
        genesis_anchor = {"event_count": 0, "last_seq": None, "root_hash": AUDIT_GENESIS}
        self.client.publish("journal-fork", genesis_anchor, [])

        # Rollback attempt
        with self.assertRaises(CheckpointError):
            self.store.store(
                "journal-fork",
                {"event_count": 0, "last_seq": None, "root_hash": "bad" * 16},
                [],
            )


class TestActionGateway(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.gateway = ActionGateway.open_local(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_safe_command_execution_end_to_end(self):
        action = {"tool": "echo", "command": ["echo", "GATEWAY_ACTIVE"]}
        res = self.gateway.execute(
            action=action,
            actor="test-agent",
            scope="shell:echo",
            executor=CommandExecutor(["echo", "GATEWAY_ACTIVE"]),
        )
        self.assertEqual(res.status, "SUCCEEDED")
        self.assertTrue(res.provider_called)
        self.assertIn("GATEWAY_ACTIVE", res.result["stdout"])
        self.assertIsNotNone(res.receipt)
        self.assertEqual(res.receipt.decision, Disposition.ALLOW)
        self.assertIsNotNone(res.checkpoint_generation)

    def test_destructive_command_blocked_by_policy(self):
        action = {"tool": "bash", "command": "rm -rf /"}
        res = self.gateway.execute(
            action=action,
            actor="rogue-agent",
            scope="shell:all",
            executor=CommandExecutor(["echo", "should_not_run"]),
        )
        self.assertEqual(res.status, "BLOCKED")
        self.assertFalse(res.provider_called)
        self.assertEqual(res.reason, "policy_blocked")

    def test_uncertain_outcome_quarantined_as_unknown(self):
        action = {"tool": "flaky_api", "url": "https://service.local/mutate"}

        def timeout_executor():
            raise TimeoutError("connection dropped while waiting for response")

        gate = self.gateway.propose(action, "agent-1", "api:mutate")
        self.assertTrue(gate.allowed)
        assert gate.effect_id is not None

        res = self.gateway.dispatch(gate.effect_id, timeout_executor)
        self.assertEqual(res.status, "UNKNOWN")
        self.assertTrue(res.provider_called)

        # Effect status in SQLite must be UNKNOWN, preventing blind auto-retry
        eff = self.gateway.guard.get_effect(gate.effect_id)
        self.assertEqual(eff["status"], "UNKNOWN")


class TestCheckpointedWorkflow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.guard = PersistentActionGuard(self.root / "guard.sqlite3")
        self.store = CheckpointStore(
            self.root / "auth.sqlite3", self.root / "auth.pem"
        )
        self.token = secrets.token_urlsafe(32)
        self.server = make_server(self.store, self.token)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        port = self.server.server_address[1]
        self.client = CheckpointHTTPClient(
            f"http://127.0.0.1:{port}", self.token, self.store.public_key_bytes()
        )
        from lycheetah.assurance import CheckpointedWorkflow

        self.workflow = CheckpointedWorkflow(self.guard, self.client, "wf-journal")

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tmp.cleanup()

    def test_workflow_cadence_and_synchronize(self):
        boot = self.workflow.bootstrap_empty_journal()
        self.assertTrue(boot.checkpointed)
        self.assertEqual(boot.checkpoint_generation, 1)

        action = {"tool": "db.migrate", "step": 1}
        now = int(time.time())
        app = self.workflow.issue_approval("app-wf", "dba", "lead-dba", action, "db:all", now, now + 100)
        self.assertTrue(app.checkpointed)
        self.assertTrue(app.decision.allowed)

        prep = self.workflow.prepare_effect("eff-wf", "app-wf", "dba", action, "db:all", now)
        self.assertTrue(prep.checkpointed)
        self.assertTrue(prep.decision.allowed)

        claim = self.workflow.claim_dispatch("eff-wf", now, action)
        self.assertTrue(claim.checkpointed)
        self.assertTrue(claim.decision.allowed)

        res = self.workflow.record_result("eff-wf", now + 1, "success", {"migrated": True})
        self.assertTrue(res.checkpointed)
        self.assertTrue(res.decision.allowed)

        status = self.workflow.synchronize_status()
        self.assertTrue(status["synchronized"])
        self.assertTrue(status["audit_chain_valid"])
        self.assertTrue(status["state_consistency_valid"])
        self.assertEqual(status["event_count"], 4)

    def test_concurrent_claim_has_single_winner(self):
        self.workflow.bootstrap_empty_journal()
        action = {"tool": "payment", "amount": 100}
        now = int(time.time())
        self.workflow.issue_approval("app-pay", "billing-bot", "finance", action, "pay", now, now + 60)
        self.workflow.prepare_effect("eff-pay", "app-pay", "billing-bot", action, "pay", now)

        winners = []
        errors = []

        def worker(idx):
            claim = self.workflow.claim_dispatch("eff-pay", now, action)
            if claim.decision.allowed:
                winners.append(idx)
            else:
                errors.append(claim.decision.reason)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(winners), 1, f"Expected exactly one winner, got {winners}")
        self.assertEqual(len(errors), 9)


if __name__ == "__main__":
    unittest.main()
