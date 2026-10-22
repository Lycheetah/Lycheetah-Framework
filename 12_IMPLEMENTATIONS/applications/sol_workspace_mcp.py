"""
Sol Workspace MCP Server
========================
Gives Sol direct tool access to the Sol project workspace — tasks, version,
gate state — without reading files manually each session.

TOOLS:
  get_open_tasks()           -- all open tasks as structured list
  get_gate_status()          -- which gates are done/open
  complete_task(id)          -- mark task done in TASKS.md
  add_task(subject, gate, file, notes) -- add new task, auto-increments HWM
  get_app_version()          -- current version from app.json
  bump_version(type)         -- patch/minor/major bump in app.json + settings.tsx

Every write is checked before anything is written. A refused or failed call
raises, so the MCP client receives a result marked isError instead of an error
message dressed as success.

PORT: 8766 (Guard runs on 8765)

Add to ~/.claude/settings.json:
  "sol-workspace": { "type": "sse", "url": "http://localhost:8766/sse" }
"""

import functools
import json
import os
import re
import sys
from pathlib import Path
from typing import Literal

# ─── Paths ────────────────────────────────────────────────────
# Both of these are SEPARATE repositories. Resolved through the environment so
# the server runs from any checkout instead of one machine's home directory.
WORKSPACE   = Path(os.environ.get("SOL_WORKSPACE", Path.home()))
VERGE_CODEX = Path(os.environ.get("VERGE_CODEX", WORKSPACE / "LYCHEETAH_VERGE_CODEX"))
MOBILE_APP  = Path(os.environ.get("MOBILE_APP", WORKSPACE / "Lycheetah-Mobile--SOLORIGINARCHIVE"))

TASKS_MD     = VERGE_CODEX / "TASKS.md"
APP_JSON     = MOBILE_APP / "app.json"
SETTINGS_TSX = MOBILE_APP / "app" / "(tabs)" / "settings.tsx"

ENCODING = "utf-8"
GATE_HEADERS = {
    "3": "## GATE 3",
    "gate3": "## GATE 3",
    "4": "## GATE 4",
    "gate4": "## GATE 4",
    "post": "## POST-LAUNCH",
    "postlaunch": "## POST-LAUNCH",
}
BUMP_TYPES = ("patch", "minor", "major")
# One pattern both reads and rewrites the high-water mark, so a write can never
# leave a line that the next read fails to find.
HWM_PATTERN = re.compile(r"\*\*#(\d+)\*\*[^\n]*high-water mark")
SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)")

# The [mcp] extra pins MCP SDK 2.x, whose server is MCPServer. SDK 1.x ships the
# same decorator API as FastMCP; the 1.x low-level Server.list_tools() decorators
# this module once used were removed in 2.x, so one tool table serves both.
try:
    from mcp.server import MCPServer
    from mcp.server.mcpserver.exceptions import ToolError
    MCP_SDK_MAJOR = 2
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP as MCPServer
        from mcp.server.fastmcp.exceptions import ToolError
        MCP_SDK_MAJOR = 1
    except ImportError:
        MCPServer = None  # type: ignore[assignment,misc]
        ToolError = RuntimeError  # type: ignore[assignment,misc]
        MCP_SDK_MAJOR = 0
MCP_AVAILABLE = MCPServer is not None


# ─── File helpers ─────────────────────────────────────────────

def _read(path: Path) -> str:
    return path.read_text(encoding=ENCODING)


def _write(path: Path, text: str) -> None:
    """Replace a file in one step, so an interrupted write never leaves half a file."""
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text, encoding=ENCODING)
    os.replace(tmp, path)


# ─── TASKS.md helpers ─────────────────────────────────────────

def _parse_tasks(text: str) -> list[dict]:
    """Parse all task rows from TASKS.md table format."""
    tasks = []
    current_gate = ""
    for line in text.splitlines():
        gate_match = re.match(r"^## (GATE \d+ —[^\n]+|POST-LAUNCH[^\n]*)", line)
        if gate_match:
            current_gate = gate_match.group(1).strip()
        row_match = re.match(r"\|\s*(\d+)\s*\|([^|]+)\|([^|]*)\|([^|]*)\|([^|]+)\|", line)
        if row_match:
            num, task, file_, fable, status = [x.strip() for x in row_match.groups()]
            tasks.append({
                "id": int(num),
                "task": task,
                "file": file_,
                "fable_ref": fable,
                "status": "open" if "open" in status else "done",
                "gate": current_gate,
            })
    return tasks


def _high_water_mark(text: str) -> "re.Match[str]":
    marks = list(HWM_PATTERN.finditer(text))
    if len(marks) != 1:
        raise ValueError(
            "TASKS.md must record exactly one high-water mark line, e.g. "
            f"'**#91** (current high-water mark)'; found {len(marks)}. "
            "Refusing to guess the next task id."
        )
    return marks[0]


