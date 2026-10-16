from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import uuid
from contextlib import closing
from dataclasses import replace
from pathlib import Path

from tool_catalog import DEFAULT_CATALOG, Field, ProposalError, ToolCatalog, ToolSpec, check_policy_catalog_binding, sha256

HERE = Path(__file__).resolve().parent
V07_HOST = HERE.parent / "authority_boundary_lab_v0_7" / "host_process.py"


def valid_proposal():
    return {"tool_name": "refund_order", "arguments": {"order_id": "ORD-42", "amount_minor": 2500, "currency": "NZD"}}


def policy_for(catalog=DEFAULT_CATALOG):
    return {"policy_id": "catalog-bound-refund", "version": 1, "refund_requires_host_approval": True, "tool_catalog_sha256": catalog.digest}


def declaration_only_decision(tool_name: str, side_effect: bool) -> str:
    """Projection of the relevant source-level branch, not a call to MCP runtime.

    For this bounded comparison we choose a non-denied tool with ordinary arguments,
    no blocked scopes and no sensitive argument keys. The actual source forwards the
    model-visible side_effect value into AssuranceEvent, and approval review is only
    triggered when that value is true and host approval is absent.
    """
    denied = ("shell", "shell.*", "shell_*", "exec", "exec.*", "exec_*", "subprocess*", "database.drop*", "identity.delete*")
    import fnmatch
    if any(fnmatch.fnmatchcase(tool_name, pattern) for pattern in denied):
        return "BLOCK"
    return "REVIEW" if side_effect else "ALLOW"


