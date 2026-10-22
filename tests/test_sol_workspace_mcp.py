"""sol_workspace_mcp writes: task ids, table placement, cell injection, version bumps, MCP errors."""
import json

import pytest

import lycheetah.applications.sol_workspace_mcp as sw

HWM_LINE = "Last issued id: **#91** (current high-water mark)\n\n"
BOARD = (
    "# TASKS\n\n" + HWM_LINE
    + "## GATE 3 — Ship\n\n"
    "| # | Task | File | Fable | Status |\n"
    "|---|---|---|---|---|\n"
    "| 90 | Wire the door | app/door.tsx | — | **open** |\n"
    "| 91 | Paint the sky | app/sky.tsx | — | ✅ done |\n\n"
    "## GATE 4 — Next\n\n"
    "| # | Task | File | Fable | Status |\n"
    "|---|---|---|---|---|\n"
    "| 85 | Tune the bell | | — | **open** |\n\n"
    "## POST-LAUNCH\n\n"
    "| # | Task | File | Fable | Status |\n"
    "|---|---|---|---|---|\n"
)


@pytest.fixture
def ws(tmp_path, monkeypatch):
    (tmp_path / "TASKS.md").write_text(BOARD, encoding="utf-8")
    monkeypatch.setattr(sw, "TASKS_MD", tmp_path / "TASKS.md")
    monkeypatch.setattr(sw, "APP_JSON", tmp_path / "app.json")
    monkeypatch.setattr(sw, "SETTINGS_TSX", tmp_path / "settings.tsx")
    return tmp_path


def board(ws):
    return (ws / "TASKS.md").read_text(encoding="utf-8")


def rows(ws):
    return sw._parse_tasks(board(ws))


def gates_of(ws, task):
    return [t["gate"] for t in rows(ws) if t["task"] == task]


def test_repeated_adds_never_reuse_an_id(ws):
    for k in range(3):
        sw.add_task_impl(f"Task {k}", "3")
    ids = [t["id"] for t in rows(ws)]
    assert len(ids) == len(set(ids))
    assert sw._get_hwm(board(ws)) == 94


def test_missing_high_water_mark_is_refused_without_writing(ws):
    (ws / "TASKS.md").write_text(BOARD.replace(HWM_LINE, ""), encoding="utf-8")
    before = board(ws)
    with pytest.raises(ValueError, match="high-water mark"):
        sw.add_task_impl("Guess my id", "3")
    assert board(ws) == before


def test_stale_high_water_mark_cannot_collide(ws):
    (ws / "TASKS.md").write_text(BOARD.replace("| 91 | Paint", "| 96 | Paint"), encoding="utf-8")
    assert "#97" in sw.add_task_impl("After the stale mark", "4")


def test_new_row_joins_its_table(ws):
    sw.add_task_impl("Place me", "3")
    lines = board(ws).splitlines()
    i = next(k for k, line in enumerate(lines) if "Place me" in line)
    assert lines[i - 1].startswith("| 91 |")
    assert gates_of(ws, "Place me") == ["GATE 3 — Ship"]


def test_first_row_of_an_empty_table(ws):
    sw.add_task_impl("First after launch", "post")
    assert gates_of(ws, "First after launch") == ["POST-LAUNCH"]
    assert board(ws).endswith("| 92 | First after launch |  | — | **open** |\n")


def test_gate_3_never_lands_in_gate_30(ws):
    later = ("## GATE 30 — Later\n\n| # | Task | File | Fable | Status |\n|---|---|---|---|---|\n"
             "| 70 | Someday | | — | **open** |\n\n")
    (ws / "TASKS.md").write_text(BOARD.replace("## GATE 4 — Next", later + "## GATE 4 — Next"), encoding="utf-8")
    sw.add_task_impl("Gate three only", "3")
    assert gates_of(ws, "Gate three only") == ["GATE 3 — Ship"]


@pytest.mark.parametrize("subject", ["Fix a | b", "Real task |  | — | **open** |\n| 999 | Injected"])
def test_table_breaking_subject_is_refused(ws, subject):
    before = board(ws)
    with pytest.raises(ValueError, match="line breaks"):
        sw.add_task_impl(subject, "3")
    assert board(ws) == before


def test_unknown_gate_is_refused(ws):
    before = board(ws)
    with pytest.raises(ValueError, match="Unknown gate"):
        sw.add_task_impl("Where am I", "5")
    assert board(ws) == before


def test_notes_are_not_reported_as_stored(ws):
    reply = sw.add_task_impl("With notes", "3", notes="remember the lamp")
    assert "not stored" in reply
    assert "remember the lamp" not in board(ws)


def test_complete_task_transitions_exactly_once(ws):
    assert "#90" in sw.complete_task_impl(90)
    assert [t["status"] for t in rows(ws) if t["id"] == 90] == ["done"]
    with pytest.raises(ValueError, match="not marked"):
        sw.complete_task_impl(90)
    with pytest.raises(ValueError, match="not in TASKS.md"):
        sw.complete_task_impl(404)


def write_app(ws, version="9.1.0", tsx='export const LABEL = "Sol v9.1.0";\n', name="Sol"):
    payload = {"expo": {"name": name, "version": version}}
    (ws / "app.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if tsx is not None:
        (ws / "settings.tsx").write_text(tsx, encoding="utf-8")


def app_version(ws):
    return json.loads((ws / "app.json").read_text(encoding="utf-8"))["expo"]["version"]


def test_bump_rejects_an_unknown_type(ws):
    write_app(ws)
    with pytest.raises(ValueError, match="bump_type"):
        sw.bump_version_impl("banana")
    assert app_version(ws) == "9.1.0"


@pytest.mark.parametrize("tsx", ['export const LABEL = "Sol";\n', None])
def test_bump_writes_nothing_unless_both_files_can_change(ws, tsx):
    write_app(ws, tsx=tsx)
    with pytest.raises((ValueError, FileNotFoundError)):
        sw.bump_version_impl("patch")
    assert app_version(ws) == "9.1.0"


def test_bump_changes_only_the_app_version(ws):
    write_app(ws, tsx='// built against sdk v51.0.0\nexport const LABEL = "Sol v9.1.0";\n', name="Sól")
    assert "9.1.0 → 9.2.0" in sw.bump_version_impl("minor")
    assert app_version(ws) == "9.2.0"
    assert (ws / "settings.tsx").read_text(encoding="utf-8") == (
        '// built against sdk v51.0.0\nexport const LABEL = "Sol v9.2.0";\n')
    assert '"Sól"' in (ws / "app.json").read_text(encoding="utf-8")


def _is_error(result):
    return getattr(result, "is_error", getattr(result, "isError", None))


@pytest.mark.skipif(not sw.MCP_AVAILABLE, reason="MCP low-level Server API unavailable")
def test_failed_tool_calls_reach_the_client_as_errors(ws):
    import anyio

    # The declared extra is MCP SDK 2.x, whose in-process client is mcp.Client. The 1.x
    # helper is kept so the test still runs where only 1.x is installed.
    try:
        from mcp import Client

        def connect():
            return Client(sw.build_server())
    except ImportError:
        from mcp.shared.memory import create_connected_server_and_client_session

        def connect():
            return create_connected_server_and_client_session(sw.build_server())

    async def call(name, arguments):
        async with connect() as client:
            return await client.call_tool(name, arguments)

    refused = anyio.run(call, "add_task", {"subject": "x", "gate": "5"})
    assert _is_error(refused) is True
    assert "Unknown gate" in refused.content[0].text
    listed = anyio.run(call, "get_open_tasks", {})
    assert _is_error(listed) is False
    assert "#90" in listed.content[0].text
