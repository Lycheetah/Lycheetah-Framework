#!/usr/bin/env python3
"""Compare v4.8 global-only attempt bucket with v4.9 tiered attempt budgets."""
from __future__ import annotations
import importlib.util
import json
import tempfile
from pathlib import Path
from shared_ingress_quota import SharedIngressQuotaStore

ROOT = Path(__file__).resolve().parent
baseline_path = ROOT / 'shared_ingress_quota_v4_8_baseline_fixture.py'
spec = importlib.util.spec_from_file_location('v48_global_only_ingress_fixture', baseline_path)
if spec is None or spec.loader is None:
    raise RuntimeError('cannot load preserved v4.8 fixture')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def exercise_baseline(db: Path) -> dict:
    store = module.SharedIngressQuotaStore(
        db, max_active_connections=32, max_connections_per_ip=16,
        max_new_connections_per_minute=5, active_lease_ttl_seconds=120,
        boot_id='differential-v4.8', auto_renew=False,
    )
    accepted = 0
    last_reason = None
    for _ in range(8):
        lease, reason = store.reserve('192.0.2.10', auto_renew=False)
        if lease is None:
            last_reason = reason
        else:
            accepted += 1
            lease.close()
    victim, victim_reason = store.reserve('192.0.2.11', auto_renew=False)
    if victim is not None:
        victim.close()
    return {
        'noisy_peer_accepted': accepted,
        'noisy_peer_final_rejection': last_reason,
        'unrelated_peer_accepted': victim is not None,
        'unrelated_peer_rejection': victim_reason,
    }


def exercise_v49(db: Path) -> dict:
    store = SharedIngressQuotaStore(
        db, max_active_connections=32, max_connections_per_ip=16,
        max_new_connections_per_minute=5,
        max_new_connections_per_peer_per_minute=2,
        active_lease_ttl_seconds=120, boot_id='differential-v4.9', auto_renew=False,
    )
    accepted = 0
    peer_denials = 0
    global_denials = 0
    for _ in range(8):
        lease, reason = store.reserve('192.0.2.10', auto_renew=False)
        if lease is None:
            if reason == 'peer-connection-rate-limit': peer_denials += 1
            elif reason == 'connection-rate-limit': global_denials += 1
        else:
            accepted += 1
            lease.close()
    victim, victim_reason = store.reserve('192.0.2.11', auto_renew=False)
    if victim is not None:
        victim.close()
    return {
        'noisy_peer_accepted': accepted,
        'noisy_peer_peer_rate_denials': peer_denials,
        'noisy_peer_global_rate_denials': global_denials,
        'unrelated_peer_accepted': victim is not None,
        'unrelated_peer_rejection': victim_reason,
        'global_tokens_approx': store.snapshot()['global_rate_tokens'],
        'bucket_count': store.snapshot()['attempt_rate_bucket_count'],
    }


with tempfile.TemporaryDirectory(prefix='lyc-attempt-rate-diff-') as td:
    td = Path(td)
    baseline = exercise_baseline(td / 'v48.sqlite3')
    tiered = exercise_v49(td / 'v49.sqlite3')
    result = {
        'comparison': 'v4.8 global-only attempt rate versus v4.9 per-peer bucket plus global budget',
        'scenario': 'one IPv4 peer makes eight rapid attempts, then an unrelated peer attempts once',
        'baseline_v4_8': baseline,
        'tiered_v4_9': tiered,
        'expected_delta_observed': (
            baseline['unrelated_peer_accepted'] is False
            and tiered['unrelated_peer_accepted'] is True
            and tiered['noisy_peer_accepted'] == 2
            and tiered['noisy_peer_peer_rate_denials'] == 6
        ),
        'scope': 'local deterministic reference stores only; no live network or hosted service',
        'limitations': [
            'The global rate limit still bounds aggregate accepted attempts after source tiers pass.',
            'Prefix buckets are network heuristics, not authenticated identity.',
            'This is an isolated store comparison, not an Internet traffic test or upstream CI.',
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result['expected_delta_observed']:
        raise SystemExit('expected global-budget fairness delta not observed')
