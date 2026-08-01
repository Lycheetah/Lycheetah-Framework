from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .bridge import BridgeError, analyze_dict


def main(argv=None):
    p = argparse.ArgumentParser(description="LAMAGUE v0.7 temporal evidence bridge")
    p.add_argument("packet", type=Path)
    p.add_argument("-o", "--output", type=Path)
    args = p.parse_args(argv)
    try:
        data = json.loads(args.packet.read_text(encoding="utf-8"))
        result = analyze_dict(data)
        text = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            args.output.write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return 0
    except (OSError, json.JSONDecodeError, BridgeError) as exc:
        print(json.dumps({"status":"REJECTED","error_type":type(exc).__name__,"error":str(exc)}, indent=2), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
