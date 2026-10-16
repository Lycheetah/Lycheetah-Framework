#!/usr/bin/env python3
"""Regenerate local v4.9 artifact pins after an intentional reviewed edit."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = [
    'shared_ingress_quota.py', 'registry_gateway_mtls.py', 'test_shared_ingress_quota.py',
    'test_remote_witness_process.py', 'shared_coordinator_quota.py', 'test_shared_coordinator_quota.py',
    'registry_checkpoint_quorum.py', 'test_registry_checkpoint_quorum.py', 'remote_witness_http.py',
    'remote_anchor_http.py', 'checkpoint_witness_quorum.py', 'spent_nonce_registry.py',
    'shared_ingress_quota_v4_5_baseline_fixture.py', 'shared_ingress_quota_v4_6_baseline_fixture.py',
    'shared_ingress_quota_v4_7_baseline_fixture.py', 'shared_ingress_quota_v4_8_baseline_fixture.py',
    'differential_probe_v4.9.py', 'run_gateway_suite_v4.9.py', 'run_gateway_shards_v4.9.sh',
    'run_v4.9_tests.sh', 'README_v4.9.md', 'API_CONTRACT_v4.9.md', 'BASELINE_COMPARISON_v4.9.md',
    'CHANGELOG_v4.9.md', 'PACK_MANIFEST_v4.9.md', 'THREAT_MODEL_v4.9.md',
    'UPSTREAM_INTEGRATION_PLAN_v4.9.md', 'UPSTREAM_NOTE_v4.9.md', 'RESULTS_v4.9.md',
    'generate_source_pin_v4.9.py', 'verify_source_pins_v4.9.py',
]
files = {}
for name in FILES:
    path = ROOT / name
    if not path.is_file():
        raise SystemExit(f'missing file to pin: {name}')
    files[name] = {
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'origin': ('preserved local v4.5/v4.6/v4.7/v4.8 comparison fixture' if 'baseline_fixture' in name
                   else 'v4.9 local reference code, tests, runner or documentation'),
    }
data = {
    'version': '4.9',
    'parent_artifact_version': '4.8',
    'observed_upstream_commit': '8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65',
    'scope_note': 'Optional per-peer and optional aggregate IPv6 attempt rate buckets atop global pre-authentication ingress budget.',
    'upstream_modified': False,
    'hosted_service_calls': 0,
    'local_fingerprint_semantics': 'Pins local artifact files only; does not assert byte identity to upstream GitHub.',
    'files': files,
}
(ROOT / 'SOURCE_PIN_v4.9.json').write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print(f'Wrote {len(files)} local source/document fingerprints')
