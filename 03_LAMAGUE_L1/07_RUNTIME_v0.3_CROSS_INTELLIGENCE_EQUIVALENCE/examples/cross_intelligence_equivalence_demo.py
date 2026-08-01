from __future__ import annotations

import json
from pathlib import Path

from lamague_runtime import BenchmarkRunner, ChallengePack


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    pack = ChallengePack.load(root / "benchmark" / "challenge_pack.json")
    report = BenchmarkRunner().run_directory(
        pack,
        root / "benchmark" / "sample_packets",
    )
    output = root / "benchmark" / "reports" / "sample_equivalence_report.json"
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
