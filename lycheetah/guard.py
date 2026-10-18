"""Lycheetah Guard module entrypoint.

Supports direct execution via:
    python -m lycheetah.guard [run|check|status|authority|mcp]
"""

from __future__ import annotations

import sys

from .cli import guard_cli

if __name__ == "__main__":
    guard_cli(sys.argv[1:])
