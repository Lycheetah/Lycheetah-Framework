"""Run a local end-to-end demonstration; no GitHub/network provider calls."""
from __future__ import annotations
import json
import secrets
import tempfile
import threading
from pathlib import Path

from action_guard_v07 import PersistentActionGuard, FakeMergeProvider
from checkpoint_authority import CheckpointStore, CheckpointHTTPClient, make_server
from checkpointed_workflow import CheckpointedWorkflow
from execution_workflow import SimulatedMergeExecutor


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="lycheetah-v08-") as tmp:
        root = Path(tmp)
        token = secrets.token_urlsafe(32)
        store = CheckpointStore(root / "checkpoint-authority" / "authority.sqlite3",
                                root / "checkpoint-authority" / "ed25519-private.pem")
        server = make_server(store, token, "127.0.0.1", 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = CheckpointHTTPClient(f"http://127.0.0.1:{server.server_address[1]}",
                                          token, store.public_key_bytes())
            guard = PersistentActionGuard(root / "guard-ledger" / "ledger.sqlite3")
            workflow = CheckpointedWorkflow(guard, client, "demo-journal")
            bootstrap = workflow.bootstrap_empty_journal()
            provider = FakeMergeProvider()
            provider.seed_pr("Lycheetah/demo", 17, "a" * 40, "b" * 40)
            action = provider.read_action("Lycheetah/demo", 17)
            approval = workflow.issue_approval("approval-demo", "agent-demo", "reviewer-demo",
                action, "merge:Lycheetah/demo#17", 100, 200)
            prepared = workflow.prepare_effect("effect-demo", "approval-demo", "agent-demo",
                action, "merge:Lycheetah/demo#17", 110)
            execution = SimulatedMergeExecutor(workflow, provider, "Lycheetah/demo", 17).execute("effect-demo", 120)
            print(json.dumps({
                "classification": "local synthetic scenario; no live GitHub calls",
                "bootstrap_checkpointed": bootstrap.checkpointed,
                "approval_checkpointed": approval.checkpointed,
                "effect_prepared_checkpointed": prepared.checkpointed,
                "execution_status": execution.status,
                "provider_called": execution.provider_called,
                "provider_is_fake": True,
                "github_request_preview": execution.request_preview,
                "final_effect_status": guard.get_effect("effect-demo")["status"],
                "audit_checkpoint_status": workflow.synchronize_status(),
            }, indent=2, sort_keys=True))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == "__main__":
    main()
