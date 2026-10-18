"""8 child-processes × 4 isolated rounds; shared SQLite database per round.

No remote API, no distributed cluster, no network calls. Repeated identical
synthetic request uses one seeded action, approval and auth token.
"""
from __future__ import annotations
import json
import multiprocessing as mp
from pathlib import Path
from tempfile import TemporaryDirectory

from authenticated_provider import SignedSQLiteProvider, TrustedIssuer
from test_authenticated_provider import AUTH, PROVIDER

ACTION = {"actor":"agent", "subject":"fictional-refund", "amount_cents":250, "scope":"refund:create"}


def _worker(db: str, token: dict) -> str:
    p = SignedSQLiteProvider(db, authority_secret=AUTH, provider_secret=PROVIDER)
    return p.commit(ACTION, token, now=120).code


def run():
    ctx = mp.get_context("spawn")
    output = []
    with TemporaryDirectory() as directory:
        for i in range(4):
            path = str(Path(directory) / f"round{i}.sqlite")
            provider = SignedSQLiteProvider(path, authority_secret=AUTH, provider_secret=PROVIDER)
            provider.seed(ACTION)
            e, policy = provider.snapshot(ACTION["subject"])
            token = TrustedIssuer(AUTH).issue(action=ACTION, effect_id="e1", approval_id="a1",
                        subject_version=e,policy_version=policy,now=100,expires_at=300,nonce="fixed")
            with ctx.Pool(processes=8) as pool:
                decisions = pool.starmap(_worker, [(path, token)]*8)
            output.append({"round":i + 1,"committed":decisions.count("COMMITTED"),
                           "idempotent_replay":decisions.count("IDEMPOTENT_REPLAY"),
                           "other": sorted(x for x in decisions if x not in {"COMMITTED","IDEMPOTENT_REPLAY"}),
                           "effect_rows":provider.effect_count(),
                           "audit":provider.verify_audit()})
    assert all(x["committed"] == 1 and x["idempotent_replay"] == 7 and x["effect_rows"]==1 and x["audit"]["valid"] for x in output)
    return {"status":"SYNTHETIC_LOCAL_SQLITE_ONLY", "processes_per_round":8,
            "independent_rounds":4,"observations":output}

if __name__ == "__main__":
    print(json.dumps(run(), indent=2,sort_keys=True))
