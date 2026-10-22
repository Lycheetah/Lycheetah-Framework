#!/usr/bin/env python3
"""Stage the RV21 patches against frozen Truth Pressure forge bundles.

The three bundles are frozen: each carries a SHA256_MANIFEST.json and a zip mirror
under TRUTH_PRESSURE/FORGE_2026-08-02/. So nothing is edited in place. Every swap
below is applied to the HEAD bytes (`git show HEAD:<path>`), must match exactly once,
and the resulting patch is checked by applying it to a fresh HEAD copy.

    python3 -B stage_rv21_patches.py <repo-root> <scratch-dir>

Writes:
    FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV21_v07_disagreement_gate.patch
    FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV21_v04_analyzer_integrity.patch
    FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV21_v08_collector_content_scan.patch

Applying any of them leaves that bundle's SHA256_MANIFEST.json, its recorded test
results and its zip mirror stale. Re-minting those is Mac's call (see the ledger).
"""
from __future__ import annotations

import filecmp
import shutil
import subprocess
import sys
from pathlib import Path

EXP = "TRUTH_PRESSURE/FORGE_2026-08-02_EXPANDED"
V07 = f"{EXP}/TRUTH_PRESSURE_SHADOW_EVIDENCE_CONSOLE_v0.7"
V04 = f"{EXP}/TRUTH_PRESSURE_MEASUREMENT_PACK_v0.4"
V08 = f"{EXP}/TRUTH_PRESSURE_LIVE_SOURCE_COLLECTOR_v0.8"

V07_GATE_OLD = """      state: summary.triggerDisagreements === 0 ? 'PASS' : 'OPEN',
      detail: summary.triggerDisagreements === 0
        ? 'No comparable trigger disagreements are currently recorded.'
        : `${summary.triggerDisagreements} trigger disagreement(s) require human review. No automatic pass threshold is assumed.`,
"""
V07_GATE_NEW = """      // Zero disagreements out of zero comparable records is absence of evidence,
      // not agreement. The gate passes only once agreement has been observed.
      state: summary.triggerDisagreements === 0 && summary.triggerAgreements > 0 ? 'PASS' : 'OPEN',
      detail: summary.triggerDisagreements > 0
        ? `${summary.triggerDisagreements} trigger disagreement(s) require human review. No automatic pass threshold is assumed.`
        : summary.triggerAgreements === 0
          ? 'No record is trigger-comparable, so agreement has not been observed; the gate stays open.'
          : 'No comparable trigger disagreements are currently recorded.',
"""

V07_TEST_SWAPS = [
    ("    disagreement?: boolean;\n  } = {},",
     "    disagreement?: boolean;\n    agreement?: boolean;\n  } = {},"),
    ("""        : options.disagreement
          ? 'DISAGREE'
          : 'NOT_COMPARABLE',""",
     """        : options.disagreement
          ? 'DISAGREE'
          : options.agreement
            ? 'AGREE'
            : 'NOT_COMPARABLE',"""),
    ("""check('100 clean records can meet the engineering gate', () => {
  const report = buildShadowEvidenceReport(
    dataset(Array.from({ length: 100 }, (_, i) => record(i))),
    '2026-08-02T00:00:00.000Z',
  );
  assert.equal(report.releaseState, 'ENGINEERING_GATE_MET');
});
""",
     """check('100 clean records can meet the engineering gate', () => {
  const report = buildShadowEvidenceReport(
    dataset(Array.from({ length: 100 }, (_, i) => record(i, { agreement: true }))),
    '2026-08-02T00:00:00.000Z',
  );
  assert.equal(report.releaseState, 'ENGINEERING_GATE_MET');
});

check('100 records with no comparable trigger do not meet the engineering gate', () => {
  const records = Array.from({ length: 100 }, (_, i) => record(i));
  const gates = buildEngineeringGates(dataset(records));
  assert.equal(gates.find(gate => gate.id === 'GATE-DISAGREEMENT-REVIEW')?.state, 'OPEN');
  const report = buildShadowEvidenceReport(dataset(records), '2026-08-02T00:00:00.000Z');
  assert.notEqual(report.releaseState, 'ENGINEERING_GATE_MET');
});
"""),
]

V04_SWAPS = [
    ("    return 1.0 if de==0 and do==0 else (None if de==0 else 1-do/de)\n",
     "    # With no variation anywhere alpha is 0/0, undefined. Reporting 1.0 would turn\n"
     "    # uniformly uninformative ratings into \"strong agreement\".\n"
     "    return None if de==0 else 1-do/de\n"),
    ("""def load_ratings(paths,key):
    by_case={}
    for rater_index,p in enumerate(paths):
        with Path(p).open(encoding='utf-8-sig',newline='') as f:
            for row in csv.DictReader(f):
""",
     """def load_key_owners(path):
    data=json.loads(Path(path).read_text())
    return {m['item_code']:rater for rater,items in data['raters'].items() for m in items}

def load_ratings(paths,key,owners=None):
    by_case={};seen={}
    for rater_index,p in enumerate(paths):
        with Path(p).open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f))
            codes=[row['item_code'].strip() for row in rows]
            if len(set(codes))!=len(codes):raise ValueError(f'Duplicate item_code in {p}')
            if owners is not None:
                # Every agreement statistic assumes independent raters. One packet
                # supplied twice agrees with itself perfectly.
                packet={owners.get(code) for code in codes}
                if len(packet)!=1 or None in packet:raise ValueError(f'{p} does not hold exactly one rater packet')
                (rater,)=packet
                if rater in seen:raise ValueError(f'Rater packet {rater} supplied twice: {seen[rater]} and {p}')
                seen[rater]=p
            for row in rows:
"""),
    ("    key=load_key(args.key);ratings=load_ratings(args.ratings,key);engine=",
     "    key=load_key(args.key);ratings=load_ratings(args.ratings,key,load_key_owners(args.key));engine="),
]

