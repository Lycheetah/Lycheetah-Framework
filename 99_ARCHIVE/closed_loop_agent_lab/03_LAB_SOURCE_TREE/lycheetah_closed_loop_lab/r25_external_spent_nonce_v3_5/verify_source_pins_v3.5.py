"""Verify retained baseline source copies against SOURCE_PIN_v3.5.json."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIN = json.loads((ROOT / "SOURCE_PIN_v3.5.json").read_text(encoding="utf-8"))
failures=[]
for rel, expected in PIN["sha256"].items():
    path=ROOT/rel
    actual=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    print(f"{rel}: {'PASS' if actual == expected else 'FAIL'} ({actual})")
    if actual != expected: failures.append(rel)
if failures:
    raise SystemExit("source-pin-mismatch: " + ", ".join(failures))
print("SOURCE_PIN_VERIFICATION=PASS")
