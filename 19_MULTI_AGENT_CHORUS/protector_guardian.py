#!/usr/bin/env python3
"""
ProtectorGuardian — individual chorus agent module.

Thin re-export from remaining_agents.py (single-file origin).
Documented in AGENTS_MANIFEST.md and remaining_agents.py docstring.
"""

from remaining_agents import ProtectorGuardian

__all__ = ["ProtectorGuardian"]


if __name__ == "__main__":
    agent = ProtectorGuardian()
    print(f"ProtectorGuardian online: {agent}")