def _get_hwm(text: str) -> int:
    """Extract current high-water mark from TASKS.md."""
    return int(_high_water_mark(text).group(1))


def _gate_header(gate: str) -> str:
    key = str(gate).lower().replace("-", "").replace("_", "").replace(" ", "")
    if key not in GATE_HEADERS:
        raise ValueError(f"Unknown gate {gate!r}; expected '3', '4' or 'post'.")
    return GATE_HEADERS[key]


def _insertion_index(lines: list[str], header: str) -> int:
    """Index just after the last table line of the section named by header.

    The header must match exactly: '## GATE 3' never matches '## GATE 30'.
    """
    pattern = re.compile(rf"{re.escape(header)}(?!\d)")
    starts = [i for i, line in enumerate(lines) if pattern.match(line)]
    if len(starts) != 1:
        raise ValueError(f"TASKS.md must contain exactly one '{header}' section; found {len(starts)}.")
    last_table_line = None
    for i in range(starts[0] + 1, len(lines)):
        if lines[i].startswith("## "):
            break
        if lines[i].lstrip().startswith("|"):
            last_table_line = i
    if last_table_line is None:
        raise ValueError(f"Section '{header}' has no task table to add a row to.")
    return last_table_line + 1


def _cell(value: str, name: str) -> str:
    """A table cell: no pipe or line break, which would rewrite the table itself."""
    value = str(value).strip()
    if "|" in value or "\n" in value or "\r" in value:
        raise ValueError(f"{name} must not contain '|' or line breaks; they would rewrite the task table.")
    return value


def get_open_tasks_impl() -> str:
    text = _read(TASKS_MD)
    tasks = [t for t in _parse_tasks(text) if t["status"] == "open"]
    if not tasks:
        return "No open tasks."
    lines = ["OPEN TASKS:\n"]
    for t in tasks:
        lines.append(f"  #{t['id']} [{t['gate']}] — {t['task']}")
        if t["file"]:
            lines.append(f"       file: {t['file']}")
    return "\n".join(lines)


def get_gate_status_impl() -> str:
    text = _read(TASKS_MD)
    tasks = _parse_tasks(text)
    gates: dict[str, list] = {}
    for t in tasks:
        gates.setdefault(t["gate"], []).append(t)
    lines = ["GATE STATUS:\n"]
    for gate, ts in gates.items():
        total = len(ts)
        done = sum(1 for t in ts if t["status"] == "done")
        pct = int(done / total * 100) if total else 0
        status = "✅ COMPLETE" if done == total else f"  {done}/{total} done ({pct}%)"
        open_ids = [f"#{t['id']}" for t in ts if t["status"] == "open"]
        line = f"  {gate}: {status}"
        if open_ids:
            line += f"  — open: {', '.join(open_ids)}"
        lines.append(line)
    return "\n".join(lines)


def complete_task_impl(task_id: int) -> str:
    if isinstance(task_id, bool) or not isinstance(task_id, int):
        raise ValueError(f"task_id must be an integer; got {task_id!r}")
    text = _read(TASKS_MD)
    pattern = rf"^(\|\s*{task_id}\s*\|[^|\n]*\|[^|\n]*\|[^|\n]*\|)\s*\*\*open\*\*\s*(\|)"
    new_text, n = re.subn(pattern, r"\1 ✅ done \2", text, flags=re.M)
    if n == 0:
        if re.search(rf"^\|\s*{task_id}\s*\|", text, re.M):
            raise ValueError(f"Task #{task_id} is in TASKS.md but not marked **open**; nothing changed.")
        raise ValueError(f"Task #{task_id} is not in TASKS.md.")
    if n > 1:
        raise ValueError(f"Task id #{task_id} is open on {n} rows; repair the duplicate ids by hand first.")
    _write(TASKS_MD, new_text)
    return f"Task #{task_id} marked ✅ done in TASKS.md."


def add_task_impl(subject: str, gate: str, file_: str = "", notes: str = "") -> str:
    subject = _cell(subject, "subject")
    if not subject:
        raise ValueError("subject must not be empty.")
    file_ = _cell(file_, "file")
    header = _gate_header(gate)

    text = _read(TASKS_MD)
    mark = _high_water_mark(text)
    used = [t["id"] for t in _parse_tasks(text)]
    # The mark guards ids of archived rows; the rows guard against a stale mark.
    new_id = max([int(mark.group(1)), *used]) + 1

    text = text[:mark.start(1)] + str(new_id) + text[mark.end(1):]
    lines = text.splitlines()
    lines.insert(_insertion_index(lines, header), f"| {new_id} | {subject} | {file_} | — | **open** |")
    _write(TASKS_MD, "\n".join(lines) + ("\n" if text.endswith("\n") else ""))

    reply = f"Task #{new_id} added to {header[3:]}: {subject}.\nHigh-water mark → #{new_id}."
    if notes:
        reply += "\nNotes were not stored: the task table has no notes column."
    return reply


