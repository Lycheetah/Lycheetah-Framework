"""Simulated demonstration only. Does not send a real message."""
import json
import tempfile
from pathlib import Path
from tests.test_intent_bridge import Action, FakeFence
from intent_bridge import IntentAuthorityBridge
from epistemic_boundary import assess


def run():
    with tempfile.TemporaryDirectory() as d:
        fence = FakeFence()
        bridge = IntentAuthorityBridge(fence, Path(d) / "journal.db")
        old = Action("human", "e-mail-1", "colleague@example.test", "Please send this.")
        new = Action("human", "e-mail-2", "colleague@example.test", "Actually, draft only.")
        initial = bridge.grant("human", "email", "Send once", old)
        old_handle = bridge.issue("human", "email", old).handle
        updated = bridge.grant("human", "email", "Review revised draft", new,
                               reason_class="changed_mind")
        rejected = bridge.commit(old_handle, old)
        accepted = bridge.commit(bridge.issue("human", "email", new).handle, new)
        epistemic = assess(followed_original_plan=False, current_grant_valid=True,
                           action_inside_grant=True, identity_verified=False)
        return {
            "note": "Simulation using FakeFence, not original GitHub upstream or real mail provider",
            "old_intention": initial.version,
            "current_intention": updated.version,
            "original_action_after_revision": rejected.state,
            "new_action_in_local_simulation": accepted.state,
            "observed_plan_adherence": epistemic.plan_adherence,
            "human_free_will": epistemic.metaphysical_free_will,
            "consent_authenticated": False,
            "external_effects": 0,
        }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
