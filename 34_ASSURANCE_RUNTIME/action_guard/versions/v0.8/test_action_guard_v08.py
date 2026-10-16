from __future__ import annotations
import base64
import json
import secrets
import sqlite3
import sys
import time
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from action_guard_v07 import AUDIT_GENESIS, PersistentActionGuard, FakeMergeProvider
from checkpoint_authority import (CheckpointConflict, CheckpointError, CheckpointStore,
                                  CheckpointHTTPClient, make_server, verify_envelope)
from checkpointed_workflow import CheckpointedWorkflow
from execution_workflow import SimulatedMergeExecutor
from github_rest_adapter import build_merge_request, dry_run_merge

class ClosingSQLiteConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc, tb):
        try:
            return super().__exit__(exc_type, exc, tb)
        finally:
            self.close()



class TogglePublishClient:
    """Test double that fails an external checkpoint write on demand."""
    def __init__(self, inner):
        self.inner, self.fail_publish = inner, False
        self.publish_calls, self.fail_on_publish_number = 0, None
    def get_latest(self, *args, **kwargs): return self.inner.get_latest(*args, **kwargs)
    def publish(self, *args, **kwargs):
        self.publish_calls += 1
        if self.fail_publish or self.publish_calls == self.fail_on_publish_number:
            raise CheckpointError("injected_checkpoint_outage")
        return self.inner.publish(*args, **kwargs)


class TimeoutAfterEffectProvider(FakeMergeProvider):
    def merge(self, action, idempotency_key):
        result = super().merge(action, idempotency_key)
        if not hasattr(self, "timeout_once"):
            self.timeout_once = True
            raise TimeoutError("response lost after simulated effect")
        return result


