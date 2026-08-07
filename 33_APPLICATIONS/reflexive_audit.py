#!/usr/bin/env python3
"""
─── ⊚ THE REFLEXIVE AUDIT ───────────────────────────────────────────────────────

Runs the repaired `semantic_extractor.py` over OUR OWN documents.

The corpus's stated purpose is detecting overclaim. It has never once been aimed
at the documents that do the claiming. Authorised by Mac, 2026-08-07:
  "i know some of the tools in them wer witing to be used as proof so go ahead
   and use them on whatever repository as you need"

⚠ THE QUOTED FLAG IS THE WHOLE DIFFICULTY. Our documents quote overclaims in order
  to RETRACT them. A naive scan reads a retraction as the offence it retracts. The
  extractor carries a `quoted` flag for attributed spans; this runner reports
  quoted and unquoted hits SEPARATELY and only ever ranks on the unquoted ones.
  A file that scores badly on quoted spans alone is doing its job.
"""
from __future__ import annotations
import sys, collections
from pathlib import Path

sys.path.insert(0, "/home/guestpc/CODEX_AURA_PRIME/12_IMPLEMENTATIONS/core")
from semantic_extractor import SemanticExtractor  # noqa: E402

TARGETS = [
    # ── the Truth Pressure line: the documents that make the claims ──
    ("TP master 08-03",   "/home/guestpc/CODEX_AURA_PRIME/TRUTH_PRESSURE/TRUTH_PRESSURE_MASTER_SOURCE_2026-08-03.md"),
    ("TP master 08-07",   "/home/guestpc/CODEX_AURA_PRIME/TRUTH_PRESSURE/TRUTH_PRESSURE_MASTER_SOURCE_2026-08-07.md"),
    ("TP canon",          "/home/guestpc/CODEX_AURA_PRIME/TRUTH_PRESSURE/TRUTH_PRESSURE_CANON.md"),
    # ── Hypermax's own new work, held to its own standard ──
    ("33_APP readme",     "/home/guestpc/CODEX_AURA_PRIME/33_APPLICATIONS/README.md"),
    ("external valid.",   "/home/guestpc/CODEX_AURA_PRIME/33_APPLICATIONS/EXTERNAL_VALIDATION_2026-08-07.md"),
    ("discrim. audit",    "/home/guestpc/CODEX_AURA_PRIME/33_APPLICATIONS/DISCRIMINATION_AUDIT_2026-08-07.md"),
    ("derived cues",      "/home/guestpc/CODEX_AURA_PRIME/33_APPLICATIONS/DERIVED_CUES_2026-08-07.md"),
    ("transfer test",     "/home/guestpc/CODEX_AURA_PRIME/33_APPLICATIONS/TRANSFER_TEST_2026-08-07.md"),
    # ── LAMAGUE ──
    ("LAMAGUE master",    "/home/guestpc/CODEX_AURA_PRIME/03_LAMAGUE_L1/LAMAGUE_MASTER_SOURCE_2026-08-03.md"),
    # ── the governing instruments ──
    ("CLAUDE.md",         "/home/guestpc/CODEX_AURA_PRIME/CLAUDE.md"),
    ("THE_SOL_PROTOCOL",  "/home/guestpc/CODEX_AURA_PRIME/THE_SOL_PROTOCOL.md"),
    # ── the game repo: the outward-facing surfaces ──
    ("game README",       "/home/guestpc/0sol-by-lycheetah/README.md"),
    ("world plan",        "/home/guestpc/0sol-by-lycheetah/docs/OPUS_SOL_WORLD_FILL_AND_BATTLE_PLAN_2026-08-07.md"),
    ("topdown plans",     "/home/guestpc/0sol-by-lycheetah/docs/WORLD_TOPDOWN_PLANS_2026-08-07.md"),
]

ex = SemanticExtractor()
rows, all_unquoted = [], []

for label, path in TARGETS:
    p = Path(path)
    if not p.exists():
        rows.append((label, path, None, None, None, 0, 0, "MISSING"))
        continue
    text = p.read_text(encoding="utf8", errors="replace")
    r = ex.extract(text)
    unq = [s for s in r.signals if s.polarity == "manipulation" and not s.quoted]
    quo = [s for s in r.signals if s.polarity == "manipulation" and s.quoted]
    integ = [s for s in r.signals if s.polarity == "integrity"]
    rows.append((label, path, r.manipulation_density, r.integrity_density,
                 r.net_integrity, len(unq), len(quo), f"{len(integ)} integrity"))
    for s in unq:
        all_unquoted.append((label, s.category, s.label, s.span))

print("═" * 86)
print("THE REFLEXIVE AUDIT — our own instrument, aimed at our own documents")
print("═" * 86)
print(f"{'document':<18} {'manip':>7} {'integ':>7} {'net':>8}   {'unquoted':>8} {'quoted':>6}  note")
print("─" * 86)
for label, path, m, i, n, nu, nq, note in sorted(
        rows, key=lambda r: (r[4] is None, r[4] if r[4] is not None else 0)):
    if m is None:
        print(f"{label:<18} {'—':>7} {'—':>7} {'—':>8}   {'—':>8} {'—':>6}  ⚠ MISSING: {path}")
        continue
    flag = "  🔴" if nu > 0 else ""
    print(f"{label:<18} {m:>7.3f} {i:>7.3f} {n:>+8.3f}   {nu:>8} {nq:>6}  {note}{flag}")

print()
print("═" * 86)
print("EVERY UNQUOTED MANIPULATION SPAN IN OUR CORPUS  (these are the real hits)")
print("═" * 86)
if not all_unquoted:
    print("  none — no unattributed manipulation cue fired in any document scanned.")
else:
    by_doc = collections.defaultdict(list)
    for label, cat, lab, span in all_unquoted:
        by_doc[label].append((cat, lab, span))
    for label, hits in by_doc.items():
        print(f"\n▸ {label}   ({len(hits)} hit{'s' if len(hits) != 1 else ''})")
        for cat, lab, span in hits:
            print(f"    {cat:<24} {lab:<32} {span!r}")

print()
print("═" * 86)
counts = collections.Counter(c for _, c, _, _ in all_unquoted)
print(f"TOTAL unquoted manipulation spans across {len([r for r in rows if r[2] is not None])} documents: {len(all_unquoted)}")
for cat, n in counts.most_common():
    print(f"  {cat:<26} {n}")
print("═" * 86)
