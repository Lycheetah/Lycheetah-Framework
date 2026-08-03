from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .engine import ClaimEvidence, PressureConfig, TruthPressureError, evaluate_claim


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Truth Pressure v0.1 — Evidence-Weighted Revision Pressure")
    parser.add_argument("packet", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.packet.read_text(encoding="utf-8"))
        config = PressureConfig(**payload.get("config", {}))
        claim = ClaimEvidence(**payload["claim"])
        foundation = ClaimEvidence(**payload["foundation"]) if payload.get("foundation") else None
        result = evaluate_claim(claim, foundation=foundation, config=config).export()
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
        return 0
    except (OSError, KeyError, TypeError, json.JSONDecodeError, TruthPressureError) as exc:
        print(json.dumps({
            "truth_pressure_version": "0.1.0",
            "status": "REJECTED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
