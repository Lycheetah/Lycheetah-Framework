#!/usr/bin/env python3
"""
Compression vs gzip — the comparison a public claim has to survive.

WHY THIS EXISTS
---------------
`03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/` reports 33.8% held-out reduction
against canonical minified JSON. Its own `CLAIM_BOUNDARY.md` is careful and
honest about scope. But the benchmark never compares against a general-purpose
compressor, and that is the first thing any reader will reach for.

They should. **gzip -9, applied per packet, reaches 54.7% on the same corpus** —
twenty-one points better than the codec. Publishing "33.8% smaller than JSON" as
a headline invites a one-line reply using a standard-library call from 1992, and
the reply would be correct.

That comparison is run here so it is on the record inside the repository rather
than discovered by a critic.

WHAT THE COMPARISON ACTUALLY SHOWS
----------------------------------
The codec and gzip are not competitors. They remove different redundancy:

* gzip finds repeated byte sequences it has to discover in each payload.
* `L1` removes the schema itself — field names, repeated record shapes — before
  gzip ever runs, and `L1D` additionally references a shared codebook.

Composed, they beat either alone:

```text
JSON minified                  76,482 bytes      —
LAMAGUE L1D                    49,850          34.8%   (worse than gzip)
JSON minified + gzip -9        34,631          54.7%
LAMAGUE L1D + gzip -9          25,272          67.0%   <- best
```

**L1D + gzip is 27.0% smaller than JSON + gzip.** That is the defensible
compression claim: the format is a preprocessing step that makes a general
compressor work better, not a replacement for one.

AND THE PART GZIP CANNOT DO AT ANY RATIO
----------------------------------------
gzip will compress a decision record whose dissent field has been deleted, and
return no signal whatsoever. The codec rejects it. Nine constructed mutation
classes, 36 packets each, 324/324 correctly classified:

    DROP_DISSENT   DROP_AFFECTED_PARTIES   DROP_UNKNOWNS   DROP_AUTHORITY
    DROP_RECOVERY  DROP_VALUE_FLOW   UNPROTECT_UNKNOWN
    REMOVE_GUARD_OPERATION   CHANGE_INVARIANT

Those are the fields that vanish first when a decision is summarised upward.
Compression ratio is the least interesting thing this artefact does.

NOTE ON THE SEALED PACKAGE
--------------------------
`22_REVERSIBLE_COMPRESSION_v1.0/` is a shipped release that verifies byte-for-byte
against its own `SHA256_MANIFEST.json` (28/28). This script lives outside it and
only reads from it, so the manifest stays valid.

USAGE
-----
    python3 33_APPLICATIONS/compression_vs_gzip.py

Author: Sol, for the Lycheetah Framework. MIT.
"""

from __future__ import annotations

import bz2
import gzip
import json
import lzma
import sys
from pathlib import Path
from typing import Callable, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
PKG = REPO_ROOT / "03_LAMAGUE_L1" / "22_REVERSIBLE_COMPRESSION_v1.0"


def canonical(packet: dict) -> bytes:
    """The benchmark's stated baseline: canonical minified JSON, UTF-8."""
    return json.dumps(packet, separators=(",", ":"), sort_keys=True).encode("utf-8")


def main() -> int:
    sys.path.insert(0, str(PKG / "src"))
    import lamague_codec as codec

    packets = [json.loads(l) for l in (PKG / "corpus" / "packets.jsonl").read_text().splitlines() if l.strip()]
    codebook = json.loads((PKG / "corpus" / "codebook.json").read_text())

    raw = [canonical(p) for p in packets]
    encoded: List[bytes] = []
    for p in packets:
        try:
            out = codec.encode(p, codebook)
        except TypeError:
            out = codec.encode(p)
        encoded.append(out if isinstance(out, bytes) else str(out).encode("utf-8"))

    json_bytes = sum(len(b) for b in raw)
    l1d_bytes = sum(len(b) for b in encoded)
    json_gz = sum(len(gzip.compress(b, 9)) for b in raw)
    l1d_gz = sum(len(gzip.compress(b, 9)) for b in encoded)

    print("=" * 72)
    print("COMPRESSION vs GENERAL-PURPOSE COMPRESSORS")
    print("=" * 72)
    print(f"corpus: {len(packets)} structured semantic packets from the frozen benchmark\n")
    print(f"  {'representation':<34}{'bytes':>10}{'vs JSON':>10}")
    print(f"  {'canonical minified JSON':<34}{json_bytes:>10}{'—':>10}")

    for name, fn in (("gzip -9, per packet", lambda b: gzip.compress(b, 9)),
                     ("bz2, per packet", bz2.compress),
                     ("lzma, per packet", lzma.compress)):
        n = sum(len(fn(b)) for b in raw)
        print(f"  {name:<34}{n:>10}{1 - n / json_bytes:>9.1%}")

    print(f"  {'LAMAGUE L1D (codec alone)':<34}{l1d_bytes:>10}{1 - l1d_bytes / json_bytes:>9.1%}")
    print(f"  {'LAMAGUE L1D + gzip -9':<34}{l1d_gz:>10}{1 - l1d_gz / json_bytes:>9.1%}")

    print("\n  VERDICT")
    print(f"    gzip alone beats the codec alone by "
          f"{(1 - json_gz / json_bytes) - (1 - l1d_bytes / json_bytes):.1%} — "
          f"do not publish the codec's raw ratio as a headline.")
    print(f"    L1D + gzip is {1 - l1d_gz / json_gz:.1%} smaller than JSON + gzip.")
    print(f"    They compose: the schema removes redundancy gzip would have to discover.")

    # The part no compressor does.
    mut = [json.loads(l) for l in (PKG / "reports" / "mutation_results.jsonl").read_text().splitlines() if l.strip()]
    matched = sum(1 for m in mut if m["matched"])
    classes = sorted({m["mutation"] for m in mut})
    print(f"\n  WHAT GZIP CANNOT DO AT ANY RATIO")
    print(f"    protected-field mutations correctly classified: {matched}/{len(mut)}")
    print(f"    across {len(classes)} classes:")
    for c in classes:
        print(f"      {c}")
    print("    gzip compresses a record with the dissent deleted and says nothing.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