class V08Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.token = secrets.token_urlsafe(32)
        self.store = CheckpointStore(self.root / "checkpoint-authority" / "authority.sqlite3",
                                     self.root / "checkpoint-authority" / "ed25519-private.pem")
        self.server = make_server(self.store, self.token)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.client = CheckpointHTTPClient(self.base_url, self.token, self.store.public_key_bytes())
        self.guard_db = self.root / "guard-ledger" / "ledger.sqlite3"
        self.guard = PersistentActionGuard(self.guard_db)
        self.workflow = CheckpointedWorkflow(self.guard, self.client, "demo-journal")
        boot = self.workflow.bootstrap_empty_journal()
        self.assertTrue(boot.checkpointed, boot)
        self.provider = FakeMergeProvider()
        self.repo, self.pr = "Lycheetah/demo", 17
        self.provider.seed_pr(self.repo, self.pr, "a" * 40, "b" * 40)
        self.action = self.provider.read_action(self.repo, self.pr)
        self.actor, self.approver, self.scope = "coding-agent-1", "human-1", "merge:Lycheetah/demo#17"
        self.assertTrue(self.workflow.issue_approval("approval-1", self.actor, self.approver,
            self.action, self.scope, 100, 200).checkpointed)
        prep = self.workflow.prepare_effect("effect-1", "approval-1", self.actor,
            self.action, self.scope, 110)
        self.assertTrue(prep.checkpointed, prep)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.tmp.cleanup()

    def test_checkpoint_signatures_and_pinned_identity(self):
        env = self.client.get_latest("demo-journal")
        self.assertTrue(verify_envelope(env, self.store.public_key_bytes(), "demo-journal"))
        tampered = dict(env); tampered["root_hash"] = "0" * 64
        self.assertFalse(verify_envelope(tampered, self.store.public_key_bytes(), "demo-journal"))
        self.assertFalse(verify_envelope(env, self.store.public_key_bytes(), "other-journal"))

    def test_unauthorized_checkpoint_request_denied(self):
        req = Request(self.base_url + "/v1/checkpoints/demo-journal",
                      headers={"Authorization": "Bearer wrong-token"})
        with self.assertRaises(HTTPError) as caught:
            urlopen(req, timeout=2)
        self.assertEqual(caught.exception.code, 401)

    def test_service_rejects_checkpoint_rollback_and_same_seq_fork(self):
        latest = self.client.get_latest("demo-journal")
        with self.assertRaises(CheckpointError) as caught:
            self.client.publish("demo-journal", {"event_count": 0, "last_seq": None,
                                                  "root_hash": AUDIT_GENESIS})
        self.assertIn("checkpoint_rollback_rejected", str(caught.exception))
        fork = {"event_count": latest["event_count"], "last_seq": latest["last_seq"],
                "root_hash": "f" * 64}
        with self.assertRaises(CheckpointError) as caught2:
            self.client.publish("demo-journal", fork)
        self.assertIn("same_sequence_different_root_rejected", str(caught2.exception))

    def test_repeat_submission_is_idempotent(self):
        latest = self.client.get_latest("demo-journal")
        returned = self.client.publish("demo-journal", {"event_count": latest["event_count"],
            "last_seq": latest["last_seq"], "root_hash": latest["root_hash"]})
        self.assertEqual(returned["envelope_hash"], latest["envelope_hash"])
        self.assertEqual(returned["generation"], latest["generation"])

    def test_normal_simulated_merge_is_checkpointed_at_each_step(self):
        result = SimulatedMergeExecutor(self.workflow, self.provider, self.repo, self.pr).execute("effect-1", 120)
        self.assertEqual(result.status, "SUCCEEDED", result)
        self.assertTrue(result.provider_called)
        self.assertTrue(result.checkpointed)
        self.assertEqual(self.guard.get_effect("effect-1")["status"], "SUCCEEDED")
        self.assertTrue(self.workflow.synchronize_status()["synchronized"])
        self.assertEqual(result.request_preview["json_body"], {"sha": "a" * 40, "merge_method": "squash"})

    def test_stale_head_after_claim_provider_rejects_conditional_merge(self):
        # Inject a state change between guard claim and fake provider operation.
        original_merge = self.provider.merge
        def racing_merge(action, key):
            self.provider.seed_pr(self.repo, self.pr, "c" * 40, "b" * 40)
            return original_merge(action, key)
        self.provider.merge = racing_merge
        result = SimulatedMergeExecutor(self.workflow, self.provider, self.repo, self.pr).execute("effect-1", 120)
        self.assertEqual(result.status, "FAILED")
        self.assertEqual(result.provider_result["reason"], "stale_sha")
        self.assertEqual(self.provider.calls, 1)

    def test_revocation_prevents_claim_and_provider_call(self):
        revoked = self.workflow.revoke_all(self.actor, 115)
        self.assertTrue(revoked.checkpointed)
        result = SimulatedMergeExecutor(self.workflow, self.provider, self.repo, self.pr).execute("effect-1", 120)
        self.assertEqual(result.status, "DENIED")
        self.assertEqual(result.reason, "revoked")
        self.assertFalse(result.provider_called)

    def test_recomputed_forged_chain_cannot_be_resigned_over_prior_checkpoint(self):
        # Rewrite old event and recompute all local hashes, so the chain is internally valid.
        with sqlite3.connect(self.guard_db, factory=ClosingSQLiteConnection) as db:
            db.row_factory = sqlite3.Row
            db.execute("UPDATE audit SET details_json='{}' WHERE seq=1")
            from action_guard_v07 import PersistentActionGuard as G
            rows = db.execute("SELECT * FROM audit ORDER BY seq").fetchall()
            prev = AUDIT_GENESIS
            for row in rows:
                digest = G._audit_hash(row["seq"], row["at"], row["actor"], row["approval_id"],
                    row["effect_id"], row["event"], row["reason"], row["details_json"], prev)
                db.execute("UPDATE audit SET prev_hash=?,event_hash=? WHERE seq=?", (prev, digest, row["seq"]))
                prev = digest
        self.assertTrue(self.guard.verify_audit_chain()["valid"])
        result = SimulatedMergeExecutor(self.workflow, self.provider, self.repo, self.pr).execute("effect-1", 120)
        self.assertEqual(result.status, "BLOCKED")
        self.assertFalse(result.provider_called)
        self.assertIn("audit_history_invalid_against_external_checkpoint", result.reason)

    def test_tail_truncation_detected_against_latest_signed_checkpoint(self):
        with sqlite3.connect(self.guard_db, factory=ClosingSQLiteConnection) as db:
            db.execute("DELETE FROM audit WHERE seq=(SELECT MAX(seq) FROM audit)")
        result = SimulatedMergeExecutor(self.workflow, self.provider, self.repo, self.pr).execute("effect-1", 120)
        self.assertEqual(result.status, "BLOCKED")
        self.assertFalse(result.provider_called)

    def test_missing_initial_checkpoint_cannot_be_bootstrapped_over_old_history(self):
        # New workflow against a non-empty local ledger but an empty separate authority.
        other_guard = PersistentActionGuard(self.root / "other-ledger.sqlite3")
        other_guard.issue_approval("old", "a", "h", {"tool": "x"}, "x", 1, 10)
        workflow = CheckpointedWorkflow(other_guard, self.client, "never-bootstrapped")
        with self.assertRaisesRegex(RuntimeError, "refusing_to_anchor_preexisting_uncheckpointed_history"):
            workflow.bootstrap_empty_journal()

    def test_checkpoint_outage_after_claim_stops_before_provider(self):
        toggle = TogglePublishClient(self.client)
        workflow = CheckpointedWorkflow(self.guard, toggle, "demo-journal")
        toggle.fail_publish = True
        # The local guard may commit DISPATCHING, but the wrapper refuses to release the claim.
        result = SimulatedMergeExecutor(workflow, self.provider, self.repo, self.pr).execute("effect-1", 120)
        self.assertEqual(result.status, "BLOCKED")
        self.assertFalse(result.provider_called)
        self.assertFalse(result.checkpointed)
        self.assertFalse(workflow.synchronize_status()["synchronized"])

    def test_uncertain_provider_outcome_is_not_automatically_retried(self):
        # Replace with a provider that commits the simulated effect then throws a timeout.
        self.provider = TimeoutAfterEffectProvider()
        self.provider.seed_pr(self.repo, self.pr, "a" * 40, "b" * 40)
        # Recreate approval and intent for the replacement provider.
        action = self.provider.read_action(self.repo, self.pr)
        # This workflow has a prepared effect bound to the same exact action, so the action is unchanged.
        result = SimulatedMergeExecutor(self.workflow, self.provider, self.repo, self.pr).execute("effect-1", 120)
        self.assertEqual(result.status, "UNKNOWN")
        self.assertEqual(self.guard.get_effect("effect-1")["status"], "UNKNOWN")
        retry = SimulatedMergeExecutor(self.workflow, self.provider, self.repo, self.pr).execute("effect-1", 121)
        self.assertIn(retry.status, ("DENIED", "BLOCKED"))
        self.assertEqual(self.provider.calls, 1)

    def test_github_request_preview_uses_expected_head_sha_and_never_sends(self):
        preview = dry_run_merge(self.action)
        self.assertEqual(preview["status"], "DRY_RUN_ONLY")
        self.assertFalse(preview["side_effect_performed"])
        request = build_merge_request(self.action)
        self.assertEqual(request.method, "PUT")
        self.assertIn("/repos/Lycheetah/demo/pulls/17/merge", request.url)
        self.assertEqual(request.json_body["sha"], self.action["head_sha"])
        self.assertNotIn("base_sha", request.json_body)


    def test_checkpoint_authority_requires_proof_of_journal_extension(self):
        latest = self.client.get_latest("demo-journal")
        forged_next_seq = latest["last_seq"] + 1
        fake_event = {"seq": forged_next_seq, "at": 125, "actor": "attacker",
            "approval_id": None, "effect_id": "fake", "event": "FAKE_EVENT", "reason": "ok",
            "details_json": "{}", "prev_hash": latest["root_hash"], "event_hash": "f" * 64}
        proposed = {"event_count": latest["event_count"] + 1,
                    "last_seq": forged_next_seq, "root_hash": "f" * 64}
        with self.assertRaises(CheckpointError) as caught:
            self.client.publish("demo-journal", proposed, [fake_event])
        self.assertIn("audit_event_hash_mismatch", str(caught.exception))
        self.assertEqual(self.client.get_latest("demo-journal")["envelope_hash"], latest["envelope_hash"])

    def test_checkpoint_service_restart_preserves_history_and_signing_identity(self):
        before = self.client.get_latest("demo-journal")
        restarted_store = CheckpointStore(self.root / "checkpoint-authority" / "authority.sqlite3",
                                          self.root / "checkpoint-authority" / "ed25519-private.pem")
        after = restarted_store.latest("demo-journal")
        self.assertEqual(after["envelope_hash"], before["envelope_hash"])
        self.assertEqual(restarted_store.public_key_bytes(), self.store.public_key_bytes())
        self.assertTrue(verify_envelope(after, restarted_store.public_key_bytes(), "demo-journal"))

    def test_journal_with_missing_initial_sequence_is_invalid_even_if_rehashed(self):
        with sqlite3.connect(self.guard_db, factory=ClosingSQLiteConnection) as db:
            db.row_factory = sqlite3.Row
            db.execute("DELETE FROM audit WHERE seq=1")
            rows = db.execute("SELECT * FROM audit ORDER BY seq").fetchall()
            from action_guard_v07 import PersistentActionGuard as G
            prev = AUDIT_GENESIS
            for row in rows:
                digest = G._audit_hash(row["seq"], row["at"], row["actor"], row["approval_id"],
                    row["effect_id"], row["event"], row["reason"], row["details_json"], prev)
                db.execute("UPDATE audit SET prev_hash=?,event_hash=? WHERE seq=?", (prev, digest, row["seq"]))
                prev = digest
        verification = self.guard.verify_audit_chain()
        self.assertFalse(verification["valid"])
        self.assertEqual(verification["reason"], "sequence_gap_from_genesis")

    def test_provider_success_without_external_result_checkpoint_locks_future_actions(self):
        toggle = TogglePublishClient(self.client)
        workflow = CheckpointedWorkflow(self.guard, toggle, "demo-journal")
        # First publish is the post-claim checkpoint; fail the second, after the
        # simulated provider has acted and the local result has been recorded.
        toggle.fail_on_publish_number = 2
        result = SimulatedMergeExecutor(workflow, self.provider, self.repo, self.pr).execute("effect-1", 120)
        self.assertEqual(result.status, "EFFECT_RESULT_UNCHECKPOINTED")
        self.assertTrue(result.provider_called)
        self.assertFalse(result.checkpointed)
        self.assertFalse(workflow.synchronize_status()["synchronized"])
        retry = SimulatedMergeExecutor(workflow, self.provider, self.repo, self.pr).execute("effect-1", 121)
        self.assertEqual(retry.status, "BLOCKED")
        self.assertEqual(self.provider.calls, 1)


    def test_materialized_effect_status_tampering_blocks_dispatch(self):
        with sqlite3.connect(self.guard_db, factory=ClosingSQLiteConnection) as db:
            db.execute("UPDATE effects SET status='FAILED', reason='success' WHERE effect_id='effect-1'")
        integrity = self.guard.verify_state_consistency()
        self.assertFalse(integrity["valid"])
        result = SimulatedMergeExecutor(self.workflow, self.provider, self.repo, self.pr).execute("effect-1", 120)
        self.assertEqual(result.status, "BLOCKED")
        self.assertFalse(result.provider_called)
        self.assertIn("operational_ledger_inconsistent_against_audit", result.reason)

    def test_approval_row_tampering_blocks_preparation(self):
        with sqlite3.connect(self.guard_db, factory=ClosingSQLiteConnection) as db:
            db.execute("UPDATE approvals SET scope='merge:attacker/repo#1' WHERE approval_id='approval-1'")
        receipt = self.workflow.prepare_effect("effect-x", "approval-1", self.actor,
                                               self.action, self.scope, 115)
        self.assertFalse(receipt.checkpointed)
        self.assertEqual(receipt.decision.reason, "workflow_blocked")
        self.assertIn("operational_ledger_inconsistent_against_audit", receipt.error)

    def test_authority_epoch_table_tampering_blocks_dispatch(self):
        receipt = self.workflow.revoke_all(self.actor, 115)
        self.assertTrue(receipt.checkpointed)
        with sqlite3.connect(self.guard_db, factory=ClosingSQLiteConnection) as db:
            db.execute("UPDATE authority SET epoch=0 WHERE actor=?", (self.actor,))
        result = SimulatedMergeExecutor(self.workflow, self.provider, self.repo, self.pr).execute("effect-1", 120)
        self.assertEqual(result.status, "BLOCKED")
        self.assertFalse(result.provider_called)
        self.assertIn("operational_ledger_inconsistent_against_audit", result.reason)

    def test_dispatch_rejects_concurrent_uncheckpointed_journal_append(self):
        latest = self.client.get_latest("demo-journal")
        # Simulate another code path appending an otherwise valid ledger event after
        # the pre-check and before the dispatch transaction.
        self.assertTrue(self.guard.issue_approval("racing-approval", self.actor, self.approver,
            {"tool": "github.read", "repo": self.repo}, "read:demo", 115, 200).allowed)
        decision = self.guard.claim_dispatch("effect-1", 120, self.provider.read_action(self.repo, self.pr),
            {"event_count": latest["event_count"], "last_seq": latest["last_seq"],
             "root_hash": latest["root_hash"]}, require_exact_audit_anchor=True)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "audit_checkpoint_stale")
        self.assertEqual(self.provider.calls, 0)


    def test_checkpoint_service_rejects_noncanonical_event_details_even_with_matching_hash(self):
        latest = self.client.get_latest("demo-journal")
        from action_guard_v07 import PersistentActionGuard as G
        seq = latest["last_seq"] + 1
        details = "{ }"  # valid JSON, but not canonical JSON as required by the journal format
        digest = G._audit_hash(seq, 125, "agent-demo", None, "effect-fake", "FAKE_EVENT",
                               "ok", details, latest["root_hash"])
        event = {"seq": seq, "at": 125, "actor": "agent-demo", "approval_id": None,
                 "effect_id": "effect-fake", "event": "FAKE_EVENT", "reason": "ok",
                 "details_json": details, "prev_hash": latest["root_hash"], "event_hash": digest}
        anchor = {"event_count": latest["event_count"] + 1, "last_seq": seq, "root_hash": digest}
        with self.assertRaises(CheckpointError) as caught:
            self.client.publish("demo-journal", anchor, [event])
        self.assertIn("noncanonical_audit_details_json", str(caught.exception))

    def test_checkpoint_store_metadata_tampering_blocks_next_signature(self):
        latest = self.client.get_latest("demo-journal")
        with sqlite3.connect(self.root / "checkpoint-authority" / "authority.sqlite3",
                             factory=ClosingSQLiteConnection) as db:
            db.execute("UPDATE checkpoint_history SET root_hash=? WHERE journal_id=? AND generation=?",
                       ("f" * 64, "demo-journal", latest["generation"]))
        proposed = {"event_count": latest["event_count"] + 1,
                    "last_seq": latest["last_seq"] + 1, "root_hash": "e" * 64}
        with self.assertRaises(CheckpointError) as caught:
            self.client.publish("demo-journal", proposed, [])
        self.assertIn("checkpoint_store_integrity_failure", str(caught.exception))


    def test_one_workflow_serializes_revocation_during_provider_call(self):
        entered_provider, release_provider = threading.Event(), threading.Event()
        original_merge = self.provider.merge
        def blocking_merge(action, key):
            entered_provider.set()
            if not release_provider.wait(timeout=5):
                raise TimeoutError("test provider gate timed out")
            return original_merge(action, key)
        self.provider.merge = blocking_merge
        executions, revocations = [], []
        exec_thread = threading.Thread(target=lambda: executions.append(
            SimulatedMergeExecutor(self.workflow, self.provider, self.repo, self.pr).execute("effect-1", 120)))
        exec_thread.start()
        self.assertTrue(entered_provider.wait(timeout=3), "provider call was not reached")
        revoke_thread = threading.Thread(target=lambda: revocations.append(self.workflow.revoke_all(self.actor, 121)))
        revoke_thread.start()
        time.sleep(0.1)
        self.assertTrue(revoke_thread.is_alive(), "revocation was not serialized behind the in-flight effect session")
        release_provider.set()
        exec_thread.join(timeout=5); revoke_thread.join(timeout=5)
        self.assertFalse(exec_thread.is_alive())
        self.assertFalse(revoke_thread.is_alive())
        self.assertEqual(executions[0].status, "SUCCEEDED")
        self.assertTrue(revocations[0].checkpointed)
        self.assertEqual(self.provider.calls, 1)
        self.assertTrue(self.workflow.synchronize_status()["synchronized"])


    def test_unicode_provider_evidence_survives_materialized_state_reconciliation(self):
        claim = self.workflow.claim_dispatch("effect-1", 120, self.provider.read_action(self.repo, self.pr))
        self.assertTrue(claim.checkpointed)
        self.assertTrue(claim.decision.allowed)
        recorded = self.workflow.record_result("effect-1", 121, "success", {"note": "café 🧪", "status": "ok"})
        self.assertTrue(recorded.checkpointed)
        consistency = self.guard.verify_state_consistency()
        self.assertTrue(consistency["valid"], consistency)
        self.assertTrue(self.workflow.synchronize_status()["synchronized"])

    def test_invalid_repository_cannot_escape_request_path(self):
        malicious = dict(self.action, repo="Lycheetah/../other")
        with self.assertRaises(ValueError):
            build_merge_request(malicious)

    def test_status_refuses_uncheckpointed_tail_after_checkpoint_failure(self):
        toggle = TogglePublishClient(self.client)
        workflow = CheckpointedWorkflow(self.guard, toggle, "demo-journal")
        toggle.fail_publish = True
        receipt = workflow.issue_approval("approval-2", self.actor, self.approver,
            {"tool": "github.read", "repo": self.repo}, "read:demo", 115, 200)
        self.assertFalse(receipt.checkpointed)
        self.assertFalse(workflow.synchronize_status()["synchronized"])
        toggle.fail_publish = False
        with self.assertRaisesRegex(RuntimeError, "bootstrap_requires_synchronized_journal"):
            # It is deliberately not silently blessed by a later call.
            workflow.bootstrap_empty_journal()


if __name__ == "__main__": unittest.main(verbosity=2)
