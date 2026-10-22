"""Apply the RV19 status notes to the two unpinned documents that carry +40.3% / +110% / -95.2%.

Usage: python3 -B apply_rv19_doc_notes.py <framework-root>

Neither file is pinned by a manifest, so the notes go in place. Each note is placed by an
exact-one anchor, the original text stays, and every fact the notes state is asserted first.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
LEDGER = "`FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH18_FINDINGS_AND_LEDGER.md`"
MATERIALS = ["50_belief_corpus.json", "annotator_labels.csv", "trial_results_200.csv",
             "analysis.py", "trial_config.json"]

# The facts the notes rest on.
history = subprocess.run(["git", "log", "--all", "--name-only", "--format="], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.split()
for name in MATERIALS + ["cascade_synthetic_experiment.py"]:
    assert not any(p.endswith(name) for p in history), name
    assert not list(ROOT.rglob(name)), name
engine = (ROOT / "12_IMPLEMENTATIONS/core/cascade_engine.py").read_text(encoding="utf-8")
assert len(engine.splitlines()) == 744
assert "def compute_coherence" not in engine and "def compute_forgetting" not in engine
pooled = ((0.063 ** 2 + 0.058 ** 2) / 2) ** 0.5
assert round((0.742 - 0.529) / pooled, 2) == 3.52
assert round((0.93 - 0.58) / 0.58 * 100, 1) == 60.3
assert round((1.0 - 0.47) / 0.47 * 100, 1) == 112.8

EMP = ("> **Status note (review 2026-10-22, RV19): UNVERIFIED.** No artifact behind this document "
       "exists in the repository. " + ", ".join(f"`{m}`" for m in MATERIALS) + " are absent from the "
       "working tree and from every commit in its history, and `12_IMPLEMENTATIONS/core/cascade_engine.py` "
       "(744 lines) defines neither `compute_coherence()` nor `compute_forgetting()`. The table's own "
       "numbers do not give the stated effect size: means 0.742 and 0.529 with SDs 0.063 and 0.058 give "
       "a pooled d of about 3.52, not 2.84. Two other accounts of the same +40.3% disagree with this one: "
       "`28_DEFENSE/CLAIMS.json` (CAS-009) and `28_DEFENSE/TESTABILITY_MANIFEST.md` give 0.58→0.93 over "
       "10 replications and 3 conditions, which is +60.3%, and cite a `cascade_synthetic_experiment.py` "
       "that has never existed in the repository. Until the materials are produced, the results below "
       "cannot be checked. The original text is kept (" + LEDGER + ").\n")
EMP_S6 = ("\n> **Status note (review 2026-10-22, RV19).** None of the materials listed in this section "
          "exist in the repository or its history; see the note under the document header.\n")

MANIFEST = {
    "CAS-009": ("> **Status note (review 2026-10-22, RV19): UNVERIFIED.** "
                "`cascade_synthetic_experiment.py` exists nowhere in the repository or its history, so "
                "this protocol cannot be run. 0.58→0.93 is +60.3%, not +40.3%. The +40.3% in "
                "`TRUTH_PRESSURE/EMPIRICAL_RESULTS.md` comes from a different design (200 trials, "
                "0.529→0.742) whose materials are also absent. The original entry is kept (" + LEDGER + ").\n"),
    "CAS-010": ("> **Status note (review 2026-10-22, RV19).** The stored run "
                "(`11_MATHEMATICAL_FOUNDATIONS/cascade_simulation_results.json`) reproduces exactly, but "
                "the additive baseline also scores 1.0 in every domain and every trial, so CASCADE ties "
                "it (t = 0, d = 0). The +110% is measured against a static baseline that never updates. "
                "0.47→1.0 is +112.8%; 110.05% is the mean of the five per-domain percentages. The 200 "
                "trials per domain are identical deterministic runs, so the p-values do not count "
                "independent samples. MEASURED: CASCADE beats no update; it does not beat additive "
                "update. The original entry is kept (" + LEDGER + ").\n"),
    "CAS-011": ("> **Status note (review 2026-10-22, RV19): UNVERIFIED.** The code path does not exist. "
                "The 0.42→0.02 here and the 1.00%→0.048% in `TRUTH_PRESSURE/EMPIRICAL_RESULTS.md` both "
                "give 95.2% from different numbers, and neither has data in the repository. The original "
                "entry is kept (" + LEDGER + ").\n"),
}


def write(rel, text):
    (ROOT / rel).write_text(text, encoding="utf-8")


rel = "TRUTH_PRESSURE/EMPIRICAL_RESULTS.md"
text = (ROOT / rel).read_text(encoding="utf-8")
if "(review 2026-10-22, RV19)" not in text:
    anchor = "**Resolves:** Task 30 — standalone verifiable results document\n"
    assert text.count(anchor) == 1
    text = text.replace(anchor, anchor + "\n" + EMP)
    hits = list(re.finditer(r"^.*All materials.*\n\n((?:- .*\n)+)", text, re.M))
    assert len(hits) == 1, len(hits)
    text = text[:hits[0].end()] + EMP_S6 + text[hits[0].end():]
    write(rel, text)

rel = "28_DEFENSE/TESTABILITY_MANIFEST.md"
text = (ROOT / rel).read_text(encoding="utf-8")
if "(review 2026-10-22, RV19)" not in text:
    for cid, note in MANIFEST.items():
        m = re.search(rf"^### {cid} .*\n\n\*\*Claim:\*\*.*\n", text, re.M)
        assert m and len(re.findall(rf"^### {cid} ", text, re.M)) == 1, cid
        text = text[:m.end()] + "\n" + note + text[m.end():]
    write(rel, text)
print("RV19 notes: EMPIRICAL_RESULTS 2, TESTABILITY_MANIFEST 3")
