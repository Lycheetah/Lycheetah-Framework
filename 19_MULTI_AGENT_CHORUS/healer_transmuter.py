#!/usr/bin/env python3
"""
HealerTransmuter — individual chorus agent module.

Thin re-export from remaining_agents.py (single-file origin).
Documented in AGENTS_MANIFEST.md and remaining_agents.py docstring.
"""

from remaining_agents import HealerTransmuter

__all__ = ["HealerTransmuter"]


if __name__ == "__main__":
    agent = HealerTransmuter()
    print(f"HealerTransmuter online: {agent}")
