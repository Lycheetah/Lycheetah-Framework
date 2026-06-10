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
  bump_version(type)         -- patch/minor bump in app.json + settings.tsx

PORT: 8766 (Guard runs on 8765)

Add to ~/.claude/settings.json:
  "sol-workspace": { "type": "sse", "url": "http://localhost:8766/sse" }
"""

import json
import re
import sys
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────
TASKS_MD   = Path("/home/guestpc/LYCHEETAH_VERGE_CODEX/TASKS.md")
APP_JSON   = Path("/home/guestpc/Lycheetah-Mobile--SOLORIGINARCHIVE/app.json")
SETTINGS_TSX = Path("/home/guestpc/Lycheetah-Mobile--SOLORIGINARCHIVE/app/(tabs)/settings.tsx")

try:
    from mcp.server import Server
    from mcp.server.sse import SseServerTransport
    from mcp import types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


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


def _get_hwm(text: str) -> int:
    """Extract current high-water mark from TASKS.md."""
    m = re.search(r"\*\*#(\d+)\*\*.*high-water mark", text)
    return int(m.group(1)) if m else 91


def get_open_tasks_impl() -> str:
    text = TASKS_MD.read_text()
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
    text = TASKS_MD.read_text()
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
    text = TASKS_MD.read_text()
    pattern = rf"(\|\s*{task_id}\s*\|[^|]*\|[^|]*\|[^|]*\|)\s*\*\*open\*\*\s*(\|)"
    new_text, n = re.subn(pattern, r"\1 ✅ done \2", text)
    if n == 0:
        # Try to find the task at all
        if re.search(rf"\|\s*{task_id}\s*\|", text):
            return f"Task #{task_id} found but not marked open — already done?"
        return f"Task #{task_id} not found in TASKS.md."
    TASKS_MD.write_text(new_text)
    return f"Task #{task_id} marked ✅ done in TASKS.md."


def add_task_impl(subject: str, gate: str, file_: str = "", notes: str = "") -> str:
    text = TASKS_MD.read_text()
    hwm = _get_hwm(text)
    new_id = hwm + 1

    # Find the gate section and append before its trailing blank line
    gate_patterns = {
        "3": "## GATE 3",
        "gate3": "## GATE 3",
        "4": "## GATE 4",
        "gate4": "## GATE 4",
        "post": "## POST-LAUNCH",
        "postlaunch": "## POST-LAUNCH",
    }
    target_header = gate_patterns.get(gate.lower().replace("-", "").replace(" ", ""), "## POST-LAUNCH")
    new_row = f"| {new_id} | {subject} | {file_} | — | **open** |"

    # Insert after the last row in the target gate section
    lines = text.splitlines()
    insert_at = None
    in_section = False
    for i, line in enumerate(lines):
        if target_header in line:
            in_section = True
        elif in_section and line.startswith("## "):
            insert_at = i
            break
        elif in_section and re.match(r"\|\s*\d+\s*\|", line):
            insert_at = i + 1

    if insert_at is None:
        return f"Could not find gate section '{gate}' in TASKS.md."

    lines.insert(insert_at, new_row)

    # Update HWM
    new_text = "\n".join(lines)
    new_text = re.sub(
        r"\*\*#\d+\*\* \(.*?high-water mark\)",
        f"**#{new_id}** (updated) — high-water mark",
        new_text
    )
    TASKS_MD.write_text(new_text)
    note_str = f" Notes: {notes}" if notes else ""
    return f"Task #{new_id} added: {subject}.{note_str}\nHigh-water mark → #{new_id}."


def get_app_version_impl() -> str:
    data = json.loads(APP_JSON.read_text())
    version = data.get("expo", data).get("version", "unknown")
    return f"Sol app version: {version}"


def bump_version_impl(bump_type: str = "patch") -> str:
    data = json.loads(APP_JSON.read_text())
    root = data.get("expo", data)
    current = root.get("version", "0.0.0")
    major, minor, patch = (int(x) for x in current.split("."))

    if bump_type == "major":
        major += 1; minor = 0; patch = 0
    elif bump_type == "minor":
        minor += 1; patch = 0
    else:
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    root["version"] = new_version
    APP_JSON.write_text(json.dumps(data, indent=2) + "\n")

    # Update settings.tsx
    tsx = SETTINGS_TSX.read_text()
    new_tsx = re.sub(
        r"v\d+\.\d+\.\d+",
        f"v{new_version}",
        tsx,
        count=1
    )
    SETTINGS_TSX.write_text(new_tsx)

    return f"Version bumped: {current} → {new_version}\nUpdated: app.json + settings.tsx"


# ─── MCP Server ───────────────────────────────────────────────

def build_server() -> "Server":
    server = Server("sol-workspace")

    @server.list_tools()
    async def list_tools():
        return [
            types.Tool(
                name="get_open_tasks",
                description="List all open tasks from Sol TASKS.md with gate and file info.",
                inputSchema={"type": "object", "properties": {}}
            ),
            types.Tool(
                name="get_gate_status",
                description="Show which Sol gates are complete and which are open, with task counts.",
                inputSchema={"type": "object", "properties": {}}
            ),
            types.Tool(
                name="complete_task",
                description="Mark a Sol task as done in TASKS.md by task ID number.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer", "description": "The task number (e.g. 45)"}
                    },
                    "required": ["task_id"]
                }
            ),
            types.Tool(
                name="add_task",
                description="Add a new task to TASKS.md. Auto-increments the high-water mark.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string", "description": "Task description"},
                        "gate": {"type": "string", "description": "Gate: '3', '4', or 'post'"},
                        "file": {"type": "string", "description": "Target file (optional)"},
                        "notes": {"type": "string", "description": "Extra notes (optional)"}
                    },
                    "required": ["subject", "gate"]
                }
            ),
            types.Tool(
                name="get_app_version",
                description="Get the current Sol app version from app.json.",
                inputSchema={"type": "object", "properties": {}}
            ),
            types.Tool(
                name="bump_version",
                description="Bump the Sol app version in app.json and settings.tsx.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "bump_type": {
                            "type": "string",
                            "enum": ["patch", "minor", "major"],
                            "description": "Which part to increment"
                        }
                    },
                    "required": ["bump_type"]
                }
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "get_open_tasks":
                result = get_open_tasks_impl()
            elif name == "get_gate_status":
                result = get_gate_status_impl()
            elif name == "complete_task":
                result = complete_task_impl(int(arguments["task_id"]))
            elif name == "add_task":
                result = add_task_impl(
                    arguments["subject"],
                    arguments["gate"],
                    arguments.get("file", ""),
                    arguments.get("notes", "")
                )
            elif name == "get_app_version":
                result = get_app_version_impl()
            elif name == "bump_version":
                result = bump_version_impl(arguments.get("bump_type", "patch"))
            else:
                result = f"Unknown tool: {name}"
        except Exception as e:
            result = f"Error: {e}"
        return [types.TextContent(type="text", text=result)]

    return server


# ─── Entry point ──────────────────────────────────────────────

def main_http(port: int = 8766):
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import Response
    from starlette.routing import Mount, Route
    import uvicorn

    server = build_server()
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as (read_stream, write_stream):
            await server.run(
                read_stream, write_stream,
                server.create_initialization_options()
            )
        return Response()

    app = Starlette(routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ])

    print(f"Sol Workspace MCP — http://localhost:{port}/sse", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    if not MCP_AVAILABLE:
        print("ERROR: mcp package not installed.", file=sys.stderr)
        sys.exit(1)
    port = 8766
    for arg in sys.argv[1:]:
        if arg.startswith("--port="):
            port = int(arg.split("=")[1])
    main_http(port)
