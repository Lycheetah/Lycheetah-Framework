#!/usr/bin/env python3
"""Build/verify v4.6 standalone and complete Lycheetah research archives."""
from __future__ import annotations
import hashlib, json, subprocess, sys, zipfile
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/mnt/data')
LAB = ROOT / 'lycheetah_closed_loop_lab'
SRC = LAB / 'r36_ingress_attempt_budget_v4_6'
STANDALONE = ROOT / 'lycheetah_ingress_attempt_budget_v4.6.zip'
COMPLETE = ROOT / 'lycheetah_closed_loop_agent_lab_v4.6.zip'
VERIFY_JSON = ROOT / 'lycheetah_v4.6_archive_verification.json'
CHECKSUMS = ROOT / 'lycheetah_v4.6_checksums.sha256'

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def zip_files(output: Path, members: list[tuple[Path, str]]) -> dict:
    output.unlink(missing_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for disk_path, archive_path in members:
            archive.write(disk_path, archive_path)
    with zipfile.ZipFile(output, 'r') as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f'ZIP CRC failure {output}: {bad}')
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise RuntimeError(f'duplicate archive paths in {output}')
    return {'path': str(output), 'bytes': output.stat().st_size,
            'sha256': sha256(output), 'entries': len(members), 'crc_test': 'PASS'}

# Exact local reference pins, syntax, differential result and final test logs.
subprocess.run([sys.executable, str(SRC / 'verify_source_pins_v4.6.py')], cwd=SRC, check=True)
pyfiles = sorted(SRC.glob('*.py'))
subprocess.run([sys.executable, '-m', 'py_compile', *map(str, pyfiles)], cwd=SRC, check=True)
probe = subprocess.run([sys.executable, str(SRC/'differential_probe_v4.6.py')], cwd=SRC,
                       check=True, capture_output=True, text=True)
probe_json = json.loads(probe.stdout)
if not probe_json.get('expected_delta_observed'):
    raise RuntimeError('differential probe did not observe expected v4.5/v4.6 delta')
expected = {
    'ingress_tests_v4.6.log': 24,
    'coordinator_tests_v4.6.log': 13,
    'quorum_tests_v4.6.log': 38,
    'gateway_tests_v4.6.log': 53,
}
log_audit = {}
for name, count in expected.items():
    path = SRC / name
    content = path.read_text(errors='replace')
    if f'Ran {count} tests in ' not in content or '\nOK\n' not in content:
        raise RuntimeError(f'Final test log validation failed: {name}')
    item = {'tests': count, 'result': 'PASS', 'sha256': sha256(path)}
    if name == 'gateway_tests_v4.6.log':
        marker = 'LIFECYCLE_SUMMARY tests=53 errors=0 failures=0 surviving_non_main_threads=[]'
        if marker not in content:
            raise RuntimeError('Gateway lifecycle summary mismatch')
        item['lifecycle_summary'] = 'PASS'
    log_audit[name] = item


full_runner_log = SRC / 'full_suite_v4.6.log'
full_runner_text = full_runner_log.read_text(errors='replace')
for n in (24, 13, 38, 53):
    if not any(line.startswith(f'Ran {n} tests in ') for line in full_runner_text.splitlines()):
        raise RuntimeError(f'Complete runner log missing suite count {n}')
if 'LIFECYCLE_SUMMARY tests=53 errors=0 failures=0 surviving_non_main_threads=[]' not in full_runner_text:
    raise RuntimeError('Complete runner lifecycle summary missing')
if '\nFAILED (' in full_runner_text:
    raise RuntimeError('Complete runner log contains a failure marker')

