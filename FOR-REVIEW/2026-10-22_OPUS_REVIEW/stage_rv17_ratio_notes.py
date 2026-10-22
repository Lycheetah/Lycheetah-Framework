"""Stage RV17_ratio_status_notes.patch for the byte-pinned LAMAGUE root corpus.

Usage: python3 -B stage_rv17_ratio_notes.py <framework-root> <scratch-dir>

The four files below are pinned by 03_LAMAGUE_L1/MASTER_MANIFEST.sha256.json, so they
are not edited in place. Each note is inserted by an exact-one swap against the HEAD
bytes, the original text stays, and the patch is checked by applying it to a HEAD copy.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
WORK = Path(sys.argv[2]).resolve() / "rv17_patch"
OUT = ROOT / "FOR-REVIEW" / "2026-10-22_OPUS_REVIEW" / "RV17_ratio_status_notes.patch"

# The "~20:1" worked example in 00_LAMAGUE_COMPLETE_EXTRACTION.md, measured, not assumed.
nl = ("If the system detects drift, it should reset to anchor state, then reorient toward purpose, "
      "and finally integrate corrections")
lam = "Ψ ↯ A₀ → Φ↑ → Ψ_inv"
char_ratio = len(nl.replace(" ", "")) / len(lam.replace(" ", ""))
byte_ratio = len(nl.encode()) / len(lam.encode())
assert (round(char_ratio, 1), round(byte_ratio, 1)) == (8.2, 3.9), (char_ratio, byte_ratio)

POINTER = ("The measured reversible result is the packet codec in `22_REVERSIBLE_COMPRESSION_v1.0/`: "
           "36/36 exact round trips and 33.8% fewer bytes than minified JSON on held-out packets, "
           "where plain per-packet gzip -9 saves 54.6% on the same split "
           "(`FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH16_FINDINGS_AND_LEDGER.md`).")

COUNT_NOTE = ("> **Status note (review 2026-10-22, RV17).** These ratios count outputs; they do not "
              "measure a codec. Twenty equations do not regenerate sixty thousand words, so "
              "\"REVERSIBLE\", \"Lossless\" and the information-loss figures were never measured. "
              "The corpus withdrew the smaller 500:1 figure in `04_BNF_GRAMMAR.md` and records 3000:1 "
              "as contradicted in `LAMAGUE_MASTER_SOURCE_2026-08-03.md`. ")

EDITS = {
    "03_LAMAGUE_L1/00_LAMAGUE_COMPLETE_EXTRACTION.md": [(
        "**The compression is REVERSIBLE** — structure extraction, not lossy compression.\n",
        "**The compression is REVERSIBLE** — structure extraction, not lossy compression.\n\n"
        + COUNT_NOTE
        + f"The \"~20:1\" example above measures {char_ratio:.1f}:1 by characters without spaces and "
          f"{byte_ratio:.1f}:1 by UTF-8 bytes. " + POINTER + " The original text above is kept.\n")],
    "03_LAMAGUE_L1/06_LAMAGUE_RAW_MATH.md": [(
        "Documentation → Theorems: 1800:1\n",
        "Documentation → Theorems: 1800:1\n\n" + COUNT_NOTE + POINTER + " The original lines above are kept.\n")],
    "03_LAMAGUE_L1/09_TRI_LINGUISTIC_DEEP_DIVE.md": [(
        "- 17,935 lines → 10 theorems = **1800:1 ratio**\n- Information loss: < 10%\n",
        "- 17,935 lines → 10 theorems = **1800:1 ratio**\n- Information loss: < 10%\n\n"
        + COUNT_NOTE + POINTER + " The original lines above are kept.\n")],
    "03_LAMAGUE_L1/04_BNF_GRAMMAR.md": [(
        "- Character ratio: **~11:1** (LAMAGUE characters vs English characters)\n",
        "- Character ratio: **~11:1** (LAMAGUE characters vs English characters)\n\n"
        "> **Status note (review 2026-10-22, RV17).** The ~11:1 counts code points with spaces "
        "removed. Each glyph costs two or three UTF-8 bytes, so the same five examples measure "
        "~4.9:1 in bytes with spaces. The English side is the author's own gloss of each "
        "expression, so both ratios compare against that gloss and not against independent text. "
        "The token ratio counts parser tokens against English words; no BPE tokenizer was run.\n")],
}

if WORK.exists():
    shutil.rmtree(WORK)
for rel, swaps in EDITS.items():
    text = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True, check=True).stdout.decode()
    (WORK / "a" / rel).parent.mkdir(parents=True, exist_ok=True)
    (WORK / "a" / rel).write_bytes(text.encode())
    for old, new in swaps:
        assert text.count(old) == 1, (rel, text.count(old))
        text = text.replace(old, new)
    (WORK / "b" / rel).parent.mkdir(parents=True, exist_ok=True)
    (WORK / "b" / rel).write_bytes(text.encode())

diff = subprocess.run(["diff", "-ruN", "a", "b"], cwd=WORK, capture_output=True).stdout
assert diff and b"\r" not in diff
OUT.write_bytes(diff)

check = WORK / "check"
shutil.copytree(WORK / "a", check)
subprocess.run(["patch", "-p1", "--quiet", "-i", str(OUT)], cwd=check, check=True)
same = all((check / rel).read_bytes() == (WORK / "b" / rel).read_bytes() for rel in EDITS)
print(f"patch {OUT.name}: {len(diff)} bytes, {len(EDITS)} files, applies to HEAD and matches: {same}, CR bytes: 0")
assert same