V08_SWAPS = [
    ("""function fail(message, code = 1) {""",
     """// Name rules cannot see a key pasted into source or config. Any selected file
// whose text matches one of these is withheld and named in the receipt instead.
const CONTENT_SECRET_PATTERNS = [
  { id: 'PRIVATE-KEY-BLOCK', pattern: /-----BEGIN [A-Z ]*PRIVATE KEY-----/ },
  { id: 'SK-STYLE-KEY', pattern: /\\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}/ },
  { id: 'GOOGLE-API-KEY', pattern: /\\bAIza[0-9A-Za-z_-]{35}/ },
  { id: 'GITHUB-TOKEN', pattern: /\\bgh[pousr]_[A-Za-z0-9]{36,}/ },
  { id: 'SLACK-TOKEN', pattern: /\\bxox[abprs]-[A-Za-z0-9-]{10,}/ },
  { id: 'AWS-ACCESS-KEY', pattern: /\\bAKIA[0-9A-Z]{16}\\b/ },
  { id: 'ASSIGNED-SECRET', pattern: /(?:api[_-]?key|secret|token|password)["']?\\s*[:=]\\s*["'][^"'\\s]{16,}["']/i },
];

function secretFindings(text) {
  return CONTENT_SECRET_PATTERNS.filter(({ pattern }) => pattern.test(text)).map(({ id }) => id);
}

function fail(message, code = 1) {"""),
    ("""const files = [];
for (const [relative, metadata] of [...selected.entries()].sort(([a], [b]) => a.localeCompare(b))) {
""",
     """const files = [];
const withheld = [];
for (const [relative, metadata] of [...selected.entries()].sort(([a], [b]) => a.localeCompare(b))) {
  const scanText = readText(metadata.absolute);
  const findings = scanText === null ? ['UNREADABLE-OR-OVERSIZE'] : secretFindings(scanText);
  if (findings.length) {
    withheld.push({ path: relative, findings });
    continue;
  }
"""),
    ("    excludedCredentialsAndKeys: true,\n",
     "    excludedCredentialsAndKeys: 'BY_NAME_AND_CONTENT_PATTERN_NOT_PROOF',\n"),
    ("  fileCount: files.length,\n};\n",
     "  fileCount: files.length,\n  withheld,\n};\n"),
    ("console.log('\\nNo .env, keys, databases, logs, dependencies, builds, or user data were collected.');\n",
     """if (withheld.length) {
  console.log(`\\nWithheld ${withheld.length} file(s) whose contents look like secrets:`);
  for (const item of withheld) console.log(`  ${item.path}  [${item.findings.join(', ')}]`);
}
console.log('\\nExcluded by name: .env, key and credential files, databases, logs, dependencies, builds.');
console.log('The content scan is pattern-based and cannot prove a file holds no secret. Read the extract before sharing it.');
"""),
]

PATCHES = {
    "RV21_v07_disagreement_gate.patch": {
        f"{V07}/lib/truth-pressure-integration/shadow-analysis.ts": [(V07_GATE_OLD, V07_GATE_NEW)],
        f"{V07}/scripts/verify-shadow-review.ts": V07_TEST_SWAPS,
    },
    "RV21_v04_analyzer_integrity.patch": {
        f"{V04}/scripts/analyze_annotations.py": V04_SWAPS,
    },
    "RV21_v08_collector_content_scan.patch": {
        f"{V08}/collect-truth-pressure-live-source.mjs": V08_SWAPS,
    },
}


def head_bytes(root: Path, rel: str) -> str:
    return subprocess.run(["git", "-C", str(root), "show", f"HEAD:{rel}"],
                          check=True, capture_output=True).stdout.decode("utf-8")


def main() -> int:
    root, scratch = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    out_dir = root / "FOR-REVIEW/2026-10-22_OPUS_REVIEW"
    work = scratch / "rv21_stage"
    if work.exists():
        shutil.rmtree(work)
    for name, files in PATCHES.items():
        a, b = work / name / "a", work / name / "b"
        for rel, swaps in files.items():
            text = head_bytes(root, rel)
            # The frozen file on disk must still equal HEAD, or the patch targets a ghost.
            assert (root / rel).read_text(encoding="utf-8") == text, f"{rel} differs from HEAD"
            new = text
            for old, rep in swaps:
                assert new.count(old) == 1, f"{name}: swap matched {new.count(old)}x in {rel}: {old[:60]!r}"
                new = new.replace(old, rep)
            assert "\r" not in new
            for base, body in ((a, text), (b, new)):
                dest = base / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(body, encoding="utf-8")
        diff = subprocess.run(["diff", "-ruN", "a", "b"], cwd=work / name, capture_output=True, text=True)
        assert diff.returncode == 1 and diff.stdout, f"{name}: empty diff"
        patch_path = out_dir / name
        patch_path.write_text(diff.stdout, encoding="utf-8")
        # Witness: the patch applies cleanly to a fresh HEAD copy and reproduces b exactly.
        check = work / name / "check"
        shutil.copytree(a, check)
        subprocess.run(["patch", "-p1", "--quiet", "-i", str(patch_path)], cwd=check, check=True)
        for rel in files:
            assert filecmp.cmp(check / rel, b / rel, shallow=False), f"{name}: {rel} mismatch after patch"
        added = sum(1 for line in diff.stdout.splitlines() if line.startswith("+") and not line.startswith("+++"))
        removed = sum(1 for line in diff.stdout.splitlines() if line.startswith("-") and not line.startswith("---"))
        print(f"STAGED {name}: {len(files)} file(s), +{added} -{removed}, applies to HEAD copy and matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
