from __future__ import annotations
import hashlib, json, os, sqlite3, subprocess, sys, tempfile, time, unittest, uuid
from contextlib import closing
from pathlib import Path
from tool_catalog import DEFAULT_CATALOG

HERE = Path(__file__).resolve().parent
HOST = HERE / "host_process.py"
PROVIDER = HERE / "provider_process.py"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


class CrashRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lyc-crash-lab-")
        self.root = Path(self.tmp.name)
        self.authority_db = self.root / "authority.sqlite"
        self.provider_db = self.root / "provider.sqlite"
        self.key_file = self.root / "issuer.key"
        self.key_file.write_bytes(b"local-test-key-only-not-for-production-0123456789")
        try: self.key_file.chmod(0o600)
        except OSError: pass
        self.policy_file = self.root / "policy.json"
        self._write_policy({"policy_id":"test-refund","version":1,"refund_requires_host_approval":True})
        self.action_file = self.root / "action.json"
        self.token_file = self.root / "token.txt"
        self.operation_id = "op-" + uuid.uuid4().hex
        self.action = DEFAULT_CATALOG.stamp(
            {"tool_name":"refund_order","arguments":{"order_id":"ORD-42","amount_minor":2500,"currency":"NZD"}},
            operation_id=self.operation_id, agent_id="fixture-agent", workspace_id="disposable-test-workspace",
        )
        self._write_action(self.action)
        r=self.host("issue")
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
        self.approved_policy_sha256 = self.output(r)["policy_sha256"]

    def tearDown(self): self.tmp.cleanup()

    def _write_policy(self, value):
        value = dict(value)
        value["tool_catalog_sha256"] = DEFAULT_CATALOG.digest
        self.policy_file.write_text(json.dumps(value,sort_keys=True),encoding="utf-8")
    def _write_action(self, value): self.action_file.write_text(json.dumps(value,sort_keys=True),encoding="utf-8")

    def host(self, command, *extra):
        args=[sys.executable,"-S",str(HOST),command]
        args += ["--authority-db",str(self.authority_db)]
        if command == "issue":
            args += ["--policy-file",str(self.policy_file),"--key-file",str(self.key_file),"--action-file",str(self.action_file),"--token-file",str(self.token_file)]
        elif command == "execute":
            args += ["--provider-db",str(self.provider_db),"--key-file",str(self.key_file),"--action-file",str(self.action_file),"--token-file",str(self.token_file)]
        elif command == "recover":
            args += ["--provider-db",str(self.provider_db),"--operation-id",self.operation_id]
        elif command == "revoke":
            args += ["--key-file",str(self.key_file),"--token-file",str(self.token_file)]
        elif command == "status":
            args += ["--operation-id",self.operation_id]
        elif command == "set-policy":
            args += ["--policy-file",str(self.policy_file)]
        else:
            raise ValueError(command)
        args += list(extra)
        return subprocess.run(args,capture_output=True,text=True,timeout=20)

    def output(self, result):
        self.assertTrue(result.stdout.strip(), f"empty stdout rc={result.returncode}; stderr={result.stderr}")
        return json.loads(result.stdout.strip().splitlines()[-1])

    def approval_nonce(self):
        with closing(sqlite3.connect(self.authority_db)) as db:
            return db.execute("SELECT nonce FROM approvals WHERE operation_id=?",(self.operation_id,)).fetchone()[0]

    def effects(self):
        if not self.provider_db.exists(): return []
        with closing(sqlite3.connect(self.provider_db)) as db:
            rows=db.execute("SELECT operation_id,action_sha256,result_json FROM effects ORDER BY operation_id").fetchall()
        return rows

    def test_happy_path_commits_one_durable_effect(self):
        r=self.host("execute"); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(self.output(r)["status"],"completed")
        self.assertEqual(len(self.effects()),1)
        self.assertEqual(self.output(self.host("status"))["state"],"COMPLETED")

    def test_crash_after_claim_restarts_and_recovers_once(self):
        r=self.host("execute","--crash-point","after_claim")
        self.assertEqual(r.returncode,81)
        self.assertEqual(self.output(self.host("status"))["state"],"CLAIMED")
        recovered=self.host("recover"); self.assertEqual(recovered.returncode,0,recovered.stdout+recovered.stderr)
        self.assertEqual(self.output(recovered)["status"],"reconciled-completed")
        self.assertEqual(len(self.effects()),1)

    def test_provider_crash_before_commit_retries_same_operation_id(self):
        r=self.host("execute","--provider-fault","before_commit")
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(self.output(r)["status"],"unknown-needs-reconciliation")
        self.assertEqual(len(self.effects()),0)
        recovered=self.host("recover"); self.assertEqual(recovered.returncode,0,recovered.stdout+recovered.stderr)
        self.assertEqual(self.output(recovered)["status"],"reconciled-completed")
        self.assertEqual(len(self.effects()),1)

    def test_provider_crash_after_commit_is_found_not_duplicated(self):
        r=self.host("execute","--provider-fault","after_commit")
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(self.output(r)["status"],"unknown-needs-reconciliation")
        self.assertEqual(len(self.effects()),1)
        recovered=self.host("recover")
        self.assertEqual(self.output(recovered)["status"],"reconciled-completed")
        self.assertEqual(len(self.effects()),1)

    def test_host_crash_after_provider_response_is_reconciled_after_restart(self):
        r=self.host("execute","--crash-point","after_provider_response")
        self.assertEqual(r.returncode,82)
        self.assertEqual(self.output(self.host("status"))["state"],"CLAIMED")
        self.assertEqual(len(self.effects()),1)
        self.assertEqual(self.output(self.host("recover"))["status"],"reconciled-completed")
        self.assertEqual(len(self.effects()),1)

    def test_recovery_can_itself_crash_after_provider_response(self):
        self.assertEqual(self.host("execute","--crash-point","after_claim").returncode,81)
        r=self.host("recover","--crash-point","after_provider_response")
        self.assertEqual(r.returncode,83)
        self.assertEqual(len(self.effects()),1)
        self.assertEqual(self.output(self.host("recover"))["status"],"reconciled-completed")
        self.assertEqual(len(self.effects()),1)

    def test_revocation_before_claim_denies_no_effect(self):
        r=self.host("revoke"); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        executed=self.host("execute"); self.assertEqual(executed.returncode,2)
        self.assertEqual(self.output(executed)["reason"],"revoked-before-claim")
        self.assertEqual(len(self.effects()),0)

    def test_revocation_after_claim_but_before_effect_stops_recovery(self):
        self.assertEqual(self.host("execute","--crash-point","after_claim").returncode,81)
        self.assertEqual(self.host("revoke").returncode,0)
        rec=self.host("recover"); self.assertEqual(rec.returncode,0,rec.stdout+rec.stderr)
        payload=self.output(rec)
        self.assertEqual(payload["status"],"needs-review")
        self.assertEqual(payload["reason"],"revoked-after-claim-before-effect")
        self.assertEqual(len(self.effects()),0)

    def test_revocation_after_provider_effect_reconciles_fact(self):
        self.assertEqual(self.host("execute","--crash-point","after_provider_response").returncode,82)
        self.assertEqual(self.host("revoke").returncode,0)
        self.assertEqual(self.output(self.host("recover"))["status"],"reconciled-completed")
        self.assertEqual(len(self.effects()),1)

    def test_policy_change_before_claim_denies(self):
        self._write_policy({"policy_id":"test-refund","version":2,"refund_requires_host_approval":True})
        self.assertEqual(self.host("set-policy").returncode,0)
        r=self.host("execute"); self.assertEqual(r.returncode,2)
        self.assertEqual(self.output(r)["reason"],"policy-changed")
        self.assertEqual(len(self.effects()),0)

    def test_policy_change_after_claim_without_effect_stops_recovery(self):
        self.assertEqual(self.host("execute","--crash-point","after_claim").returncode,81)
        self._write_policy({"policy_id":"test-refund","version":2,"refund_requires_host_approval":True})
        self.assertEqual(self.host("set-policy").returncode,0)
        r=self.host("recover"); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(self.output(r)["reason"],"policy-changed-before-retry")
        self.assertEqual(len(self.effects()),0)

    def test_action_change_after_approval_is_denied(self):
        changed=dict(self.action); changed["arguments"]={"order_id":"OTHER","amount_minor":2500,"currency":"NZD"}
        self._write_action(changed)
        r=self.host("execute"); self.assertEqual(r.returncode,2)
        self.assertEqual(self.output(r)["reason"],"action-mismatch")
        self.assertEqual(len(self.effects()),0)

    def test_replay_after_completion_is_denied(self):
        self.assertEqual(self.host("execute").returncode,0)
        r=self.host("execute"); self.assertEqual(r.returncode,2)
        self.assertEqual(self.output(r)["reason"],"approval-already-consumed")
        self.assertEqual(len(self.effects()),1)

    def test_eight_processes_reusing_token_commit_one_effect(self):
        args=[sys.executable,"-S",str(HOST),"execute","--authority-db",str(self.authority_db),"--provider-db",str(self.provider_db),"--key-file",str(self.key_file),"--action-file",str(self.action_file),"--token-file",str(self.token_file)]
        children=[subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for _ in range(8)]
        completed=[child.communicate(timeout=25)+(child.returncode,) for child in children]
        codes=[x[2] for x in completed]
        self.assertEqual(codes.count(0),1,completed)
        self.assertEqual(codes.count(2),7,completed)
        self.assertEqual(len(self.effects()),1)

    def test_provider_refuses_same_id_with_different_payload(self):
        self.assertEqual(self.host("execute").returncode,0)
        # Corrupt the fake provider's stored digest to simulate a key collision or
        # inconsistent provider record, then send the original approved request.
        with closing(sqlite3.connect(self.provider_db)) as db:
            db.execute("UPDATE effects SET action_sha256=? WHERE operation_id=?",("f"*64,self.operation_id))
            db.commit()
        digest=hashlib.sha256(canonical(self.action)).hexdigest()
        req={"operation_id":self.operation_id,"approval_nonce":self.approval_nonce(),"action_sha256":digest,"action":self.action}
        r=subprocess.run([sys.executable,"-S",str(PROVIDER),"commit","--db",str(self.provider_db),"--authority-db",str(self.authority_db),"--expected-policy-sha256",self.approved_policy_sha256],input=json.dumps(req),capture_output=True,text=True,timeout=10)
        self.assertEqual(r.returncode,4,r.stdout+r.stderr)
        self.assertIn("idempotency-key-payload-conflict",r.stdout)
        self.assertEqual(len(self.effects()),1)

    def test_revocation_racing_with_provider_dispatch_is_linearized_by_fence(self):
        marker=self.root/"provider-policy-fence-held-for-revoke"
        execute_args=[sys.executable,"-S",str(HOST),"execute","--authority-db",str(self.authority_db),"--provider-db",str(self.provider_db),"--key-file",str(self.key_file),"--action-file",str(self.action_file),"--token-file",str(self.token_file),"--provider-fault","pause_after_policy_lock","--provider-ready-marker",str(marker)]
        worker=subprocess.Popen(execute_args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        deadline=time.monotonic()+8
        while not marker.exists() and time.monotonic()<deadline:
            if worker.poll() is not None: break
            time.sleep(0.02)
        self.assertTrue(marker.exists(),"provider never acquired the dispatch fence")
        # Revocation starts after provider has locked/checked the authority row;
        # it must serialize after this effect, not slip into the middle.
        revoked=self.host("revoke")
        self.assertEqual(revoked.returncode,0,revoked.stdout+revoked.stderr)
        stdout,stderr=worker.communicate(timeout=15)
        self.assertEqual(worker.returncode,0,stdout+stderr)
        self.assertEqual(json.loads(stdout)["status"],"completed")
        self.assertEqual(len(self.effects()),1)
        # A new dispatch using the same token is now rejected after revocation.
        again=self.host("execute")
        self.assertEqual(again.returncode,2)
        self.assertEqual(self.output(again)["reason"],"approval-already-consumed")

    def test_provider_policy_fence_rejects_stale_approval_after_policy_update(self):
        self.assertEqual(self.host("execute","--crash-point","after_claim").returncode,81)
        self._write_policy({"policy_id":"test-refund","version":2,"refund_requires_host_approval":True})
        self.assertEqual(self.host("set-policy").returncode,0)
        req={"operation_id":self.operation_id,"approval_nonce":self.approval_nonce(),"action_sha256":hashlib.sha256(canonical(self.action)).hexdigest(),"action":self.action}
        r=subprocess.run([sys.executable,"-S",str(PROVIDER),"commit","--db",str(self.provider_db),"--authority-db",str(self.authority_db),"--expected-policy-sha256",self.approved_policy_sha256],input=json.dumps(req),capture_output=True,text=True,timeout=10)
        self.assertEqual(r.returncode,6,r.stdout+r.stderr)
        self.assertIn("policy-fence-rejected",r.stdout)
        self.assertEqual(len(self.effects()),0)

    def test_policy_update_waits_for_provider_fenced_commit(self):
        marker=self.root/"provider-policy-fence-held"
        execute_args=[sys.executable,"-S",str(HOST),"execute","--authority-db",str(self.authority_db),"--provider-db",str(self.provider_db),"--key-file",str(self.key_file),"--action-file",str(self.action_file),"--token-file",str(self.token_file),"--provider-fault","pause_after_policy_lock","--provider-ready-marker",str(marker)]
        worker=subprocess.Popen(execute_args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        deadline=time.monotonic()+8
        while not marker.exists() and time.monotonic()<deadline:
            if worker.poll() is not None:
                break
            time.sleep(0.02)
        self.assertTrue(marker.exists(),"provider never acquired the policy fence")
        self._write_policy({"policy_id":"test-refund","version":2,"refund_requires_host_approval":True})
        update=self.host("set-policy")
        self.assertEqual(update.returncode,0,update.stdout+update.stderr)
        stdout,stderr=worker.communicate(timeout=15)
        self.assertEqual(worker.returncode,0,stdout+stderr)
        self.assertEqual(json.loads(stdout)["status"],"completed")
        self.assertEqual(len(self.effects()),1)
        with closing(sqlite3.connect(self.authority_db)) as db:
            revision=db.execute("SELECT revision FROM policy_state WHERE singleton=1").fetchone()[0]
        self.assertEqual(revision,2)

    def test_provider_authoritative_record_matches_approved_action_digest(self):
        self.assertEqual(self.host("execute").returncode,0)
        row=self.effects()[0]
        self.assertEqual(row[0],self.operation_id)
        self.assertEqual(row[1],hashlib.sha256(canonical(self.action)).hexdigest())

    def test_bad_key_denies_before_effect(self):
        original=self.key_file.read_bytes(); self.key_file.write_bytes(b"different-key-012345678901234567890123456789")
        r=self.host("execute"); self.assertEqual(r.returncode,2)
        self.assertEqual(self.output(r)["reason"],"bad-token-signature")
        self.assertEqual(len(self.effects()),0)
        self.key_file.write_bytes(original)

    def test_valid_token_is_durable_across_new_cli_process(self):
        # Every host operation has already crossed a new Python process boundary;
        # this explicitly verifies approval state survived process reconstruction.
        status=self.output(self.host("status"))
        self.assertEqual(status["state"],"APPROVED")
        r=self.host("execute"); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(len(self.effects()),1)

    def test_recover_cannot_dispatch_approval_that_was_never_claimed(self):
        r=self.host("recover")
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        result=self.output(r)
        self.assertEqual(result["status"],"needs-review")
        self.assertEqual(result["reason"],"operation-state-not-retryable:APPROVED")
        self.assertEqual(len(self.effects()),0)

    def test_completed_operation_missing_provider_record_is_not_replayed(self):
        self.assertEqual(self.host("execute").returncode,0)
        with closing(sqlite3.connect(self.provider_db)) as db:
            db.execute("DELETE FROM effects WHERE operation_id=?",(self.operation_id,))
            db.commit()
        r=self.host("recover")
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(self.output(r)["reason"],"completed-operation-missing-provider-record")
        self.assertEqual(len(self.effects()),0)

    def test_provider_effect_without_durable_claim_is_reported_as_conflict(self):
        self.provider_db.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.provider_db)) as db:
            db.execute("CREATE TABLE effects (operation_id TEXT PRIMARY KEY, action_sha256 TEXT NOT NULL, result_json TEXT NOT NULL, committed_at REAL NOT NULL)")
            fake_result={"status":"committed","operation_id":self.operation_id,"action_sha256":hashlib.sha256(canonical(self.action)).hexdigest()}
            db.execute("INSERT INTO effects VALUES(?,?,?,?)",(self.operation_id,fake_result["action_sha256"],json.dumps(fake_result),time.time()))
            db.commit()
        rec=self.host("recover")
        self.assertEqual(rec.returncode,3,rec.stdout+rec.stderr)
        self.assertEqual(self.output(rec)["reason"],"provider-effect-without-durable-claim")
        self.assertEqual(len(self.effects()),1)

    def test_uncommitted_policy_file_edit_does_not_change_active_policy(self):
        self._write_policy({"policy_id":"test-refund","version":2,"refund_requires_host_approval":True})
        # The durable authority DB is the active policy source. Editing a file is
        # not a policy update; a deliberate set-policy operation is required.
        r=self.host("execute")
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(self.output(r)["status"],"completed")
        self.assertEqual(len(self.effects()),1)

    def test_policy_update_is_required_before_issuing_new_approval(self):
        self._write_policy({"policy_id":"test-refund","version":2,"refund_requires_host_approval":True})
        r=self.host("issue")
        self.assertEqual(r.returncode,1,r.stdout+r.stderr)
        self.assertIn("policy-file-differs-from-authoritative-policy",self.output(r)["detail"])

    def test_host_validates_stored_policy_catalog_binding_before_claim(self):
        # Forge the persisted policy JSON while retaining the old stored digest.
        # The host must stop before claiming/dispatching a consequential action.
        with closing(sqlite3.connect(self.authority_db)) as db:
            db.execute("UPDATE policy_state SET policy_json=? WHERE singleton=1", (json.dumps({"policy_id":"test-refund","version":1,"refund_requires_host_approval":True,"tool_catalog_sha256":"0"*64}, sort_keys=True),))
            db.commit()
        r=self.host("execute")
        self.assertEqual(r.returncode,2,r.stdout+r.stderr)
        self.assertEqual(self.output(r)["reason"], "policy-catalog-binding-invalid")
        self.assertEqual(len(self.effects()),0)

    def test_provider_validates_policy_catalog_binding_at_effect_boundary(self):
        # Crash after durable claim, then tamper only with the stored policy body.
        # Invoke the provider boundary directly to prove it checks the binding too.
        r=self.host("execute", "--crash-point", "after_claim")
        self.assertEqual(r.returncode,81)
        nonce=self.approval_nonce()
        with closing(sqlite3.connect(self.authority_db)) as db:
            db.execute("UPDATE policy_state SET policy_json=? WHERE singleton=1", (json.dumps({"policy_id":"test-refund","version":1,"refund_requires_host_approval":True,"tool_catalog_sha256":"0"*64}, sort_keys=True),))
            db.commit()
        request={"operation_id":self.operation_id,"approval_nonce":nonce,"action_sha256":hashlib.sha256(canonical(self.action)).hexdigest(),"action":self.action}
        provider=subprocess.run([sys.executable,"-S",str(PROVIDER),"commit","--db",str(self.provider_db),"--authority-db",str(self.authority_db),"--expected-policy-sha256",self.approved_policy_sha256,"--fault","none"],input=json.dumps(request),capture_output=True,text=True,timeout=10)
        self.assertEqual(provider.returncode,6,provider.stdout+provider.stderr)
        self.assertEqual(self.output(provider)["error"],"policy-catalog-binding-rejected")
        self.assertEqual(len(self.effects()),0)



if __name__ == "__main__": unittest.main(verbosity=2)