class TrustedCatalogTests(unittest.TestCase):
    def test_mutation_classification_comes_from_catalog(self):
        action = DEFAULT_CATALOG.stamp(valid_proposal(), operation_id="op-test", agent_id="fixture-agent", workspace_id="workspace-1")
        self.assertTrue(action["side_effect"])
        self.assertEqual(action["scopes"], ["orders:refund"])
        self.assertEqual(action["dispatcher_id"], "fake-provider.refund")
        self.assertEqual(action["dispatcher_version"], "1")

    def test_read_classification_comes_from_catalog(self):
        action = DEFAULT_CATALOG.stamp({"tool_name":"read_order","arguments":{"order_id":"ORD-42"}}, operation_id="op-read", agent_id="fixture-agent", workspace_id="workspace-1")
        self.assertFalse(action["side_effect"])
        self.assertEqual(action["scopes"], ["orders:read"])

    def test_model_cannot_downgrade_side_effect_classification(self):
        proposal = {**valid_proposal(), "side_effect": False}
        with self.assertRaisesRegex(ProposalError, "only-tool_name-and-arguments"):
            DEFAULT_CATALOG.stamp(proposal, operation_id="op-test", agent_id="fixture-agent", workspace_id="workspace-1")

    def test_model_cannot_supply_scopes_or_dispatcher(self):
        for extra in ({"scopes": []}, {"dispatcher_id":"fake-provider.read"}, {"dispatcher_version":"99"}, {"operation_id":"agent-chosen"}, {"workspace_id":"host-root"}):
            with self.subTest(extra=extra), self.assertRaises(ProposalError):
                DEFAULT_CATALOG.stamp({**valid_proposal(), **extra}, operation_id="op-test", agent_id="fixture-agent", workspace_id="workspace-1")

    def test_unknown_tool_rejected(self):
        with self.assertRaisesRegex(ProposalError, "unknown-tool"):
            DEFAULT_CATALOG.stamp({"tool_name":"refund_order_v2","arguments":valid_proposal()["arguments"]}, operation_id="op", agent_id="a", workspace_id="w")

    def test_unknown_and_missing_argument_fields_rejected(self):
        with self.assertRaisesRegex(ProposalError, "unknown-argument-fields"):
            DEFAULT_CATALOG.stamp({"tool_name":"refund_order","arguments":{**valid_proposal()["arguments"],"approved":True}}, operation_id="op", agent_id="a", workspace_id="w")
        with self.assertRaisesRegex(ProposalError, "missing-argument-fields"):
            DEFAULT_CATALOG.stamp({"tool_name":"refund_order","arguments":{"order_id":"ORD-42"}}, operation_id="op", agent_id="a", workspace_id="w")

    def test_bool_is_not_accepted_as_integer_amount(self):
        p = valid_proposal(); p["arguments"]["amount_minor"] = True
        with self.assertRaisesRegex(ProposalError, "expected-integer-not-bool"):
            DEFAULT_CATALOG.stamp(p, operation_id="op", agent_id="a", workspace_id="w")

    def test_nonpositive_amount_rejected(self):
        p = valid_proposal(); p["arguments"]["amount_minor"] = 0
        with self.assertRaisesRegex(ProposalError, "below-minimum"):
            DEFAULT_CATALOG.stamp(p, operation_id="op", agent_id="a", workspace_id="w")

    def test_invalid_currency_rejected(self):
        p = valid_proposal(); p["arguments"]["currency"] = "BTC"
        with self.assertRaisesRegex(ProposalError, "unsupported-choice"):
            DEFAULT_CATALOG.stamp(p, operation_id="op", agent_id="a", workspace_id="w")

    def test_policy_must_bind_exact_catalog_digest(self):
        with tempfile.TemporaryDirectory() as td:
            policy = Path(td) / "policy.json"
            policy.write_text(json.dumps(policy_for()), encoding="utf-8")
            self.assertEqual(check_policy_catalog_binding(policy)["tool_catalog_sha256"], DEFAULT_CATALOG.digest)
            policy.write_text(json.dumps({**policy_for(), "tool_catalog_sha256":"0"*64}), encoding="utf-8")
            with self.assertRaisesRegex(ProposalError, "catalog-digest-mismatch"):
                check_policy_catalog_binding(policy)

    def test_registry_revision_change_breaks_old_policy_binding(self):
        refund = DEFAULT_CATALOG.get("refund_order")
        changed_refund = replace(refund, dispatcher_version="2")
        changed = ToolCatalog((changed_refund, DEFAULT_CATALOG.get("read_order")))
        self.assertNotEqual(changed.digest, DEFAULT_CATALOG.digest)
        with tempfile.TemporaryDirectory() as td:
            policy = Path(td) / "policy.json"
            policy.write_text(json.dumps(policy_for(DEFAULT_CATALOG)), encoding="utf-8")
            with self.assertRaisesRegex(ProposalError, "catalog-digest-mismatch"):
                check_policy_catalog_binding(policy, changed)

    def test_operation_id_and_workspace_come_from_trusted_caller(self):
        p = valid_proposal()
        action = DEFAULT_CATALOG.stamp(p, operation_id="host-op-1", agent_id="host-session-9", workspace_id="workspace-7")
        self.assertEqual(action["operation_id"], "host-op-1")
        self.assertEqual(action["agent_id"], "host-session-9")
        self.assertEqual(action["workspace_id"], "workspace-7")
        self.assertNotIn("operation_id", p)

    def test_declaration_only_projection_demonstrates_classification_downgrade(self):
        # This mirrors only the relevant branch in the existing source; it is not a
        # whole-runtime execution result or proof that the MCP server dispatches tools.
        self.assertEqual(declaration_only_decision("refund_order", False), "ALLOW")
        self.assertEqual(declaration_only_decision("refund_order", True), "REVIEW")
        action = DEFAULT_CATALOG.stamp(valid_proposal(), operation_id="op", agent_id="a", workspace_id="w")
        self.assertTrue(action["side_effect"])

    def test_catalog_freezes_caller_owned_nested_lists(self):
        scopes = ["orders:refund"]
        choices = ["NZD", "USD"]
        fields = {"currency": Field("string", choices=choices)}
        spec = ToolSpec("refund_order", "fake-provider.refund", "1", True, scopes, fields, "test")
        catalog = ToolCatalog((spec,))
        digest = catalog.digest
        scopes.append("secrets.read")
        choices.append("BTC")
        fields.clear()
        self.assertEqual(catalog.digest, digest)
        self.assertEqual(catalog.get("refund_order").scopes, ("orders:refund",))
        self.assertEqual(catalog.get("refund_order").fields["currency"].choices, ("NZD", "USD"))

    def test_catalog_field_mapping_is_immutable_after_digest(self):
        spec = DEFAULT_CATALOG.get("refund_order")
        before = DEFAULT_CATALOG.digest
        with self.assertRaises(TypeError):
            spec.fields["amount_minor"] = Field("string")
        with self.assertRaises(TypeError):
            DEFAULT_CATALOG._tools["new.tool"] = spec
        self.assertEqual(DEFAULT_CATALOG.digest, before)

    def test_same_proposal_is_deterministically_stamped_except_host_context(self):
        p = valid_proposal()
        a = DEFAULT_CATALOG.stamp(p, operation_id="op-fixed", agent_id="a", workspace_id="w")
        b = DEFAULT_CATALOG.stamp(p, operation_id="op-fixed", agent_id="a", workspace_id="w")
        self.assertEqual(sha256(a), sha256(b))


