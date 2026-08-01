from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

from lamague_native import (
    parse_source,
    compile_program,
    NativeSyntaxError,
    NativeCompileError,
)

rows = []
for path in sorted((ROOT / "cases").glob("*.lmg")):
    try:
        result = compile_program(
            parse_source(path.read_text(encoding="utf-8"))
        ).to_dict()
        rows.append({
            "id": path.stem,
            "outcome": "PASS",
            "status": result["analysis"]["status"],
            "result": result,
        })
    except (NativeSyntaxError, NativeCompileError) as exc:
        rows.append({
            "id": path.stem,
            "outcome": "REJECTED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        })

(ROOT / "report.json").write_text(
    json.dumps(rows, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(json.dumps({
    "cases": len(rows),
    "pass": sum(x["outcome"] == "PASS" for x in rows),
    "rejected": sum(x["outcome"] == "REJECTED" for x in rows),
}, indent=2))
