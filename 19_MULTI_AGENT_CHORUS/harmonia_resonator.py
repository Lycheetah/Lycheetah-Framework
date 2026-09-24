#!/usr/bin/env python3
"""
HarmoniaResonator — individual chorus agent module.

Thin re-export from remaining_agents.py (single-file origin).
Documented in AGENTS_MANIFEST.md and remaining_agents.py docstring.
"""

from remaining_agents import HarmoniaResonator

__all__ = ["HarmoniaResonator"]


if __name__ == "__main__":
    agent = HarmoniaResonator()
    print(f"HarmoniaResonator online: {agent}")
