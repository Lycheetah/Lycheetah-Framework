#!/usr/bin/env python3
"""Compare the preserved v4.6 exact-IP bucket with v4.7 IPv6-prefix policy."""
from __future__ import annotations
import importlib.util
import json
import tempfile
from pathlib import Path
from shared_ingress_quota import SharedIngressQuotaStore, canonical_peer_identity

ROOT = Path(__file__).resolve().parent
A = '2001:db8:1234:5678::1'
B = '2001:db8:1234:5678:ffff:ffff:ffff:99'
C = '2001:db8:1234:5679::1'

def load_baseline():
    path = ROOT / 'shared_ingress_quota_v4_6_baseline_fixture.py'
    spec = importlib.util.spec_from_file_location('baseline_v46_ingress', path)
    if spec is None or spec.loader is None:
        raise RuntimeError('cannot-load-v4.6-baseline')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    baseline = load_baseline()
    with tempfile.TemporaryDirectory(prefix='lyc-v47-diff-') as td:
        old = baseline.SharedIngressQuotaStore(
            Path(td) / 'old.sqlite3', max_active_connections=4,
            max_connections_per_ip=1, max_new_connections_per_minute=60,
            active_lease_ttl_seconds=3, auto_renew=False, boot_id='v46-baseline')
        old_a, why_a = old.reserve(A, auto_renew=False)
        old_b, why_b = old.reserve(B, auto_renew=False)
        old_distinct_addresses_both_admitted = old_a is not None and old_b is not None
        if old_b is not None: old_b.close()
        if old_a is not None: old_a.close()

        new = SharedIngressQuotaStore(
            Path(td) / 'new.sqlite3', max_active_connections=4,
            max_connections_per_ip=1, max_new_connections_per_minute=60,
            active_lease_ttl_seconds=3, auto_renew=False, boot_id='v47-candidate')
        new_a, why_new_a = new.reserve(A, auto_renew=False)
        new_b, why_new_b = new.reserve(B, auto_renew=False)
        other, why_other = new.reserve(C, auto_renew=False)
        mapped_same = canonical_peer_identity('192.0.2.44') == canonical_peer_identity('::ffff:192.0.2.44')
        result = {
            'comparison': 'preserved-v4.6-source-fixture-vs-v4.7-prefix-identity',
            'addresses': {'a': A, 'b': B, 'c': C},
            'v4_6': {
                'peer_key_a': old._peer(A), 'peer_key_b': old._peer(B),
                'peer_keys_equal': old._peer(A) == old._peer(B),
                'both_same_64_admitted': old_distinct_addresses_both_admitted,
                'first_reason': why_a, 'second_reason': why_b,
            },
            'v4_7': {
                'peer_key_a': canonical_peer_identity(A), 'peer_key_b': canonical_peer_identity(B),
                'same_64_equal': canonical_peer_identity(A) == canonical_peer_identity(B),
                'first_admitted': new_a is not None, 'second_admitted': new_b is not None,
                'second_reason': why_new_b, 'different_64_admitted': other is not None,
                'different_64_reason': why_other, 'mapped_ipv4_alias_same_identity': mapped_same,
            },
            'expected_delta_observed': bool(
                old_distinct_addresses_both_admitted and new_a is not None and new_b is None
                and why_new_b == 'per-ip-connection-limit' and other is not None and mapped_same),
        }
        for lease in (new_a, new_b, other):
            if lease is not None: lease.close()
        if not result['expected_delta_observed']:
            raise SystemExit(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))

if __name__ == '__main__': main()