class TrustedCatalogIntegrationTests(unittest.TestCase):
    def test_stamped_action_runs_through_v07_fake_host_and_provider(self):
        with tempfile.TemporaryDirectory(prefix="lyc-v08-e2e-") as td:
            root=Path(td)
            action_path=root/"action.json"; policy_path=root/"policy.json"; key_path=root/"issuer.key"
            token_path=root/"token.txt"; authority_db=root/"authority.sqlite"; provider_db=root/"provider.sqlite"
            key_path.write_bytes(b"test-only-catalog-key-long-enough-for-hmac-0123456789")
            key_path.chmod(0o600)
            policy_path.write_text(json.dumps(policy_for(), sort_keys=True), encoding="utf-8")
            check_policy_catalog_binding(policy_path)
            action=DEFAULT_CATALOG.stamp(valid_proposal(), operation_id="op-"+uuid.uuid4().hex, agent_id="fixture-agent", workspace_id="disposable-workspace")
            action_path.write_text(json.dumps(action, sort_keys=True), encoding="utf-8")

            issue=subprocess.run([sys.executable,"-S",str(V07_HOST),"issue","--authority-db",str(authority_db),"--policy-file",str(policy_path),"--key-file",str(key_path),"--action-file",str(action_path),"--token-file",str(token_path),"--ttl","120","--reviewer-id","fixture-human","--approval-ref","fixture-ticket-1"],capture_output=True,text=True,timeout=10)
            self.assertEqual(issue.returncode,0,issue.stdout+issue.stderr)
            issue_data=json.loads(issue.stdout.strip().splitlines()[-1])
            self.assertEqual(issue_data["status"],"approved-in-test-fixture")

            execute=subprocess.run([sys.executable,"-S",str(V07_HOST),"execute","--authority-db",str(authority_db),"--provider-db",str(provider_db),"--key-file",str(key_path),"--action-file",str(action_path),"--token-file",str(token_path)],capture_output=True,text=True,timeout=15)
            self.assertEqual(execute.returncode,0,execute.stdout+execute.stderr)
            self.assertEqual(json.loads(execute.stdout.strip().splitlines()[-1])["status"],"completed")
            with closing(sqlite3.connect(provider_db)) as db:
                rows=db.execute("SELECT operation_id,action_sha256,result_json FROM effects").fetchall()
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0][0],action["operation_id"])
            result=json.loads(rows[0][2])
            self.assertTrue(result["status"], "provider recorded effect status")
            self.assertEqual(result["tool_name"],"refund_order")

    def test_tampering_stamped_effect_type_cannot_dispatch(self):
        with tempfile.TemporaryDirectory(prefix="lyc-v08-tamper-") as td:
            root=Path(td); action_path=root/"action.json"; policy_path=root/"policy.json"; key_path=root/"issuer.key"; token_path=root/"token.txt"; authority_db=root/"authority.sqlite"; provider_db=root/"provider.sqlite"
            key_path.write_bytes(b"test-only-catalog-key-long-enough-for-hmac-0123456789"); key_path.chmod(0o600)
            policy_path.write_text(json.dumps(policy_for(),sort_keys=True),encoding="utf-8")
            action=DEFAULT_CATALOG.stamp(valid_proposal(),operation_id="op-"+uuid.uuid4().hex,agent_id="fixture-agent",workspace_id="disposable-workspace")
            action_path.write_text(json.dumps(action,sort_keys=True),encoding="utf-8")
            issue=subprocess.run([sys.executable,"-S",str(V07_HOST),"issue","--authority-db",str(authority_db),"--policy-file",str(policy_path),"--key-file",str(key_path),"--action-file",str(action_path),"--token-file",str(token_path)],capture_output=True,text=True,timeout=10)
            self.assertEqual(issue.returncode,0,issue.stdout+issue.stderr)
            tampered=dict(action); tampered["side_effect"]=False
            action_path.write_text(json.dumps(tampered,sort_keys=True),encoding="utf-8")
            execute=subprocess.run([sys.executable,"-S",str(V07_HOST),"execute","--authority-db",str(authority_db),"--provider-db",str(provider_db),"--key-file",str(key_path),"--action-file",str(action_path),"--token-file",str(token_path)],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(execute.returncode,0)
            self.assertFalse(provider_db.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