def get_app_version_impl() -> str:
    data = json.loads(_read(APP_JSON))
    version = data.get("expo", data).get("version")
    if not isinstance(version, str):
        raise ValueError("app.json has no version string.")
    return f"Sol app version: {version}"


def bump_version_impl(bump_type: str = "patch") -> str:
    if bump_type not in BUMP_TYPES:
        raise ValueError(f"bump_type must be one of {', '.join(BUMP_TYPES)}; got {bump_type!r}")
    data = json.loads(_read(APP_JSON))
    root = data.get("expo", data)
    current = root.get("version")
    match = SEMVER.fullmatch(current) if isinstance(current, str) else None
    if match is None:
        raise ValueError(f"app.json version {current!r} is not MAJOR.MINOR.PATCH.")
    major, minor, patch = (int(x) for x in match.groups())

    if bump_type == "major":
        major += 1; minor = 0; patch = 0
    elif bump_type == "minor":
        minor += 1; patch = 0
    else:
        patch += 1
    new_version = f"{major}.{minor}.{patch}"

    # Check both files before writing either, so a refusal leaves them agreeing.
    tsx = _read(SETTINGS_TSX)
    label = re.compile(rf"(?<![\w.])v{re.escape(current)}(?![\w.])")
    shown = len(label.findall(tsx))
    if shown != 1:
        raise ValueError(
            f"{SETTINGS_TSX.name} must show 'v{current}' exactly once to be bumped with "
            f"app.json; found {shown}. Nothing was written."
        )
    root["version"] = new_version
    _write(APP_JSON, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    _write(SETTINGS_TSX, label.sub(f"v{new_version}", tsx))

    return f"Version bumped: {current} → {new_version}\nUpdated: {APP_JSON.name} + {SETTINGS_TSX.name}"


# ─── MCP Server ───────────────────────────────────────────────
# Failures propagate: the SDK turns a raised exception into a result marked
# isError, which a returned "Error: ..." string never is. SDK 2.x withholds the
# text of any exception that is not a ToolError, so a deliberate refusal is
# re-raised as one and its reason reaches the client. The SDK builds each input
# schema from the signature, so the argument names below are the wire names.

def _refusals_reach_client(tool):
    @functools.wraps(tool)
    def wrapped(*args, **kwargs):
        try:
            return tool(*args, **kwargs)
        except (ValueError, OSError) as exc:
            raise ToolError(str(exc)) from exc
    return wrapped


def get_open_tasks() -> str:
    """List all open tasks from Sol TASKS.md with gate and file info."""
    return get_open_tasks_impl()


def get_gate_status() -> str:
    """Show which Sol gates are complete and which are open, with task counts."""
    return get_gate_status_impl()


def complete_task(task_id: int) -> str:
    """Mark a Sol task as done in TASKS.md by task ID number (e.g. 45)."""
    return complete_task_impl(task_id)


def add_task(subject: str, gate: str, file: str = "", notes: str = "") -> str:
    """Add a new task to TASKS.md. Auto-increments the high-water mark.

    gate is '3', '4' or 'post'; file is the optional target file. notes are not
    stored, because the task table has no notes column.
    """
    return add_task_impl(subject, gate, file, notes)


def get_app_version() -> str:
    """Get the current Sol app version from app.json."""
    return get_app_version_impl()


def bump_version(bump_type: Literal["patch", "minor", "major"]) -> str:
    """Bump the Sol app version in app.json and settings.tsx."""
    return bump_version_impl(bump_type)


MCP_TOOLS = (get_open_tasks, get_gate_status, complete_task, add_task,
             get_app_version, bump_version)


def build_server():
    if not MCP_AVAILABLE:
        raise RuntimeError("mcp package not installed: pip install 'lycheetah-framework[mcp]'")
    server = MCPServer("sol-workspace")
    for tool in MCP_TOOLS:
        server.tool(name=tool.__name__)(_refusals_reach_client(tool))
    return server


# ─── Entry point ──────────────────────────────────────────────

def main_http(port: int = 8766):
    server = build_server()
    print(f"Sol Workspace MCP — http://localhost:{port}/sse", flush=True)
    if MCP_SDK_MAJOR >= 2:
        server.run("sse", host="127.0.0.1", port=port)
    else:
        server.settings.host = "127.0.0.1"
        server.settings.port = port
        server.run("sse")


if __name__ == "__main__":
    if not MCP_AVAILABLE:
        print("ERROR: mcp package not installed.", file=sys.stderr)
        sys.exit(1)
    port = 8766
    for arg in sys.argv[1:]:
        if arg.startswith("--port="):
            port = int(arg.split("=")[1])
    main_http(port)
