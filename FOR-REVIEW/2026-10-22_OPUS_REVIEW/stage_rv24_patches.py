#!/usr/bin/env python3
"""Stage the RV24 patch against the Anon Politician Civic Signal validator, and witness it.

`civic_signal_validator.py` is pinned by both `anon_politician/SHA256SUMS.txt` and the
v1.3 handoff's `SHA256SUMS.txt`, so nothing is edited in place. Each swap is applied to
the HEAD bytes and must match exactly once. The patch is then applied to a fresh HEAD
copy of the kit, which is checked three ways:

  1. the kit's own 16 unittest cases still pass;
  2. the claim-shape probes reach the claim gate after the patch (UNSUPPORTED_POPULATION_CLAIM
     or INVALID_CLAIMS), and bypass it on the unpatched HEAD copy. The unpatched copy is the
     known-bad witness.
  3. the benign control (an opt-in record making no population claim) gains no claim error.

    python3 -B stage_rv24_patches.py <repo-root> <scratch-dir>

Writes:
    FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV24_civic_signal_claim_shape.patch

Applying it changes a checksummed file, so both SHA256SUMS lists need a dated re-mint in
the same change. That is Mac's call (see the ledger).
"""
from __future__ import annotations

import copy
import filecmp
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

KIT = ("23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/"
       "08_CIVIC_SIGNAL_v0.3/Anon_Politician_Civic_Signal_Kit_v0_3")
TARGET = KIT + "/src/civic_signal_validator.py"

SWAPS = [
    ('    claims = set(record.get("claims", []) or [])\n',
     '    raw_claims = record.get("claims", []) or []\n'
     '    if isinstance(raw_claims, str):\n'
     '        raw_claims = [raw_claims]\n'
     '    if not isinstance(raw_claims, list) or not all(isinstance(c, str) for c in raw_claims):\n'
     '        out.append(finding("error", "INVALID_CLAIMS", "claims must be a list of claim codes (strings)."))\n'
     '        raw_claims = [c for c in raw_claims if isinstance(c, str)] if isinstance(raw_claims, list) else []\n'
     '    # Normalise, so "Representative" or a bare string cannot slip past the claim gates.\n'
     '    claims = {c.strip().lower() for c in raw_claims}\n'),
]

PATCH_NAME = "RV24_civic_signal_claim_shape.patch"
PROBES = [("string claim", "representative", "UNSUPPORTED_POPULATION_CLAIM"),
          ("capitalised", ["Representative"], "UNSUPPORTED_POPULATION_CLAIM"),
          ("padded", [" national_consensus "], "UNSUPPORTED_POPULATION_CLAIM"),
          ("dict in list", [{"x": 1}], "INVALID_CLAIMS")]
CLAIM_CODES = {"UNSUPPORTED_POPULATION_CLAIM", "INVALID_CLAIMS"}


def error_codes(kit: Path, record: dict) -> set[str] | str:
    spec = importlib.util.spec_from_file_location(f"csv_{id(kit)}_{kit.name}", kit / "src/civic_signal_validator.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        return {f["code"] for f in mod.validate(record) if f["severity"] == "error"}
    except Exception as exc:  # the unpatched validator crashes on unhashable claims
        return f"CRASH {type(exc).__name__}"


def main() -> int:
    root, scratch = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    out = root / "FOR-REVIEW/2026-10-22_OPUS_REVIEW" / PATCH_NAME
    work = scratch / "rv24_stage"
    if work.exists():
        shutil.rmtree(work)
    text = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{TARGET}"],
                          check=True, capture_output=True).stdout.decode("utf-8")
    assert (root / TARGET).read_text(encoding="utf-8") == text, f"{TARGET} differs from HEAD"
    new = text
    for old, rep in SWAPS:
        assert new.count(old) == 1, f"swap matched {new.count(old)}x: {old[:60]!r}"
        new = new.replace(old, rep)
    assert "\r" not in new
    for side, body in (("a", text), ("b", new)):
        dest = work / side / TARGET
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
    diff = subprocess.run(["diff", "-ruN", "a", "b"], cwd=work, capture_output=True, text=True)
    assert diff.returncode == 1 and diff.stdout, "empty diff"
    out.write_text(diff.stdout, encoding="utf-8")

    # Two whole-kit copies from HEAD: one left alone, one patched.
    for name in ("head", "patched"):
        dest = work / name
        dest.mkdir()
        archive = subprocess.run(["git", "-C", str(root), "archive", "HEAD", KIT], check=True, capture_output=True)
        subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)
    subprocess.run(["patch", "-p1", "--quiet", "-i", str(out)], cwd=work / "patched", check=True)
    assert filecmp.cmp(work / "patched" / TARGET, work / "b" / TARGET, shallow=False), "mismatch after patch"

    ok = True
    suite = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"],
                           cwd=work / "patched" / KIT, capture_output=True, text=True)
    tail = suite.stderr.strip().splitlines()
    print(f"patched kit suite: {tail[-3] if len(tail) >= 3 else tail} / {tail[-1] if tail else ''}")
    ok &= suite.returncode == 0 and "Ran 16 tests" in suite.stderr

    head_kit, new_kit = work / "head" / KIT, work / "patched" / KIT
    base = json.loads((head_kit / "examples/open_pulse_descriptive_only.json").read_text(encoding="utf-8"))
    assert base["recruitment"]["method"] == "open_opt_in"
    for label, claims, want in PROBES:
        rec = copy.deepcopy(base)
        rec["claims"] = claims
        before, after = error_codes(head_kit, rec), error_codes(new_kit, rec)
        bypassed = isinstance(before, str) or not (before & CLAIM_CODES)
        caught = not isinstance(after, str) and want in after
        print(f"{label:13} HEAD: {'bypass' if bypassed else 'caught'} {before if isinstance(before, str) else ''}"
              f"  patched: {'caught ' + want if caught else 'MISSED'}")
        ok &= bypassed and caught
    benign = copy.deepcopy(base)
    benign["claims"] = ["participant_themes"]
    after = error_codes(new_kit, benign)
    print(f"benign control patched claim errors: {sorted(after & CLAIM_CODES)}")
    ok &= not (after & CLAIM_CODES)

    added = sum(1 for line in diff.stdout.splitlines() if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff.stdout.splitlines() if line.startswith("-") and not line.startswith("---"))
    print(f"{'STAGED' if ok else 'FAILED'} {PATCH_NAME}: 1 file, +{added} -{removed}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
