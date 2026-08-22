#!/usr/bin/env python3
"""Cold-room acceptance for the base wheel without optional extras."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def console(name: str) -> subprocess.CompletedProcess[str]:
    executable = Path(sys.executable).parent / name
    require(executable.is_file(), f"missing console script: {executable}")
    return subprocess.run(
        [str(executable)],
        check=False,
        capture_output=True,
        text=True,
    )


def main() -> int:
    import lycheetah
    from lycheetah.applications import lycheetah_guard_mcp, web_demo
    from lycheetah.assurance import AssuranceRuntime

    repo_root = Path(__file__).resolve().parents[1]
    installed_path = Path(lycheetah.__file__).resolve()
    require(repo_root not in installed_path.parents, "package resolved from checkout")
    require(lycheetah.check("Offer reversible options.").alignment_percent >= 0, "API failed")
    require(AssuranceRuntime().evaluate_tool("order.read", {}).verify().valid, "receipt failed")

    require(web_demo.FLASK_AVAILABLE is False, "base wheel unexpectedly contains Flask")
    require(web_demo.app is None, "web app should be unavailable without Flask")
    require(
        lycheetah_guard_mcp.MCP_AVAILABLE is False,
        "base wheel unexpectedly contains MCP",
    )

    web_result = console("lycheetah-web")
    guard_result = console("lycheetah-guard")
    require(web_result.returncode != 0 and "[web]" in web_result.stderr, "web extra error failed")
    require(
        guard_result.returncode != 0 and "[mcp]" in guard_result.stderr,
        "MCP extra error failed",
    )

    print(
        json.dumps(
            {
                "status": "PASS",
                "package": str(installed_path),
                "base_api": True,
                "web_extra_boundary": True,
                "mcp_extra_boundary": True,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
