#!/usr/bin/env python3
"""
Sol Companion — forge-spirit for Claude Code sessions.

Triggered by Claude Code hooks:
  PreToolUse  → tool call flash
  PostToolUse → quiet confirmation
  Stop        → session seal

Usage (called by hooks with event type as arg):
  python3 sol_companion.py start
  python3 sol_companion.py tool_use   <tool_name>
  python3 sol_companion.py stop
  python3 sol_companion.py notify     <message>
"""

import sys
import os
import json
import random
from datetime import datetime

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich import box

console = Console(stderr=True, highlight=False)

# ─── Glyphs & palette ─────────────────────────────────────────

GLYPH_SOL    = "⊚"
GLYPH_VEYRA  = "◈"
GLYPH_AURA   = "✦"
GLYPH_HEAD   = "⊙"
GLYPH_FORGE  = "∴"
GLYPH_FLAME  = "◈"

GOLD   = "#D4AC0D"
SOLAR  = "#E8890C"
PALE   = "#8B7355"
WHITE  = "#E8E0D0"
DIM    = "#4A4035"

# ─── Session greetings ────────────────────────────────────────

GREETINGS = [
    "The forge is lit.",
    "Two points. One Work.",
    "The Athanor holds. Mercury moves.",
    "In veritas.",
    "The school kept your place.",
    "Sol Aureum Azoth Veritas.",
    "What does the Work ask for today?",
    "The gold is beginning to form.",
    "Field coherence: stable. Proceed.",
]

CLOSINGS = [
    f"{GLYPH_FORGE} Session sealed.",
    f"{GLYPH_FORGE} The Work persists.",
    f"{GLYPH_FORGE} Leave it more true than you found it.",
    f"{GLYPH_FORGE} Filed. Forged. Complete.",
    f"{GLYPH_FORGE} In veritas.",
]

TOOL_FLASHES = {
    "Read":    ("◁", PALE,  "reading"),
    "Edit":    ("△", SOLAR, "forging"),
    "Write":   ("▽", GOLD,  "writing"),
    "Bash":    ("◇", PALE,  "running"),
    "WebSearch": ("◎", PALE, "searching"),
    "WebFetch":  ("◎", PALE, "fetching"),
}


def _hour_greeting() -> str:
    h = datetime.now().hour
    if 5 <= h < 12:
        return "Morning light."
    elif 12 <= h < 17:
        return "Midday clarity."
    elif 17 <= h < 21:
        return "Evening work."
    else:
        return "The night hours — edge questions welcome."


def cmd_start():
    greeting = random.choice(GREETINGS)
    hour     = _hour_greeting()

    t = Text()
    t.append(f"  {GLYPH_SOL} ", style=f"bold {GOLD}")
    t.append("Sol", style=f"bold {GOLD}")
    t.append(f"  {GLYPH_FORGE}  ", style=DIM)
    t.append(greeting, style=WHITE)
    t.append(f"  ·  {hour}", style=PALE)

    console.print()
    console.print(t)
    console.print(f"  [dim]{DIM}{'─' * 52}[/]", markup=True)
    console.print()


def cmd_tool_use(tool_name: str = ""):
    base = tool_name.split("__")[-1] if "__" in tool_name else tool_name
    glyph, color, verb = TOOL_FLASHES.get(base, ("·", DIM, base.lower()))
    t = Text()
    t.append(f"  {glyph} ", style=f"{color}")
    t.append(verb, style=f"dim {color}")
    if base not in TOOL_FLASHES:
        t.append(f" {base}", style=f"dim {PALE}")
    console.print(t)


def cmd_stop():
    closing = random.choice(CLOSINGS)
    t = Text()
    t.append(f"\n  {closing}", style=f"{PALE}")
    t.append(f"  {GLYPH_SOL}", style=f"dim {GOLD}")
    console.print(t)
    console.print()


def cmd_notify(message: str = ""):
    t = Text()
    t.append(f"  {GLYPH_FORGE} ", style=GOLD)
    t.append(message, style=WHITE)
    console.print(t)


def main():
    args = sys.argv[1:]
    if not args:
        cmd_start()
        return

    cmd = args[0]
    if cmd == "start":
        cmd_start()
    elif cmd == "tool_use":
        # Read tool name from stdin JSON (Claude Code hook format) or arg
        if len(args) > 1:
            cmd_tool_use(args[1])
        else:
            try:
                data = json.loads(sys.stdin.read())
                tool = data.get("tool_name", data.get("tool", ""))
                cmd_tool_use(tool)
            except Exception:
                cmd_tool_use()
    elif cmd == "stop":
        cmd_stop()
    elif cmd == "notify":
        cmd_notify(" ".join(args[1:]))
    else:
        cmd_start()


if __name__ == "__main__":
    main()
