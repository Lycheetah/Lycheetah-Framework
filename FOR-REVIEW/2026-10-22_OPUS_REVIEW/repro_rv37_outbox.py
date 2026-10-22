"""RV37 L1: does the v0.9 outbox bind its payload to the admitted Action?

Usage: python3 repro_rv37_outbox.py <empty scratch dir> [gate dir]
The gate dir defaults to the repository copy; pass a patched copy to witness the patch. Scratch DBs only."""
import importlib.util, sys, json
from pathlib import Path
R = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[2] / "papers/agent-safety/frontier-controls/03_atomic_resource_authority_finality_v0_9"
spec = importlib.util.spec_from_file_location("af", R / "atomic_finality.py"); af = importlib.util.module_from_spec(spec); sys.modules["af"] = af; spec.loader.exec_module(af)
from research_support import Action
D = Path(sys.argv[1])
def gate(name):
    g = af.AtomicFinalityGate(D / f"{name}.sqlite"); g.create_account("acct", 10); g.activate("agent", "scope"); return g
def act(job, eid):
    return Action(principal="agent", tool="job", operation="run", object_id=f"job-{job}", destination="local-worker", arguments={"job": job}, effect_id=eid)

# Known-bad: admitted job 1, payload says job 999
g = gate("payload"); a = act(1, "e1")
print("admit :", g.admit("agent", "scope", "acct", a, 2).state)
c = g.commit("e1", a, {"tool": "job", "operation": "run", "object_id": "job-999", "arguments": {"job": 999}})
print("commit:", c.state, c.reason)
row = g.outbox_row("e1")
if row is None:
    print("outbox: no row, so nothing can be relayed (the patched gate)")
else:
    print("outbox action_hash == admitted:", row["action_hash"] == a.action_hash, "| payload:", row["payload_json"])
    prov = af.DurableIdempotentProvider(D / "prov.sqlite"); r = af.OutboxRelay(g, prov).deliver("e1", 1)
    print("relay :", r["state"])
    import sqlite3; con = sqlite3.connect(D / "prov.sqlite"); print("provider executed:", con.execute("select payload_json from provider_effects").fetchall())

# Control: action substitution is still denied (the benchmark's case 11)
g2 = gate("subst"); a2 = act(1, "e2"); g2.admit("agent", "scope", "acct", a2, 2)
d = g2.commit("e2", act(999, "e2"), {"job": 999}); print("control action-substitution:", d.state, d.reason, "| outbox:", g2.outbox_row("e2"))
