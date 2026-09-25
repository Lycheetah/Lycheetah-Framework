#!/usr/bin/env python3
"""
SolsticeIlluminator — individual chorus agent module.

Thin re-export from remaining_agents.py (single-file origin).
Documented in AGENTS_MANIFEST.md and remaining_agents.py docstring.
"""

from remaining_agents import SolsticeIlluminator

__all__ = ["SolsticeIlluminator"]


if __name__ == "__main__":
    agent = SolsticeIlluminator()
    print(f"SolsticeIlluminator online: {agent}")
