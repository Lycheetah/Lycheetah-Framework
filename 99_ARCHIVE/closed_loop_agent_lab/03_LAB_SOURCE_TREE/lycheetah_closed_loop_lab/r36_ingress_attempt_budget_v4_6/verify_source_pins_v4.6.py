#!/usr/bin/env python3
"""Verify exact local files included in the v4.6 reference artifact."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
PIN = ROOT / 'SOURCE_PIN_v4.6.json'

def main() -> int:
    data = json.loads(PIN.read_text(encoding='utf-8'))
    failures = []
    for rel, metadata in data['files'].items():
        path = ROOT / rel
        if not path.is_file():
            print(f'FAIL missing {rel}'); failures.append(rel); continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != metadata['sha256']:
            print(f'FAIL {rel} expected={metadata["sha256"]} got={digest}'); failures.append(rel)
        else:
            print(f'PASS {rel} sha256={digest}')
    if failures:
        print(f'FAIL: {len(failures)} fingerprint mismatch(es)'); return 1
    print(f'PASS: {len(data["files"])} exact local reference fingerprints verified')
    print('Note: local fingerprints pin this research artifact; they do not claim upstream equivalence.')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
