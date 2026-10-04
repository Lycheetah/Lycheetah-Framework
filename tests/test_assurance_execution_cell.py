import os
from pathlib import Path
import tempfile

import pytest

from lycheetah.assurance.execution_cell import ExecutionCell, ExecutionCellSpec


@pytest.fixture
def available_cell():
    status = ExecutionCell.availability(active_probe=True)
    if not status.available:
        pytest.skip(status.reason)
    return ExecutionCell()


def test_static_availability_shape():
    status = ExecutionCell.availability(active_probe=False)
    assert isinstance(status.available, bool)
    assert status.reason


def test_workspace_write_root_read_only_network_and_data_mask(available_cell):
    with tempfile.TemporaryDirectory(prefix="cell-work-") as td:
        workspace = Path(td)
        sibling = workspace.parent / f"{workspace.name}-SECRET"
        sibling.write_text("SECRET", encoding="utf-8")
        try:
            script = r"""
from pathlib import Path
import os, socket, subprocess
Path("out.txt").write_text("ok", encoding="utf-8")
print("WORK_WRITE=" + Path("out.txt").read_text())
try:
    Path("/etc/lycheetah-cell-should-fail").write_text("x")
    print("ROOT_WRITE=BAD")
except Exception:
    print("ROOT_WRITE=BLOCKED")
print("SIBLING_VISIBLE=" + str(Path(%r).exists()))
print("AMBIENT_SECRET=" + str(os.getenv("LYCHEETAH_TEST_SECRET")))
try:
    s=socket.socket(); s.settimeout(.5)
    s.connect(("1.1.1.1", 53))
    print("NETWORK=BAD")
except Exception:
    print("NETWORK=BLOCKED")
mount = subprocess.run(
    ["mount","-o","remount,rw","/"],
    capture_output=True,text=True
)
print("REMOUNT_RC=" + str(mount.returncode))
""" % str(sibling)
            old = os.environ.get("LYCHEETAH_TEST_SECRET")
            os.environ["LYCHEETAH_TEST_SECRET"] = "DO_NOT_LEAK"
            try:
                result = available_cell.run(
                    ExecutionCellSpec(
                        str(workspace),
                        ("python3", "-c", script),
                        timeout_seconds=10,
                    )
                )
            finally:
                if old is None:
                    os.environ.pop("LYCHEETAH_TEST_SECRET", None)
                else:
                    os.environ["LYCHEETAH_TEST_SECRET"] = old

            assert result.succeeded, result.stderr
            assert "WORK_WRITE=ok" in result.stdout
            assert "ROOT_WRITE=BLOCKED" in result.stdout
            assert "SIBLING_VISIBLE=False" in result.stdout
            assert "AMBIENT_SECRET=None" in result.stdout
            assert "NETWORK=BLOCKED" in result.stdout
            assert "REMOUNT_RC=" in result.stdout
            remount_line = next(
                line for line in result.stdout.splitlines()
                if line.startswith("REMOUNT_RC=")
            )
            assert remount_line != "REMOUNT_RC=0"
            assert (workspace/"out.txt").read_text() == "ok"
        finally:
            sibling.unlink(missing_ok=True)


def test_explicit_environment_is_available_but_ambient_is_not(available_cell):
    with tempfile.TemporaryDirectory(prefix="cell-env-") as td:
        result = available_cell.run(
            ExecutionCellSpec(
                td,
                (
                    "python3",
                    "-c",
                    "import os; print(os.getenv('EXPLICIT')); "
                    "print(os.getenv('PATH')); print(os.getenv('HOME'))",
                ),
                env={"EXPLICIT": "yes"},
                timeout_seconds=10,
            )
        )
        assert result.succeeded
        lines = result.stdout.splitlines()
        assert lines[0] == "yes"
        assert "/usr/bin" in lines[1]
        assert lines[2] == "/tmp"


def test_timeout_kills_cell(available_cell):
    with tempfile.TemporaryDirectory(prefix="cell-time-") as td:
        result = available_cell.run(
            ExecutionCellSpec(
                td,
                ("python3", "-c", "import time; time.sleep(5)"),
                timeout_seconds=0.3,
            )
        )
        assert result.timed_out
        assert result.ready
        assert not result.succeeded


def test_workspace_must_exist(available_cell):
    with pytest.raises(ValueError):
        available_cell.run(
            ExecutionCellSpec(
                "/definitely/not/a/real/workspace",
                ("python3", "-c", "print('x')"),
            )
        )