standalone_names = [
    'remote_anchor_http.py', 'checkpoint_witness_quorum.py', 'spent_nonce_registry.py',
    'registry_checkpoint_quorum.py', 'remote_witness_http.py', 'registry_gateway_mtls.py',
    'shared_coordinator_quota.py', 'shared_ingress_quota.py',
    'shared_ingress_quota_v4_5_baseline_fixture.py', 'differential_probe_v4.6.py',
    'test_registry_checkpoint_quorum.py', 'test_remote_witness_process.py',
    'test_shared_coordinator_quota.py', 'test_shared_ingress_quota.py',
    'run_gateway_suite_v4.6.py', 'run_v4.6_tests.sh', 'verify_source_pins_v4.6.py',
    'SOURCE_PIN_v4.6.json', 'README_v4.6.md', 'API_CONTRACT_v4.6.md',
    'CHANGELOG_v4.6.md', 'PACK_MANIFEST_v4.6.md', 'RESULTS_v4.6.md',
    'THREAT_MODEL_v4.6.md', 'UPSTREAM_INTEGRATION_PLAN_v4.6.md',
    'BASELINE_COMPARISON_v4.6.md', 'results_v4.6.json', 'differential_probe_v4.6.json',
    'source_pin_verify_v4.6.log', 'python_compile_v4.6.log', 'full_suite_v4.6.log', 'ingress_tests_v4.6.log',
    'coordinator_tests_v4.6.log', 'quorum_tests_v4.6.log', 'gateway_tests_v4.6.log',
]
missing = [name for name in standalone_names if not (SRC / name).is_file()]
if missing:
    raise RuntimeError(f'Missing standalone components: {missing}')
standalone_info = zip_files(STANDALONE, [(SRC/n, f'ingress_attempt_budget_v4.6/{n}') for n in standalone_names])

complete_members = []
for path in sorted(LAB.rglob('*')):
    if not path.is_file():
        continue
    rel = path.relative_to(LAB)
    parts = set(rel.parts)
    if '__pycache__' in parts or '.pytest_cache' in parts or '.mypy_cache' in parts:
        continue
    if path.suffix in {'.pyc', '.pyo', '.sqlite', '.sqlite3', '.db'} or path.name.endswith(('-wal', '-shm', '.sqlite-wal', '.sqlite-shm')):
        continue
    complete_members.append((path, f'lycheetah_closed_loop_lab/{rel.as_posix()}'))
complete_info = zip_files(COMPLETE, complete_members)

report = {
    'artifact_version': '4.6',
    'built_at_utc': datetime.now(timezone.utc).isoformat(),
    'parent_artifact_version': '4.5',
    'upstream_commit_observed': '8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65',
    'upstream_modified': False,
    'hosted_service_calls': 0,
    'source_fingerprint_validation': 'PASS: 16 exact local reference fingerprints',
    'python_compile': 'PASS',
    'differential_probe': {'result': 'PASS', 'sha256': sha256(SRC/'differential_probe_v4.6.json'),
                           'expected_delta_observed': True},
    'test_suites': log_audit,
    'combined_test_methods': sum(expected.values()),
    'complete_runner_invocation': {
        'command': './run_v4.6_tests.sh all',
        'result': 'PASS',
        'sha256': sha256(full_runner_log),
        'combined_methods': 128,
        'lifecycle_summary': 'PASS: zero errors, failures, or surviving non-main threads'
    },
    'limitations': [
        'Local reference artifact results, not upstream repository CI or production certification.',
        'Local source fingerprints pin this artifact, not exact source equivalence to GitHub.',
        'Shared SQLite authority is same-host and same-PID-namespace trusted local infrastructure.',
        'Attempt rate budget applies after TCP accept and does not mitigate SYN floods or upstream connection floods.',
        'The current gateway binds IPv4 only; mapped IPv6 normalization is tested in the generic quota store and internal helper.',
        'IPv6 prefix aggregation is not implemented.',
        'No upstream file, branch, or pull request was changed; no hosted service was called.'
    ],
    'archives': {'standalone': standalone_info, 'complete_lab': complete_info},
}
VERIFY_JSON.write_text(json.dumps(report, indent=2) + '\n')
CHECKSUMS.write_text(''.join(f'{sha256(ROOT/name)}  {name}\n' for name in [STANDALONE.name, COMPLETE.name, VERIFY_JSON.name]))
for line in CHECKSUMS.read_text().splitlines():
    digest, name = line.split('  ', 1)
    if sha256(ROOT/name) != digest:
        raise RuntimeError(f'checksum mismatch: {name}')
json.loads(VERIFY_JSON.read_text())
print(json.dumps({'standalone': standalone_info, 'complete_lab': complete_info,
                  'verification_json': str(VERIFY_JSON), 'checksums': str(CHECKSUMS),
                  'test_methods': sum(expected.values())}, indent=2))
