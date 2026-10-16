#!/usr/bin/env python3
"""Verify hashes pinned in SOURCE_PIN_v4.7.json for this local artifact."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'SOURCE_PIN_v4.7.json'
data = json.loads(MANIFEST.read_text(encoding='utf-8'))
errors=[]
for name, info in data['files'].items():
    path = ROOT / name
    if not path.is_file():
        errors.append(f'MISSING {name}')
        continue
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != info['sha256']:
        errors.append(f'HASH_MISMATCH {name}: expected={info["sha256"]} actual={got}')
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print(f'PASS: {len(data["files"])} exact local artifact fingerprints verified')
print(f'observed_upstream_commit={data["observed_upstream_commit"]}; upstream_modified={data["upstream_modified"]}')
